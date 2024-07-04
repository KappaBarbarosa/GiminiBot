import google.generativeai as genai
GOOGLE_API_KEY = 'AIzaSyAY6Q1GIxBg-s5ocjPxwvjh1D0IB-nKglY'
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-pro')
chat = model.start_chat(history=[])
while(True):
    text = input()
    if text == "-1":
        break
    response = chat.send_message(text)
    print(response.text)