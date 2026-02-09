from django.urls import path
from .views import mode_selection_view, transport_details_view, route_days_view

urlpatterns = [
    path('', mode_selection_view, name='mode_selection'),
    path('transport/',transport_details_view, name='transport_details'),
    path('route/',route_days_view, name='route_days'),
]


