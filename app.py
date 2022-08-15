# Imports
from flask import Flask, render_template, request, flash, redirect, session
import secrets, requests
from flask_sqlalchemy import SQLAlchemy

# Global variables
app = Flask(__name__)
app.secret_key = secrets.token_hex(16)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
db = SQLAlchemy(app)
API = '9dd5a007254678bd11aee4e1877d4cf2'

# Send a http request to get the weather from api
def get_weather(name):
    result = requests.get(f"https://api.openweathermap.org/data/2.5/weather?q={name}&appid={API}").json()
    
    match result['cod']:
        case '404':
            return None
            
        case _:
            city = {
                'name': name.title(),
                'c': round(result['main']['temp'] - 273.15),
                'f': round(result['main']['temp'] * 1.8 - 459.67),
                'description': result['weather'][0]['description'],
                'icon': result['weather'][0]['icon']
            }
            return city

# Database
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(50), nullable=False)
    
class City(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40), nullable=False, unique=True)
    
# Main route
@app.route('/', methods=["GET", "POST"])
def index():
    cities = [get_weather(city.name) for city in City.query.all()]
    
    match request.method:
        case "GET":
            return render_template('index.html', cities=cities)
        
        case "POST":
            city_name = request.form.get('city', '').strip()
            
            if (city := get_weather(city_name)) != None:
                for i in cities:
                    if i['name'] == city['name']:
                        flash(f"You've added \"{city['name']}\" already.", "warning")
                        break
                else:
                    db.session.add(City(name=city['name']))
                    db.session.commit()
                    cities.append(city)
                    
                return render_template('index.html', cities=cities)
            
            flash(f'"{city_name}" is not found.', "error")
            return render_template('index.html', cities=cities)

match __name__:
    case "__main__":
        app.run(debug=True) # Run the server