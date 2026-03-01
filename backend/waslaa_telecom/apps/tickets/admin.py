from django.contrib import admin
from waslaa_telecom.apps.tickets.models import SupportTicket


@admin.register(SupportTicket)
class SupportTicketAdmin(admin.ModelAdmin):
    list_display = ['subject', 'customer', 'status', 'created_at']
    list_filter = ['status']
    search_fields = ['subject', 'customer__email']
    ordering = ['-created_at']