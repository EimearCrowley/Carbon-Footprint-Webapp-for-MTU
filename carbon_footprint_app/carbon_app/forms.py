from django import forms



DAYS_OF_WEEK = [
    ("mon","Mon"),
    ("tue","Tue"),
    ("wed","Wed"),
    ("thu","Thu"),
    ("fri","Fri"),
    ("sat","Sat"),
    ("sun","Sun"),
]

class ModeSelectionForm(forms.Form):
    MODE_CHOICES = [
        ('car', 'Car'),
        ('bus', 'Bus'),
        ('bike', 'Bike'),
        ('walk', 'Walk'),
        ('train', 'Train'),
        ('scooter', 'E‑Scooter/Bike'),   # NEW OPTION
    ]
    mode_1 = forms.ChoiceField(choices=MODE_CHOICES, widget=forms.RadioSelect, label="Primary Mode of Transport")
    duo_mode = forms.BooleanField(required=False, label="Use two modes of transport?")
    mode_2 = forms.ChoiceField(choices=MODE_CHOICES, required=False, label="Secondary Mode of Transport")

CARPOOL_CHOICES = [
(1, "1 person (Just me)"),
(2, "2 people"),
(3, "3 people"),
(4, "4 people"),
(5, "5 people"),
]
class TransportDetailsForm(forms.Form):
    fuel_type = forms.ChoiceField(
        choices=[('petrol', 'Petrol'), ('diesel', 'Diesel'), ('electric', 'Electric')],
        widget=forms.RadioSelect(attrs={'class': 'fuel-type'})
    )
    engine_option = forms.CharField(widget=forms.HiddenInput(), required=False)

MODE_CHOICES = [ 
    ('car', 'Car'), 
    ('bus', 'Bus'), 
    ('bike', 'Bike'), 
    ('walk', 'Walk'), 
    ('train', 'Train'),
    ('scooter', 'E‑Scooter/Bike'),   # NEW OPTION
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
passengers = forms.ChoiceField(
    choices=CARPOOL_CHOICES,
    label="How many people are in the car?",
    initial=1
)
    

# Route days form (location + optional secondary location)
class RouteDaysForm(forms.Form):
    origin = forms.CharField(
        label='Start Location',
        max_length=100,
        widget=forms.TextInput(attrs={'placeholder': 'e.g. Cork City'})
    )

    CAR_PARK_CHOICES = [
        ("bishopstown", "MTU Bishopstown Barrier Car Park"), # 🅿️
        ("sports_hall", "MTU Bishopstown Tiered Car Park"), #🏋️‍♂️
        ("student_centre", "MTU Bishopstown Student Centre Car Park"), #🎓
        ("park_ride", "Park & Ride"), #🚌
        ("st_finbarrs", "St Finbarr’s"), # 🏛️️
        ("carrolls_quay", "Carroll’s Quay"), #🌉
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
        required=False,
        widget=forms.NumberInput(attrs={'placeholder': 'e.g. 5'})
    )

    secondary_origin = forms.CharField(
        required=False,
        label="Secondary Start Location",
        widget=forms.TextInput(attrs={'placeholder': 'e.g. Cork Train Station'})
    )

    secondary_destination = forms.CharField(
        required=False,
        label="Secondary Destination",
        widget=forms.TextInput(attrs={'placeholder': 'e.g. MTU Bishopstown'})
    )

    def __init__(self, *args, **kwargs):    # override init to set initial value for days_selected
        self.remaining_days = kwargs.pop("remaining_days", None)  # get remaining_days from kwargs
        if self.remaining_days is not None:
            self.remaining_days = int(self.remaining_days)
        super().__init__(*args, **kwargs)
        
class SelectDaysForm(forms.Form):
    DAYS = DAYS_OF_WEEK
    days_selected = forms.MultipleChoiceField(
        choices=DAYS,
        widget=forms.CheckboxSelectMultiple,
        label="Select the days that this route applies to"
    )
    def clean_days_selected(self):
        days = self.cleaned_data["days_selected"]
        if self.remaining_days is not None and len(days) > self.remaining_days:
            raise forms.ValidationError(f"You can only select up to {self.remaining_days} days based on your previous selections.")
        return days
        