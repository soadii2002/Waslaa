from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from waslaa_telecom.apps.users.models import User


class TestSupportTickets(TestCase):
    """
    TDD Cycle 6 — Support Tickets
    Red Phase: These tests MUST fail before any implementation exists.
    """

    def setUp(self):
        self.client = APIClient()

        self.customer = User.objects.create_user(
            email='customer@waslaa.com',
            password='SecurePass123!',
            first_name='Ahmed',
            last_name='Ali',
            phone_number='+966501234567',
            role='customer',
        )
        self.other_customer = User.objects.create_user(
            email='other@waslaa.com',
            password='OtherPass123!',
            first_name='Other',
            last_name='User',
            phone_number='+966509999999',
            role='customer',
        )
        self.admin = User.objects.create_user(
            email='admin@waslaa.com',
            password='AdminPass123!',
            first_name='Admin',
            last_name='User',
            phone_number='+966500000001',
            role='admin',
            is_staff=True,
        )

        self.tickets_url = reverse('tickets:ticket-list')
        self.valid_ticket = {
            'subject': 'My internet is down',
            'message': 'I have no connectivity since this morning.',
        }

    def _login_customer(self):
        self.client.post(reverse('users:login'), {
            'email': 'customer@waslaa.com',
            'password': 'SecurePass123!',
        }, format='json')

    def _login_other_customer(self):
        self.client.post(reverse('users:login'), {
            'email': 'other@waslaa.com',
            'password': 'OtherPass123!',
        }, format='json')

    def _login_admin(self):
        self.client.post(reverse('users:login'), {
            'email': 'admin@waslaa.com',
            'password': 'AdminPass123!',
        }, format='json')

    # --- Customer Ticket Submission ---

    def test_customer_can_submit_ticket(self):
        """Customer should be able to submit a support ticket."""
        self._login_customer()
        response = self.client.post(
            self.tickets_url, self.valid_ticket, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_ticket_status_is_open_on_creation(self):
        """Newly created ticket should have status 'open'."""
        self._login_customer()
        self.client.post(self.tickets_url, self.valid_ticket, format='json')
        from waslaa_telecom.apps.tickets.models import SupportTicket
        ticket = SupportTicket.objects.get(customer=self.customer)
        self.assertEqual(ticket.status, 'open')

    def test_ticket_has_no_reply_on_creation(self):
        """Newly created ticket should have no admin reply."""
        self._login_customer()
        self.client.post(self.tickets_url, self.valid_ticket, format='json')
        from waslaa_telecom.apps.tickets.models import SupportTicket
        ticket = SupportTicket.objects.get(customer=self.customer)
        self.assertIsNone(ticket.admin_reply)

    def test_unauthenticated_user_cannot_submit_ticket(self):
        """Unauthenticated users cannot submit tickets."""
        response = self.client.post(
            self.tickets_url, self.valid_ticket, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_ticket_missing_subject_returns_400(self):
        """Ticket without subject should be rejected."""
        self._login_customer()
        response = self.client.post(
            self.tickets_url, {'message': 'No subject here'}, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # --- Customer Views Own Tickets ---

    def test_customer_can_list_own_tickets(self):
        """Customer should see only their own tickets."""
        self._login_customer()
        self.client.post(self.tickets_url, self.valid_ticket, format='json')
        response = self.client.get(self.tickets_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_customer_cannot_see_other_customers_tickets(self):
        """Customer should not see tickets submitted by others."""
        # Other customer submits a ticket
        self._login_other_customer()
        self.client.post(self.tickets_url, {
            'subject': 'Other issue',
            'message': 'Other message',
        }, format='json')

        # Our customer lists tickets
        self.client.logout()
        self._login_customer()
        response = self.client.get(self.tickets_url)
        self.assertEqual(len(response.data), 0)

    # --- Admin Ticket Management ---

    def test_admin_can_list_all_tickets(self):
        """Admin should see all tickets from all customers."""
        self._login_customer()
        self.client.post(self.tickets_url, self.valid_ticket, format='json')
        self.client.logout()
        self._login_other_customer()
        self.client.post(self.tickets_url, {
            'subject': 'Another issue',
            'message': 'Another message',
        }, format='json')
        self.client.logout()
        self._login_admin()
        response = self.client.get(reverse('tickets:admin-ticket-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_admin_can_reply_to_ticket(self):
        """Admin should be able to post a reply to a ticket."""
        self._login_customer()
        self.client.post(self.tickets_url, self.valid_ticket, format='json')
        self.client.logout()

        from waslaa_telecom.apps.tickets.models import SupportTicket
        ticket = SupportTicket.objects.get(customer=self.customer)

        self._login_admin()
        url = reverse('tickets:admin-ticket-reply', kwargs={'pk': ticket.pk})
        response = self.client.patch(url, {
            'admin_reply': 'We are looking into this issue.',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data['admin_reply'],
            'We are looking into this issue.'
        )

    def test_customer_cannot_reply_to_ticket(self):
        """Customers should not be able to post admin replies."""
        self._login_customer()
        self.client.post(self.tickets_url, self.valid_ticket, format='json')
        from waslaa_telecom.apps.tickets.models import SupportTicket
        ticket = SupportTicket.objects.get(customer=self.customer)
        url = reverse('tickets:admin-ticket-reply', kwargs={'pk': ticket.pk})
        response = self.client.patch(url, {
            'admin_reply': 'Hacking the reply',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_reply_is_visible_to_customer(self):
        """Customer should see admin reply in their ticket detail."""
        self._login_customer()
        self.client.post(self.tickets_url, self.valid_ticket, format='json')
        self.client.logout()

        from waslaa_telecom.apps.tickets.models import SupportTicket
        ticket = SupportTicket.objects.get(customer=self.customer)
        ticket.admin_reply = 'Issue resolved.'
        ticket.replied_by = self.admin
        ticket.save()

        self._login_customer()
        url = reverse('tickets:ticket-detail', kwargs={'pk': ticket.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['admin_reply'], 'Issue resolved.')