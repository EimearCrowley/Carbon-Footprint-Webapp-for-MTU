from django.shortcuts import render, HttpResponse
from .forms import LocationForm
from .utils import calculate_emissions
from .google_maps import get_distance_km

# Contains logic that runs when a user visits a page
# Create your views here.

def index(request):
    result = None
    distance = None

    if request.method == "POST":            # when user clicks calculate button
        form = LocationForm(request.POST)   # populates the form in the variable form
        if form.is_valid():                 # checks if all fields are valid
            days = form.cleaned_data["days"]
            mode = form.cleaned_data["mode"]
            origin = form.cleaned_data["origin"]
            destination = form.cleaned_data["destination"] 
            distance = get_distance_km(origin, destination)

            if distance:                    # checks if distance is not None
                result = calculate_emissions(distance, days, mode)  # calls function to calculate emissions
    else:                                   # runs when user first visits page
        form = LocationForm()
# render index.html and pass it form, result and distance (template sees the left hand side variables)
    return render(request, "index.html", {
        "form": form, 
        "result": result,
        "distance": distance,
    })
