import requests
import csv
import json
from datetime import datetime

# Function to safely convert to float
def safe_float_convert(value, default=None):
    try:
        return float(value)
    except (ValueError, TypeError):
        return default

# Function to fetch station data with coordinates for England
def fetch_station_data_eng():
    url = 'https://environment.data.gov.uk/flood-monitoring/id/stations?parameter=rainfall'
    response = requests.get(url)
    eng_station_data = {}
    if response.status_code == 200:
        data = response.json()
        for station in data['items']:
            if station.get('lat') is not None and station.get('long') is not None:
                eng_station_data[station.get('notation')] = {
                    'latitude': station.get('lat'),
                    'longitude': station.get('long')
                }
    return eng_station_data

# Function to fetch station data with coordinates for Scotland
def get_scotland_rainfall_data(base_url):
    # Fetch the list of stations
    stations_url = f"{base_url}/api/Stations"
    stations_response = requests.get(stations_url)
    scotland_rainfall_data = []
    if stations_response.status_code == 200:
        stations = json.loads(stations_response.content)

        # Fetch latest data for each station
        for station in stations:
            station_id = station.get("station_no")
            station_data_url = f"{base_url}/api/Stations/{station_id}"
            try:
                response = requests.get(station_data_url)
                if response.status_code == 200 and response.content:
                    data = json.loads(response.content)
                    # Convert data types
                    latitude = float(data.get("station_latitude"))
                    longitude = float(data.get("station_longitude"))
                    rainfall = float(data.get("itemValue")) / 4  # Dividing rainfall value by 4
                    station_id = int(station_id)  # Convert station_id to integer

                    if latitude is not None and longitude is not None and rainfall is not None:
                        scotland_rainfall_data.append({
                            'station_id': station_id,
                            'latitude': latitude,
                            'longitude': longitude,
                            'rainfall': rainfall
                        })
                else:
                    print(f"Error fetching data for station {station_id}: HTTP {response.status_code}")
            except json.JSONDecodeError:
                print(f"Invalid JSON response for station {station_id}")
            except Exception as e:
                print(f"An error occurred: {e}")

    return scotland_rainfall_data



# Function to fetch station data with rainfall measurements for Wales
def get_wales_rainfall_data(api_key):
    url = 'https://api.naturalresources.wales/rivers-and-seas/v1/api/StationData'
    headers = {'Ocp-Apim-Subscription-Key': api_key}
    response = requests.get(url, headers=headers)
    wales_rainfall_data = []
    if response.status_code == 200:
        wales_data = response.json()
        for station in wales_data:
            if station['coordinates']['latitude'] is not None and station['coordinates']['longitude'] is not None:
                station_id = station['location']
                latitude = station['coordinates']['latitude']
                longitude = station['coordinates']['longitude']
                rainfall = None
                for parameter in station['parameters']:
                    if parameter['paramNameEN'] == 'Rainfall':
                        rainfall = parameter['latestValue']
                        break
                if rainfall is not None:
                    wales_rainfall_data.append({
                        'station_id': station_id,
                        'rainfall': rainfall,
                        'latitude': latitude,
                        'longitude': longitude
                    })
    return wales_rainfall_data

# Additional helper functions for calculations
def calculate_average_rainfall(data_list):
    if not data_list:
        return 0
    return sum(data_list) / len(data_list)

def calculate_total_rainfall(data_list):
    return sum(data_list)

def count_stations_with_rainfall(data_list):
    return sum(1 for value in data_list if value > 0)

# Fetching and processing data for England, Scotland, and Wales
eng_station_coordinates = fetch_station_data_eng()
eng_rainfall_data = get_rainfall_data_eng()
base_url = "https://www2.sepa.org.uk/rainfall"
scotland_rainfall_data = get_scotland_rainfall_data(base_url)
wales_rainfall_data = get_wales_rainfall_data('413a14f470f64b70a010cfa3b4ed6a79')  # Replace with actual API key

# Combine the data using latitude and longitude as the key
combined_data = []

# Process and combine England data
# Process and combine England data
for measurement in eng_rainfall_data:
    station_id = measurement.get('stationReference')
    rainfall = safe_float_convert(measurement.get('latestReading', {}).get('value'))
    coordinates = eng_station_coordinates.get(station_id, {'latitude': None, 'longitude': None})
    lat_long_key = (coordinates['latitude'], coordinates['longitude'])
    if coordinates['latitude'] is not None and coordinates['longitude'] is not None:
        combined_data.append([lat_long_key, rainfall, 'England'])

# Process and combine Scotland data
for station_data in scotland_rainfall_data:
    rainfall = safe_float_convert(station_data['rainfall'])
    latitude = station_data['latitude']
    longitude = station_data['longitude']
    lat_long_key = (latitude, longitude)
    if latitude is not None and longitude is not None:
        combined_data.append([lat_long_key, rainfall, 'Scotland'])

# Process and combine Wales data
for station_data in wales_rainfall_data:
    rainfall = safe_float_convert(station_data['rainfall'])
    latitude = station_data['latitude']
    longitude = station_data['longitude']
    lat_long_key = (latitude, longitude)
    if latitude is not None and longitude is not None:
        combined_data.append([lat_long_key, rainfall, 'Wales'])

# Calculate required values
eng_rainfall_values = [rainfall for _, rainfall, region in combined_data if region == 'England' and rainfall is not None]
sco_rainfall_values = [rainfall for _, rainfall, region in combined_data if region == 'Scotland' and rainfall is not None]
wales_rainfall_values = [rainfall for _, rainfall, region in combined_data if region == 'Wales' and rainfall is not None]

avg_eng_rainfall = calculate_average_rainfall(eng_rainfall_values)
avg_sco_rainfall = calculate_average_rainfall(sco_rainfall_values)
avg_wales_rainfall = calculate_average_rainfall(wales_rainfall_values)

total_eng_rainfall = calculate_total_rainfall(eng_rainfall_values)
total_sco_rainfall = calculate_total_rainfall(sco_rainfall_values)
total_wales_rainfall = calculate_total_rainfall(wales_rainfall_values)

stations_eng = count_stations_with_rainfall(eng_rainfall_values)
stations_sco = count_stations_with_rainfall(sco_rainfall_values)
stations_wales = count_stations_with_rainfall(wales_rainfall_values)

total_rainfall = total_eng_rainfall + total_sco_rainfall + total_wales_rainfall
avg_rainfall = calculate_average_rainfall(eng_rainfall_values + sco_rainfall_values + wales_rainfall_values)
total_stations = stations_eng + stations_sco + stations_wales

# Function to check if a row is empty
def is_row_empty(row):
    return not any(row)

# Filepath for the CSV file
csv_filename = "rainfall_data.csv"

# First, open the file in read mode to find the first empty row
empty_row_index = None
with open(csv_filename, mode='r', newline='', encoding='utf-8') as file:
    reader = csv.reader(file)
    for index, row in enumerate(reader):
        if is_row_empty(row):
            empty_row_index = index
            break

# Then, open the file in append mode to write the new data
with open(csv_filename, mode='a', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)

    # If no empty row was found, append the new data
    if empty_row_index is None:
        writer.writerow([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), avg_rainfall,
                         avg_eng_rainfall, avg_sco_rainfall, avg_wales_rainfall,
                         total_rainfall, total_eng_rainfall,
                         total_sco_rainfall, total_wales_rainfall,
                         total_stations, stations_eng, stations_sco, stations_wales])

# Final print statement with current datetime
current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
print(f"Data has been appended to {csv_filename}. Current time is {current_time}")
