from django.db import models
from django.utils import timezone


class Subscription(models.Model):
    PLAN_CHOICES   = (('monthly', 'Monthly'), ('yearly', 'Yearly'))
    STATUS_CHOICES = (('active', 'Active'), ('expired', 'Expired'),
                      ('cancelled', 'Cancelled'), ('pending', 'Pending'))

    user_id            = models.BigIntegerField(db_index=True)
    plan               = models.CharField(max_length=20, choices=PLAN_CHOICES)
    status             = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    amount             = models.DecimalField(max_digits=10, decimal_places=2)
    charity_percent    = models.DecimalField(max_digits=5,  decimal_places=2, default=10)
    prize_pool_amount  = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    charity_amount     = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    stripe_sub_id      = models.CharField(max_length=255, null=True, blank=True)
    stripe_customer_id = models.CharField(max_length=255, null=True, blank=True)
    start_date         = models.DateField(null=True, blank=True)
    end_date           = models.DateField(null=True, blank=True)
    renewal_date       = models.DateField(null=True, blank=True)
    auto_renew         = models.BooleanField(default=True)
    meta               = models.JSONField(null=True, blank=True)
    soft_delete        = models.BooleanField(default=False)
    created_at         = models.DateTimeField(default=timezone.now)
    updated_at         = models.DateTimeField(default=timezone.now)


class PaymentHistory(models.Model):
    STATUS_CHOICES = (('success', 'Success'), ('failed', 'Failed'),
                      ('pending', 'Pending'), ('refunded', 'Refunded'))

    user_id           = models.BigIntegerField(db_index=True)
    subscription_id   = models.BigIntegerField(null=True, blank=True)
    stripe_payment_id = models.CharField(max_length=255, null=True, blank=True)
    amount            = models.DecimalField(max_digits=10, decimal_places=2)
    currency          = models.CharField(max_length=10, default='gbp')
    status            = models.CharField(max_length=20, choices=STATUS_CHOICES)
    description       = models.CharField(max_length=255, null=True, blank=True)
    meta              = models.JSONField(null=True, blank=True)
    created_at        = models.DateTimeField(default=timezone.now)
