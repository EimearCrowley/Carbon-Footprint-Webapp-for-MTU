from turtle import mode

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from urllib3 import request
from .forms import TransportDetailsForm, ModeSelectionForm, RouteDaysForm, SelectDaysForm
from .google_maps import get_distance_km
from .models import EmissionRecord
import re
import json

CAR_PARK_NAMES = {
    "bishopstown": "MTU Bishopstown Barrier Car Park",
    "sports_hall": "MTU Bishopstown Tiered Car Park",
    "student_centre": "MTU Bishopstown Student Centre Car Park",
    "park_ride": "Park & Ride",
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
def mode_selection_view(request): # request - HttpRequest object that contains data about the current HTTP request (POST, session, method)

    if request.method == "POST":    # user clicks Next and browser sends POST request with form data
        form = ModeSelectionForm(request.POST)  # create form bound to user data - can validate.
        # request.POST - dictionary with submitted form data

        if form.is_valid(): # if form data is valid - required fields filled, correct format 

            # cleaned data - normalising to consistent format, removing extra spaces, converting to lowercase 
            request.session["mode_1"] = form.cleaned_data["mode_1"] 
            request.session["duo_mode"] = form.cleaned_data["duo_mode"]
            request.session["mode_2"] = form.cleaned_data.get("mode_2") # .get for optional fields

            if form.cleaned_data["mode_1"] == "car" or (form.cleaned_data["duo_mode"] and form.cleaned_data.get("mode_2") == "car"):
                return redirect("transport_details")
            else:
                return redirect("route_days")

    else:
        form = ModeSelectionForm()  # create empty form

    return render(request, "mode_selection.html", {"form": form})   # render template with empty form


# -----------------------------
# TRANSPORT DETAILS (CAR ONLY)
# -----------------------------
def transport_details_view(request):

    if request.session.get("mode_1") != "car" and request.session.get("mode_2") != "car":
        return redirect("route_days")

    if request.method == "POST":

        form = TransportDetailsForm(request.POST)

        if form.is_valid():
            if request.session.get("mode_1") == "car":
                request.session['passengers'] = form.cleaned_data.get("passengers")
                request.session['fuel_type'] = form.cleaned_data.get("fuel_type")
                request.session['engine_option'] = form.cleaned_data.get("engine_option")
            
            if request.session.get("mode_2") == "car":
                request.session["fuel_type_2"] = request.POST.get("fuel_type_2")
                request.session["engine_option_2"] = request.POST.get("engine_option_2")
                request.session["passengers_2"] = int(request.POST.get("passengers_2", 1))

            return redirect('route_days')

    else:
        form = TransportDetailsForm()

    petrol_diesel_engines = [   # engine sizes
        ("1.0L","1.0L"),
        ("1.2L","1.2L"),
        ("1.4L","1.4L"),
        ("1.6L","1.6L"),
        ("2.0L+","2.0L+"),
    ]

    electric_engines = [    # electric car types
        ("Hybrid","Hybrid"),
        ("Fully Electric","Fully Electric"),
    ]

    return render(request,"transport_details.html",{
        "form":form,
        "mode": request.session.get("mode_1"),
        "petrol_diesel_engines":petrol_diesel_engines,
        "electric_engines":electric_engines,
        "mode_2": request.session.get("mode_2")
    })


# -----------------------------
# EIRCODE FORMATTER
# -----------------------------
def is_eircode(value):

    cleaned = value.replace(" ","").upper() # cleaning input origin

    pattern = r"^[A-Z]\d{2}[A-Z0-9]{4}$"    # Eircode pattern: 1 letter, 2 digits, 4 alphanumeric characters (no spaces)

    if re.match(pattern, cleaned):  # if cleaned matches pattern, return formatted Eircode
        return cleaned[:3] + " " + cleaned[3:]

    return None # if not a valid Eircode, return None


# -----------------------------
# ROUTE + DAYS
# -----------------------------
def route_days_view(request):

    duo_mode = request.session.get("duo_mode")  # true or false

    if "journeys" not in request.session:   # if journeys doesn't exist, create empty list
        request.session["journeys"] = []

    
    journeys = request.session.get("journeys", [])  # get session journeys
    first_journey = request.session.get("days_per_week") is None    # if days_per_week does not exist, returns True

    if request.method == "POST":    # if user submits form
        
        remaining_days = request.session.get("remaining_days")  # determine remaining days, None if first journey

        if first_journey:   # if first journey, remaining days is days per week
            remaining_days = request.POST.get("days_per_week")  # POST because value exists only in form, not session yet

        form = RouteDaysForm(   # create form with variables
            request.POST,   # contains submitted form data - validate against form fields
            remaining_days=request.session.get("remaining_days"),
            first_journey=first_journey # show days per week field if first journey
    )

        if form.is_valid():

            origin = form.cleaned_data["origin"]
            secondary_origin = form.cleaned_data.get("secondary_origin")
            destination = form.cleaned_data["destination"]

            
            if first_journey:
                days_per_week = form.cleaned_data["days_per_week"]

                request.session["days_per_week"] = days_per_week

            else:   # if not first journey, use existing days per week
                days_per_week = request.session.get("days_per_week")

            formatted_origin = is_eircode(origin)   # format if origin is valid Eircode

            if formatted_origin:
                origin = formatted_origin
            else:
                origin = origin.title() # else capitalise location

            # Create journey object
            if destination == "park_ride":
                request.session["mode_2"] = "bus"   # fixed second mode for Park & Ride option
                journey = {
                    "origin": origin,
                    "secondary_origin": "Curraheen Park Greyhound Stadium", # fixed secondary origin for Park & Ride option
                    "destination": "MTU Bishopstown Barrier Car Park",
                    "mode": request.session.get("mode_1"),
                    "mode_2": "bus",
                    "fuel_type": request.session.get("fuel_type"),
                    "engine_option": request.session.get("engine_option"),
                    "days": [],  # added in select_days_view 
                    "fuel_type_2": None,
                    "engine_option_2": None,
                    }
            else:
                journey = {
                    "origin": origin,
                    "secondary_origin": secondary_origin,
                    "destination": destination,
                    "mode": request.session.get("mode_1"),
                    "mode_2": request.session.get("mode_2"),
                    "fuel_type": request.session.get("fuel_type"),
                    "engine_option": request.session.get("engine_option"),
                    "days": [],  # added in select_days_view 
                    "fuel_type_2": request.session.get("fuel_type_2"),
                    "engine_option_2": request.session.get("engine_option_2"),
                }

            journeys = request.session.get("journeys", [])  # get existing journeys from session, if none - []
            journeys.append(journey)

            request.session["journeys"] = journeys  # saving new journeys to session
            
            return redirect("select_days")
        else:
            print(form.errors)  # if form is not valid, print error

    else:   # if first load (GET request), create form with remaining days and whether first journey
        remaining_days = request.session.get("remaining_days")  # None for first journey
        form = RouteDaysForm(
            remaining_days=remaining_days,
            first_journey=first_journey
        )

    used_days = []  # days already assigned to journeys
    for j in journeys:
        used_days.extend(j["days"]) # add days from each journey to used_days list

    return render(request,"route_days.html",{   # render template
        "form":form,
        "duo_mode":duo_mode,
        "remaining_days": request.session.get("remaining_days",0),  # 0 prevents errors in template
        "first_journey": first_journey,
        "used_days": used_days
    })

# Select Days
def select_days_view(request):

    journeys = request.session.get("journeys", [])
    total_days = request.session.get("days_per_week", 7)

    used_days = []

    for j in journeys[:-1]: # loop through all journeys except current one
        used_days.extend(j.get("days", []))

    if request.method == "POST":

        selected_days = request.POST.getlist("days_selected")

        if not selected_days: # if no days selected, show error and re-render form with existing data
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

        journeys[-1]["days"] = selected_days    # update days for current journey in session data

        request.session["journeys"] = journeys

        used_days_count = sum(len(j.get("days",[])) for j in journeys) 

        remaining_days = total_days - used_days_count

        request.session["remaining_days"] = remaining_days

        if remaining_days > 0:
            return redirect("mode_selection")

        return redirect("results")

    current_days = journeys[-1].get("days",[]) if journeys else [] # pre-fill form with any previously selected days

    selected_total = sum(len(j.get("days",[])) for j in journeys[:-1]) # total selected days from previous journeys

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
# RESULTS PAGE
# -----------------------------
def results_view(request):

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

    for j in journeys:  # looping through journeys
        print(j)

        if j.get("mode_2"): # if mode_2 exists
            mode_display = f"{j['mode']} → {j['mode_2']}"
        else:
            mode_display = j["mode"]

        for d in j.get("days", []): # looping through days and creating a schedule
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

        fuel_type_2 = j.get("fuel_type_2")
        engine_option_2 = j.get("engine_option_2")

        days = len(j["days"]) # number of days assigned to each journey

        # Distances
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

        passengers = int(j.get("passengers",1))
        passengers_2 = int(j.get("passengers_2",1)) 

        # Mode 1 emission factor
        if mode == "car":

            if fuel_type == "petrol":
                factor_1 = emission_factors["car_petrol"][engine_option]

            elif fuel_type == "diesel":
                factor_1 = emission_factors["car_diesel"][engine_option]

            else:
                factor_1 = emission_factors["car_electric"][engine_option]

        else:
            factor_1 = emission_factors.get(mode, 0.05)

        # Mode 2 emission factor
        if mode_2 == "car":

            fuel_type_2 = j.get("fuel_type_2")
            engine_option_2 = j.get("engine_option_2")

            if fuel_type_2 == "petrol":
                factor_2 = emission_factors["car_petrol"][engine_option_2]

            elif fuel_type_2 == "diesel":
                factor_2 = emission_factors["car_diesel"][engine_option_2]

            else:
                factor_2 = emission_factors["car_electric"][engine_option_2]
        else:
            factor_2 = emission_factors.get(mode_2, 0) if mode_2 else 0

        emissions = ((distance_1 * factor_1) / passengers + (distance_2 * factor_2) / passengers_2) * 2 * days

        total_weekly_emissions += emissions
    
    weekly_emissions = round(total_weekly_emissions, 2) # round to 2 decimal places

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
    active_days = set() # to store unique active days across all journeys (set - no duplicates)
    for j in journeys:  # for each journey, add its days to the active_days set
        for d in j["days"]:
            active_days.add(d)

    schedule = []
    for key, label in day_names.items():    # key = "mon", label = "Mon"
        day_mode = None
        
        for j in journeys:
            if key in j["days"]:
                if j.get("mode_2"): # if mode_2 exists, show mode_1 → mode_2 in schedule
                    day_mode = f"{j['mode']} → {j['mode_2']}"
                else:
                    day_mode = j["mode"]
                break

        schedule.append({   # create schedule list
            "day": label,
            "mode": day_mode
        })

    raw_difference = weekly_emissions - national_weekly
    max_diff = max(abs(difference), national_weekly)

    # convert to percentage of half bar (50%)
    offset_percent = (raw_difference / max_diff) * 50 if max_diff else 0

        # Save each route
    if request.user.is_authenticated:   # save to database if user is logged in
        EmissionRecord.objects.create(  # creates new row in database table
            user=request.user,  # current logged-in user
            origin=journeys[0]["origin"] if journeys else "",   # take origin from first journey (if exists), else empty string
            destination=journeys[-1]["destination"] if journeys else "", # last destination
            transport_mode=journeys[0]["mode"] if journeys else "car",  # mode of first journey
            mode_2=journeys[0].get("mode_2"),   # second mode if exists
            secondary_origin=journeys[0].get("secondary_origin"),   # secondary origin if exists
            distance_km=total_distance, # calculated distance
            weekly_emissions=weekly_emissions,  # calculated emissions
            days=json.dumps(schedule_data)  # save schedule list as string in database
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
    

# -----------------------------
# SIGNUP
# -----------------------------
def signup_view(request):
    return render(request,"registration/disabled.html")
    # if request.method == "POST":

    #     form = UserCreationForm(request.POST)

    #     if form.is_valid():
    #         user = form.save()    # creates new user and saves to database
    #         login(request,user)   # immediately logs user in, creates session

    #         return redirect("mode_selection")

    # else:
    #     form = UserCreationForm()

    # return render(request,"registration/signup.html",{"form":form})

# -----------------------------
# DISABLED VIEW
# -----------------------------
def disabled_view(request, page_type):
    return render(request,"registration/disabled.html", {
        "page_type": page_type
    })

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
    # retrieves specific user's history from database, ordered by creation date 
        
    for r in results:
        try:    # convert r.days into list
            schedule_data = json.loads(r.days)
        except: # use empty list if fails
            schedule_data = []

        routes_set = set()  # create set to store unique routes

        for item in schedule_data:  # each item has origin, secondary_origin, destination, mode, etc.
            origin = item.get("origin")
            destination = item.get("destination")
            secondary = item.get("secondary_origin")

            destination_display = CAR_PARK_NAMES.get(destination, destination)

            if origin and destination:  # create route string
                route_str = origin

                if secondary:
                    route_str += f" → {secondary}"  # add secondary origin if exists

                route_str += f" → {destination_display}"    # add destination

                routes_set.add(route_str)   # add route string to route set

        r.routes_list = list(routes_set)    # convert set to list for template use

        day_map = {item["day"]: item["mode"] for item in schedule_data} # create day schedule
        full_schedule = []

        for d in day_order: # check if days in schedule_data match day and add to full_schedule
            full_schedule.append({
                "day": day_names.get(d, d),
                "mode": day_map.get(d),
                "used": d in day_map    # None if not used
            })

        r.schedule = full_schedule  # template can use
        r.total_distance = r.distance_km    # renaming

    if results:
        total = sum(r.weekly_emissions for r in results)    # total emissions
        average = round(total / len(results),2) # average emissions 
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

    result = get_object_or_404(EmissionRecord,id=result_id,user=request.user)   # find result by id and user, Error 404 if not found
    result.delete() # delete from database

    return redirect("previous_results")
    
# Reset Calculator - clear session data, remain logged in
def reset_calculator(request):

    request.session.pop("journeys", None)   # remove keys from session (clicking logo)
    request.session.pop("days_per_week", None)  
    request.session.pop("remaining_days", None)

    return redirect("mode_selection")

# Reset Full Session
def reset_and_start(request):
    keys_to_clear = ["journeys", "days_per_week", "remaining_days", "mode_1", "mode_2", "fuel_type", "engine_option", "passengers"]

    for key in keys_to_clear:
        request.session.pop(key, None)
    return redirect("mode_selection")