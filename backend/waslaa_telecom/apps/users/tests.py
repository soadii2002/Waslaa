from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient


class TestUserRegistration(TestCase):
    """
    TDD Cycle 1 — User Registration
    Red Phase: These tests MUST fail before any implementation exists.
    """

    def setUp(self):
        self.client = APIClient()
        self.register_url = reverse('users:register')
        self.valid_payload = {
            'email': 'customer@waslaa.com',
            'password': 'SecurePass123!',
            'password_confirm': 'SecurePass123!',
            'first_name': 'Ahmed',
            'last_name': 'Ali',
            'phone_number': '+966501234567',
        }

    def test_register_with_valid_data_returns_201(self):
        """A valid registration payload should create a user and return 201."""
        response = self.client.post(
            self.register_url,
            self.valid_payload,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_register_creates_user_in_database(self):
        """After registration, the user should exist in the database."""
        from waslaa_telecom.apps.users.models import User
        self.client.post(self.register_url, self.valid_payload, format='json')
        self.assertTrue(User.objects.filter(email='customer@waslaa.com').exists())

    def test_register_with_duplicate_email_returns_400(self):
        """Registering with an already-used email should return 400."""
        self.client.post(self.register_url, self.valid_payload, format='json')
        response = self.client.post(
            self.register_url,
            self.valid_payload,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_with_mismatched_passwords_returns_400(self):
        """Password and confirm password must match."""
        payload = {**self.valid_payload, 'password_confirm': 'WrongPass999!'}
        response = self.client.post(self.register_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_without_phone_returns_400(self):
        """Phone number is required."""
        payload = {**self.valid_payload}
        del payload['phone_number']
        response = self.client.post(self.register_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_with_invalid_email_returns_400(self):
        """Invalid email format should be rejected."""
        payload = {**self.valid_payload, 'email': 'not-an-email'}
        response = self.client.post(self.register_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_registered_user_password_is_hashed(self):
        """Passwords must never be stored in plain text."""
        from waslaa_telecom.apps.users.models import User
        self.client.post(self.register_url, self.valid_payload, format='json')
        user = User.objects.get(email='customer@waslaa.com')
        self.assertNotEqual(user.password, 'SecurePass123!')
        self.assertTrue(user.password.startswith('pbkdf2_'))

    def test_registered_user_has_customer_role(self):
        """Newly registered users should have the 'customer' role by default."""
        from waslaa_telecom.apps.users.models import User
        self.client.post(self.register_url, self.valid_payload, format='json')
        user = User.objects.get(email='customer@waslaa.com')
        self.assertEqual(user.role, 'customer')

class TestUserAuth(TestCase):
    """
    TDD  User Login & Logout
    """

    def setUp(self):
        self.client = APIClient()
        self.login_url = reverse('users:login')
        self.logout_url = reverse('users:logout')

        # Create a verified customer to test login with
        from waslaa_telecom.apps.users.models import User
        self.user = User.objects.create_user(
            email='customer@waslaa.com',
            password='SecurePass123!',
            first_name='Ahmed',
            last_name='Ali',
            phone_number='+966501234567',
            role='customer',
        )

    def test_login_with_valid_credentials_returns_200(self):
        """Valid email and password should return 200."""
        response = self.client.post(self.login_url, {
            'email': 'customer@waslaa.com',
            'password': 'SecurePass123!',
        }, format='json')
        self.assertEqual(response.status_code, 200)

    def test_login_returns_user_data(self):
        """Login response should include email and role."""
        response = self.client.post(self.login_url, {
            'email': 'customer@waslaa.com',
            'password': 'SecurePass123!',
        }, format='json')
        self.assertIn('email', response.data)
        self.assertIn('role', response.data)
        self.assertEqual(response.data['email'], 'customer@waslaa.com')
        self.assertEqual(response.data['role'], 'customer')

    def test_login_with_wrong_password_returns_400(self):
        """Wrong password should be rejected with 400."""
        response = self.client.post(self.login_url, {
            'email': 'customer@waslaa.com',
            'password': 'WrongPassword!',
        }, format='json')
        self.assertEqual(response.status_code, 400)

    def test_login_with_nonexistent_email_returns_400(self):
        """Login with unregistered email should return 400."""
        response = self.client.post(self.login_url, {
            'email': 'ghost@waslaa.com',
            'password': 'SecurePass123!',
        }, format='json')
        self.assertEqual(response.status_code, 400)

    def test_login_with_missing_fields_returns_400(self):
        """Login with missing email or password should return 400."""
        response = self.client.post(self.login_url, {
            'email': 'customer@waslaa.com',
        }, format='json')
        self.assertEqual(response.status_code, 400)

    def test_logout_authenticated_user_returns_200(self):
        """An authenticated user should be able to log out successfully."""
        self.client.post(self.login_url, {
            'email': 'customer@waslaa.com',
            'password': 'SecurePass123!',
        }, format='json')
        response = self.client.post(self.logout_url, format='json')
        self.assertEqual(response.status_code, 200)

    def test_logout_unauthenticated_user_returns_403(self):
        """An unauthenticated user should not be able to call logout."""
        response = self.client.post(self.logout_url, format='json')
        self.assertEqual(response.status_code, 403)