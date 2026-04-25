from django.urls import path
from . import views

urlpatterns = [
    path('create-draw/',   views.create_draw,   name='api-create-draw'),
    path('simulate-draw/', views.simulate_draw, name='api-simulate-draw'),
    path('publish-draw/',  views.publish_draw,  name='api-publish-draw'),
    path('view-draw/',     views.view_draw,      name='api-view-draw'),
    path('draw-list/',     views.list_draws,     name='api-draw-list'),
]
