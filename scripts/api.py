import requests
import csv
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

# Function to fetch rainfall measurements for England
def get_rainfall_data_eng():
    eng_url = "http://environment.data.gov.uk/flood-monitoring/id/measures?parameter=rainfall"
    eng_response = requests.get(eng_url)
    if eng_response.status_code == 200:
        eng_data = eng_response.json()
        return eng_data['items']
    return []

# Function to fetch station data with coordinates for Scotland
def fetch_station_data_sco():
    sco_url = "https://www2.sepa.org.uk/rainfall/api/Stations"
    sco_response = requests.get(sco_url)
    sco_station_data = {}
    if sco_response.status_code == 200:
        sco_stations = sco_response.json()
        for station in sco_stations:
            latitude = safe_float_convert(station.get('station_latitude'))
            longitude = safe_float_convert(station.get('station_longitude'))
            if latitude is not None and longitude is not None:
                sco_station_data[station['station_no']] = {
                    'latitude': latitude,
                    'longitude': longitude
                }
    return sco_station_data

# Function to fetch latest hourly rainfall data for Scotland
def get_rainfall_data_sco(station_id):
    sco_url = f"https://www2.sepa.org.uk/rainfall/api/Hourly/{station_id}?all=true"
    sco_response = requests.get(sco_url)
    if sco_response.status_code == 200 and sco_response.json():
        return sco_response.json()[-1]
    return None

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
sco_station_coordinates = fetch_station_data_sco()
sco_rainfall_data = {station_id: get_rainfall_data_sco(station_id) for station_id in sco_station_coordinates}
wales_rainfall_data = get_wales_rainfall_data('413a14f470f64b70a010cfa3b4ed6a79')  # Replace 'YOUR_API_KEY' with the actual API key

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
for station_id, coordinates in sco_station_coordinates.items():
    sco_rainfall = get_rainfall_data_sco(station_id)
    if sco_rainfall:
        rainfall = safe_float_convert(sco_rainfall.get('Value'))
        lat_long_key = (coordinates['latitude'], coordinates['longitude'])
        if coordinates['latitude'] is not None and coordinates['longitude'] is not None:
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

# Write to an existing CSV file, appending to the next empty row
csv_filename = "rainfall_data.csv"

# First, open the file in read mode to find the first empty row
empty_row_index = None
with open(csv_filename, mode='w', newline='', encoding='utf-8') as file:
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
