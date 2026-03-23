from turtle import mode

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from .forms import TransportDetailsForm, ModeSelectionForm, RouteDaysForm, SelectDaysForm
from .google_maps import get_distance_km
from .models import EmissionRecord
import re
import json

CAR_PARK_NAMES = {
    "bishopstown": "MTU Bishopstown Barrier Car Park",
    "sports_hall": "MTU Bishopstown Tiered Car Park",
    "student_centre": "MTU Bishopstown Student Centre Car Park",
    "park_ride": "MTU Park & Ride",
    "st_finbarrs": "St Finbarr's Car Park",
    "carrolls_quay": "Carroll's Quay Car Park"
}

day_names = {
    "mon": "Mon",
    "tue": "Tue",
    "wed": "Wed",
    "thu": "Thu",
    "fri": "Fri",
    "sat": "Sat",
    "sun": "Sun"
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

    if "journeys" not in request.session:
        request.session["journeys"] = []

    
    journeys = request.session.get("journeys", [])
    first_journey = request.session.get("days_per_week") is None

    if request.method == "POST":
        
        remaining_days = request.session.get("remaining_days")

        if first_journey:
            remaining_days = request.POST.get("days_per_week")

        form = RouteDaysForm(
            request.POST,
            remaining_days=request.session.get("remaining_days"),
            first_journey=first_journey
    )

        if form.is_valid():

            origin = form.cleaned_data["origin"]
            secondary_origin = form.cleaned_data.get("secondary_origin")
            destination = form.cleaned_data["destination"]

            
            if first_journey:
                days_per_week = form.cleaned_data["days_per_week"]
                
                if not days_per_week:
                    form.add_error("days_per_week", "Please enter how many days you travel per week.")
                    return render(request, "route_days.html", {
                        "form": form,
                        "duo_mode": duo_mode,
                        "remaining_days": request.session.get("remaining_days", 0),
                        "first_journey": first_journey,
                        "used_days": used_days
                    })

                request.session["days_per_week"] = days_per_week

            else:
                days_per_week = request.session.get("days_per_week")

            formatted_origin = is_eircode(origin)

            if formatted_origin:
                origin = formatted_origin
            else:
                origin = origin.title()

            # store weekly days once
            if first_journey:
                request.session["days_per_week"] = days_per_week

            # create journey
            journey = {
                "origin": origin,
                "secondary_origin": secondary_origin,
                "destination": destination,
                "mode": request.session.get("mode_1"),
                "mode_2": request.session.get("mode_2"),
                "fuel_type": request.session.get("fuel_type"),
                "engine_option": request.session.get("engine_option"),
                "days": []
            }

            journeys = request.session.get("journeys", [])
            journeys.append(journey)

            request.session["journeys"] = journeys

            
            total_days = request.session.get("days_per_week")

            
            return redirect("select_days")
        else:
            print(form.errors)  # if form is not valid, print error

    else:
        remaining_days = request.session.get("remaining_days")
        form = RouteDaysForm(
            remaining_days=remaining_days,
            first_journey=first_journey
        )

    used_days = []
    for j in journeys:
        used_days.extend(j["days"])

    return render(request,"route_days.html",{
        "form":form,
        "duo_mode":duo_mode,
        "remaining_days": request.session.get("remaining_days",0),
        "first_journey": first_journey,
        "used_days": used_days
    })


# -----------------------------
# RESULTS PAGE
# -----------------------------
def results_view(request):

    passengers = int(request.session.get("passengers",1))

    journeys = request.session.get("journeys", [])

    emission_factors = {

        "car_petrol": {
            '1.0L': 0.116,
            '1.2L': 0.127,
            '1.4L': 0.136,
            '1.6L': 0.15,
            '2.0L+': 0.215,
        },

        "car_diesel": {
            '1.0L': 0.097,
            '1.2L': 0.108,
            '1.4L': 0.115,
            '1.6L': 0.131,
            '2.0L+': 0.164,
        },

        "car_electric": {
            'Hybrid': 0.072,
            'Fully Electric': 0.06,
        },

        "bus": 0.101,
        "train": 0.041,
        "bike": 0.021,
        "walk": 0.0,
        "scooter": 0.022
    }
    total_weekly_emissions = 0
    total_distance = 0

    schedule_data = []

    for j in journeys:

        if j.get("mode_2"):
            mode_display = f"{j['mode']} → {j['mode_2']}"
        else:
            mode_display = j["mode"]

        for d in j.get("days", []):
            schedule_data.append({
                "day": d,
                "mode": mode_display,
                "origin": j["origin"],
                "destination": j["destination"],
                "secondary_origin": j.get("secondary_origin")
            })

        mode = j["mode"]
        mode_2 = j.get("mode_2")

        origin = j["origin"]
        secondary_origin = j.get("secondary_origin")
        destination = j["destination"]

        fuel_type = j.get("fuel_type")
        engine_option = j.get("engine_option")

        days = len(j["days"])

        # DISTANCES
        if mode_2 and secondary_origin:

            distance_1 = get_distance_km(origin, secondary_origin, mode)
            distance_2 = get_distance_km(secondary_origin, destination, mode_2)
        else:
            distance_1 = get_distance_km(origin, destination, mode)
            distance_2 = 0

        distance_km = distance_1 + distance_2

        round_trip_distance = distance_km * 2
        weekly_distance = round_trip_distance * days

        total_distance += weekly_distance

        # FACTOR MODE 1
        if mode == "car":

            if fuel_type == "petrol":
                factor_1 = emission_factors["car_petrol"][engine_option]

            elif fuel_type == "diesel":
                factor_1 = emission_factors["car_diesel"][engine_option]

            else:
                factor_1 = emission_factors["car_electric"][engine_option]

        else:
            factor_1 = emission_factors.get(mode, 0.05)

        # FACTOR MODE 2
        factor_2 = emission_factors.get(mode_2, 0) if mode_2 else 0

        emissions = (distance_1 * factor_1 + distance_2 * factor_2) * 2 * days

        total_weekly_emissions += emissions

    weekly_emissions = round(total_weekly_emissions / passengers, 2)

    request.session["weekly_emissions"] = weekly_emissions

    national_weekly = 32.7

    difference = round(weekly_emissions - national_weekly, 2)

    if difference > 0:
        comparison = "above"
    elif difference < 0:
        comparison = "below"
        difference = abs(difference)
    else:
        comparison = "equal"

    all_days = ["mon","tue","wed","thu","fri","sat","sun"]
    active_days = set()
    for j in journeys:
        for d in j["days"]:
            active_days.add(d)

    schedule = []
    for key, label in day_names.items():
        day_mode = None
        
        for j in journeys:
            if key in j["days"]:
                if j.get("mode_2"):
                    day_mode = f"{j['mode']} → {j['mode_2']}"
                else:
                    day_mode = j["mode"]
                break

        schedule.append({
            "day": label,
            "mode": day_mode
        })

    raw_difference = weekly_emissions - national_weekly
    max_diff = max(abs(difference), national_weekly)

    # convert to percentage of half bar (50%)
    offset_percent = (raw_difference / max_diff) * 50 if max_diff else 0

        # ✅ SAVE EACH ROUTE
    if request.user.is_authenticated:
        EmissionRecord.objects.create(
            user=request.user,
            origin=journeys[0]["origin"] if journeys else "",
            destination=journeys[-1]["destination"] if journeys else "",
            transport_mode=journeys[0]["mode"] if journeys else "car",
            mode_2=journeys[0].get("mode_2"),
            secondary_origin=journeys[0].get("secondary_origin"),
            distance_km=total_distance,
            weekly_emissions=weekly_emissions,
            days=json.dumps(schedule_data)
)

    return render(request, "results.html", {
        "weekly_emissions": weekly_emissions,
        "distance_km": total_distance,
        "national_weekly": national_weekly,
        "difference": difference,
        "comparison": comparison,
        "journeys": journeys,
        "all_days": all_days,
        "active_days": active_days,
        "schedule": schedule,
        "offset_percent": offset_percent
    })

# Select Days
def select_days_view(request):

    journeys = request.session.get("journeys", [])
    total_days = request.session.get("days_per_week", 7)

    used_days = []

    for j in journeys[:-1]:
        used_days.extend(j.get("days", []))

    if request.method == "POST":

        selected_days = request.POST.getlist("days_selected")

        if not selected_days:
    # rebuild values properly
            used_days = []
            for j in journeys[:-1]:
                used_days.extend(j.get("days", []))

            selected_total = sum(len(j.get("days", [])) for j in journeys[:-1])
            remaining_days = total_days - selected_total

            return render(request, "select_days.html", {
                "error": "Please select at least one day.",
                "remaining_days": remaining_days,
                "used_days": used_days,
                "selected_total": selected_total,
                "total_days": total_days,
                "current_days": [],
                "day_names": day_names
            })

        # ✅ ONLY inside POST
        journeys[-1]["days"] = selected_days

        request.session["journeys"] = journeys

        used_days_count = sum(len(j.get("days",[])) for j in journeys)

        remaining_days = total_days - used_days_count

        request.session["remaining_days"] = remaining_days

        if remaining_days > 0:
            return redirect("mode_selection")

        return redirect("results")

    # ✅ GET request logic (no selected_days here)

    current_days = journeys[-1].get("days",[]) if journeys else []

    selected_total = sum(len(j.get("days",[])) for j in journeys[:-1])

    remaining_days = total_days - selected_total

    return render(request,"select_days.html",{

        "remaining_days":remaining_days,
        "used_days":used_days,
        "selected_total":selected_total,
        "total_days":total_days,
        "current_days":current_days,
        "day_names":day_names

    })
    

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
    day_order = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]

    results = EmissionRecord.objects.filter(user=request.user).order_by("created_at")
        
    for r in results:
        r.destination_display = CAR_PARK_NAMES.get(r.destination, r.destination.title())

        try:
            schedule_data = json.loads(r.days)
        except:
            schedule_data = []

        routes_set = set()

        for item in schedule_data:
            mode = item.get("mode")

            origin = item.get("origin")
            destination = item.get("destination")
            secondary = item.get("secondary_origin")

            destination_display = CAR_PARK_NAMES.get(destination, destination)

            if origin and destination:
                route_str = origin

                if secondary:
                    route_str += f" → {secondary}"

                route_str += f" → {destination_display}"

                routes_set.add(route_str)

        r.routes_list = list(routes_set)

        day_map = {item["day"]: item["mode"] for item in schedule_data}
        full_schedule = []

        for d in day_order:
            full_schedule.append({
                "day": day_names.get(d, d),
                "mode": day_map.get(d),
                "used": d in day_map
            })

        r.schedule = full_schedule

        r.total_distance = r.distance_km 

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
    
# Reset Calculator - clear session data
def reset_calculator(request):

    request.session.pop("journeys", None)
    request.session.pop("days_per_week", None)
    request.session.pop("remaining_days", None)

    return redirect("mode_selection")

# Reset Session
def reset_and_start(request):
    keys_to_clear = ["journeys", "days_per_week", "remaining_days", "mode_1", "mode_2", "fuel_type", "engine_option", "passengers"]

    for key in keys_to_clear:
        request.session.pop(key, None)
    return redirect("mode_selection")