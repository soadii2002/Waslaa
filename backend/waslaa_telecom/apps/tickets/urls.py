from django.urls import path
from waslaa_telecom.apps.tickets.views import (
    TicketListCreateView,
    TicketDetailView,
    AdminTicketListView,
    AdminTicketReplyView,
)

app_name = 'tickets'

urlpatterns = [
    path('', TicketListCreateView.as_view(), name='ticket-list'),
    path('<int:pk>/', TicketDetailView.as_view(), name='ticket-detail'),
    path('admin/', AdminTicketListView.as_view(), name='admin-ticket-list'),
    path('admin/<int:pk>/reply/', AdminTicketReplyView.as_view(), name='admin-ticket-reply'),
]