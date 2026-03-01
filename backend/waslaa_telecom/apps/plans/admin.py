from django.contrib import admin
from waslaa_telecom.apps.plans.models import Plan


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ['name', 'plan_type', 'price', 'is_active', 'created_at']
    list_filter = ['plan_type', 'is_active']
    search_fields = ['name']
    ordering = ['-created_at']