from django.urls import path
from . import views

urlpatterns = [
    path('',views.mode_selection_view, name='mode_selection'),
    path('transport/', views.transport_details_view, name='transport_details'),
    path('route/', views.route_days_view, name='route_days'),
    path('results/', views.results_view, name='results'),
    path('summary/',views.summary_view, name='summary'),
]