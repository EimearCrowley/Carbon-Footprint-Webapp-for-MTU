from django.contrib import admin
from django.urls import path, include
from carbon_app import views


urlpatterns = [

    # login/logout urls
    path('', views.mode_selection_view, name='home'),
    path('previous-results/', views.previous_results, name='previous_results'),
    path('delete-result/<int:result_id>/', views.delete_result, name='delete_result'),

    path('dashboard/', views.dashboard_view, name='dashboard'),

    # app pages
    path('', views.mode_selection_view, name='mode_selection'),
    path('transport/', views.transport_details_view, name='transport_details'),
    path('route/', views.route_days_view, name='route_days'),
    path("select-days/", views.select_days_view, name="select_days"),
    path('results/', views.results_view, name='results'),
    path("reset/", views.reset_calculator, name="reset_calculator"),
    path("reset-start/", views.reset_and_start, name="reset_start"),
]