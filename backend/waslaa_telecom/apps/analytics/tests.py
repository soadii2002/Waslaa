from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from waslaa_telecom.apps.users.models import User
from waslaa_telecom.apps.plans.models import Plan
from waslaa_telecom.apps.subscriptions.models import Subscription
from waslaa_telecom.apps.payments.models import Payment
import uuid


class TestAdminAnalytics(TestCase):
    """
    TDD Cycle 7 — Admin Analytics Dashboard
    Red Phase: These tests MUST fail before any implementation exists.
    """

    def setUp(self):
        self.client = APIClient()

        self.admin = User.objects.create_user(
            email='admin@waslaa.com',
            password='AdminPass123!',
            first_name='Admin',
            last_name='User',
            phone_number='+966500000001',
            role='admin',
            is_staff=True,
        )
        self.customer1 = User.objects.create_user(
            email='customer1@waslaa.com',
            password='SecurePass123!',
            first_name='Ahmed',
            last_name='Ali',
            phone_number='+966501234567',
            role='customer',
        )
        self.customer2 = User.objects.create_user(
            email='customer2@waslaa.com',
            password='SecurePass123!',
            first_name='Sara',
            last_name='Hassan',
            phone_number='+966507654321',
            role='customer',
        )

        self.plan = Plan.objects.create(
            name='Basic Mobile',
            plan_type='mobile',
            price='29.99',
            description='Basic plan',
            features={'data_gb': 5},
            is_active=True,
        )

        self.sub1 = Subscription.objects.create(
            customer=self.customer1,
            plan=self.plan,
            status='active',
        )
        self.sub2 = Subscription.objects.create(
            customer=self.customer2,
            plan=self.plan,
            status='active',
        )

        Payment.objects.create(
            subscription=self.sub1,
            amount='29.99',
            status='completed',
            mock_reference=str(uuid.uuid4()),
        )
        Payment.objects.create(
            subscription=self.sub2,
            amount='29.99',
            status='completed',
            mock_reference=str(uuid.uuid4()),
        )

        self.analytics_url = reverse('analytics:dashboard')

    def _login_admin(self):
        self.client.post(reverse('users:login'), {
            'email': 'admin@waslaa.com',
            'password': 'AdminPass123!',
        }, format='json')

    def _login_customer(self):
        self.client.post(reverse('users:login'), {
            'email': 'customer1@waslaa.com',
            'password': 'SecurePass123!',
        }, format='json')

    # --- Access Control ---

    def test_admin_can_access_analytics(self):
        """Admin should be able to access the analytics dashboard."""
        self._login_admin()
        response = self.client.get(self.analytics_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_customer_cannot_access_analytics(self):
        """Customers should be blocked from the analytics dashboard."""
        self._login_customer()
        response = self.client.get(self.analytics_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_cannot_access_analytics(self):
        """Unauthenticated users should be blocked."""
        response = self.client.get(self.analytics_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # --- Analytics Data ---

    def test_analytics_returns_total_customers(self):
        """Analytics should return the total number of customers."""
        self._login_admin()
        response = self.client.get(self.analytics_url)
        self.assertIn('total_customers', response.data)
        self.assertEqual(response.data['total_customers'], 2)

    def test_analytics_returns_total_active_subscriptions(self):
        """Analytics should return the total active subscriptions."""
        self._login_admin()
        response = self.client.get(self.analytics_url)
        self.assertIn('total_active_subscriptions', response.data)
        self.assertEqual(response.data['total_active_subscriptions'], 2)

    def test_analytics_returns_total_revenue(self):
        """Analytics should return total revenue from completed payments."""
        self._login_admin()
        response = self.client.get(self.analytics_url)
        self.assertIn('total_revenue', response.data)
        from decimal import Decimal
        self.assertEqual(Decimal(str(response.data['total_revenue'])), Decimal('59.98'))

    def test_analytics_returns_total_plans(self):
        """Analytics should return total number of plans."""
        self._login_admin()
        response = self.client.get(self.analytics_url)
        self.assertIn('total_plans', response.data)
        self.assertEqual(response.data['total_plans'], 1)

    def test_analytics_returns_plans_breakdown(self):
        """Analytics should return subscription count per plan."""
        self._login_admin()
        response = self.client.get(self.analytics_url)
        self.assertIn('plans_breakdown', response.data)
        self.assertIsInstance(response.data['plans_breakdown'], list)
        self.assertEqual(len(response.data['plans_breakdown']), 1)
        self.assertEqual(
            response.data['plans_breakdown'][0]['plan__name'],
            'Basic Mobile'
        )

    def test_analytics_returns_open_tickets_count(self):
        """Analytics should return number of open support tickets."""
        self._login_admin()
        response = self.client.get(self.analytics_url)
        self.assertIn('open_tickets', response.data)
        self.assertEqual(response.data['open_tickets'], 0)

    def test_analytics_returns_mobile_vs_internet_count(self):
        """Analytics should return count of mobile vs internet plans."""
        self._login_admin()
        response = self.client.get(self.analytics_url)
        self.assertIn('mobile_plans_count', response.data)
        self.assertIn('internet_plans_count', response.data)
        self.assertEqual(response.data['mobile_plans_count'], 1)
        self.assertEqual(response.data['internet_plans_count'], 0)