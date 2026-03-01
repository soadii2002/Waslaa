from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from waslaa_telecom.apps.users.models import User


class TestPlanManagement(TestCase):
    """
    TDD Cycle 3 — Plan Management
    Red Phase: These tests MUST fail before any implementation exists.
    """

    def setUp(self):
        self.client = APIClient()

        # Create admin user
        self.admin = User.objects.create_user(
            email='admin@waslaa.com',
            password='AdminPass123!',
            first_name='Admin',
            last_name='User',
            phone_number='+966500000001',
            role='admin',
            is_staff=True,
        )

        # Create customer user
        self.customer = User.objects.create_user(
            email='customer@waslaa.com',
            password='SecurePass123!',
            first_name='Ahmed',
            last_name='Ali',
            phone_number='+966501234567',
            role='customer',
        )

        self.plans_url = reverse('plans:plan-list')
        self.valid_mobile_plan = {
            'name': 'Basic Mobile',
            'plan_type': 'mobile',
            'price': '29.99',
            'description': 'Basic mobile plan',
            'features': {
                'data_gb': 5,
                'voice_minutes': 100,
                'sms_count': 50
            },
            'is_active': True,
        }
        self.valid_internet_plan = {
            'name': 'Fiber 100',
            'plan_type': 'internet',
            'price': '99.99',
            'description': 'Fast fiber internet',
            'features': {
                'speed_mbps': 100,
            },
            'is_active': True,
        }

    def _login_admin(self):
        self.client.post(reverse('users:login'), {
            'email': 'admin@waslaa.com',
            'password': 'AdminPass123!',
        }, format='json')

    def _login_customer(self):
        self.client.post(reverse('users:login'), {
            'email': 'customer@waslaa.com',
            'password': 'SecurePass123!',
        }, format='json')

    # --- Admin Plan Creation ---

    def test_admin_can_create_mobile_plan(self):
        """Admin should be able to create a mobile plan."""
        self._login_admin()
        response = self.client.post(
            self.plans_url, self.valid_mobile_plan, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_admin_can_create_internet_plan(self):
        """Admin should be able to create an internet plan."""
        self._login_admin()
        response = self.client.post(
            self.plans_url, self.valid_internet_plan, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_customer_cannot_create_plan(self):
        """Customers should not be allowed to create plans."""
        self._login_customer()
        response = self.client.post(
            self.plans_url, self.valid_mobile_plan, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_user_cannot_create_plan(self):
        """Unauthenticated requests should be rejected."""
        response = self.client.post(
            self.plans_url, self.valid_mobile_plan, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # --- Plan Listing ---

    def test_anyone_can_list_plans(self):
        """Both customers and guests can browse plans."""
        response = self.client.get(self.plans_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_returns_only_active_plans(self):
        """Inactive plans should not appear in the public listing."""
        from waslaa_telecom.apps.plans.models import Plan
        Plan.objects.create(
            name='Hidden Plan',
            plan_type='mobile',
            price='9.99',
            description='Inactive',
            features={},
            is_active=False,
        )
        Plan.objects.create(
            name='Visible Plan',
            plan_type='mobile',
            price='19.99',
            description='Active',
            features={},
            is_active=True,
        )
        response = self.client.get(self.plans_url)
        names = [p['name'] for p in response.data]
        self.assertNotIn('Hidden Plan', names)
        self.assertIn('Visible Plan', names)

    # --- Plan Detail ---

    def test_anyone_can_retrieve_plan_detail(self):
        """Anyone can view a single plan's details."""
        from waslaa_telecom.apps.plans.models import Plan
        plan = Plan.objects.create(
            name='Detail Plan',
            plan_type='internet',
            price='49.99',
            description='Test',
            features={'speed_mbps': 50},
            is_active=True,
        )
        url = reverse('plans:plan-detail', kwargs={'pk': plan.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Detail Plan')

    # --- Plan Update ---

    def test_admin_can_update_plan(self):
        """Admin should be able to update an existing plan."""
        from waslaa_telecom.apps.plans.models import Plan
        self._login_admin()
        plan = Plan.objects.create(
            name='Old Name',
            plan_type='mobile',
            price='19.99',
            description='Old',
            features={},
            is_active=True,
        )
        url = reverse('plans:plan-detail', kwargs={'pk': plan.pk})
        response = self.client.patch(url, {'name': 'New Name'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'New Name')

    def test_customer_cannot_update_plan(self):
        """Customers should not be able to update plans."""
        from waslaa_telecom.apps.plans.models import Plan
        self._login_customer()
        plan = Plan.objects.create(
            name='Locked Plan',
            plan_type='mobile',
            price='19.99',
            description='Test',
            features={},
            is_active=True,
        )
        url = reverse('plans:plan-detail', kwargs={'pk': plan.pk})
        response = self.client.patch(url, {'name': 'Hacked'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # --- Plan Delete ---

    def test_admin_can_delete_plan(self):
        """Admin should be able to delete a plan."""
        from waslaa_telecom.apps.plans.models import Plan
        self._login_admin()
        plan = Plan.objects.create(
            name='To Delete',
            plan_type='internet',
            price='9.99',
            description='Bye',
            features={},
            is_active=True,
        )
        url = reverse('plans:plan-detail', kwargs={'pk': plan.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_customer_cannot_delete_plan(self):
        """Customers should not be able to delete plans."""
        from waslaa_telecom.apps.plans.models import Plan
        self._login_customer()
        plan = Plan.objects.create(
            name='Protected Plan',
            plan_type='internet',
            price='9.99',
            description='Safe',
            features={},
            is_active=True,
        )
        url = reverse('plans:plan-detail', kwargs={'pk': plan.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)