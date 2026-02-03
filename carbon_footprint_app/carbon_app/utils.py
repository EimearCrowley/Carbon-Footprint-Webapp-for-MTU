EMISSION_FACTORS = {
    "petrol_car": 0.192,
    "diesel_car": 0.171,
    "electric_car": 0.053,
    # "hybrid_car": ____
    "bus": 0.105,
    "train": 0.041,
    # "e-bike/scooter": ____
    "bike": 0.0,
    "walk": 0.0,
}

def calculate_emissions(distance,days,mode):
    factor = EMISSION_FACTORS.get(mode, 0)
    return distance * days * factor * 2

