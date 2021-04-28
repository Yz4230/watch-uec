# 電通大コロナ対策ページ監視bot
電通大のコロナ対策ページを監視して、更新があった場合にDiscordに通知します。

# セットアップ

## 必須要件
- `python >= 3.9`
- `pipenv >= 2020.11.15`

## 依存関係のインストール
```bash
pipenv install --deploy
```

## Webhook URLの設定
1. `main.py`と同じディレクトリに`.env`ファイルを作成します。
2. `DISCORD_WEBHOOK_URL`に使用するURLを指定してください。

設定の例↓

```.env:.env
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/XXX/XXX
```

## アプリのスタート
`main.py`のあるディレクトリで、以下を実行してください。

```bash
pipenv run start
```

# 定期実行するには
`pipenv run start`では、一回だけ監視処理を実行します。
そのため、定期実行するためには別途`cron`などで定期実行を指定する必要があります。
