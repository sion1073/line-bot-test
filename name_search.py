import os
import json
import yaml
import requests


LINE_CHANNEL_ACCESS_TOKEN = os.environ["LINE_CHANNEL_ACCESS_TOKEN"]


def message_to_line(id):
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer {' + LINE_CHANNEL_ACCESS_TOKEN + '}'
    }

    payload = {
        'to': id,
        'messages': [
            {
                'type': 'text',
                'text': "このトークはまだ名前登録がされていません。\n\n" +
                "カメラで撮影した写真を配信するためには、配信先のトークに名前登録が必要になります" +
                "名前を登録するときは、以下の形式でメッセージを送信してください。\n\n" +
                "名前登録「名前」\n\n通知を表示しないようにするには、この画面の右上にあるメニューから[通知]をオフにしてください"
            }
        ]
    }

    requests.post('https://api.line.me/v2/bot/message/push', headers=headers, data=json.dumps(payload))


def search_name():

    response = requests.get('https://nishinaga-test-line-bot.herokuapp.com/ids')
    body = yaml.load(response.text, Loader=yaml.SafeLoader)

    for user in body['ids']['user']:
        if user['name'] == '':
            message_to_line(user['id'])

    for user in body['ids']['group']:
        if user['name'] == '':
            message_to_line(user['id'])


if __name__ == "__main__":
    search_name()
