import pandas as pd
import geopy.distance

# Load the dataset of EV charging stations from the CSV file
def load_station_data(csv_file_path):
    df = pd.read_csv(csv_file_path)
    stations = df.to_dict('records')  # Convert DataFrame to a list of dictionaries
    print(f"Loaded {len(stations)} charging stations from the CSV file.")  # Debugging
    return stations

# Coordinates for cities in Tamil Nadu (add more cities here)
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

# Function to calculate distance between two coordinates
def calculate_distance(coords1, coords2):
    return geopy.distance.distance(coords1, coords2).km

# EV vehicle details
def get_ev_details():
    max_range = int(input("Enter the max range of the EV (in km): "))
    remaining_charge = int(input("Enter the remaining battery percentage: "))
    remaining_km = (max_range * remaining_charge) / 100  # Remaining km the EV can travel
    return max_range, remaining_km

# Step 5: Find the optimized route and charging stations
def find_optimized_route(source, destination, max_range, remaining_km, stations):
    current_location = city_coords[source]
    destination_coords = city_coords[destination]
    route = []
    visited_stations = set()  # Track visited stations to avoid infinite loops
    iteration = 0  # To keep track of the iterations

    while remaining_km < calculate_distance(current_location, destination_coords):
        iteration += 1
        print(f"\nIteration {iteration}:")
        print(f"Current location: {current_location}")
        print(f"Remaining km: {remaining_km}")

        # Find the furthest charging station within the remaining km range
        best_station = None
        best_distance = 0
        for station in stations:
            station_coords = (station['latitude'], station['longitude'])
            distance_to_station = calculate_distance(current_location, station_coords)
            
            # Skip already visited stations
            if station['station_id'] in visited_stations:
                continue
            
            # Select the furthest station within range
            if distance_to_station <= remaining_km and distance_to_station > best_distance:
                best_station = station
                best_distance = distance_to_station

        if best_station is None:
            print("No reachable charging station found within the remaining distance.")
            break

        # Recharge at the best station
        remaining_km = max_range  # Recharge to full range at the station
        print(f"Recharging at station {best_station['station_id']} located at {best_station['latitude']}, {best_station['longitude']}.")
        print(f"Distance to station: {best_distance} km")

        route.append({
            'station_id': best_station['station_id'],
            'station_coords': (best_station['latitude'], best_station['longitude']),
            'distance_from_previous': best_distance
        })

        # Set the current location to the charging station and mark it as visited
        current_location = (best_station['latitude'], best_station['longitude'])
        visited_stations.add(best_station['station_id'])
        remaining_km -= best_distance

    # Final segment to destination
    remaining_distance = calculate_distance(current_location, destination_coords)
    print(f"\nFinal segment to {destination}. Remaining distance: {remaining_distance} km.")
    if remaining_distance <= remaining_km:
        route.append({
            'station_id': destination,
            'station_coords': destination_coords,
            'distance_from_previous': remaining_distance
        })
        print(f"Destination reached: {destination}!")
    else:
        print(f"Unable to reach {destination} with the remaining battery.")

    return route

# Main program
def main():
    print("Welcome to the EV Charging Service!\n")
    print("Select your source city from the list below:")
    for idx, city in enumerate(city_coords.keys(), 1):
        print(f"{idx}. {city}")

    source_choice = int(input("\nEnter the number corresponding to your source city: "))
    source = list(city_coords.keys())[source_choice - 1]

    print("\nSelect your destination city from the list below (same set of cities):")
    for idx, city in enumerate(city_coords.keys(), 1):
        if city != source:
            print(f"{idx}. {city}")

    destination_choice = int(input("\nEnter the number corresponding to your destination city: "))
    destination = list(city_coords.keys())[destination_choice - 1]

    max_range, remaining_km = get_ev_details()

    # Load charging stations data (you should replace the file path with the actual one)
    csv_file_path = 'tamilnadu_ev_stations_random.csv'  # Update with your actual file path
    stations = load_station_data(csv_file_path)

    # Find optimized route
    optimized_route = find_optimized_route(source, destination, max_range, remaining_km, stations)

    # Output the route details
    print("\nStarting point:", source)
    print(f"Max range: {max_range} km")
    print(f"Remaining charge: {(remaining_km/max_range)*100}%")
    print(f"Remaining km: {remaining_km} km\n")

    for idx, station in enumerate(optimized_route):
        if station['station_id'] == destination:
            print(f"Destination: {station['station_id']}")
            print(f"Coordinates: {station['station_coords']}")
            print(f"Distance from last station: {station['distance_from_previous']} km")
        else:
            print(f"Station {idx + 1}: {station['station_id']}")
            print(f"Coordinates: {station['station_coords']}")
            print(f"Distance from last station: {station['distance_from_previous']} km")

if __name__ == '__main__':
    main()
