from django.urls import path
from . import views

urlpatterns = [
    path('submit-proof/',         views.submit_proof,         name='api-submit-proof'),
    path('view-verification/',    views.view_verification,    name='api-view-verification'),
    path('verification-list/',    views.list_verifications,   name='api-verification-list'),
    path('approve-verification/', views.approve_verification, name='api-approve-verification'),
    path('reject-verification/',  views.reject_verification,  name='api-reject-verification'),
    path('mark-payout-paid/',     views.mark_payout_paid,     name='api-mark-payout-paid'),
]
