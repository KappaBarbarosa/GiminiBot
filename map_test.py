import googlemaps   ##導入googlemaps模組
import google.generativeai as genai
import os
gmaps = googlemaps.Client(key='AIzaSyAXUON5rTwo6UvB8WjJs5C5i6wvPHd-CHs') ##利用API建立客戶端

# Geocoding an address
geocode_result = gmaps.geocode('Taiwan')[0] ##利用Geocode函數進行定位
location = geocode_result['geometry']['location'] #取得定位後經緯度
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel('gemini-pro')

#location回傳格式如下圖，可依照格式自訂義變數，就不用調用Geodcode API

# Search for places
#(keyword參數="輸入你想查詢的物件",radius="公尺單位")

places_result = gmaps.places_nearby(location, keyword='餐廳', radius=10000,language='zh-TW')['results'][:11]
print(places_result)
data=[]
keypoints=['business_status','name','plus_code','rating','types','vicinity']
for result in places_result:
    d = {}
    for keypoint in keypoints:
        d[keypoint] = result[keypoint]
    data.append(d)
sample = f'這是一些餐廳的google map資訊，請你根據這些資訊介紹這些餐廳:{str(data)}'
r = model.generate_content(sample)
print(r.text)
