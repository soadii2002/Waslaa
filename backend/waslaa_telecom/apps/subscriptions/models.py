from django.db import models
from waslaa_telecom.apps.users.models import User
from waslaa_telecom.apps.plans.models import Plan


class Subscription(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('suspended', 'Suspended'),
        ('cancelled', 'Cancelled'),
    ]

    customer = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='subscriptions'
    )
    plan = models.ForeignKey(
        Plan, on_delete=models.PROTECT, related_name='subscriptions'
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.customer.email} — {self.plan.name} ({self.status})"