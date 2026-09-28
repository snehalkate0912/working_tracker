from django.urls import path
from django.contrib.auth import views as auth_views
from . import views


urlpatterns = [

    # Login
    path(
        'login/',
        auth_views.LoginView.as_view(
            template_name='attendance/login.html'
        ),
        name='login'
    ),

    # Logout
    path(
        'logout/',
        auth_views.LogoutView.as_view(),
        name='logout'
    ),

    # Dashboard
    path(
        '',
        views.dashboard,
        name='dashboard'
    ),

    # Check In
    path(
        'check-in/<int:employee_id>/',
        views.check_in,
        name='check_in'
    ),

    # Check Out
    path(
        'check-out/<int:employee_id>/',
        views.check_out,
        name='check_out'
    ),

    # Visit History
    path(
        'visit-history/',
        views.visit_history,
        name='visit_history'
    ),

    # Attendance
    path(
        'attendance/',
        views.attendance,
        name='attendance'
    ),
]