from rest_framework import generics
from waslaa_telecom.apps.announcements.models import Announcement
from waslaa_telecom.apps.announcements.serializers import AnnouncementSerializer
from waslaa_telecom.apps.announcements.permissions import IsAdminOrReadOnly


class AnnouncementListCreateView(generics.ListCreateAPIView):
    serializer_class = AnnouncementSerializer
    permission_classes = [IsAdminOrReadOnly]
    queryset = Announcement.objects.all().order_by('-created_at')


class AnnouncementDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = AnnouncementSerializer
    permission_classes = [IsAdminOrReadOnly]
    queryset = Announcement.objects.all()