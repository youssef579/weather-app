from flask import Flask, render_template, request, flash
import requests
from os import urandom

app = Flask(__name__)
app.secret_key = urandom(24)

API = '9dd5a007254678bd11aee4e1877d4cf2'
cities = []     

@app.route('/', methods=["GET", "POST"])
def index():
    match request.method:
        case "GET":
            return render_template('index.html')
        
        case "POST":
            city_name = request.form.get('city', '').strip()
            result = requests.get(f"https://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={API}").json()
            
            if result['cod'] != '404':
                city = {
                    'name': city_name.title(),
                    'c': int(result['main']['temp'] - 273.15),
                    'f': int(result['main']['temp'] * 1.8 - 459.67),
                    'description': result['weather'][0]['description'].capitalize(),
                    'icon': result['weather'][0]['icon']
                }
                
                for i in cities:
                    if i['name'] == city['name']:
                        flash(f"You've added \"{city['name']}\" already.", "warning")
                        break
                else:
                    cities.append(city)
                    
                return render_template('index.html', cities=cities)
            
            flash(f'"{city_name}" is not found.', "error")
            return render_template('index.html', cities=cities)

match __name__:
    case "__main__":
        app.run(debug=True)