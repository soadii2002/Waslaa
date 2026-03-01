from django.db import models
from waslaa_telecom.apps.users.models import User


class SupportTicket(models.Model):
    STATUS_CHOICES = [
        ('open', 'Open'),
    ]

    customer = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='tickets'
    )
    subject = models.CharField(max_length=200)
    message = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='open')
    admin_reply = models.TextField(null=True, blank=True)
    replied_by = models.ForeignKey(
        User, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='replied_tickets'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[{self.status}] {self.subject} — {self.customer.email}"