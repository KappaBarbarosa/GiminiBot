

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
from parameters import *
from functions import *
import googlemaps
import os
import random

gmaps =googlemaps.Client(key=os.getenv("GOOGLE_MAPS_API_KEY"))
line_bot_api = LineBotApi(os.getenv("CHANNEL_ACCESS_TOKEN"))
handler = WebhookHandler(os.getenv("CHANNEL_SECRET"))
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

Users = {}
Textmodel = genai.GenerativeModel('gemini-pro')
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

def pushTextMessage(userid,text,emojis=None):
    message = TextSendMessage(text=text,emojis=emojis)
    line_bot_api.push_message(userid.reply_token,message)

def varified_user(uid):
    if uid not in Users:
        Users[uid] = User(uid,Textmodel)

def Introduction(event,**kwargs):
    replyTextMessage(event,intro,emojis=emojis)
    return "sucess"

def AskForUserLocation(event):
    replyTextMessage(event,"請告訴我你的位置!")
    
def FindRestaurant(event=None,query="",keyword="Restaurant",radius=1000):
    uid = event.source.user_id
    varified_user(uid)

    if Users[uid].Location is None:
        AskForUserLocation(event)
        Users[uid].WaitForLocation = {"type":"Restaurant","query":query,"keyword":keyword,"radius":radius}
        return "sucess"
    places_result = gmaps.places_nearby(Users[uid].Location, keyword=keyword,type='restaurant', radius=radius,language='zh-TW')['results']
    data=[]
    keypoints=['business_status','name','plus_code','rating','types','vicinity']
    for result in places_result:
        if(len(data)>5):
            break
        d = {}
        for keypoint in keypoints:
            d[keypoint] = result[keypoint]
        data.append(d)

    sample = f'這是一些餐廳的google map資訊，請你根據這些資訊:{str(data)}，回答用戶的問題: {query}'
    response = Textmodel.generate_content(sample)
    replyTextMessage(event,response.text)
    Users[uid].update_chat([sample,response.text])
    return "sucess"


def FindWeather(event,query):
    uid = event.source.user_id
    varified_user(uid)
    if Users[uid].Location is None:
        AskForUserLocation(event)
        Users[uid].WaitForLocation = {"type":"Weather","query":query}
        return "sucess"

    cur_data,forcast = RequestWeather(Users[uid].weather_parameters)
    sample = f'你是一名氣象專家，請你根據現在天氣的資訊{cur_data}和接下來的天氣{forcast}，回答用戶的問題: {query}'
    response = Textmodel.generate_content(sample)
    replyTextMessage(event,response.text)
    Users[uid].update_chat([sample,response.text])
    return "sucess"

def DM(event):
    uid = event.source.user_id
    varified_user(uid)
    
    
    sample = f'你剛提到摳摳嗎? 摳摳最棒!摳摳最棒!'
    # response = Textmodel.generate_content(sample)
    pushTextMessage(uid,sample)
    # Users[uid].update_chat([sample])
    return "sucess"

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
        result = eval(response.text)
        if result != "sucess":
            replyTextMessage(event,result)
        else:
            replyTextMessage(event,"Failed:"+result)
        # except Exception as e:
        #     print(e)
        #     replyTextMessage(event,response.text)


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


@handler.add(MessageEvent, message=LocationMessage)
def handle_location_message(event):
    uid = event.source.user_id
    varified_user(uid)
    location_message = event.message
    Users[uid].update_location(location_message)
    WaitForLocation = Users[uid].WaitForLocation
    if WaitForLocation is not None:
        if WaitForLocation['type'] == "Restaurant":
            FindRestaurant(event,query=WaitForLocation['query'],keyword=WaitForLocation['keyword'],radius=WaitForLocation['radius'])
        elif WaitForLocation['type'] == "Weather":
            FindWeather(event,query=WaitForLocation['query'])
    
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)