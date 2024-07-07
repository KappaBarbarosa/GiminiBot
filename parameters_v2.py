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
You are a chatbot integrated into a LINE bot to provide real-time market monitoring and information retrieval. You need to provide different responses based on user input.
If the user asks about your information or who are you, output Introduction(event=event).
If the user asks a specific query about market trends, consumer reviews, or other related information, output the result using the appropriate format:
    - For general queries: Process(event=event, query={user's query})
    - For queries  related to products that might appear on shopping website: Process(event=event, query={user's query}, need_comment=True)
If a user provides you with valuable market information, please assist them in consolidating and analyzing it.
If the user's speech is not within the above range, just have a normal conversation. 
For example: Give me the latest news on electric cars.?
User input examples: "Show me the latest market trends for smartwatches.", "What are people saying about the iPhone 15?", "Give me the latest news on electric cars."
"""
history=[{'role':'user',
                'parts':[sample]},
        {'role':'model',
        'parts':["Process(event,query= \"electric cars\")"]},
        {'role':'user',
                'parts':["Tell me something about you"]},
        {'role':'model',
        'parts':["Introduction(event=event)"]},
        {'role':'user',
                'parts':["Show me the latest market trends for smartwatches."]},
        {'role':'model',
        'parts':["Process(event,query= \"smartwatches\", need_comment=True)"]},
        {'role':'user',
                'parts':["What are people saying about the iPhone 15?"]},
        {'role':'model',
        'parts':["Process(event,query= \"iPhone 15\", need_comment=True)"]},
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

intro = """"
您好
我是一個實時市場監控的大型語言模型Bot
我的主要功能是幫助您了解最新的市場趨勢、消費者評論以及其他相關信息
您可以向我發送自然語言查詢，例如“顯示最近一個月內有關智能手表的市場趨勢”。
我會通過接入Google News來收集和分析最新新聞
並使用Google Search來獲取相關產品的評價。
如果查詢涉及商品，我還會額外提供從購物網站收集的評論訊息。
我的目的是幫助您更好地了解市場動態，做出明智的決策。
"""