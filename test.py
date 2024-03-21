import google.generativeai as genai
import google.ai.generativelanguage as glm
from PIL import Image
GOOGLE_API_KEY = 'AIzaSyAY6Q1GIxBg-s5ocjPxwvjh1D0IB-nKglY'
genai.configure(api_key=GOOGLE_API_KEY)
from google.generativeai.types import HarmCategory, HarmBlockThreshold
model = genai.GenerativeModel('gemini-pro')
chat = model.start_chat(history=[])
history=[]

while(True):
    text = input()
    if text == "-1":
        break

    history = chat.history
    history.extend([{'role':'user',
                'parts':[f'I send an image to you and ask Who is in this image?']},
                {'role':'model',
                'parts':["Bob is in this picture"]}
                ])
    chat = model.start_chat(history=history)
    response = chat.send_message(text)
    print(response.text)
    history.append(response.candidates[0].content)
