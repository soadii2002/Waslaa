from rest_framework import serializers
from waslaa_telecom.apps.plans.models import Plan


class PlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plan
        fields = [
            'id', 'name', 'plan_type', 'price',
            'description', 'features', 'is_active', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']