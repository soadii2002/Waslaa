from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from waslaa_telecom.apps.users.models import User


class TestAnnouncements(TestCase):
    """
    TDD Cycle 8 — Announcements
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
        self.customer = User.objects.create_user(
            email='customer@waslaa.com',
            password='SecurePass123!',
            first_name='Ahmed',
            last_name='Ali',
            phone_number='+966501234567',
            role='customer',
        )

        self.list_url = reverse('announcements:announcement-list')
        self.valid_announcement = {
            'title': 'Scheduled Maintenance',
            'body': 'We will be down for maintenance on Friday from 2AM to 4AM.',
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

    # --- Access Control ---

    def test_admin_can_create_announcement(self):
        """Admin should be able to create an announcement."""
        self._login_admin()
        response = self.client.post(
            self.list_url, self.valid_announcement, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_customer_cannot_create_announcement(self):
        """Customers should not be able to create announcements."""
        self._login_customer()
        response = self.client.post(
            self.list_url, self.valid_announcement, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_cannot_create_announcement(self):
        """Unauthenticated users cannot create announcements."""
        response = self.client.post(
            self.list_url, self.valid_announcement, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # --- Listing ---

    def test_customer_can_list_announcements(self):
        """Customers should be able to read announcements."""
        self._login_customer()
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_unauthenticated_can_list_announcements(self):
        """Anyone can read announcements without logging in."""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_announcement_list_returns_all_announcements(self):
        """List should return all created announcements."""
        self._login_admin()
        self.client.post(self.list_url, self.valid_announcement, format='json')
        self.client.post(self.list_url, {
            'title': 'New Plans Available',
            'body': 'Check out our new internet plans!',
        }, format='json')
        response = self.client.get(self.list_url)
        self.assertEqual(len(response.data), 2)

    # --- Creation Data ---

    def test_announcement_is_saved_with_correct_data(self):
        """Created announcement should have correct title and body."""
        self._login_admin()
        self.client.post(self.list_url, self.valid_announcement, format='json')
        from waslaa_telecom.apps.announcements.models import Announcement
        announcement = Announcement.objects.get(title='Scheduled Maintenance')
        self.assertEqual(
            announcement.body,
            'We will be down for maintenance on Friday from 2AM to 4AM.'
        )

    def test_announcement_is_linked_to_admin_creator(self):
        """Announcement should be linked to the admin who created it."""
        self._login_admin()
        self.client.post(self.list_url, self.valid_announcement, format='json')
        from waslaa_telecom.apps.announcements.models import Announcement
        announcement = Announcement.objects.get(title='Scheduled Maintenance')
        self.assertEqual(announcement.created_by, self.admin)

    def test_announcement_missing_title_returns_400(self):
        """Announcement without title should be rejected."""
        self._login_admin()
        response = self.client.post(self.list_url, {
            'body': 'No title here'
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_announcement_missing_body_returns_400(self):
        """Announcement without body should be rejected."""
        self._login_admin()
        response = self.client.post(self.list_url, {
            'title': 'No body here'
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # --- Delete ---

    def test_admin_can_delete_announcement(self):
        """Admin should be able to delete an announcement."""
        self._login_admin()
        self.client.post(self.list_url, self.valid_announcement, format='json')
        from waslaa_telecom.apps.announcements.models import Announcement
        announcement = Announcement.objects.get(title='Scheduled Maintenance')
        url = reverse('announcements:announcement-detail', kwargs={'pk': announcement.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_customer_cannot_delete_announcement(self):
        """Customers should not be able to delete announcements."""
        self._login_admin()
        self.client.post(self.list_url, self.valid_announcement, format='json')
        self.client.logout()
        from waslaa_telecom.apps.announcements.models import Announcement
        announcement = Announcement.objects.get(title='Scheduled Maintenance')
        self._login_customer()
        url = reverse('announcements:announcement-detail', kwargs={'pk': announcement.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)