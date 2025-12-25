from kafka import KafkaProducer
import requests
import json
import time

# Kafka broker addresses
bootstrap_servers = ['10.0.0.82:9092', '10.0.0.83:9092']

# Create Kafka producer
producer = KafkaProducer(
    bootstrap_servers=bootstrap_servers,
    value_serializer=lambda v: json.dumps(v).encode('utf-8'),
    acks='all',  
    retries=5    
)

# Velib API URL
velib_api_url = "https://velib-metropole-opendata.smovengo.cloud/opendata/Velib_Metropole/station_status.json"

while True:
    try:
        # Fetch data from Velib API
        response = requests.get(velib_api_url)
        data = response.json()

        # Extract stations
        stations = data['data']['stations']

        for station in stations:
            payload = {
                "station_id": station.get("station_id"),
                "num_bikes_available": station.get("num_bikes_available"),
                "num_docks_available": station.get("num_docks_available"),
                "is_installed": station.get("is_installed"),
                "is_renting": station.get("is_renting"),
                "is_returning": station.get("is_returning"),
                "last_reported": station.get("last_reported")
            }

            producer.send("velib-station-status", payload)
            print("Sent:", payload)

        producer.flush()
        print("Batch sent. Waiting 60 seconds...\n")
        time.sleep(60)

    except Exception as e:
        print(f"Error: {e}")
        time.sleep(60)

