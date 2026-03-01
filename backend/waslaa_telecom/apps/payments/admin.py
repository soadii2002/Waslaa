from django.contrib import admin
from waslaa_telecom.apps.payments.models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['mock_reference', 'subscription', 'amount', 'status', 'paid_at']
    list_filter = ['status']
    search_fields = ['mock_reference', 'subscription__customer__email']
    ordering = ['-created_at']