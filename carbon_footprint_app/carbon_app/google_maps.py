import requests
from django.conf import settings

DESTINATIONS = {
    "bishopstown": "Dunromin, Rossa Ave, Bishopstown, Cork, Ireland",
    "sports_hall": "MTU Sports Hall, Bishopstown, Cork, Ireland",
    "student_centre": "MTU Student Centre, Bishopstown, Cork, Ireland",
    "park_ride": "Curraheen Park Greyhound Stadium, Cork, Ireland",
    "st_finbarrs": "Ivyville Medical Centre, 1 Douglas Rd, Ballinlough, Cork, T12 AK2H, Ireland",
    "carrolls_quay": "Carrolls Quay Car Park, Carroll's Quay, Victorian Quarter, Cork, Ireland"
}

mode_map = {
    "car": "driving",
    "bus": "transit",
    "train": "transit",
    "bike": "bicycling",
    "walk": "walking",
    "scooter": "bicycling",
}

def get_distance_km(origin, destination, mode="driving"):

    api_key = settings.GOOGLE_MAPS_API_KEY

    # convert short name to real location
    destination = DESTINATIONS.get(destination, destination)

    url = "https://maps.googleapis.com/maps/api/distancematrix/json"

    params = {
        "origins": origin,
        "destinations": destination,
        "mode": mode_map.get(mode, "driving"),
        "units": "metric",
        "key": api_key,
    }

    response = requests.get(url, params=params).json()  # get request with query parameters, convert to dictionary
    print(response)

    try:    # try block incase of failure
        distance_meters = response["rows"][0]["elements"][0]["distance"]["value"]   # extract distance in meters
        return distance_meters / 1000   # convert to km
    except (KeyError, IndexError):
        return None