from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from waslaa_telecom.apps.users.models import User

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

class TestAdminCustomerList(TestCase):
    """
    TDD Cycle 9 — Admin Customer List Endpoint
    Red Phase: These tests MUST fail before any implementation exists.
    """

    def setUp(self):
        self.client = APIClient()

        self.admin = User.objects.create_user(
            email='admin@waslaa.com',
            password='AdminPass123!',
            first_name='Admin',
            last_name='User',
            phone_number='+201000000001',
            role='admin',
            is_staff=True,
        )
        self.customer1 = User.objects.create_user(
            email='customer1@waslaa.com',
            password='SecurePass123!',
            first_name='Ahmed',
            last_name='Ali',
            phone_number='+201001234567',
            role='customer',
        )
        self.customer2 = User.objects.create_user(
            email='customer2@waslaa.com',
            password='SecurePass123!',
            first_name='Sara',
            last_name='Hassan',
            phone_number='+201007654321',
            role='customer',
        )

        self.url = reverse('users:customer-list')

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

    def test_admin_can_list_all_customers(self):
        """Admin should be able to retrieve all customers."""
        self._login_admin()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_customer_list_returns_only_customers(self):
        """Response should not include admin accounts."""
        self._login_admin()
        response = self.client.get(self.url)
        roles = [u['role'] for u in response.data]
        self.assertNotIn('admin', roles)

    def test_customer_list_returns_correct_count(self):
        """Should return exactly 2 customers."""
        self._login_admin()
        response = self.client.get(self.url)
        self.assertEqual(len(response.data), 2)

    def test_customer_list_contains_expected_fields(self):
        """Each customer entry should have key fields."""
        self._login_admin()
        response = self.client.get(self.url)
        customer = response.data[0]
        self.assertIn('email', customer)
        self.assertIn('first_name', customer)
        self.assertIn('last_name', customer)
        self.assertIn('phone_number', customer)
        self.assertIn('role', customer)
        self.assertIn('is_active', customer)

    def test_customer_cannot_access_customer_list(self):
        """Regular customers should be blocked from this endpoint."""
        self._login_customer()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_cannot_access_customer_list(self):
        """Unauthenticated requests should be rejected."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_not_in_customer_list(self):
        """Admin account itself should not appear in the list."""
        self._login_admin()
        response = self.client.get(self.url)
        emails = [u['email'] for u in response.data]
        self.assertNotIn('admin@waslaa.com', emails)

class TestPasswordReset(TestCase):
    """
    TDD Cycle 10 — Password Reset via Email Token
    """

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='customer@waslaa.com',
            password='OldPass123!',
            first_name='Ahmed',
            last_name='Ali',
            phone_number='+201001234567',
            role='customer',
        )
        self.request_url = reverse('users:password-reset-request')
        self.confirm_url = reverse('users:password-reset-confirm')

    def test_valid_email_returns_200(self):
        """Valid email should return 200 and success message."""
        res = self.client.post(self.request_url, {'email': 'customer@waslaa.com'}, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_invalid_email_still_returns_200(self):
        """Non-existent email should still return 200 to prevent enumeration."""
        res = self.client.post(self.request_url, {'email': 'nobody@waslaa.com'}, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_reset_token_created_for_valid_email(self):
        """A reset token should be created in the database."""
        from waslaa_telecom.apps.users.models import PasswordResetToken
        self.client.post(self.request_url, {'email': 'customer@waslaa.com'}, format='json')
        self.assertTrue(PasswordResetToken.objects.filter(user=self.user).exists())

    def test_valid_token_resets_password(self):
        """Valid token + new password should reset successfully."""
        from waslaa_telecom.apps.users.models import PasswordResetToken
        self.client.post(self.request_url, {'email': 'customer@waslaa.com'}, format='json')
        token = PasswordResetToken.objects.get(user=self.user)
        res = self.client.post(self.confirm_url, {
            'token': str(token.token),
            'password': 'NewPass123!',
            'password_confirm': 'NewPass123!',
        }, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_new_password_works_for_login(self):
        """After reset, user should be able to login with new password."""
        from waslaa_telecom.apps.users.models import PasswordResetToken
        self.client.post(self.request_url, {'email': 'customer@waslaa.com'}, format='json')
        token = PasswordResetToken.objects.get(user=self.user)
        self.client.post(self.confirm_url, {
            'token': str(token.token),
            'password': 'NewPass123!',
            'password_confirm': 'NewPass123!',
        }, format='json')
        login_res = self.client.post(reverse('users:login'), {
            'email': 'customer@waslaa.com',
            'password': 'NewPass123!',
        }, format='json')
        self.assertEqual(login_res.status_code, status.HTTP_200_OK)

    def test_old_password_fails_after_reset(self):
        """After reset, old password should no longer work."""
        from waslaa_telecom.apps.users.models import PasswordResetToken
        self.client.post(self.request_url, {'email': 'customer@waslaa.com'}, format='json')
        token = PasswordResetToken.objects.get(user=self.user)
        self.client.post(self.confirm_url, {
            'token': str(token.token),
            'password': 'NewPass123!',
            'password_confirm': 'NewPass123!',
        }, format='json')
        login_res = self.client.post(reverse('users:login'), {
            'email': 'customer@waslaa.com',
            'password': 'OldPass123!',
        }, format='json')
        self.assertEqual(login_res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_token_returns_400(self):
        """Invalid token should return 400."""
        res = self.client.post(self.confirm_url, {
            'token': '00000000-0000-0000-0000-000000000000',
            'password': 'NewPass123!',
            'password_confirm': 'NewPass123!',
        }, format='json')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_token_cannot_be_reused(self):
        """Token should be invalid after first use."""
        from waslaa_telecom.apps.users.models import PasswordResetToken
        self.client.post(self.request_url, {'email': 'customer@waslaa.com'}, format='json')
        token = PasswordResetToken.objects.get(user=self.user)
        self.client.post(self.confirm_url, {
            'token': str(token.token),
            'password': 'NewPass123!',
            'password_confirm': 'NewPass123!',
        }, format='json')
        res = self.client.post(self.confirm_url, {
            'token': str(token.token),
            'password': 'AnotherPass123!',
            'password_confirm': 'AnotherPass123!',
        }, format='json')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_mismatched_passwords_returns_400(self):
        """Mismatched passwords should return 400."""
        from waslaa_telecom.apps.users.models import PasswordResetToken
        self.client.post(self.request_url, {'email': 'customer@waslaa.com'}, format='json')
        token = PasswordResetToken.objects.get(user=self.user)
        res = self.client.post(self.confirm_url, {
            'token': str(token.token),
            'password': 'NewPass123!',
            'password_confirm': 'WrongPass123!',
        }, format='json')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)