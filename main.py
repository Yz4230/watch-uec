import re
import json
import os
import requests
import discord
from typing import Optional
from pprint import pprint
from difflib import unified_diff
from datetime import datetime
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv('.env')

DISCORD_WEBHOOK_URL = os.environ.get('DISCORD_WEBHOOK_URL')
HISTORY_PATH = './history.json'
TARGET_URL = 'https://www.uec.ac.jp/students/urgent_info/index.html'
MESSAGE_TEMPLATE = '''\
ページが更新されました。更新内容は次の通りです。
```diff
{diff}
```
ページのURLはこちらです。\
'''


def get_iso_time() -> str:
    return datetime.now().astimezone().isoformat()


def load_history() -> Optional[dict]:
    try:
        with open(HISTORY_PATH) as rf:
            return json.load(rf)
    except FileNotFoundError:
        return None


def save_history(history_content: str) -> None:
    with open(HISTORY_PATH, mode='w') as wf:
        json.dump({
            'content': history_content,
            'savedAt': get_iso_time()
        }, wf, ensure_ascii=False, indent=2)


def get_current_website_content() -> str:
    res = requests.get(TARGET_URL)
    soup = BeautifulSoup(res.text, 'html.parser')
    text = soup.select_one('#primary').text
    text = re.sub(r'\n+', '\n', text)
    text = '\n'.join(map(lambda s: s.strip(), text.split()))
    return text


def get_unified_diff(a: str, b: str) -> str:
    diff = unified_diff(a.split('\n'), b.split('\n'), n=2)
    return '\n'.join(diff)


def post_message(content: str) -> None:
    requests.post(DISCORD_WEBHOOK_URL, json={
        'content': content,
        'embeds': [{
            'title': '新型コロナウイルスに係る在学生へのお知らせ│電気通信大学',
            'url': 'https://www.uec.ac.jp/students/urgent_info/index.html',
            'image': {
                'url': 'https://www.uec.ac.jp/images_new/mv/mv_corona_sp.jpg'
            }
        }]
    })


content = get_current_website_content()
history_content = history['content'] if (history := load_history()) else ''

if content != history_content:
    save_history(content)
    diff = get_unified_diff(history_content, content)

    message_content = MESSAGE_TEMPLATE.format(diff=diff)
    print(message_content)
    post_message(message_content)
