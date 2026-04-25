from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_CHOICES = (
        ('public', 'Public Visitor'),
        ('subscriber', 'Subscriber'),
        ('admin', 'Administrator'),
    )

    username = models.CharField(max_length=150, unique=True, null=True, blank=True)
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150, blank=True, null=True)

    country_code = models.CharField(max_length=10, blank=True, null=True)
    contact_no = models.CharField(max_length=15, blank=True, null=True)

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='public')

    profile_image = models.ImageField(upload_to='user_images/', blank=True, null=True)

    charity_id = models.BigIntegerField(blank=True, null=True)
    charity_percent = models.DecimalField(max_digits=5, decimal_places=2, default=10.00)

    email_verified = models.BooleanField(default=False)
    meta = models.JSONField(blank=True, null=True)

    soft_delete = models.BooleanField(default=False)


    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']