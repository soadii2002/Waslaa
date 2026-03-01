from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from waslaa_telecom.apps.payments.models import Payment
from waslaa_telecom.apps.payments.serializers import (
    PaymentSerializer,
    CheckoutSerializer,
    AdminPaymentSerializer,
)
from waslaa_telecom.apps.payments.permissions import IsAdmin


class CheckoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = CheckoutSerializer(
            data=request.data, context={'request': request}
        )
        if serializer.is_valid():
            payment = serializer.save()
            return Response(
                PaymentSerializer(payment).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BillingHistoryView(generics.ListAPIView):
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Payment.objects.filter(
            subscription__customer=self.request.user
        ).order_by('-created_at')


class AdminPaymentListView(generics.ListAPIView):
    serializer_class = AdminPaymentSerializer
    permission_classes = [IsAdmin]
    queryset = Payment.objects.all().order_by('-created_at')


class AdminPaymentDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = AdminPaymentSerializer
    permission_classes = [IsAdmin]
    queryset = Payment.objects.all()