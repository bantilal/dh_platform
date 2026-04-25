from django.db import models
from django.utils import timezone


class Draw(models.Model):
    TYPE_CHOICES   = (('random', 'Random'), ('algorithmic', 'Algorithmic'))
    STATUS_CHOICES = (('draft', 'Draft'), ('simulated', 'Simulated'), ('published', 'Published'))

    title            = models.CharField(max_length=255)
    draw_type        = models.CharField(max_length=20, choices=TYPE_CHOICES, default='random')
    status           = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    draw_month       = models.IntegerField()
    draw_year        = models.IntegerField()
    winning_numbers  = models.JSONField(null=True, blank=True)
    prize_pool_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    jackpot_rollover = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    jackpot_claimed  = models.BooleanField(default=False)
    published_by     = models.BigIntegerField(null=True, blank=True)
    published_at     = models.DateTimeField(null=True, blank=True)
    simulation_data  = models.JSONField(null=True, blank=True)
    soft_delete      = models.BooleanField(default=False)
    created_at       = models.DateTimeField(default=timezone.now)
    updated_at       = models.DateTimeField(default=timezone.now)



class DrawParticipant(models.Model):
    draw_id          = models.BigIntegerField(db_index=True)
    user_id          = models.BigIntegerField(db_index=True)
    submitted_scores = models.JSONField()
    matched_count    = models.IntegerField(default=0)
    is_winner        = models.BooleanField(default=False)
    created_at       = models.DateTimeField(default=timezone.now)


class DrawWinner(models.Model):
    MATCH_CHOICES = (('5_match', '5 Match'), ('4_match', '4 Match'), ('3_match', '3 Match'))

    draw_id      = models.BigIntegerField(db_index=True)
    user_id      = models.BigIntegerField(db_index=True)
    match_type   = models.CharField(max_length=20, choices=MATCH_CHOICES)
    prize_amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at   = models.DateTimeField(default=timezone.now)
