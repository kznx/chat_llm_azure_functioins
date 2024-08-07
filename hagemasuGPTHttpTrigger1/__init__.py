import logging
import os
import json
import openai
import azure.functions as func

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)

# Azure FunctionsのApplication Settingに設定した値から取得する↓
channel_secret = os.getenv('LINE_CHANNEL_SECRET', None)
channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', None)
openai.api_key = os.getenv('OPENAI_API_KEY', None)

line_bot_api = LineBotApi(channel_access_token)
handler = WebhookHandler(channel_secret)

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    # get x-line-signature header value
    signature = req.headers['x-line-signature']

    # get request body as text
    body = req.get_body().decode("utf-8")
    logging.info("Request body: HttpTrigger1" + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        func.HttpResponse(status_code=400)

    return func.HttpResponse('OK')

def isLimit(userID):
    islimit=False

    return islimit

def generate_response(message):
    # OpenAI APIを使用して返答を生成する

    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": \
             "あなたは優秀な30歳の女性心理カウンセラーです。私の悩みに寄り添って励ます文章を次の条件に従って例を参考にして作成して下さい。\
            条件：\
            ・他者とのつながりを持ち、認められたいという欲求を満たすこと\
            ・自分自身を認めてもらい、自分自身に自信を持ちたいという欲求を満たすこと\
            ・一文を短く、最大でも50文字ぐらい\
            ・全体で150文字ぐらい\
            ・箇条書きで記載\
            ・励まし優しく語りかけるように口語調\
            ・もし悩みの内容が挨拶だったら、あなたも挨拶をする\
            ・もし悩みの内容が悩みでも挨拶でもなかったら、「何かお悩みがありますか？」と聞く\
            例：\
            怒られると、自信が失われたり落ち込んだりすることがあるよね。\
            そんな時は、自分にとって大切なことや自分が成し遂げたことを振り返ってみましょう。\
            一人で悩みを抱え込んでしまうのは辛いですよね。\
            悩み："
             },
            {"role": "user", "content": message}
        ]
    )
    return response.choices[0].message.content.strip()

@handler.add(MessageEvent, message=TextMessage)
def message_text(event):
    message = event.message.text
    # userIDプロパティを取得する https://teratail.com/questions/214390
    userID=event.source.user_id
    logging.info("in messege_text userID=%s", userID)
    dispname=line_bot_api.get_profile(userID).display_name

    if not isLimit(userID):
        logging.info("under limit")
        response1 = generate_response(message)
    else:
        logging.info("exceed limit")
        response1 = "See you tommorrow!"

    response = dispname + "さん、" + response1
    logging.info("in messege_text response=%s", response)

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=response)
    )