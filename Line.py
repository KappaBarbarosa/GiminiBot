from linebot import LineBotApi
from linebot.models import TextSendMessage
import os
linebotapi = LineBotApi(os.getenv("CHANNEL_ACCESS_TOKEN"))
