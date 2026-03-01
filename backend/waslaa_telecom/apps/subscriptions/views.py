from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from rest_framework.views import APIView

from waslaa_telecom.apps.subscriptions.models import Subscription
from waslaa_telecom.apps.subscriptions.serializers import (
    SubscriptionSerializer,
    SubscribeSerializer,
    SubscriptionUpdateSerializer,
)


class SubscribeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = SubscribeSerializer(
            data=request.data, context={'request': request}
        )
        if serializer.is_valid():
            subscription = serializer.save()
            return Response(
                SubscriptionSerializer(subscription).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MySubscriptionView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            subscription = Subscription.objects.select_related('plan').get(
                customer=request.user,
                status='active'
            )
            return Response(SubscriptionSerializer(subscription).data)
        except Subscription.DoesNotExist:
            return Response(
                {'detail': 'No active subscription found.'},
                status=status.HTTP_404_NOT_FOUND
            )


class SubscriptionDetailView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = SubscriptionUpdateSerializer

    def get_queryset(self):
        return Subscription.objects.filter(customer=self.request.user)

    def get_object(self):
        try:
            obj = Subscription.objects.get(pk=self.kwargs['pk'])
        except Subscription.DoesNotExist:
            from rest_framework.exceptions import NotFound
            raise NotFound("Subscription not found.")
        if obj.customer != self.request.user:
            raise PermissionDenied("You do not have permission to modify this subscription.")
        return obj