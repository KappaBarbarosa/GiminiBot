

from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import (
    TextMessage,MessageEvent,TextSendMessage, ImageMessage, LocationMessage,StickerMessage,StickerSendMessage
)
from PIL import Image
import io
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
import googlemaps
import os
from datetime import datetime
from sticker_list import sticks,keys
import requests
import random

gmaps =googlemaps.Client(key=os.getenv("GOOGLE_MAPS_API_KEY"))
line_bot_api = LineBotApi(os.getenv("CHANNEL_ACCESS_TOKEN"))
handler = WebhookHandler(os.getenv("CHANNEL_SECRET"))
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
Weather_parameters = {
    "lat": None,
    "lon": None,
    "appid": os.getenv("WEATHER_KEY"),
    "units":"metric"
    }

Textmodel = genai.GenerativeModel('gemini-pro')
ImageModel = genai.GenerativeModel('gemini-pro-vision')
safety_config = {
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT : HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
    }
sample = "You need to provide different responses based on user input: If the user asks about your information or who are you, output Introduction(event=event). If the user expresses a desire to eat something), output FindRestaurant(event,query= {user's text}, keyword = {the thing of interest in the user's text},radius = {desired distance}). If the user inquires about the weather, output FindWeather(event=event,query={user's query}). If the user want to change the location, output AskForUserLocation(event).If the user's speech is not within the above range, just have a normal conversation. For example: I am hungry, what is for dinner?"
history=[{'role':'user',
                'parts':[sample]},
        {'role':'model',
        'parts':["FindRestaurant(event,query= \"I am hungry, what is for dinner?\")"]},
        {'role':'user',
                'parts':["Tell me something about you"]},
        {'role':'model',
        'parts':["Introduction(event=event)"]},
        {'role':'user',
                'parts':["how about some ramen nearby?"]},
        {'role':'model',
        'parts':["FindRestaurant(event=event, query = \"how about some ramen nearby?\"), keyword = \"ramen\",radius=1000)"]},
        {'role':'user',
                'parts':["Will today be hot?"]},
        {'role':'model',
        'parts':["FindWeather(event=event,query = \"Will today be hot?\")"]},
                ]
chat = Textmodel.start_chat(history=history)
app = Flask(__name__)

hold_image = None
last_response = None
Location = None
WaitForLocation = None
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

def sendTextMessage(event,text):
    message = TextSendMessage(text=text)
    line_bot_api.reply_message(event.reply_token,message)
def Update_Chat(last_response):
    global chat
    history = chat.history
    history.extend([
        {'role':'user',
        'parts':[last_response[0]]},
        {'role':'model',
        'parts':[last_response[1]]},
        ])
    chat = Textmodel.start_chat(history=history)

def Introduction(event,**kwargs):
    intro = "我是摳摳霸特~~~\n"
    intro +="我是由Google Gemini API串接的Linebot，可以回答各種問題\n"
    intro+="如果想要問我關於圖片的意見，請在傳一張圖片後下達一行指示!\n"
    intro+="祝您使用愉快"
    sendTextMessage(event,intro)
    return "sucess"
def AskForUserLocation(event):
    sendTextMessage(event,"請告訴我你的位置!")
    
def FindRestaurant(event=None,query="",keyword="Restaurant",radius=1000):
    global WaitForLocation
    if Location is None:
        AskForUserLocation(event)
        WaitForLocation = {"type":"Restaurant","query":query,"keyword":keyword,"radius":radius}
        return "sucess"
    else:
        places_result = gmaps.places_nearby(Location, keyword=keyword,type='restaurant', radius=radius,language='zh-TW')['results']
    if len(places_result) >5:
        places_result = places_result[:6]
    data=[]
    keypoints=['business_status','name','plus_code','rating','types','vicinity']
    for result in places_result:
        d = {}
        for keypoint in keypoints:
            d[keypoint] = result[keypoint]
        data.append(d)
    sample = f'這是一些餐廳的google map資訊，請你根據這些資訊推薦這些餐廳:{str(data)}，並回答用戶的問題: {query}'
    response = Textmodel.generate_content(sample)
    sendTextMessage(event,response.text)
    Update_Chat([sample,response.text])
    return "sucess"

def FindWeather(event,query):
    global WaitForLocation
    if Location is None:
        AskForUserLocation(event)
        WaitForLocation = {"type":"Weather","query":query}
        return "sucess"
    else:
        Weather_parameters['lat'] = Location['lat']
        Weather_parameters['lon'] = Location['lng']

    response = requests.get(url="https://api.openweathermap.org/data/2.5/weather?", params=Weather_parameters)
    response.raise_for_status()
    cur_data = response.json()
    response = requests.get(url="https://api.openweathermap.org/data/2.5/forecast?", params=Weather_parameters)
    response.raise_for_status()
    weather_data = response.json()
    forcast = []
    now = datetime.now()
    ct = 0
    for data in weather_data['list']:
        dt = datetime.fromtimestamp(data['dt']) 
        if dt < now:
            continue
        if ct > 6:
             break
        
        forcast.append({
            'time': dt.strftime('%m-%d %H:%M:%S'),
            'main': data['main'],
            'weather': data['weather'][0]['main'],
            'weather discription':data['weather'][0]['description']
        })
        ct+=1
    sample = f'你是一名氣象專家，請你根據現在天氣的資訊{cur_data}和接下來的天氣{forcast}，回答用戶的問題: {query}'
    response = Textmodel.generate_content(sample)
    sendTextMessage(event,response.text)
    Update_Chat([sample,response.text])
    return "sucess"

@handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event):
    global hold_image,last_response

    msg= event.message.text
    if hold_image is not None:
        response = ImageModel.generate_content([msg,hold_image],safety_settings=safety_config)
        hold_image=None
        Update_Chat([f'I send an image to you and ask {msg}',response.text])
    else:
        response = chat.send_message(msg,safety_settings=safety_config)
        try:
            result = eval(response.text)
            if result != "sucess":
                sendTextMessage(event,result)
        except:
            sendTextMessage(event,response.text)

@handler.add(MessageEvent, message=StickerMessage)
def handle_sticker_message(event):
    random_package_id = random.choice(keys)
    random_sticker_id = random.randint(sticks[keys][0],sticks[keys][1])
    sticker_message = StickerSendMessage(package_id=random_package_id, sticker_id=random_sticker_id)
    line_bot_api.reply_message(event.reply_token,sticker_message)

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
    global Location
    location_message = event.message
    Location={}
    Location['lat'] = location_message.latitude
    Location['lng'] = location_message.longitude
    if WaitForLocation is not None:
        if WaitForLocation['type'] == "Restaurant":
            FindRestaurant(event,query=WaitForLocation['query'],keyword=WaitForLocation['keyword'],radius=WaitForLocation['radius'])
        elif WaitForLocation['type'] == "Weather":
            FindWeather(event,query=WaitForLocation['query'])
    
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)