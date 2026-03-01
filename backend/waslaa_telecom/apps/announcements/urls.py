from django.urls import path
from waslaa_telecom.apps.announcements.views import (
    AnnouncementListCreateView,
    AnnouncementDetailView,
)

app_name = 'announcements'

urlpatterns = [
    path('', AnnouncementListCreateView.as_view(), name='announcement-list'),
    path('<int:pk>/', AnnouncementDetailView.as_view(), name='announcement-detail'),
]