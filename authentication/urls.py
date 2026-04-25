from django.urls import path
from . import views

urlpatterns = [
    path('register/',    views.register_view,  name='api-register'),
    path('login/',       views.login_view,      name='api-login'),
    path('check-auth/',  views.check_auth_view, name='api-check-auth'),
    path('logout/',      views.logout_view,     name='api-logout'),
    path('add-user/',    views.add_user_view,   name='api-add-user'),
    path('view-user/',   views.view_user,        name='api-view-user'),
    path('user-list/',   views.list_users,       name='api-user-list'),
    path('edit-user/',   views.edit_user,        name='api-edit-user'),
    path('user-status/', views.user_status,      name='api-user-status'),
]
