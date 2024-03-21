

from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import (
    TextMessage,MessageEvent,TextSendMessage, ImageMessage, LocationMessage
)
from PIL import Image
import io
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
#line token
channel_access_token ="IXl5v4axMyRa12vRaXxRoeQ/Pv+7qwnxZIEWAKdL2wJvFAkDtCZuLRAFBQ6qZNinBufdH1lxlQox4IYM9jHi0PGlSVqQJ9NfeFIm/Bmi0xUArKLZaYc8FGmqzReJbO683dmTxN39WenEKaya9oKigQdB04t89/1O/w1cDnyilFU="
channel_secret = '574b98318f04d6c1d8c4ca5508d280bd'
GOOGLE_API_KEY = 'AIzaSyAY6Q1GIxBg-s5ocjPxwvjh1D0IB-nKglY'
line_bot_api = LineBotApi(channel_access_token)
handler = WebhookHandler(channel_secret)
genai.configure(api_key=GOOGLE_API_KEY)


Textmodel = genai.GenerativeModel('gemini-pro')
ImageModel = genai.GenerativeModel('gemini-pro-vision')
safety_config = {
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT : HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
    }
chat = Textmodel.start_chat(history=[])
app = Flask(__name__)

hold_image = None
last_response = None
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

def Update_Chat(last_response):
    global chat
    history = chat.history
    history.extend([
        {'role':'user',
        'parts':[f'I send an image to you and ask {last_response[0]}']},
        {'role':'model',
        'parts':[last_response[1]]},
        ])
    chat = Textmodel.start_chat(history=history)


@handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event):
    global hold_image
    global last_response
    
    msg= event.message.text
    if hold_image is not None:
        response = ImageModel.generate_content([msg,hold_image],safety_settings=safety_config)
        hold_image=None
        last_response=[msg,response.text]
    else:
        if last_response is not None:
            Update_Chat(last_response)
            last_response = None
        response = chat.send_message(msg,safety_settings=safety_config)
    message = TextSendMessage(text=response.text)
    line_bot_api.reply_message(event.reply_token,message)

@handler.add(MessageEvent, message=ImageMessage)
def handle_image_message(event):
    #echo
    global hold_image
    message_content = line_bot_api.get_message_content(event.message.id)
    image_data = b""
    for chunk in message_content.iter_content():
        image_data += chunk
    image_file = io.BytesIO(image_data)
    hold_image = Image.open(image_file)

@handler.add(MessageEvent, message=LocationMessage)
def handle_location_message(event):
    location_message = event.message

    # 取得位置訊息的各個部分
    title = location_message.title
    address = location_message.address
    latitude = location_message.latitude
    longitude = location_message.longitude

    # 建立一個回覆訊息
    reply_message = TextSendMessage(
        text=f"Received location:\nTitle: {title}\nAddress: {address}\nLatitude: {latitude}\nLongitude: {longitude}"
    )

    # 使用 Line Bot API 回覆訊息
    line_bot_api.reply_message(event.reply_token, reply_message)
    

import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)