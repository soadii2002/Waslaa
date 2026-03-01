from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from waslaa_telecom.apps.users.models import User
from waslaa_telecom.apps.plans.models import Plan
from waslaa_telecom.apps.subscriptions.models import Subscription


class TestMockPayment(TestCase):
    """
    TDD Cycle 5 — Mock Payments
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

        # Create plan and subscription
        self.plan = Plan.objects.create(
            name='Basic Mobile',
            plan_type='mobile',
            price='29.99',
            description='Basic mobile plan',
            features={'data_gb': 5},
            is_active=True,
        )
        self.subscription = Subscription.objects.create(
            customer=self.customer,
            plan=self.plan,
            status='active',
        )

        self.checkout_url = reverse('payments:checkout')
        self.billing_url = reverse('payments:billing-history')

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

    # --- Checkout ---

    def test_customer_can_checkout(self):
        """Customer with active subscription can make a payment."""
        self._login_customer()
        response = self.client.post(self.checkout_url, {
            'subscription': self.subscription.pk,
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_checkout_creates_completed_payment(self):
        """Mock checkout should create a payment with status 'completed'."""
        self._login_customer()
        self.client.post(self.checkout_url, {
            'subscription': self.subscription.pk,
        }, format='json')
        from waslaa_telecom.apps.payments.models import Payment
        payment = Payment.objects.get(subscription=self.subscription)
        self.assertEqual(payment.status, 'completed')

    def test_checkout_generates_mock_reference(self):
        """Payment should have an auto-generated mock reference."""
        self._login_customer()
        self.client.post(self.checkout_url, {
            'subscription': self.subscription.pk,
        }, format='json')
        from waslaa_telecom.apps.payments.models import Payment
        payment = Payment.objects.get(subscription=self.subscription)
        self.assertIsNotNone(payment.mock_reference)
        self.assertTrue(len(payment.mock_reference) > 0)

    def test_checkout_amount_matches_plan_price(self):
        """Payment amount should match the plan price."""
        from decimal import Decimal
        self._login_customer()
        self.client.post(self.checkout_url, {
            'subscription': self.subscription.pk,
        }, format='json')
        from waslaa_telecom.apps.payments.models import Payment
        payment = Payment.objects.get(subscription=self.subscription)
        self.assertEqual(payment.amount, Decimal('29.99'))

    def test_unauthenticated_user_cannot_checkout(self):
        """Unauthenticated users cannot access checkout."""
        response = self.client.post(self.checkout_url, {
            'subscription': self.subscription.pk,
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_customer_cannot_checkout_another_customers_subscription(self):
        """Customer cannot pay for another customer's subscription."""
        other_customer = User.objects.create_user(
            email='other@waslaa.com',
            password='OtherPass123!',
            first_name='Other',
            last_name='User',
            phone_number='+966509999999',
            role='customer',
        )
        other_sub = Subscription.objects.create(
            customer=other_customer,
            plan=self.plan,
            status='active',
        )
        self._login_customer()
        response = self.client.post(self.checkout_url, {
            'subscription': other_sub.pk,
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # --- Billing History ---

    def test_customer_can_view_billing_history(self):
        """Customer can retrieve their list of payments."""
        self._login_customer()
        response = self.client.get(self.billing_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_billing_history_shows_own_payments_only(self):
        """Customer should only see their own payments."""
        from waslaa_telecom.apps.payments.models import Payment
        import uuid

        # Customer's own payment
        Payment.objects.create(
            subscription=self.subscription,
            amount=self.plan.price,
            status='completed',
            mock_reference=str(uuid.uuid4()),
        )

        # Another customer's payment
        other_customer = User.objects.create_user(
            email='other@waslaa.com',
            password='OtherPass123!',
            first_name='Other',
            last_name='User',
            phone_number='+966509999999',
            role='customer',
        )
        other_sub = Subscription.objects.create(
            customer=other_customer,
            plan=self.plan,
            status='active',
        )
        Payment.objects.create(
            subscription=other_sub,
            amount=self.plan.price,
            status='completed',
            mock_reference=str(uuid.uuid4()),
        )

        self._login_customer()
        response = self.client.get(self.billing_url)
        self.assertEqual(len(response.data), 1)

    def test_unauthenticated_user_cannot_view_billing(self):
        """Unauthenticated users cannot access billing history."""
        response = self.client.get(self.billing_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # --- Admin Payment Overview ---

    def test_admin_can_view_all_payments(self):
        """Admin can see all payments across all customers."""
        self._login_admin()
        response = self.client.get(reverse('payments:admin-payments'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_admin_can_override_payment_status(self):
        """Admin can manually change a payment's status."""
        from waslaa_telecom.apps.payments.models import Payment
        import uuid
        payment = Payment.objects.create(
            subscription=self.subscription,
            amount=self.plan.price,
            status='pending',
            mock_reference=str(uuid.uuid4()),
        )
        self._login_admin()
        url = reverse('payments:admin-payment-detail', kwargs={'pk': payment.pk})
        response = self.client.patch(url, {'status': 'completed'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'completed')