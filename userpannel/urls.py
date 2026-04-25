from django.urls import path
from . import views

urlpatterns = [
    # Public
    path('',               views.home,             name='home'),
    path('login/',         views.login_page,        name='login'),
    path('register/',      views.register_page,     name='register'),

    # User panel
    path('dashboard/',     views.user_dashboard,    name='user-dashboard'),
    path('scores/',        views.user_scores,       name='user-scores'),
    path('draws/',         views.user_draws,        name='user-draws'),
    path('charity/',       views.user_charity,      name='user-charity'),
    path('subscription/',  views.user_subscription, name='user-subscription'),
    path('winnings/',      views.user_winnings,     name='user-winnings'),

    # Admin panel
    path('admin-panel/',            views.admin_dashboard, name='admin-dashboard'),
    path('admin-panel/users/',      views.admin_users,     name='admin-users'),
    path('admin-panel/draws/',      views.admin_draws,     name='admin-draws'),
    path('admin-panel/charities/',  views.admin_charities, name='admin-charities'),
    path('admin-panel/winners/',    views.admin_winners,   name='admin-winners'),
]
