from django import forms

TRANSPORT_CHOICES = [
    ("petrol_car", "Petrol Car"),
    ("diesel_car", "Diesel Car"),
    ("electric_car", "Electric Car"),
    ("bus", "Bus"),
    ("train", "Train"),
    ("bike", "Bike"),
    ("walk", "Walk"),
]

# class TravelForm(forms.Form):
#     distance = forms.FloatField(label="Distance to college (km)")
#     days = forms.IntegerField(label="Days per week")
#     mode = forms.ChoiceField(choices=TRANSPORT_CHOICES)

class LocationForm(forms.Form):
    origin = forms.CharField(label="Your Location")
    destination = forms.CharField(label="College Location")
    mode = forms.ChoiceField(choices=TRANSPORT_CHOICES)
    days = forms.IntegerField(label="Days per week")