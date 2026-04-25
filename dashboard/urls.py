from django.urls import path
from . import views

urlpatterns = [
    path('user-dashboard/',  views.user_dashboard,  name='api-user-dashboard'),
    path('admin-dashboard/', views.admin_dashboard, name='api-admin-dashboard'),
    path('admin-reports/',   views.admin_reports,   name='api-admin-reports'),
]
