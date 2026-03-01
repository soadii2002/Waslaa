from rest_framework import generics
from waslaa_telecom.apps.plans.models import Plan
from waslaa_telecom.apps.plans.serializers import PlanSerializer
from waslaa_telecom.apps.plans.permissions import IsAdminOrReadOnly


class PlanListCreateView(generics.ListCreateAPIView):
    serializer_class = PlanSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        user = self.request.user
        # Admins see all plans, everyone else sees only active plans
        if user.is_authenticated and user.role == 'admin':
            return Plan.objects.all().order_by('-created_at')
        return Plan.objects.filter(is_active=True).order_by('-created_at')


class PlanDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PlanSerializer
    permission_classes = [IsAdminOrReadOnly]
    queryset = Plan.objects.all()