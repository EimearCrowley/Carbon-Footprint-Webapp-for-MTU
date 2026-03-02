from django.contrib import admin
from django.urls import path, include
from carbon_app import views


urlpatterns = [
    path('admin/', admin.site.urls),

    # login/logout urls
    path('accounts/', include('django.contrib.auth.urls')),
    path('', views.mode_selection_view, name='home'),
    path('previous-results/', views.previous_results, name='previous_results'),
    path('delete-result/<int:result_id>/', views.delete_result, name='delete_result'),

    # signup page
    path('accounts/signup/', views.signup_view, name='signup'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    # app pages
    path('', views.mode_selection_view, name='mode_selection'),
    path('transport/', views.transport_details_view, name='transport_details'),
    path('route/', views.route_days_view, name='route_days'),
    path('results/', views.results_view, name='results'),
    path('summary/', views.summary_view, name='summary'),
]