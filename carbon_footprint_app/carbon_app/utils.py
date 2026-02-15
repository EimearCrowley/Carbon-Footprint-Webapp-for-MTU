EMISSION_FACTORS = {
    "petrol_car": 0.192,    # defined in views
    "diesel_car": 0.171,    # defined in views
    "electric_car": 0.053,    # defined in views
    "bus": 0.101,    # per passenger
    "train": 0.041,     # per passenger
    "bike": 0.0, 
    "walk": 0.0, 
    'scooter': 0.022 # electric scooter or e-bike
}

def calculate_emissions(distance,days,mode):
    factor = EMISSION_FACTORS.get(mode, 0)
    return distance * days * factor * 2
