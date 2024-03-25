# CocoBot: Gemini with LINE Bot

This repo is a weekly side project for learning how to combine Google services with  LINE Messaging API.

## Prerequisites
Before getting started, ensure you have the following:
- A dedicated [Messaging API channel](https://developers.line.biz/en/docs/messaging-api/getting-started/) for your bot.
- [Google Gemini API key](https://ai.google.dev/?gad_source=1&gclid=Cj0KCQjwwYSwBhDcARIsAOyL0fg2TKRmD0X3U-M9uM0aj5aWsmJOPDBpRare6pMc1oujvC9Z0wVHbKQaAi08EALw_wcB)
- [Google Maps API key](https://developers.google.com/maps?hl=zh-tw)
- [OpenWeatherMap API key](https://openweathermap.org/api)
- A [Render account](https://dashboard.render.com/register) (no credit card required).
- You can follow [this repository](https://github.com/haojiwu/line-bot-python-on-render) to learn how to deploy the LINE bot to Render.

## Features

### 1. Text Conversation
- Users can engage in conversations with the bot on various topics.
- The bot utilizes the **Gemini-Pro** model to generate responses, incorporating historical context and basic rules.
- **Prompt Engineering**: Enable users to execute functions via natural language prompts rather than explicit instructions.
    - ~~!restaurant~~ 
    - I'm hungry, what's for dinner?

### 2. Image Description
- Upon receiving an image and a prompt, the bot leverages the **Gemini-Pro-Vision** model to generate a response.
- Note: Gemini-Pro-Vision does not support history memory.

### 3. Location-based Recommendations
- Users can request restaurant recommendations based on their current location.
- The bot utilizes the Google Maps API to find nearby restaurants and provide tailored recommendations.
- Users can modify **Keywords** and **Search radius** using natural language.

### 4. Weather Information
- Users can inquire about current weather conditions and forecasts for their location.
- The bot fetches weather data using the OpenWeatherMap API and presents it to the users.

### 5. LINE Stickers Reply
- Upon receiving a LINE Sticker, the bot randomly selects a LINE Official Sticker to reply.

## Implementation Details
- **Example-driven Adaptation**: Utilize a set of examples to guide the LLM towards generating outputs aligned with desired criteria or context.
- **Parsing**: Extract required function parameters from user queries via the Gemini model. This enables dynamic adjustment of function results based on user feedback.
- For more details, refer to [parameter.py](https://github.com/KappaBarbarosa/CocoBot/blob/master/parameters.py).

## Future Plans
- Integrate a **database** system for permanent storage of conversation content and enhance **RAG** (Retrieval-Augmented Generation) effectiveness.
- Connect to more useful APIs, such as Google Search, Google News, and bus information.
- Integrate additional **LINE features** to create a more lifestyle-oriented bot.

