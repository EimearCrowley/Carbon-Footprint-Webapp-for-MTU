import requests
from django.conf import settings

DESTINATIONS = {
    "bishopstown": "MTU Bishopstown Campus, Bishopstown, Cork, Ireland",
    "sports_hall": "MTU Sports Hall, Bishopstown, Cork, Ireland",
    "student_centre": "MTU Student Centre, Bishopstown, Cork, Ireland",
    "park_ride": "MTU Park and Ride, Bishopstown, Cork, Ireland",
    "st_finbarrs": "St Fin Barre's Cathedral, Cork, Ireland",
    "carrolls_quay": "Carroll's Quay Car Park, Cork, Ireland"
}

mode_map = {
    "car": "driving",
    "bus": "transit",
    "train": "transit",
    "bike": "bicycling",
    "walk": "walking",
    "scooter": "driving"
}

def get_distance_km(origin, destination, mode="driving"):

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