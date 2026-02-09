from django import forms

class ModeSelectionForm(forms.Form):
    MODE_CHOICES = [
        ('car', 'Car'),
        ('bus', 'Bus'),
        ('bike', 'Bike'),
        ('walk', 'Walk'),
        ('train', 'Train'),
    ]
    mode_1 = forms.ChoiceField(choices=MODE_CHOICES, widget=forms.RadioSelect, label="Primary Mode of Transport")
    duo_mode = forms.BooleanField(required=False, label="Use two modes of transport?")
    mode_2 = forms.ChoiceField(choices=MODE_CHOICES, required=False, label="Secondary Mode of Transport")

class TransportDetailsForm(forms.Form):
    fuel_type = forms.ChoiceField(
        choices=[('petrol', 'Petrol'), ('diesel', 'Diesel'), ('electric', 'Electric')],
        widget=forms.RadioSelect(attrs={'class': 'fuel-type'})
    )
    engine_option = forms.CharField(widget=forms.HiddenInput(), required=False)

from django import forms

DAYS_OF_WEEK = [
    ('mon', 'Monday'),
    ('tue', 'Tuesday'),
    ('wed', 'Wednesday'),
    ('thu', 'Thursday'),
    ('fri', 'Friday'),
    ('sat', 'Saturday'),
    ('sun', 'Sunday'),
]

class RouteDaysForm(forms.Form):
    start_location = forms.CharField(label="Your Location", max_length=100)
    destination = forms.CharField(label="College Location", max_length=100)
    travel_days = forms.MultipleChoiceField(
        choices=DAYS_OF_WEEK,
        widget=forms.CheckboxSelectMultiple,
        label="Which days do you travel?"
    )
