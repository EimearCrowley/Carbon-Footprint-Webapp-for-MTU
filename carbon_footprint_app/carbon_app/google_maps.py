import requests
from django.conf import settings

def get_distance_km(origin, destinaiton):
    api_key = settings.GOOGLE_MAPS_API_KEY
    url = "https://maps.googleapis.com/maps/api/directions/json"
    params = {
        "origin": origin,
        "destination": destinaiton,
        "mode": "driving",
        "units": "metric",
        "key": api_key,
    }
    response = requests.get(url, params=params).json()

    try:
        distance_meters = response["rows"][0]["elements"][0]["distance"]["value"]
        return distance_meters / 1000  # Convert to kilometers
    except (KeyError, IndexError):
        return None