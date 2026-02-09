import requests
from django.conf import settings

def get_distance_km(origin, destination):
    api_key = settings.GOOGLE_MAPS_API_KEY
    url = "https://maps.googleapis.com/maps/api/distancematrix/json"
    params = {
        "origins": origin,
        "destinations": destination,
        "mode": "driving",
        "units": "metric",
        "key": api_key,
    }
    response = requests.get(url, params=params).json()
    print("Google Maps API response:", response)  # Debugging statement

    try:
        distance_meters = response["rows"][0]["elements"][0]["distance"]["value"]
        return distance_meters / 1000  # Convert to kilometers
    except (KeyError, IndexError):
        return None