from django.shortcuts import render, HttpResponse

from .utils import calculate_emissions
from google_maps import get_distance_km


# Create your views here.

from django.shortcuts import render, redirect
from forms import ModeSelectionForm, TransportDetailsForm, RouteDaysForm

def mode_selection_view(request):
    return HttpResponse("SCREEN 1: Mode Selection")
    # if request.method == 'POST':
    #     form = ModeSelectionForm(request.POST)
    #     if form.is_valid():
    #         request.session['mode_1'] = form.cleaned_data['mode_1']
    #         request.session['duo_mode'] = form.cleaned_data['duo_mode']
    #         request.session['mode_2'] = form.cleaned_data.get('mode_2')
    #         return redirect('transport_details')
    # else:
    #     form = ModeSelectionForm()
    # return render(request, 'mode_selection.html', {'form': form})

def transport_details_view(request):
    if request.method == 'POST':
        form = TransportDetailsForm(request.POST)
        if form.is_valid():
            request.session['fuel_type'] = form.cleaned_data['fuel_type']
            request.session['engine_option'] = form.cleaned_data['engine_option']
            return redirect('route_days')  # Next screen
    else:
        form = TransportDetailsForm()
    return render(request, 'transport_details.html', {'form': form})

def route_days_view(request):
    if request.method == 'POST':
        form = RouteDaysForm(request.POST)
        if form.is_valid():
            request.session['start_location'] = form.cleaned_data['start_location']
            request.session['destination'] = form.cleaned_data['destination']
            request.session['travel_days'] = form.cleaned_data['travel_days']
            return redirect('daily_result')  # Next screen
    else:
        form = RouteDaysForm()
    return render(request, 'route_days.html', {'form': form})

