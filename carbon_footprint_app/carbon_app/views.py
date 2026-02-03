from django.shortcuts import render, HttpResponse
from .forms import LocationForm
from .utils import calculate_emissions
from .google_maps import get_distance_km


# Create your views here.

def index(request):
    result = None
    distance = None

    if request.method == "POST":
        form = LocationForm(request.POST)
        if form.is_valid():
            days = form.cleaned_data["days"]
            mode = form.cleaned_data["mode"]
            origin = form.cleaned_data["origin"]
            destination = form.cleaned_data["destination"] 
            distance = get_distance_km(origin, destination)
            print("Distance:", distance)

            if distance:
                result = calculate_emissions(distance, days, mode)
    else:
        form = LocationForm()

    return render(request, "index.html", {
        "form": form, 
        "result": result,
        "distance": distance,
    })
