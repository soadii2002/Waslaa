from decimal import Decimal
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from django.db.models import Sum, Count

from waslaa_telecom.apps.users.models import User
from waslaa_telecom.apps.plans.models import Plan
from waslaa_telecom.apps.subscriptions.models import Subscription
from waslaa_telecom.apps.payments.models import Payment
from waslaa_telecom.apps.tickets.models import SupportTicket


class IsAdmin(IsAuthenticated):
    def has_permission(self, request, view):
        return (
            super().has_permission(request, view) and
            request.user.role == 'admin'
        )


class AnalyticsDashboardView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        # Total customers
        total_customers = User.objects.filter(role='customer').count()

        # Total active subscriptions
        total_active_subscriptions = Subscription.objects.filter(
            status='active'
        ).count()

        # Total revenue from completed payments
        revenue = Payment.objects.filter(
            status='completed'
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

        # Total plans
        total_plans = Plan.objects.count()

        # Plans breakdown — subscriptions per plan
        plans_breakdown = list(
            Subscription.objects.filter(status='active')
            .values('plan__name')
            .annotate(subscription_count=Count('id'))
            .order_by('-subscription_count')
        )

        # Open tickets
        open_tickets = SupportTicket.objects.filter(status='open').count()

        # Mobile vs Internet plans count
        mobile_plans_count = Plan.objects.filter(plan_type='mobile').count()
        internet_plans_count = Plan.objects.filter(plan_type='internet').count()

        return Response({
            'total_customers': total_customers,
            'total_active_subscriptions': total_active_subscriptions,
            'total_revenue': revenue,
            'total_plans': total_plans,
            'plans_breakdown': plans_breakdown,
            'open_tickets': open_tickets,
            'mobile_plans_count': mobile_plans_count,
            'internet_plans_count': internet_plans_count,
        }, status=status.HTTP_200_OK)