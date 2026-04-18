from django import forms

MODE_CHOICES = [ 
    ('car', 'Car'), 
    ('bus', 'Bus'), 
    ('bike', 'Bike'), 
    ('walk', 'Walk'), 
    ('train', 'Train'),
    ('scooter', 'E‑Scooter/Bike'),  
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

DAYS_OF_WEEK = [
    ("mon","Mon"),
    ("tue","Tue"),
    ("wed","Wed"),
    ("thu","Thu"),
    ("fri","Fri"),
    ("sat","Sat"),
    ("sun","Sun"),
]

CARPOOL_CHOICES = [
(1, "1 person (Just me)"),
(2, "2 people"),
(3, "3 people"),
(4, "4 people"),
(5, "5 people"),
]

class ModeSelectionForm(forms.Form):
    MODE_CHOICES = [
        ('car', 'Car'),
        ('bus', 'Bus'),
        ('bike', 'Bike'),
        ('walk', 'Walk'),
        ('train', 'Train'),
        ('scooter', 'E‑Scooter/Bike'),
    ]
    mode_1 = forms.ChoiceField(choices=MODE_CHOICES, widget=forms.RadioSelect, label="Primary Mode of Transport") # one transport type, options from MODE_CHOICES, rendered as radio buttons, label for form field
    duo_mode = forms.BooleanField(required=False, label="Use two modes of transport?") # checkbox, doesn't give error if not ticked
    mode_2 = forms.ChoiceField(choices=MODE_CHOICES, required=False, label="Secondary Mode of Transport")
    
    def clean(self):
        cleaned_data = super().clean() # get cleaned data from form

        duo_mode = cleaned_data.get("duo_mode") 
        mode_2 = cleaned_data.get("mode_2")

        if duo_mode and not mode_2:
            self.add_error("mode_2", "Please select a second mode of transport.")

        return cleaned_data
    

class TransportDetailsForm(forms.Form):
    fuel_type = forms.ChoiceField(
        choices=[('petrol', 'Petrol'), ('diesel', 'Diesel'), ('electric', 'Electric')],
        widget=forms.RadioSelect(attrs={'class': 'fuel-type'}), required=False
    )
    
    engine_option = forms.CharField(widget=forms.HiddenInput(), required=False)
    # hidden field, set dynamically based on fuel type and mode selection

    passengers = forms.ChoiceField(
    choices=CARPOOL_CHOICES,
    label="How many people are in the car?",
    initial=1, required=False
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
        required=True,
        widget=forms.NumberInput(attrs={'placeholder': 'e.g. 5'})
    )

    secondary_origin = forms.CharField(
        required=False,
        label="Secondary Start Location",
        widget=forms.TextInput(attrs={'placeholder': 'e.g. Cork Train Station'})
    )


    def __init__(self, *args, **kwargs):    # flexible arguments - any number of positional arguments, any number of named arguments

        self.remaining_days = kwargs.pop("remaining_days", None)    # removes from kwargs
        self.first_journey = kwargs.pop("first_journey", True)

        if self.remaining_days is not None: # session data always stored as strings
            self.remaining_days = int(self.remaining_days) # convert to int

        super().__init__(*args, **kwargs)   # call parent constructor method

        # Only require days on first journey
        if not self.first_journey:
            self.fields["days_per_week"].required = False
        
class SelectDaysForm(forms.Form):
    DAYS = DAYS_OF_WEEK
    days_selected = forms.MultipleChoiceField(
        choices=DAYS,
        widget=forms.CheckboxSelectMultiple,
        label="Select the days that this route applies to"
    )
    def clean_days_selected(self):
        days = self.cleaned_data["days_selected"]
        return days
        