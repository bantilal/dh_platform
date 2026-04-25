from django.urls import path, include

urlpatterns = [
    path('auth/',          include('authentication.urls')),
    path('subscriptions/', include('subscriptions.urls')),
    path('scores/',        include('scores.urls')),
    path('draws/',         include('draws.urls')),
    path('charities/',     include('charities.urls')),
    path('winners/',       include('winners.urls')),
    path('dashboard/',     include('dashboard.urls')),
]
