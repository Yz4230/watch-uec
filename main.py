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
HISTORY_JSON_PATH = './history.json'
WATCH_TARGET_URL = 'https://www.uec.ac.jp/students/urgent_info/index.html'
DISCORD_MESSAGE_URL = '''\
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
        with open(HISTORY_JSON_PATH) as rf:
            return json.load(rf)
    except FileNotFoundError:
        return None


def save_history(history_content: str) -> None:
    with open(HISTORY_JSON_PATH, mode='w') as wf:
        json.dump({
            'content': history_content,
            'savedAt': get_iso_time()
        }, wf, ensure_ascii=False, indent=2)


def fetch_current_website_content() -> str:
    res = requests.get(WATCH_TARGET_URL)
    soup = BeautifulSoup(res.text, 'html.parser')
    text = soup.select_one('#primary').text
    text = re.sub(r'\n+', '\n', text)
    text = '\n'.join(map(lambda s: s.strip(), text.split()))
    return text


def compute_unified_diff(a: str, b: str) -> str:
    diff = unified_diff(a.split('\n'), b.split('\n'), n=2)
    return '\n'.join(diff)


def post_discord_message(message_content: str) -> None:
    requests.post(DISCORD_WEBHOOK_URL, json={
        'content': message_content,
        'embeds': [{
            'title': '新型コロナウイルスに係る在学生へのお知らせ│電気通信大学',
            'url': 'https://www.uec.ac.jp/students/urgent_info/index.html',
            'image': {
                'url': 'https://www.uec.ac.jp/images_new/mv/mv_corona_sp.jpg'
            }
        }]
    })


current_website_content = fetch_current_website_content()
last_website_content = history['content'] if (
    history := load_history()) else None

if last_website_content is None:
    save_history(current_website_content)
elif current_website_content != last_website_content:
    save_history(current_website_content)
    diff = compute_unified_diff(last_website_content, current_website_content)

    discord_message_content = DISCORD_MESSAGE_URL.format(diff=diff)
    post_discord_message(discord_message_content)
