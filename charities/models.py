from django.db import models
from django.utils import timezone


class Charity(models.Model):
    name           = models.CharField(max_length=255)
    description    = models.TextField()
    short_bio      = models.CharField(max_length=500, null=True, blank=True)
    logo           = models.ImageField(upload_to='charity_logos/',   null=True, blank=True)
    banner         = models.ImageField(upload_to='charity_banners/', null=True, blank=True)
    website        = models.URLField(null=True, blank=True)
    category       = models.CharField(max_length=100, null=True, blank=True)
    is_featured    = models.BooleanField(default=False)
    status         = models.BooleanField(default=True)
    total_received = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    soft_delete    = models.BooleanField(default=False)
    created_at     = models.DateTimeField(default=timezone.now)
    updated_at     = models.DateTimeField(default=timezone.now)



class CharityEvent(models.Model):
    charity_id  = models.BigIntegerField(db_index=True)
    title       = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    event_date  = models.DateField()
    location    = models.CharField(max_length=255, null=True, blank=True)
    image       = models.ImageField(upload_to='charity_events/', null=True, blank=True)
    soft_delete = models.BooleanField(default=False)
    created_at  = models.DateTimeField(default=timezone.now)

class CharityDonation(models.Model):
    user_id           = models.BigIntegerField(db_index=True)
    charity_id        = models.BigIntegerField(db_index=True)
    amount            = models.DecimalField(max_digits=10, decimal_places=2)
    stripe_payment_id = models.CharField(max_length=255, null=True, blank=True)
    status            = models.CharField(max_length=20, default='completed')
    created_at        = models.DateTimeField(default=timezone.now)
