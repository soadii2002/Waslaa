from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from waslaa_telecom.apps.users.models import User
from waslaa_telecom.apps.plans.models import Plan


class TestSubscription(TestCase):
    """
    TDD Cycle 4 — Subscriptions
    Red Phase: These tests MUST fail before any implementation exists.
    """

    def setUp(self):
        self.client = APIClient()

        # Create customer
        self.customer = User.objects.create_user(
            email='customer@waslaa.com',
            password='SecurePass123!',
            first_name='Ahmed',
            last_name='Ali',
            phone_number='+966501234567',
            role='customer',
        )

        # Create admin
        self.admin = User.objects.create_user(
            email='admin@waslaa.com',
            password='AdminPass123!',
            first_name='Admin',
            last_name='User',
            phone_number='+966500000001',
            role='admin',
            is_staff=True,
        )

        # Create plans
        self.mobile_plan = Plan.objects.create(
            name='Basic Mobile',
            plan_type='mobile',
            price='29.99',
            description='Basic mobile plan',
            features={'data_gb': 5, 'voice_minutes': 100},
            is_active=True,
        )
        self.premium_plan = Plan.objects.create(
            name='Premium Mobile',
            plan_type='mobile',
            price='59.99',
            description='Premium mobile plan',
            features={'data_gb': 20, 'voice_minutes': 500},
            is_active=True,
        )

        self.subscribe_url = reverse('subscriptions:subscribe')
        self.my_subscription_url = reverse('subscriptions:my-subscription')

    def _login_customer(self):
        self.client.post(reverse('users:login'), {
            'email': 'customer@waslaa.com',
            'password': 'SecurePass123!',
        }, format='json')

    def _login_admin(self):
        self.client.post(reverse('users:login'), {
            'email': 'admin@waslaa.com',
            'password': 'AdminPass123!',
        }, format='json')

    # --- Subscribe ---

    def test_customer_can_subscribe_to_plan(self):
        """Customer should be able to subscribe to an active plan."""
        self._login_customer()
        response = self.client.post(self.subscribe_url, {
            'plan': self.mobile_plan.pk,
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_subscription_is_active_after_creation(self):
        """Newly created subscription should have status 'active'."""
        self._login_customer()
        self.client.post(self.subscribe_url, {
            'plan': self.mobile_plan.pk,
        }, format='json')
        from waslaa_telecom.apps.subscriptions.models import Subscription
        sub = Subscription.objects.get(customer=self.customer)
        self.assertEqual(sub.status, 'active')

    def test_customer_cannot_have_two_active_subscriptions(self):
        """A customer should not be able to subscribe twice."""
        self._login_customer()
        self.client.post(self.subscribe_url, {
            'plan': self.mobile_plan.pk,
        }, format='json')
        response = self.client.post(self.subscribe_url, {
            'plan': self.premium_plan.pk,
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unauthenticated_user_cannot_subscribe(self):
        """Unauthenticated users should not be able to subscribe."""
        response = self.client.post(self.subscribe_url, {
            'plan': self.mobile_plan.pk,
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_customer_cannot_subscribe_to_inactive_plan(self):
        """Subscribing to an inactive plan should be rejected."""
        inactive_plan = Plan.objects.create(
            name='Inactive Plan',
            plan_type='mobile',
            price='9.99',
            description='Not available',
            features={},
            is_active=False,
        )
        self._login_customer()
        response = self.client.post(self.subscribe_url, {
            'plan': inactive_plan.pk,
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # --- View My Subscription ---

    def test_customer_can_view_own_subscription(self):
        """Customer should be able to see their current subscription."""
        self._login_customer()
        self.client.post(self.subscribe_url, {
            'plan': self.mobile_plan.pk,
        }, format='json')
        response = self.client.get(self.my_subscription_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['plan']['name'], 'Basic Mobile')

    def test_customer_with_no_subscription_gets_404(self):
        """Customer with no subscription should get 404."""
        self._login_customer()
        response = self.client.get(self.my_subscription_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # --- Upgrade / Downgrade ---

    def test_customer_can_upgrade_plan(self):
        """Customer should be able to switch to a different plan."""
        self._login_customer()
        self.client.post(self.subscribe_url, {
            'plan': self.mobile_plan.pk,
        }, format='json')
        from waslaa_telecom.apps.subscriptions.models import Subscription
        sub = Subscription.objects.get(customer=self.customer)
        url = reverse('subscriptions:subscription-detail', kwargs={'pk': sub.pk})
        response = self.client.patch(url, {
            'plan': self.premium_plan.pk,
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['plan']['name'], 'Premium Mobile')

    def test_customer_can_cancel_subscription(self):
        """Customer should be able to cancel their subscription."""
        self._login_customer()
        self.client.post(self.subscribe_url, {
            'plan': self.mobile_plan.pk,
        }, format='json')
        from waslaa_telecom.apps.subscriptions.models import Subscription
        sub = Subscription.objects.get(customer=self.customer)
        url = reverse('subscriptions:subscription-detail', kwargs={'pk': sub.pk})
        response = self.client.patch(url, {
            'status': 'cancelled',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'cancelled')

    def test_customer_cannot_modify_another_customers_subscription(self):
        """A customer should only be able to modify their own subscription."""
        # Create second customer with a subscription
        other_customer = User.objects.create_user(
            email='other@waslaa.com',
            password='OtherPass123!',
            first_name='Other',
            last_name='User',
            phone_number='+966509999999',
            role='customer',
        )
        from waslaa_telecom.apps.subscriptions.models import Subscription
        other_sub = Subscription.objects.create(
            customer=other_customer,
            plan=self.mobile_plan,
            status='active',
        )
        self._login_customer()
        url = reverse('subscriptions:subscription-detail', kwargs={'pk': other_sub.pk})
        response = self.client.patch(url, {'status': 'cancelled'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)