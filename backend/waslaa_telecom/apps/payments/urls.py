from django.urls import path
from waslaa_telecom.apps.payments.views import (
    CheckoutView,
    BillingHistoryView,
    AdminPaymentListView,
    AdminPaymentDetailView,
)

app_name = 'payments'

urlpatterns = [
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('billing/', BillingHistoryView.as_view(), name='billing-history'),
    path('admin/', AdminPaymentListView.as_view(), name='admin-payments'),
    path('admin/<int:pk>/', AdminPaymentDetailView.as_view(), name='admin-payment-detail'),
]