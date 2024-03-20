

from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import pathlib
import textwrap
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
#line token
channel_access_token ="IXl5v4axMyRa12vRaXxRoeQ/Pv+7qwnxZIEWAKdL2wJvFAkDtCZuLRAFBQ6qZNinBufdH1lxlQox4IYM9jHi0PGlSVqQJ9NfeFIm/Bmi0xUArKLZaYc8FGmqzReJbO683dmTxN39WenEKaya9oKigQdB04t89/1O/w1cDnyilFU="
channel_secret = '574b98318f04d6c1d8c4ca5508d280bd'
GOOGLE_API_KEY = 'AIzaSyAY6Q1GIxBg-s5ocjPxwvjh1D0IB-nKglY'
line_bot_api = LineBotApi(channel_access_token)
handler = WebhookHandler(channel_secret)
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-pro-vision')
safety_config = {
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT : HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
    }
chat = model.start_chat(history=[])
app = Flask(__name__)


# 監聽所有來自 /callback 的 Post Request
@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    #echo
    msg= event.message.text
    response = chat.send_message(msg,safety_settings=safety_config)
    try:
        message = TextSendMessage(text=response.text)
    except ValueError:
        message = TextSendMessage(text=response.candidates[0].finish_reason)
    line_bot_api.reply_message(event.reply_token,message)

import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)