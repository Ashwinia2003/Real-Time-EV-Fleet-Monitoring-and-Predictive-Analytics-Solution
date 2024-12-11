import pandas as pd
import geopy.distance
csv_file_path="C:\Users\ashwini\OneDrive\Desktop\Ev management\flask-login-master\flask-login-master\tamilnadu_ev_stations_random.csv"
def load_station_data(csv_file_path):
    data = pd.read_csv(csv_file_path)
    stations = data.to_dict('records')
    print(f"Loaded {len(stations)} charging stations from the csv file")

#Coordinates for cities
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
    'Dharmapuri': (12.1189, 78.1393),
    'Tiruppur': (11.1085, 77.3411),
    'Theni': (10.0111, 77.4777),
    'Sivakasi': (9.4511, 77.7974),
    'Karur': (10.9576, 78.0807),
    'Nagapattinam': (10.7639, 79.8424),
    'Nagercoil': (8.1784, 77.4280),
    'Cuddalore': (11.7460, 79.7714),
    'Perambalur': (11.2333, 78.8667),
    'Krishnagiri': (12.5186, 78.2138),
    'Ariyalur': (11.1442, 79.0788)
    }
def calculate_distance(coords1,coords2):
    return geopy.distance.distance(coords1,coords2).km

def get_ev_details():
    max_range = int(input("Enter the max range of the EV (in km):"))
    remaining_charge = int(input("Enter the remaining battery percentage:"))
    remaining_km = (max_range*remaining_charge)/100
    return max_range , remaining_km

def find_optimized_route(source,destination,max_range,remaining_km,stations):
    current_location = city_coords[source]
    destination_coords = city_coords[destination]
    route = []
    visited_stations = set()
    iterations = 0
    while remaining_km < calculate_distance(current_location,destination_coords):
        iterations+=1
        print(f"Iteration :{iterations}")
        print(f"Current location: {current_location}")
        print(f"Remaining km: {remaining_km}")
    best_station = None
    best_distance = 0
    for station in stations:
        station_coords = (station['latitude'],station['longtitude'])
        distance_to_station = calculate_distance(current_location,station_coords)
        if station ['station_id'] in visited_stations:
            continue
        if distance_to_station <= remaining_km and distance_to_station > best_distance:
            best_station = station
            best_distance = distance_to_station

        if best_station is None:
            print("There is no station found within the remaining distance")
            break
        remaining_km = max_range
        print(f" Recharghing at station {best_station['station_id']} located at {best_station['latitude']},{best_station['longitude']}")
        print(f"Distance to station: {best_distance}km")
        


