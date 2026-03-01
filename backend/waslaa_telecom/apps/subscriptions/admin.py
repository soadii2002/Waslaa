from django.contrib import admin
from waslaa_telecom.apps.subscriptions.models import Subscription


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ['customer', 'plan', 'status', 'start_date']
    list_filter = ['status', 'plan']
    search_fields = ['customer__email', 'plan__name']
    ordering = ['-start_date']