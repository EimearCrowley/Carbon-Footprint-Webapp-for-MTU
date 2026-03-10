import requests
from django.conf import settings

DESTINATIONS = {
    "bishopstown": "MTU Cork Bishopstown Campus",
    "sports_hall": "MTU Cork Sports Hall",
    "student_centre": "MTU Cork Student Centre",
    "park_ride": "MTU Cork Park and Ride",
    "st_finbarrs": "St Fin Barre's Cathedral Cork",
    "carrolls_quay": "Carroll's Quay Cork"
}

def get_distance_km(origin, destination):

    api_key = settings.GOOGLE_MAPS_API_KEY

    # convert short name to real location
    destination = DESTINATIONS.get(destination, destination)

    url = "https://maps.googleapis.com/maps/api/distancematrix/json"

    params = {
        "origins": origin,
        "destinations": destination,
        "mode": "driving",
        "units": "metric",
        "key": api_key,
    }

    response = requests.get(url, params=params).json()
    print("Google Maps API response:", response)

    try:
        distance_meters = response["rows"][0]["elements"][0]["distance"]["value"]
        return distance_meters / 1000
    except (KeyError, IndexError):
        return None