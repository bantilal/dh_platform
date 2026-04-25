from django.db import models
from django.utils import timezone


class WinnerVerification(models.Model):
    STATUS_CHOICES  = (('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected'))
    PAYMENT_CHOICES = (('pending', 'Pending'), ('paid', 'Paid'))

    user_id        = models.BigIntegerField(db_index=True)
    draw_id        = models.BigIntegerField(db_index=True)
    draw_winner_id = models.BigIntegerField(null=True, blank=True)
    match_type     = models.CharField(max_length=20)
    prize_amount   = models.DecimalField(max_digits=10, decimal_places=2)
    proof_file     = models.FileField(upload_to='winner_proofs/', null=True, blank=True)
    proof_notes    = models.TextField(null=True, blank=True)
    status         = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_CHOICES, default='pending')
    reviewed_by    = models.BigIntegerField(null=True, blank=True)
    reviewed_at    = models.DateTimeField(null=True, blank=True)
    rejection_note = models.TextField(null=True, blank=True)
    soft_delete    = models.BooleanField(default=False)
    created_at     = models.DateTimeField(default=timezone.now)
    updated_at     = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'dh_winner_verifications'

    def __str__(self):
        return f"User {self.user_id} – Draw {self.draw_id} ({self.status})"
