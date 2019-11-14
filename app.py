import os
import re
import yaml

from flask import Flask, request, abort, jsonify
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, TemplateSendMessage, CarouselTemplate, CarouselColumn)

app = Flask(__name__)

LINE_CHANNEL_ACCESS_TOKEN = os.environ["LINE_CHANNEL_ACCESS_TOKEN"]
LINE_CHANNEL_SECRET = os.environ["LINE_CHANNEL_SECRET"]

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)


def update_ids(event, name):

    if os.path.exists('ids.yaml'):
        with open('ids.yaml', "r") as file:
            ids = yaml.load(file)

            is_found = False
            if event.source.type == "user":
                for user in ids["ids"]["user"]:
                    if event.source.user_id == user['id']:
                        is_found = True
                        if len(name) > 0:
                            user['name'] = name
            elif event.source.type == "group":
                for group in ids["ids"]["group"]:
                    if event.source.group_id == group['id']:
                        is_found = True
                        if len(name) > 0:
                            group['name'] = name

            if not is_found:
                if event.source.type == "user":
                    ids["ids"]["user"].append({'name': name, 'id': event.source.user_id})
                elif event.source.type == "group":
                    ids["ids"]["group"].append({'name': name, 'id': event.source.group_id})
    else:
        ids = {'ids': {'user': [], 'group': []}}
        if event.source.type == "user":
            ids["ids"]["user"].append({'name': name, 'id': event.source.user_id})
        elif event.source.type == "group":
            ids["ids"]["group"].append({'name': name, 'id': event.source.group_id})

    with open('ids.yaml', "w") as yaml_file:
        yaml.dump(ids, yaml_file)


@app.route("/ids", methods=['GET'])
def get_ids():

    if os.path.exists('ids.yaml'):
        with open('ids.yaml') as file:
            ids = yaml.load(file)
            return jsonify(ids)

    return jsonify({})


@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']

    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def response_message(event):

    update_ids(event, '')

    if event.message.text == "でーこむ" or event.message.text == "デーコム":
        notes = [CarouselColumn(thumbnail_image_url="https://www.dcom-web.co.jp/wp-content/uploads/2014/10/logo_dcom.png",
                            title="株式会社デーコム",
                            text="でーこむホームページ",
                            actions=[{"type": "message", "label": "サイトURL", "text": "http://www.dcom-web.co.jp/"}]),

             CarouselColumn(thumbnail_image_url="https://www.dcom-web.co.jp/wp-content/uploads/2014/10/logo_dcom.png",
                            title="デーコム ブログ",
                            text="部活や社員旅行、社内イベントのご紹介ヽ(=´▽`=)ﾉ",
                            actions=[
                                {"type": "message", "label": "サイトURL", "text": "http://www.dcom-web.co.jp/blog/"}]),

             CarouselColumn(thumbnail_image_url="https://www.dcom-web.co.jp/wp-content/uploads/2017/05/img_portfolio_dcomlab_1-653x450.png",
                            title="デーコム Lab",
                            text="IT技術ブログφ(..)",
                            actions=[
                                {"type": "message", "label": "サイトURL", "text": "http://www.dcom-web.co.jp/portfolio/dcom-lab/"}]),

             CarouselColumn(thumbnail_image_url="https://job.rikunabi.com/2020/static/common/contents/logos/rikunabi/image/popup_headerlogo.gif",
                           title="デーコム リクナビ2020",
                           text="エントリーはこちらからっ(｀･ω･´)ゞ",
                           actions=[
                               {"type": "message", "label": "サイトURL", "text": "https://job.rikunabi.com/2020/company/r847700062/"}])]

        messages = TemplateSendMessage(
            alt_text='template',
            template=CarouselTemplate(columns=notes),
        )
    elif "名前登録" in event.message.text:
        name = re.search(r"名前登録「(.*)」", event.message.text)

        if name:
            update_ids(event, name.group(1))
            messages = TextSendMessage(text='名前登録ありがとうございます。\n' + name.group(1) + 'で登録しました！')

    else:
        messages = TextSendMessage(text='すみません、よくわかりません')

    line_bot_api.reply_message(event.reply_token, messages=messages)


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
