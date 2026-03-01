from rest_framework import serializers
from waslaa_telecom.apps.subscriptions.models import Subscription
from waslaa_telecom.apps.plans.serializers import PlanSerializer
from waslaa_telecom.apps.plans.models import Plan


class SubscriptionSerializer(serializers.ModelSerializer):
    plan = PlanSerializer(read_only=True)

    class Meta:
        model = Subscription
        fields = ['id', 'customer', 'plan', 'status', 'start_date', 'created_at']
        read_only_fields = ['id', 'customer', 'start_date', 'created_at']


class SubscribeSerializer(serializers.ModelSerializer):
    plan = serializers.PrimaryKeyRelatedField(queryset=Plan.objects.all())

    class Meta:
        model = Subscription
        fields = ['plan']

    def validate_plan(self, plan):
        if not plan.is_active:
            raise serializers.ValidationError("Cannot subscribe to an inactive plan.")
        return plan

    def validate(self, attrs):
        customer = self.context['request'].user
        active_sub = Subscription.objects.filter(
            customer=customer,
            status='active'
        ).exists()
        if active_sub:
            raise serializers.ValidationError(
                "You already have an active subscription."
            )
        return attrs

    def create(self, validated_data):
        customer = self.context['request'].user
        subscription = Subscription.objects.create(
            customer=customer,
            plan=validated_data['plan'],
            status='active',
        )
        return subscription


class SubscriptionUpdateSerializer(serializers.ModelSerializer):
    plan = serializers.PrimaryKeyRelatedField(
        queryset=Plan.objects.filter(is_active=True),
        required=False
    )

    class Meta:
        model = Subscription
        fields = ['plan', 'status']

    def update(self, instance, validated_data):
        if 'plan' in validated_data:
            instance.plan = validated_data['plan']
        if 'status' in validated_data:
            instance.status = validated_data['status']
        instance.save()
        return instance

    def to_representation(self, instance):
        return SubscriptionSerializer(instance, context=self.context).data