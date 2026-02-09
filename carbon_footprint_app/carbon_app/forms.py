# define forms as classes

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