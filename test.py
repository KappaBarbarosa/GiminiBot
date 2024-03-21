import google.generativeai as genai
import google.ai.generativelanguage as glm
from PIL import Image
import os

from google.generativeai.types import HarmCategory, HarmBlockThreshold


sample = "You need to provide different responses based on user input: If the user asks about your personal information, output Introduction(). If the user expresses a desire to eat dinner (or something else), output FindRestaurant(keyword = {the thing of interest in the user's text},radius = {desired distance}). If the user inquires about the weather, output FindWeather().If the user's speech is not within the above range, just have a normal conversation. For example: I am hungry, what is for dinner?"
history=[{'role':'user',
                'parts':[sample]},
        {'role':'model',
        'parts':["FindRestaurant()"]},
        {'role':'user',
                'parts':["Tell me something about you"]},
        {'role':'model',
        'parts':["Introduction()"]},
        {'role':'user',
                'parts':["how about some ramen nearby?"]},
        {'role':'model',
        'parts':["FindRestaurant(keyword = \"ramen\",radius=1000)"]},
                ]

def Introduction():
    intro = "我是摳摳霸特，你的最佳助理\n"
    intro +="我是由Google Gemini API串接的Linebot，可以回答各種問題\n"
    intro+="如果想要問我關於圖片的意見，請在傳一張圖片後下達一行指示!\n"
    intro+="祝您使用愉快\n"
    print(intro)


def FindRestaurant(keyword="restaurant",radius=1000):
    print(f"你想在{radius}公尺內尋找{keyword}的餐廳")
def FindWeather():
    print("今天天氣很好")

if __name__ == "__main__":
    channel_access_token = os.getenv("CHANNEL_ACCESS_TOKEN")
    channel_secret = os.getenv("CHANNEL_SECRET")
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
    print(channel_access_token)
    print(channel_secret)
    print(GOOGLE_API_KEY)
    print(GOOGLE_MAPS_API_KEY)
    # genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
    # model = genai.GenerativeModel('gemini-pro')
    # chat = model.start_chat(history=history)
    # info = str([{
    #     "price_level": 2,
    #     "rating": 4,
    #     "types":
    #         ["bar", "restaurant", "food", "point_of_interest", "establishment"],
    #     "user_ratings_total": 1269,
    #     "name": "Cruise Bar",
    #     "opening_hours": { "open_now": False },
    # },{
    #     "price_level": 3,
    #     "rating": 5,
    #     "types":
    #         ["bar", "restaurant", "food", "barbeque", "ramen"],
    #     "user_ratings_total": 9999,
    #     "name": "Coco Bar",
    #     "opening_hours": { "open_now": True },
    # }])
    # sample = f'這是一些餐廳的google map資訊，請你根據這些資訊簡介這些餐廳:{info}'
    # r = model.generate_content(sample)
    # print(r.text)
    # while(True):
    #     text = input()
    #     if text == "-1":
    #         break
    #     response = chat.send_message(text)
    #     reponse2 = model.generate_content(text)
    #     print(reponse2.text)
    #     try:
    #         eval(response.text)
    #     except (SyntaxError, NameError,TypeError) as e:
    #         print(f"An error occurred: {e}")
    #         print(response.text)
    #     history.append(response.candidates[0].content)
