from django.urls import path
from waslaa_telecom.apps.subscriptions.views import (
    SubscribeView,
    MySubscriptionView,
    SubscriptionDetailView,
)

app_name = 'subscriptions'

urlpatterns = [
    path('subscribe/', SubscribeView.as_view(), name='subscribe'),
    path('me/', MySubscriptionView.as_view(), name='my-subscription'),
    path('<int:pk>/', SubscriptionDetailView.as_view(), name='subscription-detail'),
]