# defines app configurations (each app automatically gets an AppConfig class that inherits from django's AppConfig)

from django.apps import AppConfig


class CarbonAppConfig(AppConfig):
    name = 'carbon_app'
