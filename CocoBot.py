

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
import googlemaps
import os
#line token

gmaps =googlemaps.Client(key=os.getenv("GOOGLE_MAPS_API_KEY"))
line_bot_api = LineBotApi(os.getenv("CHANNEL_ACCESS_TOKEN"))
handler = WebhookHandler(os.getenv("CHANNEL_SECRET"))
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
Textmodel = genai.GenerativeModel('gemini-pro')
ImageModel = genai.GenerativeModel('gemini-pro-vision')
safety_config = {
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT : HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
    }
sample = "You need to provide different responses based on user input: If the user asks about your personal information, output Introduction(event=event). If the user expresses a desire to eat dinner (or something else), output FindRestaurant(event,keyword = {the thing of interest in the user's text},radius = {desired distance}). If the user inquires about the weather, output FindWeather(event).If the user's speech is not within the above range, just have a normal conversation. For example: I am hungry, what is for dinner?"
history=[{'role':'user',
                'parts':[sample]},
        {'role':'model',
        'parts':["FindRestaurant(event=event)"]},
        {'role':'user',
                'parts':["Tell me something about you"]},
        {'role':'model',
        'parts':["Introduction(event=event)"]},
        {'role':'user',
                'parts':["how about some ramen nearby?"]},
        {'role':'model',
        'parts':["FindRestaurant(event=event,keyword = \"ramen\",radius=1000)"]},
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
    
def FindRestaurant(event,keyword="",radius=1000,**kwargs):
    global WaitForLocation
    if Location is None:
        AskForUserLocation(event)
        WaitForLocation = {"type":"Restaurant","keyword":keyword,"radius":radius}
        return "sucess"
    else:
        places_result = gmaps.places_nearby(Location, keyword=keyword,type='restaurant', radius=radius,language='zh-TW')['results']
    if len(places_result) >5:
        places_result = radius[:6]
    data=[]
    keypoints=['business_status','name','plus_code','rating','types','vicinity']
    for result in places_result:
        d = {}
        for keypoint in keypoints:
            d[keypoint] = result[keypoint]
        data.append(d)
    sample = f'這是一些餐廳的google map資訊，請你根據這些資訊推薦這些餐廳:{str(data)}'
    response = Textmodel.generate_content(sample)
    sendTextMessage(event,response.text)
    Update_Chat([sample,response.text])
    return "sucess"

def FindWeather(event,**kwargs):
    print("今天天氣很好")
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
        if(WaitForLocation['type'] == "Restaurant"):
            FindRestaurant(event=event,keyword=WaitForLocation['keyword'],radius=WaitForLocation['radius'])
    
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)