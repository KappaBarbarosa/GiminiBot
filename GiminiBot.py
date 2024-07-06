

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
from weather import *
from news import GetInquiredNewsContent
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
    
    
    sample = f'你剛提到香蕉嗎? 香蕉好吃!'
    # response = Textmodel.generate_content(sample)
    pushTextMessage(event,sample)
    # Users[uid].update_chat([sample])
    return "sucess"

def Embedding(event,text):
    uid = event.source.user_id
    varified_user(uid)
    result = genai.embed_content(
    model="models/embedding-001",
    content=text,
    task_type="retrieval_document",
    title="Embedding of single string")
    Embeddings[text] = result['embedding']
    response = f"{text} 的嵌入 " + str(result['embedding'])[:3] 
    replyTextMessage(event,response)
    Users[uid].update_chat([f"我想知道 {text}的嵌入",response])
    return "sucess"

def query_fn(event,  query):
    uid = event.source.user_id
    varified_user(uid)
    if len(Embeddings) == 0:
        replyTextMessage(event,"目前沒有嵌入資料")
        return "sucess"
    request = genai.embed_content(model="models/embedding-001",
                              content=query,
                              task_type="retrieval_query")['embedding']
    embeddings_matrix = np.array(list(Embeddings.values()))
    dot_products = np.dot(embeddings_matrix, np.array(request).T)
    sorted_indices = np.argsort(-dot_products)
    ranked_texts = np.array(list(Embeddings.keys()))[sorted_indices]
    
    # 選出排名最高的前N個結果
    top_n = 3 if len(Embeddings) <3 else len(Embeddings)  # 例如，選出排名最高的前5個
    top_n_texts = ranked_texts[:top_n]
    top_n_similarities = dot_products[sorted_indices][:top_n]

    response = f"{query} 的相似度排名：\n" + "\n".join([f"{text}: {np.round(similarity,2) }" for text, similarity in zip(top_n_texts, top_n_similarities)])
    
    replyTextMessage(event, response)
    Users[uid].update_chat([event.message.text,response])
    return "sucess"

def FindNews(event,query,range=10,force_search=False):
    # try:
    responses = GetInquiredNewsContent(query,range,force_search)
    # except Exception as e:
    #     replyTextMessage(event,str(e))
    #     return "sucess"
    
    pushTextMessage(event,f"以下是{query}的搜尋結果:")
    news = ""
    for response in responses:
        # pushTextMessage(event.source.user_id,f"原始內容長度{len(response['content'])}字")
        sample = f"這是從一個新聞網頁上擷取下來的html訊息,標題為{response['title']}，請你根據這些資訊:{response['content']}，對這份新聞做一個完整中文摘要，如果資訊和標題無關，只要回答 無相關三個字就好。"
        # try:
        res = Textmodel.generate_content(sample,safety_settings=safety_config)
        if res.text != "無相關":
            output = response['title'] + "\n" + res.text + "\n"+ f'原文連結: {response["url"]}'        
            pushTextMessage(event,output)
            news+=   response['title'] + "\n" + res.text + "\n"
        # except Exception as e:
        #     pushTextMessage(event,str(e))
    sample = f"這是多個新聞的摘要,，請你根據這些資訊:{news}，對所有內容進行總結。"
    # try:
    res = Textmodel.generate_content(sample,safety_settings=safety_config)
    pushTextMessage(event,res.text)
    # except Exception as e:
    #     pushTextMessage(event,str(e))
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