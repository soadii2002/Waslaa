from django.urls import path
from waslaa_telecom.apps.plans.views import PlanListCreateView, PlanDetailView

app_name = 'plans'

urlpatterns = [
    path('', PlanListCreateView.as_view(), name='plan-list'),
    path('<int:pk>/', PlanDetailView.as_view(), name='plan-detail'),
]