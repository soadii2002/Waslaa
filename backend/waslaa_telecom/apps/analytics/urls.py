from django.urls import path
from waslaa_telecom.apps.analytics.views import AnalyticsDashboardView

app_name = 'analytics'

urlpatterns = [
    path('dashboard/', AnalyticsDashboardView.as_view(), name='dashboard'),
]