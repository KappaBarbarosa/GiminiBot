

from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import (
    TextMessage,MessageEvent,TextSendMessage, ImageMessage, LocationMessage,StickerMessage,StickerSendMessage
)
from PIL import Image
import io
import google.generativeai as genai
from User import User
from parameters_v2 import *

from news import NewsAPI
from search import SearchAPI
import googlemaps
import os
import random
import numpy as np
gmaps =googlemaps.Client(key=os.getenv("GOOGLE_MAPS_API_KEY"))
line_bot_api = LineBotApi(os.getenv("CHANNEL_ACCESS_TOKEN"))
handler = WebhookHandler(os.getenv("CHANNEL_SECRET"))
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

Users = {}
Embeddings = {}
Textmodel = genai.GenerativeModel('gemini-1.5-flash')
ImageModel = genai.GenerativeModel('gemini-pro-vision')
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

def replyTextMessage(event,text,emojis=None):
    message = TextSendMessage(text=text,emojis=emojis)
    line_bot_api.reply_message(event.reply_token,message)

def pushTextMessage(event,text,emojis=None):
    message = TextSendMessage(text=text,emojis=emojis)
    if event.source.type == 'group':
        id = event.source.group_id
    elif event.source.type == 'room':
        id = event.source.room_id
    else:
        id = event.source.user_id
    line_bot_api.push_message(id,message)

def varified_user(uid):
    if uid not in Users:
        Users[uid] = User(uid,Textmodel)

def Introduction(event,**kwargs):
    replyTextMessage(event,intro)
    return "sucess"

def Process(event,query,need_comment=True):
    uid = event.source.user_id
    varified_user(uid)
    news_result = NewsAPI(query,Textmodel)
    search_result = SearchAPI(query,Textmodel)
    # if need_comment:
    #     comment_result = CommentAPI(query)
    prompt = f"這是有關{query}的新聞資訊{news_result}，以及市場監控情形{search_result}，請你根據這些資訊，幫助我更好地了解市場動態，做出明智的決策。"
    response =Users[uid].chat.send_message(prompt)
    pushTextMessage(event,response.text)

@handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event):
    uid = event.source.user_id
    varified_user(uid)
    msg= event.message.text
    if Users[uid].hold_image is not None:
        response = ImageModel.generate_content([msg,Users[uid].hold_image],safety_settings=safety_config)
        Users[uid].hold_image=None
        Users[uid].update_chat([f'I send an image to you and ask {msg}',response.text])
        replyTextMessage(event,response.text)
    else:
        response = Users[uid].chat.send_message(msg,safety_settings=safety_config)
        # try:
        pushTextMessage(event,response.text)
        result = eval(response.text)
        if result != "sucess":
            replyTextMessage(event,result)
        # except Exception as e:
        #     replyTextMessage(event,(response.text+"\n Error:\n" +str(e)))


@handler.add(MessageEvent, message=StickerMessage)
def handle_sticker_message(event):
    random_package_id = random.choice(keys)
    random_sticker_id = random.randint(sticks[random_package_id][0],sticks[random_package_id][1])
    sticker_message = StickerSendMessage(package_id=random_package_id, sticker_id=random_sticker_id)
    line_bot_api.reply_message(event.reply_token,sticker_message)


@handler.add(MessageEvent, message=ImageMessage)
def handle_image_message(event):
    uid = event.source.user_id
    varified_user(uid)
    message_content = line_bot_api.get_message_content(event.message.id)
    image_data = b""
    for chunk in message_content.iter_content():
        image_data += chunk
    image_file = io.BytesIO(image_data)
    Users[uid].hold_image = Image.open(image_file)



if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)