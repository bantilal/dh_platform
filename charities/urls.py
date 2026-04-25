from django.urls import path
from . import views

urlpatterns = [
    path('add-charity/',    views.add_charity,    name='api-add-charity'),
    path('edit-charity/',   views.edit_charity,   name='api-edit-charity'),
    path('delete-charity/', views.delete_charity, name='api-delete-charity'),
    path('view-charity/',   views.view_charity,   name='api-view-charity'),
    path('charity-list/',   views.list_charities, name='api-charity-list'),
    path('donate/',         views.donate_charity, name='api-donate'),
]
