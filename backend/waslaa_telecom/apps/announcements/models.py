from django.db import models
from waslaa_telecom.apps.users.models import User


class Announcement(models.Model):
    title = models.CharField(max_length=200)
    body = models.TextField()
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL,
        null=True, related_name='announcements'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title