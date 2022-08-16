# Imports
from flask import Flask, render_template, request, flash, session, redirect
import secrets, requests
from flask_session import Session

# Global variables
app = Flask(__name__)
app.secret_key = secrets.token_hex(16)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
API = '9dd5a007254678bd11aee4e1877d4cf2'

# Send a http request to get the weather from api
def get_weather(name):
    result = requests.get(f"https://api.openweathermap.org/data/2.5/weather?q={name}&appid={API}").json()
    
    match result['cod']:
        case '404':
            return None
            
        case _:
            return {
                'name': name.title(),
                'c': round(result['main']['temp'] - 273.15),
                'f': round(result['main']['temp'] * 1.8 - 459.67),
                'description': result['weather'][0]['description'],
                'icon': result['weather'][0]['icon']
            }
    
    
@app.route('/<path:path>')
def redirecting(path):
    return redirect('/')

# Main route
@app.route('/', methods=["GET", "POST"])
def index():
    if 'cities' not in session:
        session['cities'] = []
    
    match request.method:
        case "GET":
            return render_template('index.html', cities=session['cities'])
        
        case "POST":
            city_name = request.form.get('city', '').strip()
            
            if (city := get_weather(city_name)) != None:
                for i in session['cities']:
                    if i['name'] == city['name']:
                        flash(f"You've added \"{city['name']}\" already.", "warning")
                        break
                else:
                    session['cities'].append(city)
                    
                return render_template('index.html', cities=session['cities'])
            
            flash(f'"{city_name}" is not found.', "error")
            return render_template('index.html', cities=session['cities'])

match __name__:
    case "__main__":
        app.run(debug=True) # Run the server