from rest_framework import serializers
from waslaa_telecom.apps.tickets.models import SupportTicket


class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupportTicket
        fields = [
            'id', 'customer', 'subject', 'message',
            'status', 'admin_reply', 'replied_by', 'created_at'
        ]
        read_only_fields = [
            'id', 'customer', 'status',
            'admin_reply', 'replied_by', 'created_at'
        ]


class TicketCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupportTicket
        fields = ['subject', 'message']

    def create(self, validated_data):
        customer = self.context['request'].user
        return SupportTicket.objects.create(
            customer=customer,
            **validated_data
        )


class AdminTicketReplySerializer(serializers.ModelSerializer):
    class Meta:
        model = SupportTicket
        fields = [
            'id', 'customer', 'subject', 'message',
            'status', 'admin_reply', 'replied_by', 'created_at'
        ]
        read_only_fields = [
            'id', 'customer', 'subject', 'message',
            'status', 'replied_by', 'created_at'
        ]

    def update(self, instance, validated_data):
        instance.admin_reply = validated_data.get('admin_reply', instance.admin_reply)
        instance.replied_by = self.context['request'].user
        instance.save()
        return instance