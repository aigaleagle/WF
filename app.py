from flask import Flask, render_template, request, jsonify
import requests
from datetime import datetime, timedelta

app = Flask(__name__)

API_KEY = 'f34c742159778db7dfc203789a8ae285'

def get_hourly_weather(lat, lon):
    url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"
    res = requests.get(url)
    return res.json()

def get_weekly_forecast(lat, lon):
    url = f"https://api.openweathermap.org/data/2.5/forecast/daily?lat={lat}&lon={lon}&cnt=7&appid={API_KEY}&units=metric"
    res = requests.get(url)
    return res.json()

def get_past_weather(lat, lon):
    past_data = []
    for i in range(1, 8):
        dt = int((datetime.utcnow() - timedelta(days=i)).timestamp())
        url = f"https://api.openweathermap.org/data/3.0/onecall/timemachine?lat={lat}&lon={lon}&dt={dt}&appid={API_KEY}&units=metric"
        res = requests.get(url)
        data = res.json()
        temp = data.get('data', [{}])[0].get('temp') if 'data' in data and len(data['data']) > 0 else None
        date_str = (datetime.utcnow() - timedelta(days=i)).strftime('%d-%m-%Y')  # Indian format
        past_data.append({'date': date_str, 'temp': temp})
    return past_data

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_hourly', methods=['POST'])
def get_hourly():
    content = request.json
    lat = content.get('lat')
    lon = content.get('lon')
    weather_data = get_hourly_weather(lat, lon)
    
    if weather_data.get('cod') != "200" and weather_data.get('cod') != 200:
        return jsonify({'error': 'Invalid coordinates or data not available'})

    today = []
    weather_count = {}

    for i in range(0, 8):  # next 8 x 3-hour data
        item = weather_data['list'][i]
        dt_txt = item['dt_txt']
        dt_obj = datetime.strptime(dt_txt, '%Y-%m-%d %H:%M:%S')
        date_str = dt_obj.strftime('%d-%m-%Y')
        time_str = dt_obj.strftime('%I:%M %p')
        temp = item['main']['temp']
        icon = item['weather'][0]['icon']
        desc = item['weather'][0]['description'].capitalize()

        # Count descriptions
        weather_count[desc] = weather_count.get(desc, 0) + 1

        today.append({'date': date_str, 'time': time_str, 'temp': temp, 'icon': icon, 'desc': desc})

    # Calculate percentage
    total = sum(weather_count.values())
    summary = [{'desc': key, 'percent': round((value/total)*100, 2)} for key, value in weather_count.items()]

    return jsonify({'today': today, 'summary': summary})

@app.route('/get_forecast', methods=['POST'])
def get_forecast():
    content = request.json
    lat = content.get('lat')
    lon = content.get('lon')
    weather_data = get_hourly_weather(lat, lon)
    
    if weather_data.get('cod') != "200" and weather_data.get('cod') != 200:
        return jsonify({'error': 'Invalid coordinates or data not available'})

    forecast = []
    for i in range(0, 40, 8):  # next 5 days approx
        item = weather_data['list'][i]
        dt_txt = item['dt_txt']
        dt_obj = datetime.strptime(dt_txt, '%Y-%m-%d %H:%M:%S')
        date_str = dt_obj.strftime('%d-%m-%Y')
        temp = item['main']['temp']
        icon = item['weather'][0]['icon']
        desc = item['weather'][0]['description'].capitalize()
        forecast.append({'date': date_str, 'temp': temp, 'icon': icon, 'desc': desc})

    return jsonify({'forecast': forecast})


@app.route('/get_past', methods=['POST'])
def get_past():
    content = request.json
    lat = content.get('lat')
    lon = content.get('lon')
    past = get_past_weather(lat, lon)
    return jsonify({'past': past})

if __name__ == '__main__':
    app.run(debug=True)
