from django.db import models
from django.contrib.auth.models import User

class EmissionRecord(models.Model): # creating a database table

    user = models.ForeignKey(User, on_delete=models.CASCADE)    # each record belongs to a user, if user deleted - their records automatically deleted

    origin = models.CharField(max_length=200)
    destination = models.CharField(max_length=200)

    transport_mode = models.CharField(max_length=50, default="car")
    mode_2 = models.CharField(max_length=20, blank=True, null=True)
    secondary_origin = models.CharField(max_length=200, blank=True, null=True)

    distance_km = models.FloatField()
    weekly_emissions = models.FloatField()

    days = models.CharField(max_length=50, blank=True) # mon, tues, etc.

    created_at = models.DateTimeField(auto_now_add=True)    # timestamp when record created

    def __str__(self):
        return f"{self.user.username} - {self.weekly_emissions} kg" # when you print the object, shows user - emissions kg