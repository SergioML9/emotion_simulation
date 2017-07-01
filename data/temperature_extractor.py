# http://api.apixu.com/v1/forecast.json?key=07678eaa834a47dcb6f162815170107&q=Madrid&days=10

import urllib.request
import urllib.parse
import json
import numpy as np
import pandas as pd

data = {}
data['key'] = '07678eaa834a47dcb6f162815170107'
data['q'] = 'Madrid'
data['days'] = 10

url_values = urllib.parse.urlencode(data)
#print(url_values)  # The order may differ from below.

url = 'http://api.apixu.com/v1/forecast.json'
full_url = url + '?' + url_values
data = urllib.request.urlopen(full_url)
response = json.loads(data.read().decode('utf-8'))

days = response["forecast"]["forecastday"]

days_col = []
hours_col = []
temperature_col = []
humidity_col = []

for day in days:
    hours = day["hour"]
    for hour in hours:
        days_col.append(day["date"].split('-')[2])
        hours_col.append(hour["time"].split(' ')[1])
        temperature_col.append(hour["temp_c"])
        humidity_col.append(hour["humidity"])
    #print(hours)

for d in range(11,30):
    for h in range(0,23):
        days_col.append(d)
        hours_col.append(hours_col[h])
        temperature_col.append(temperature_col[(d%5+5)*24+h])
        humidity_col.append(humidity_col[(d%5+5)*24+h])

percentile_list = pd.DataFrame(
    {'day': days_col,
     'hour': hours_col,
     'temp': temperature_col,
     'humidity': humidity_col
    })
percentile_list.to_csv('temperature_data.csv', index=False)
#[0]["onyx:hasEmotion"][0]["onyx:hasEmotionCategory"]
