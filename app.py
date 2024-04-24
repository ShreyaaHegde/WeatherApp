from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

API_KEY = '9632af7a634373dc56cc1388162d3db4'

# Function to read cities from file
def read_cities():
    try:
        with open('cities.txt', 'r') as file:
            cities = file.read().splitlines()
        return cities
    except FileNotFoundError:
        return []

# Function to write city to file
def write_city(city):
    with open('cities.txt', 'a') as file:
        file.write(city + '\n')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/weather', methods=['GET', 'POST'])
def weather():
    if request.method == 'POST':
        city = request.form['city']
        write_city(city)  # Write searched city to file
    else:
        city = request.args.get('city')
    if not city:
        return render_template('error.html', message='Please enter a city name')
    
    try:
        weather_data = get_weather_data(city)
        if not weather_data:
            return render_template('error.html', message='City not found')
        return render_template('weather.html', weather=weather_data)
    except Exception as e:
        return render_template('error.html', message='Error fetching weather data')

def get_weather_data(city):
    url = f'http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={API_KEY}&units=metric'
    response = requests.get(url)
    data = response.json()

    if data['cod'] == '200':
        weather = {
            'city': city,
            'temperature': data['list'][0]['main']['temp'],
            'description': data['list'][0]['weather'][0]['description'].capitalize(),
            'icon': data['list'][0]['weather'][0]['icon'],
            'forecast': []
        }
        
        # Extract 7-day forecast data with only one time of the day
        forecast_dates = set()
        for forecast in data['list']:
            date = forecast['dt_txt'].split(' ')[0]  # Extract date part
            if date not in forecast_dates:
                weather['forecast'].append({
                    'date': forecast['dt_txt'],
                    'temperature': forecast['main']['temp'],
                    'description': forecast['weather'][0]['description'].capitalize(),
                    'icon': forecast['weather'][0]['icon']
                })
                forecast_dates.add(date)
                if len(forecast_dates) == 7:  # Stop when 7 days forecast is collected
                    break
        
        return weather
    else:
        return None

@app.route('/cities')
def get_cities():
    cities = read_cities()  # Read cities from file
    return jsonify(cities)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html', message='Page not found'), 404

if __name__ == '__main__':
    app.run(debug=True)
