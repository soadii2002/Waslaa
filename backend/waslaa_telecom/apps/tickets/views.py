from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from waslaa_telecom.apps.tickets.models import SupportTicket
from waslaa_telecom.apps.tickets.serializers import (
    TicketSerializer,
    TicketCreateSerializer,
    AdminTicketReplySerializer,
)
from waslaa_telecom.apps.tickets.permissions import IsAdmin


class TicketListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        tickets = SupportTicket.objects.filter(
            customer=request.user
        ).order_by('-created_at')
        serializer = TicketSerializer(tickets, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = TicketCreateSerializer(
            data=request.data, context={'request': request}
        )
        if serializer.is_valid():
            ticket = serializer.save()
            return Response(
                TicketSerializer(ticket).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TicketDetailView(generics.RetrieveAPIView):
    serializer_class = TicketSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return SupportTicket.objects.filter(customer=self.request.user)


class AdminTicketListView(generics.ListAPIView):
    serializer_class = TicketSerializer
    permission_classes = [IsAdmin]
    queryset = SupportTicket.objects.all().order_by('-created_at')


class AdminTicketReplyView(generics.UpdateAPIView):
    serializer_class = AdminTicketReplySerializer
    permission_classes = [IsAdmin]
    queryset = SupportTicket.objects.all()
    http_method_names = ['patch']