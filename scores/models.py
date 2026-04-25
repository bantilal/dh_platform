from django.db import models
from django.utils import timezone


class GolfScore(models.Model):
    user_id     = models.BigIntegerField(db_index=True)
    score       = models.IntegerField()       # 1–45 Stableford
    score_date  = models.DateField()
    notes       = models.TextField(null=True, blank=True)
    soft_delete = models.BooleanField(default=False)
    created_at  = models.DateTimeField(default=timezone.now)
    updated_at  = models.DateTimeField(default=timezone.now)
