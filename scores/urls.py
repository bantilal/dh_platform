from django.urls import path
from . import views

urlpatterns = [
    path('add-score/',        views.add_score,       name='api-add-score'),
    path('edit-score/',       views.edit_score,       name='api-edit-score'),
    path('delete-score/',     views.delete_score,     name='api-delete-score'),
    path('score-list/',       views.list_scores,      name='api-score-list'),
    path('admin-edit-score/', views.admin_edit_score, name='api-admin-edit-score'),
]
