from google.generativeai.types import HarmCategory, HarmBlockThreshold
import requests
from datetime import datetime
safety_config = {
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT : HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
    }

sample = """
You need to provide different responses based on user input:
If the user asks about your information or who are you, output Introduction(event=event).
If the user expresses a desire to eat something, output FindRestaurant(event, query={user's text}, keyword={the thing of interest in the user's text}, radius={desired distance}).
If the user inquires about the weather, output FindWeather(event=event, query={user's query}).
If the user wants to change the location, output AskForUserLocation(event).
If the user mentions about the fruit banana, output DM(event).
If the user wants to find some news, output FindNews(event,query={user's query keywords}, range={the number of news to be displayed,default is 10}).
if the user wants to search for a specific news again, output FindNews(event=event,query={user's query},force_search=True).
If the user's speech is not within the above range, just have a normal conversation. 
For example: I am hungry, what is for dinner?
"""
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
        {'role':'user',
                'parts':["我想了解一些關於生成式AI的新聞"]},
        {'role':'model',
        'parts':["FindNews(event=event,query = \"生成式AI\")"]},
                ]

sticks = {
    446:[1988,2027],
    789:[10855,10894],
    1070:[17839,17878],
    6136:[10551376,10551399],
    6325:[10979904,10979927],
    6359:[11069848,11069871],
    6362:[11087920,11087943],
    6370:[11088016,11088039],
    6632:[11825374,11825397],
    8515:[16581242,16581265],
    8522:[16581266,16581289],
    8525:[16581290,16581313],
    11537:[52002734,52002773],
    11538:[51626494,51626533],
    11539:[52114110,52114149]
}
keys = list(sticks.keys())

intro = "我是 $$$$$\n"
intro +="我是由Google Gemini API串接的Linebot，可以回答各種問題 $\n"
intro +="如果想要問我關於圖片的意見，請在傳一張圖片後下達一行指示!\n"
intro +="當我向您詢問位置時，請輸入Line的位置資訊!\n"
intro +="祝您使用愉快!"
emojis = [
      {
        "index": 3,
        "productId": "5ac21a8c040ab15980c9b43f",
        "emojiId": "003"
      },
      {
        "index": 4,
        "productId": "5ac21a8c040ab15980c9b43f",
        "emojiId": "015"
      },
      {
        "index": 5,
        "productId": "5ac21a8c040ab15980c9b43f",
        "emojiId": "003"
      },
      {
        "index": 6,
        "productId": "5ac21a8c040ab15980c9b43f",
        "emojiId": "015"
      },
      {
        "index": 7,
        "productId": "5ac22bad031a6752fb806d67",
        "emojiId": "051"
      },
      {
        "index": 49,
        "productId": "5ac1bfd5040ab15980c9b435",
        "emojiId": "082"
      }
    ] 

