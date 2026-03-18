from django.db import models
from django.contrib.auth.models import User

class EmissionRecord(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    origin = models.CharField(max_length=200)
    destination = models.CharField(max_length=200)

    transport_mode = models.CharField(max_length=50, default="car")
    mode_2 = models.CharField(max_length=20, blank=True, null=True)
    secondary_origin = models.CharField(max_length=200, blank=True, null=True)

    distance_km = models.FloatField()
    weekly_emissions = models.FloatField()

    days = models.CharField(max_length=50, blank=True) 

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.weekly_emissions} kg"