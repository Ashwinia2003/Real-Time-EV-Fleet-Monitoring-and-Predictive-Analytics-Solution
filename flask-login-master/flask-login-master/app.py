from flask import Flask, request, render_template, redirect, url_for, session, jsonify
from flask_sqlalchemy import SQLAlchemy
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
import pickle
import random, datetime
from geopy.distance import distance as geopy_distance
import requests
import plotly.graph_objects as go


# Initialize the app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.secret_key = "ThisIsNotASecret:p"
db = SQLAlchemy(app)

# User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))

    def __init__(self, username, password):
        self.username = username
        self.password = password

# Vehicle model
class Vehicle(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    vehicle_id = db.Column(db.String(100), unique=True)
    owner = db.Column(db.String(100))
    registration_number = db.Column(db.String(100))
    battery_status = db.Column(db.String(100))
    speed = db.Column(db.Float)
    location = db.Column(db.String(200))

    def __init__(self, vehicle_id, owner, registration_number, battery_status, speed, location):
        self.vehicle_id = vehicle_id
        self.owner = owner
        self.registration_number = registration_number
        self.battery_status = battery_status
        self.speed = speed
        self.location = location
# Load ML Model

model_path = "battery_health_model.pkl"  # Path to your trained model file

try:
    with open(model_path, "rb") as f:
        model = pickle.load(f)
except Exception as e:
    print(f"Error loading model: {e}")

@app.route('/battery_health_status/', methods=['GET', 'POST'], endpoint='battery_health_status')
def predict_battery_health():
    if request.method == 'POST':
        try:
            # Retrieve form data
            input_params = {
                "Capacity (mAh)": float(request.form['capacity']),
                "Cycle Count": int(request.form['cycle_count']),
                "Voltage (V)": float(request.form['voltage']),
                "Temperature (°C)": float(request.form['temperature']),
                "Internal Resistance (mΩ)": float(request.form['internal_resistance'])
            }
            
            # Create a DataFrame for prediction
            input_data = pd.DataFrame([input_params])
            prediction = model.predict(input_data)[0]  # Predict battery health
            
            return render_template(
                'battery_health_status.html',
                prediction=round(prediction, 2),
                data=input_params
            )
        except Exception as e:
            return render_template('battery_health_status.html', error=str(e))
    return render_template('battery_health_status.html')

# Routes
@app.route('/', methods=['GET'])
def index():
    if session.get('logged_in'):
        return render_template('home.html', message="Welcome back!")
    else:
        return render_template('index.html', message="Hello!")

@app.route('/register/', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            db.session.add(User(username=request.form['username'], password=request.form['password']))
            db.session.commit()
            return redirect(url_for('login'))
        except:
            return render_template('register.html', message="User Already Exists")
    else:
        return render_template('register.html')

@app.route('/login/', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        u = request.form['username']
        p = request.form['password']
        user = User.query.filter_by(username=u, password=p).first()
        if user:
            session['logged_in'] = True
            session['user_id'] = user.id  # Save user ID in session
            return redirect(url_for('index'))
        return render_template('login.html', message="Incorrect Details")

@app.route('/logout/', methods=['GET'])
def logout():
    session.clear()  # Clear all session variables
    return redirect(url_for('index'))

@app.route('/register_vehicle/', methods=['GET', 'POST'])
def register_vehicle():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    if request.method == 'POST':
        try:
            vehicle = Vehicle(
                vehicle_id=request.form['vehicle_id'],
                owner=request.form['owner'],
                registration_number=request.form['registration_number'],
                battery_status=request.form['battery_status'],
                speed=request.form['speed'],
                location=request.form['location']  # Ensure location is being captured correctly
            )
            db.session.add(vehicle)
            db.session.commit()  # Make sure data is committed to the database
            return render_template('home.html', message="Vehicle registered successfully!")
        except Exception as e:
            return render_template('home.html', message=f"Error: {str(e)}")
    return render_template('register_vehicle.html')

@app.route('/vehicle_status/', methods=['GET'])
def vehicle_status():
    if request.method == 'GET':
        return render_template('vehicle_status.html')

@app.route('/api/real_time_vehicle_status/', methods=['GET'])
@app.route('/api/real_time_vehicle_status', methods=['GET'])   
def real_time_vehicle_status():
    if not session.get('logged_in'):
        return jsonify({"error": "Unauthorized access"}), 401

    vehicles = Vehicle.query.all()  # Fetch all vehicles from the database
    vehicle_data = []

    for vehicle in vehicles:
        # Random data generation for demonstration purposes
        vehicle.speed = random.uniform(20, 100)
        vehicle.battery_status = f"{random.randint(10, 100)}%"
        vehicle.location = f"{random.uniform(-90, 90)}, {random.uniform(-180, 180)}"
        db.session.commit()

        latitude, longitude = vehicle.location.split(", ")
        vehicle_data.append({
            "vehicle_id": vehicle.vehicle_id,
            "speed": round(vehicle.speed, 2),
            "battery_status": vehicle.battery_status,
            "latitude": latitude,
            "longitude": longitude,
            "last_updated": datetime.utcnow().isoformat()
        })

    return jsonify(vehicle_data)  # Ensure JSON data is returned to frontend

# City coordinates for route optimization
city_coords = {
    'Chennai': (13.0827, 80.2707),
    'Coimbatore': (11.0168, 76.9558),
    'Madurai': (9.9250, 78.1198),
    'Salem': (11.6643, 78.1460),
    'Trichy': (10.7905, 78.7047),
    'Erode': (11.3410, 77.7172),
    'Vellore': (12.9165, 79.1323),
    'Tirunelveli': (8.7277, 77.7063),
    'Puducherry': (11.9416, 79.8083),
    'Kanchipuram': (12.8333, 79.7056),
    'Tanjore': (10.7870, 79.1590),
    'Ramanagaram': (12.7324, 78.2495),
    'Dindigul': (10.3640, 77.9800),
    'Dharmapuri': (12.1189, 78.1393)
}

# Load EV charging stations
def load_station_data(csv_file_path):
    df = pd.read_csv(csv_file_path)
    return df.to_dict('records')

charging_stations_file = r'C:\Users\ashwini\OneDrive\Desktop\Ev management\flask-login-master\flask-login-master\tamilnadu_ev_stations_random.csv'
stations = load_station_data(charging_stations_file)

if not stations:
    print("Error: Stations data is empty.")

# Calculate distance
def calculate_distance(coords1, coords2):
    return geopy_distance(coords1, coords2).km

# Find optimized route
def find_optimized_route(source, destination, max_range, remaining_km, stations):
    current_location = city_coords[source]
    destination_coords = city_coords[destination]
    route = []
    visited_stations = set()

    while remaining_km < calculate_distance(current_location, destination_coords):
        best_station = None
        best_distance = 0

        for station in stations:
            station_coords = (station['latitude'], station['longitude'])
            distance_to_station = calculate_distance(current_location, station_coords)
            
            if station['station_id'] in visited_stations:
                continue
            
            if distance_to_station <= remaining_km and distance_to_station > best_distance:
                best_station = station
                best_distance = distance_to_station

        if best_station is None:
            break

        remaining_km = max_range
        route.append({
            'station_id': best_station['station_id'],
            'station_coords': (best_station['latitude'], best_station['longitude']),
            'distance_from_previous': best_distance
        })

        current_location = (best_station['latitude'], best_station['longitude'])
        visited_stations.add(best_station['station_id'])
        remaining_km -= best_distance

    remaining_distance = calculate_distance(current_location, destination_coords)
    if remaining_distance <= remaining_km:
        route.append({
            'station_id': destination,
            'station_coords': destination_coords,
            'distance_from_previous': remaining_distance
        })

    return route
@app.route('/route_optimization', methods=['GET', 'POST'])
def route_optimization():
    if request.method == 'POST':
        source = request.form['source']
        destination = request.form['destination']
        max_range = float(request.form['max_range'])
        remaining_charge = float(request.form['remaining_charge'])
        remaining_km = (max_range * remaining_charge) / 100

        if source not in city_coords or destination not in city_coords:
            return render_template(
                'route_optimization.html',
                error="Invalid source or destination."
            )

        route = find_optimized_route(source, destination, max_range, remaining_km, stations)
        return render_template('route_optimization.html', route=route, source=source, destination=destination)

    return render_template('route_optimization.html', cities=list(city_coords.keys()))

# OpenWeather API configuration
API_KEY = '269cd9d63b71b57a3134fbe597aceb8b'
BASE_URL = 'http://api.openweathermap.org/data/2.5/weather'

# Function to fetch weather data
def get_weather_data(city_name):
    try:
        url = f'{BASE_URL}?q={city_name}&appid={API_KEY}&units=metric'
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            main_data = data['main']
            weather_data = data['weather'][0]
            wind_data = data['wind']

            temperature = main_data['temp']
            humidity = main_data['humidity']
            weather_description = weather_data['description']
            wind_speed = wind_data['speed']

            return {
                'temperature': temperature,
                'humidity': humidity,
                'weather_description': weather_description,
                'wind_speed': wind_speed
            }
        else:
            return None
    except Exception as e:
        return str(e)

# Routes and models (already in your original app)
# ... (existing routes like /register, /login, etc.)

# Route for weather information
@app.route('/weather/', methods=['GET', 'POST'])
def weather():
    if request.method == 'POST':
        city_name = request.form['city_name']
        weather_info = get_weather_data(city_name)

        if weather_info:
            return render_template('weather.html', city=city_name, weather=weather_info)
        else:
            return render_template('weather.html', error="Could not fetch weather data. Please try again.")
    
    return render_template('weather.html')

# Display Behavior Analysis and Alerts page route
@app.route("/Display Behavior Analysis and Alerts.html/")
def Display_Behavior_Analysis_and_Alerts():
    return render_template("Display Behavior Analysis and Alerts.html")

@app.route('/energy_consumption_analysis', methods=['GET'])
def energy_consumption_analysis():
    try:
        # Load the dataset from the CSV file
        df = pd.read_csv(r'C:\Users\ashwini\OneDrive\Desktop\Ev management\flask-login-master\flask-login-master\COMED_hourly.csv', parse_dates=['Datetime'], index_col='Datetime')

        # Convert 'COMED_MW' column to numeric values (if necessary)
        df['COMED_MW'] = pd.to_numeric(df['COMED_MW'], errors='coerce')

        # Fill missing values
        df['COMED_MW'] = df['COMED_MW'].fillna(0)

        # Define the cost per MWh (e.g., $100 per MWh)
        cost_per_MWh = 100

        # Resample to daily energy consumption
        df_resampled = df.resample('D').sum()

        # Calculate the operational costs based on energy consumption
        df_resampled['Operational Costs'] = df_resampled['COMED_MW'] * cost_per_MWh

        # Create Plotly figure for line chart
        fig = go.Figure()

        # Add Energy Consumption line
        fig.add_trace(go.Scatter(x=df_resampled.index,
                                 y=df_resampled['COMED_MW'],
                                 mode='lines',
                                 name='Energy Consumption (MW)',
                                 line=dict(color='blue')))

        # Add Operational Costs line
        fig.add_trace(go.Scatter(x=df_resampled.index,
                                 y=df_resampled['Operational Costs'],
                                 mode='lines',
                                 name='Operational Costs ($)',
                                 line=dict(color='green')))

        # Update layout for the graph
        fig.update_layout(
            title="Energy Consumption and Operational Costs Over Time",
            xaxis_title="Date",
            yaxis_title="Value",
            legend_title="Metrics",
            template="plotly_dark",
            xaxis=dict(tickformat="%Y-%m-%d"),  # Date format for x-axis
            height=600,
            width=1000
        )

        # Create Pie chart for energy consumption distribution
        total_energy_per_day = df_resampled['COMED_MW'].resample('M').sum()  # Monthly energy consumption
        pie_fig = go.Figure(go.Pie(
            labels=total_energy_per_day.index.strftime('%Y-%m'),  # Format as YYYY-MM
            values=total_energy_per_day,
            title="Monthly Energy Consumption Distribution",
            textinfo="label+percent",
            hoverinfo="label+value+percent"
        ))

        pie_fig.update_layout(
            template="plotly_dark",
            height=500,
            width=700
        )

        # Convert Plotly graphs to HTML
        graph_html = fig.to_html(full_html=False)
        pie_chart_html = pie_fig.to_html(full_html=False)

        # Render the template with the graphs
        return render_template('energy_consumption_analysis.html', graph_html=graph_html, pie_chart_html=pie_chart_html)

    except Exception as e:
        return render_template('energy_consumption_analysis.html', error=str(e))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Ensure all tables are created
    app.run(debug=True)
