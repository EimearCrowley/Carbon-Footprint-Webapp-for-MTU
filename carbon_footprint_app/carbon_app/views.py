from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from .forms import TransportDetailsForm, ModeSelectionForm, RouteDaysForm
from .google_maps import get_distance_km
from .models import EmissionRecord
import re

CAR_PARK_NAMES = {
    "bishopstown": "MTU Bishopstown Barrier Car Park",
    "sports_hall": "MTU Bishopstown Tiered Car Park",
    "student_centre": "MTU Bishopstown Student Centre Car Park",
    "park_ride": "MTU Park & Ride",
    "st_finbarrs": "St Finbarr's Car Park",
    "carrolls_quay": "Carroll's Quay Car Park"
}

# -----------------------------
# MODE SELECTION
# -----------------------------
def mode_selection_view(request):

    if request.method == "POST":
        form = ModeSelectionForm(request.POST)

        if form.is_valid():

            request.session["mode_1"] = form.cleaned_data["mode_1"]
            request.session["duo_mode"] = form.cleaned_data["duo_mode"]
            request.session["mode_2"] = form.cleaned_data.get("mode_2")

            if form.cleaned_data["mode_1"] == "car":
                return redirect("transport_details")
            else:
                return redirect("route_days")

    else:
        form = ModeSelectionForm()

    return render(request, "mode_selection.html", {"form": form})


# -----------------------------
# TRANSPORT DETAILS (CAR ONLY)
# -----------------------------
def transport_details_view(request):

    if request.session.get("mode_1") != "car":
        return redirect("route_days")

    if request.method == "POST":

        form = TransportDetailsForm(request.POST)

        if form.is_valid():

            passengers = int(request.POST.get("passengers", 1))
            request.session['passengers'] = passengers

            request.session['fuel_type'] = form.cleaned_data['fuel_type']
            request.session['engine_option'] = form.cleaned_data['engine_option']

            return redirect('route_days')

    else:
        form = TransportDetailsForm()

    petrol_diesel_engines = [
        ("1.0L","1.0L"),
        ("1.2L","1.2L"),
        ("1.4L","1.4L"),
        ("1.6L","1.6L"),
        ("2.0L+","2.0L+"),
    ]

    electric_engines = [
        ("Hybrid","Hybrid"),
        ("Fully Electric","Fully Electric"),
    ]

    return render(request,"transport_details.html",{
        "form":form,
        "petrol_diesel_engines":petrol_diesel_engines,
        "electric_engines":electric_engines
    })


# -----------------------------
# EIRCODE FORMATTER
# -----------------------------
def is_eircode(value):

    cleaned = value.replace(" ","").upper()

    pattern = r"^[A-Z]\d{2}[A-Z0-9]{4}$"

    if re.match(pattern, cleaned):
        return cleaned[:3] + " " + cleaned[3:]

    return None


# -----------------------------
# ROUTE + DAYS
# -----------------------------
def route_days_view(request):

    duo_mode = request.session.get("duo_mode")

    if request.method == "POST":

        form = RouteDaysForm(request.POST)

        if form.is_valid():

            origin = form.cleaned_data["origin"]
            destination = form.cleaned_data["destination"]
            days = form.cleaned_data["days_per_week"]

            formatted_origin = is_eircode(origin)

            if formatted_origin:
                origin = formatted_origin
            else:
                origin = origin.title()

            request.session["origin"] = origin
            request.session["destination"] = destination
            request.session["days"] = days

            return redirect("results")

    else:
        form = RouteDaysForm()

    return render(request,"route_days.html",{
        "form":form,
        "duo_mode":duo_mode
    })


# -----------------------------
# RESULTS PAGE
# -----------------------------
def results_view(request):

    mode = request.session.get('mode_1')
    fuel_type = request.session.get('fuel_type')
    engine_option = request.session.get('engine_option')
    passengers = int(request.session.get("passengers",1))
    origin = request.session.get('origin')
    destination = request.session.get('destination')
    days = int(request.session.get('days', 0))

    distance_km = get_distance_km(origin, destination,mode)

    # ADD BUS DISTANCE IF PARK & RIDE
    if destination == "park_ride":
        distance_km += 4.5
        
    request.session['distance_km'] = distance_km

    destination_display = CAR_PARK_NAMES.get(destination, destination)

    # EMISSION FACTORS
    emission_factors = {

        "car_petrol": {
            '1.0L': 0.12,
            '1.2L': 0.14,
            '1.4L': 0.16,
            '1.6L': 0.18,
            '2.0L+': 0.22,
        },

        "car_diesel": {
            '1.0L': 0.11,
            '1.2L': 0.13,
            '1.4L': 0.15,
            '1.6L': 0.17,
            '2.0L+': 0.20,
        },

        "car_electric": {
            'Hybrid': 0.05,
            'Fully Electric': 0.02,
        },

        "bus": 0.05,
        "train": 0.04,
        "bike": 0.0,
        "walk": 0.0,
        "scooter": 0.02
    }

    weekly_emissions = None

    try:

        if mode == "car":

            if fuel_type == "petrol":
                factor = emission_factors["car_petrol"][engine_option]

            elif fuel_type == "diesel":
                factor = emission_factors["car_diesel"][engine_option]

            else:
                factor = emission_factors["car_electric"][engine_option]

        else:
            factor = emission_factors.get(mode, 0.05)   # default value of 0.05 for unknown modes

        total_emissions = distance_km * 2 * days * factor
        weekly_emissions = round(total_emissions / passengers, 2)

    except Exception:
        weekly_emissions = None

    # SAVE TO SESSION
    request.session['weekly_emissions'] = weekly_emissions

    # SAVE TO DATABASE
    if request.user.is_authenticated and weekly_emissions:
        EmissionRecord.objects.create(
            user=request.user,
            origin=origin,
            destination=destination,
            distance_km=distance_km,
            weekly_emissions=weekly_emissions
        )

    national_weekly = 32.7

    difference = None
    comparison = None

    if weekly_emissions is not None:

        difference = round(weekly_emissions - national_weekly, 2)

        if difference > 0:
            comparison = "above"
        elif difference < 0:
            comparison = "below"
            difference = abs(difference)
        else:
            comparison = "equal"

    return render(request, 'results.html', {

        'mode': mode,
        'origin': origin,
        'destination': destination_display,
        'days': days,
        'distance_km': distance_km,
        'weekly_emissions': weekly_emissions,
        'fuel_type': fuel_type,
        'engine_option': engine_option,
        'national_weekly': national_weekly,
        'difference': difference,
        'comparison': comparison,

    })




# -----------------------------
# SUMMARY PAGE
# -----------------------------
def summary_view(request):

    weekly_emissions = request.session.get("weekly_emissions")

    national_average = 32.7

    difference = 0
    comparison = ""
    status = "yellow"

    if weekly_emissions:

        difference = round(weekly_emissions - national_average,2)

        if weekly_emissions < national_average * 0.7:
            status = "green"
            comparison = "well below"

        elif weekly_emissions <= national_average:
            status = "yellow"
            comparison = "around"

        else:
            status = "red"
            comparison = "above"

    destination = request.session.get("destination")

    destination_display = CAR_PARK_NAMES.get(destination, destination)

    context = {

        "mode_1": request.session.get("mode_1"),
        "mode_2": request.session.get("mode_2"),
        "fuel_type": request.session.get("fuel_type"),
        "engine_option": request.session.get("engine_option"),

        "origin": request.session.get("origin"),
        "destination": destination_display,
        "days": request.session.get("days"),
        "distance_km": request.session.get("distance_km"),

        "weekly_emissions": weekly_emissions,

        "national_average": national_average,
        "difference": abs(difference),
        "comparison": comparison,
        "status": status
}

    return render(request,"summary.html",context)


# -----------------------------
# SIGNUP
# -----------------------------
def signup_view(request):

    if request.method == "POST":

        form = UserCreationForm(request.POST)

        if form.is_valid():
            user = form.save()
            login(request,user)

            return redirect("mode_selection")

    else:
        form = UserCreationForm()

    return render(request,"registration/signup.html",{"form":form})


# -----------------------------
# DASHBOARD
# -----------------------------
@login_required
def dashboard_view(request):

    return render(request,"dashboard.html")


# -----------------------------
# PREVIOUS RESULTS
# -----------------------------
@login_required
def previous_results(request):

    results = EmissionRecord.objects.filter(user=request.user).order_by("created_at")
    
    for r in results:
        r.destination_display = CAR_PARK_NAMES.get(r.destination, r.destination.title())

    if results:
        total = sum(r.weekly_emissions for r in results)
        average = round(total / len(results),2)
    else:
        average = 0

    return render(request,"previous_results.html",{
        "results":results,
        "average_emissions":average
    })


# -----------------------------
# DELETE RESULT
# -----------------------------
@login_required
def delete_result(request, result_id):

    result = get_object_or_404(EmissionRecord,id=result_id,user=request.user)
    result.delete()

    return redirect("previous_results")
    