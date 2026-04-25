from django.urls import path
from . import views

urlpatterns = [
    path('create/',          views.create_subscription, name='api-sub-create'),
    path('view/',            views.view_subscription,   name='api-sub-view'),
    path('list/',            views.list_subscriptions,  name='api-sub-list'),
    path('cancel/',          views.cancel_subscription, name='api-sub-cancel'),
    path('payment-history/', views.payment_history,     name='api-sub-payment-history'),
    path('prize-pool/',      views.prize_pool_summary,  name='api-sub-prize-pool'),
]
