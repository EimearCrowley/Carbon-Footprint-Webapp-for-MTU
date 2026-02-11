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

MODE_CHOICES = [ 
    ('car', 'Car'), 
    ('bus', 'Bus'), 
    ('bike', 'Bike'), 
    ('walk', 'Walk'), 
    ('train', 'Train'),
]
                
FUEL_CHOICES = [
    ('petrol', 'Petrol'),
    ('diesel', 'Diesel'),
    ('electric', 'Electric'),
]

ENGINE_CHOICES_PETROL_DIESEL = [
    ('1.0L','1.0L'),
    ('1.2L','1.2L'),
    ('1.4L','1.4L'),
    ('1.6L','1.6L'),
    ('2.0L+','2.0L+'),
]

ENGINE_CHOICES_ELECTRIC = [
    ('Hybrid','Hybrid'),
    ('Fully Electric','Fully Electric')
]

class ModeSelectionForm(forms.Form):
    mode_1 = forms.ChoiceField(choices=MODE_CHOICES, widget=forms.RadioSelect, label="Primary Mode of Transport")
    duo_mode = forms.BooleanField(required=False, label="Do you use a secondary mode of transport?")
    mode_2 = forms.ChoiceField(choices=MODE_CHOICES, required=False, label="Secondary Mode of Transport")

class TransportDetailsForm(forms.Form):
    fuel_type = forms.ChoiceField(choices=FUEL_CHOICES, widget=forms.RadioSelect)
    engine_option = forms.ChoiceField(
        choices=ENGINE_CHOICES_PETROL_DIESEL + ENGINE_CHOICES_ELECTRIC,
        widget=forms.RadioSelect)
    

class RouteDaysForm(forms.Form):
    origin = forms.CharField(
        label='Start Location',
        max_length=100,
        widget=forms.TextInput(attrs={'placeholder': 'e.g. Cork City'})
    )

    CAR_PARK_CHOICES = [
        ("bishopstown", "Bishopstown Main 🅿️"),
        ("sports_hall", "Sports Hall 🏋️‍♂️"),
        ("student_centre", "Student Centre 🎓"),
        ("park_ride", "Park & Ride 🚌"),
        ("st_finbarrs", "St Finbarr’s 🏛️"),
        ("carrolls_quay", "Carroll’s Quay 🌉"),
    ]

    destination = forms.ChoiceField(
        choices=CAR_PARK_CHOICES,
        widget=forms.RadioSelect,
        label="Select Destination Car Park"
    )

    days_per_week = forms.IntegerField(
        label='Days per week',
        min_value=1,
        max_value=7,
        widget=forms.NumberInput(attrs={'placeholder': 'e.g. 5'})
    )

