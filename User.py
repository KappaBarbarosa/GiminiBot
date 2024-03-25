import os
import google.generativeai as genai
from utils import safety_config,history
class User():
    def __init__(self, user_id,Textmodel):
        self.user_id = user_id
        self.weather_parameter  = {
        "lat": None,
        "lon": None,
        "appid": os.getenv("WEATHER_KEY"),
        "units":"metric"
        }
        self.Textmodel = Textmodel
        self.chat = Textmodel.start_chat(history=history)
        self.hold_image = None
        self.last_response = None
        self.Location = None
        self.WaitForLocation = None 
    
    def update_chat(self,last_response):
        history = self.chat.history
        history.extend([
            {'role':'user',
            'parts':[last_response[0]]},
            {'role':'model',
            'parts':[last_response[1]]},
            ])
        self.chat = self.Textmodel.start_chat(history=history)
    
    def update_location(self,location_message):
        self.Location = {}
        self.weather_parameters['lat'] = location_message.latitude
        self.Location['lat'] = location_message.latitude
        self.weather_parameters['lon'] = location_message.longitude
        self.Location['lng'] = location_message.longitude