from rest_framework import serializers
from waslaa_telecom.apps.payments.models import Payment
from waslaa_telecom.apps.subscriptions.models import Subscription
from django.utils import timezone


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = [
            'id', 'subscription', 'amount',
            'status', 'mock_reference', 'paid_at', 'created_at'
        ]
        read_only_fields = [
            'id', 'amount', 'mock_reference', 'paid_at', 'created_at'
        ]


class CheckoutSerializer(serializers.Serializer):
    subscription = serializers.PrimaryKeyRelatedField(
        queryset=Subscription.objects.all()
    )

    def validate_subscription(self, subscription):
        request = self.context['request']
        if subscription.customer != request.user:
            raise serializers.ValidationError(
                "You can only pay for your own subscription."
            )
        if subscription.status != 'active':
            raise serializers.ValidationError(
                "Subscription is not active."
            )
        return subscription

    def create(self, validated_data):
        subscription = validated_data['subscription']
        payment = Payment.objects.create(
            subscription=subscription,
            amount=subscription.plan.price,
            status='completed',
            paid_at=timezone.now(),
        )
        return payment


class AdminPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = [
            'id', 'subscription', 'amount',
            'status', 'mock_reference', 'paid_at', 'created_at'
        ]
        read_only_fields = [
            'id', 'amount', 'mock_reference', 'paid_at', 'created_at'
        ]