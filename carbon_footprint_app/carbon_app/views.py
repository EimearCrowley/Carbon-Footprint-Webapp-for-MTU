from django.shortcuts import render, redirect
from .forms import TransportDetailsForm, ModeSelectionForm
from .google_maps import get_distance_km
from .forms import RouteDaysForm  # Add this import

# View for selecting transport mode
def mode_selection_view(request):
    if request.method == "POST":
        form = ModeSelectionForm(request.POST)
        if form.is_valid():
            mode = form.cleaned_data['mode_1']
            request.session['mode_1'] = mode
            request.session['duo_mode'] = form.cleaned_data['duo_mode']
            request.session['mode_2'] = form.cleaned_data.get('mode_2')

            if mode == 'car':
                return redirect('transport_details')  # Go to fuel type screen
            else:
                return redirect('route_days')  # Skip fuel screen
    else:
        form = ModeSelectionForm()
    return render(request, "mode_selection.html", {"form": form})

# View for selecting fuel type and engine (only for cars)
def transport_details_view(request):
    if request.session.get('mode_1') != 'car':
        return redirect('route_days')  # Prevent access if not car

    if request.method == "POST":
        form = TransportDetailsForm(request.POST)
        if form.is_valid():
            request.session['fuel_type'] = form.cleaned_data['fuel_type']
            request.session['engine_option'] = form.cleaned_data['engine_option']
            return redirect('route_days')
    else:
        form = TransportDetailsForm()

    petrol_diesel_engines = [
        ('1.0L', '1.0L'),
        ('1.2L', '1.2L'),
        ('1.4L', '1.4L'),
        ('1.6L', '1.6L'),
        ('2.0L+', '2.0L+'),
    ]

    electric_engines = [
        ('Hybrid', 'Hybrid'),
        ('Fully Electric', 'Fully Electric'),
    ]

    return render(request, "transport_details.html", {
        "form": form,
        "petrol_diesel_engines": petrol_diesel_engines,
        "electric_engines": electric_engines
    })

# View for entering route and number of days
def route_days_view(request):
    if request.method == "POST":
        form = RouteDaysForm(request.POST)
        if form.is_valid():
            request.session['origin'] = form.cleaned_data['origin']
            request.session['destination'] = form.cleaned_data['destination']
            request.session['days'] = form.cleaned_data['days_per_week']
            return redirect('results')
    else:
        form = RouteDaysForm()

    return render(request, "route_days.html", {"form": form})


# View for calculating and displaying results
def results_view(request):
    print("Session contents:", dict(request.session))  # Debugging

    fuel_type = request.session.get('fuel_type')
    engine_option = request.session.get('engine_option')
    origin = request.session.get('origin')
    destination = request.session.get('destination')
    days_raw = request.session.get('days')
    days = int(days_raw) if days_raw is not None else 0

    distance_km = get_distance_km(origin, destination)

    emission_factors = {
        'petrol': {
            '1.0L': 0.12,
            '1.2L': 0.14,
            '1.4L': 0.16,
            '1.6L': 0.18,
            '2.0L+': 0.22,
        },
        'diesel': {
            '1.0L': 0.11,
            '1.2L': 0.13,
            '1.4L': 0.15,
            '1.6L': 0.17,
            '2.0L+': 0.20,
        },
        'electric': {
            'Hybrid': 0.05,
            'Fully Electric': 0.02,
        }
    }

    try:
        factor = emission_factors[fuel_type][engine_option]
        weekly_emissions = distance_km * 2 * days * factor  # round trip
    except Exception:
        weekly_emissions = None

    request.session['distance_km'] = distance_km
    request.session['weekly_emissions'] = weekly_emissions

    return render(request, 'results.html', {
        'origin': origin,
        'destination': destination,
        'days': days,
        'distance_km': distance_km,
        'weekly_emissions': weekly_emissions,
        'fuel_type': fuel_type,
        'engine_option': engine_option,
    })

# View for displaying summary
def summary_view(request):
    context = {
        'mode_1': request.session.get('mode_1'),
        'duo_mode': request.session.get('duo_mode'),
        'mode_2': request.session.get('mode_2'),
        'fuel_type': request.session.get('fuel_type'),
        'engine_option': request.session.get('engine_option'),
        'origin': request.session.get('origin'),
        'destination': request.session.get('destination'),
        'days': request.session.get('days'),
        'distance_km': request.session.get('distance_km'),
        'weekly_emissions': request.session.get('weekly_emissions'),
    }
    return render(request, 'summary.html', context)

