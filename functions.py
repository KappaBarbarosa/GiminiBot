import requests
import datetime

def RequestWeather(weather_parameters):
    response = requests.get(url="https://api.openweathermap.org/data/2.5/weather?", params=weather_parameters)
    response.raise_for_status()
    cur_data = response.json()
    response = requests.get(url="https://api.openweathermap.org/data/2.5/forecast?", params=weather_parameters)
    response.raise_for_status()
    weather_data = response.json()
    forcast = []
    now = datetime.now()
    for data in weather_data['list']:
        dt = datetime.fromtimestamp(data['dt']) 
        if dt < now:
            continue
        if len(forcast) > 6:
             break
        forcast.append({
            'time': dt.strftime('%m-%d %H:%M:%S'),
            'main': data['main'],
            'weather': data['weather'][0]['main'],
            'weather discription':data['weather'][0]['description']
        })
    return cur_data,forcast