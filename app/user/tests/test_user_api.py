"""Test for user api"""
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model

from core.models import ActiveAccount, Account
from decimal import Decimal

# Define any necessary URLs
# For example:
CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')
ACTIVE_ACCOUNT_URL = reverse('user:active-account')
ME_URL = reverse('user:me')
ACCOUNTS_URL = reverse('user:accounts')
def create_user(**params):
    """Create and return new user."""
    return get_user_model().objects.create_user(**params)


class PublicUserApiTests(APITestCase):
    """Test the users API (public)."""

    def test_create_user_success(self):
        """Test creating user is successful."""
        payload = {
            'email': 'test@example.com',
            'username': 'testuser',
            'password': 'testpass123',
        }
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(**res.data)
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', res.data)

        # Check if an Account and ActiveAccount are created
        self.assertTrue(hasattr(user, 'active_account'))
        self.assertTrue(ActiveAccount.objects.filter(user=user).exists())

    def test_user_exists(self):
        """Test creating user that already exists fails."""
        payload = {
            'email': 'test@example.com',
            'username': 'testuser',
            'password': 'testpass123',
        }
        get_user_model().objects.create_user(**payload)
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        """Test that the password must be more than 5 characters."""
        payload = {
            'email': 'test@example.com',
            'username': 'testuser',
            'password': 'abc',
        }
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()
        self.assertFalse(user_exists)

    def test_create_token_for_user(self):
        """Test is creating token for user."""

        user_details = {
            'email': 'test@example.com',
            'password': 'test123',
            'username': 'test123',
        }
        create_user(**user_details)

        payload = {
            'username': 'test123',
            'password': 'test123',
        }

        res = self.client.post(TOKEN_URL, payload)

        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_token_bad_credentials(self):
        """Test for creating token with bad credentials."""

        user_details = {
            'email': 'test@example.com',
            'password': 'test123',
            'username': 'test123',
        }
        create_user(**user_details)

        payload = {
            'username': 'test12',
            'password': 'test123',
            }

        res = self.client.post(TOKEN_URL, payload)
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        payload2 = {
            'username': 'test123',
            'password': 'test1234',
            }

        res2 = self.client.post(TOKEN_URL, payload2)
        self.assertNotIn('token', res2.data)
        self.assertEqual(res2.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_with_blank_password(self):
        user_details = {
            'email': 'test@example.com',
            'password': 'test123',
            'username': 'test123',
        }
        create_user(**user_details)

        payload = {
            'username': 'test123',
            'password': '',
            }
        res = self.client.post(TOKEN_URL, payload)
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)


class PrivateUserApiTests(APITestCase):
    """Test API requests that require authentication"""
    def setUp(self):
        self.user = create_user(email='anpch@example.com',
                           username='testuser', password='testpass123')
        self.client.force_authenticate(user=self.user)
        self.active_account = ActiveAccount.objects.get(user=self.user)
        self.account1 = Account.objects.create(user=self.user, name='Savings', balance=100)

    def test_retrieve_profile_success(self):
        """Test retrieving profile for logged in user"""
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {
            'email': self.user.email,
            'username': self.user.username,
            'balance': '0.00',
        })

    def test_post_me_not_allowed(self):
        """Test that POST is not allowed on the users endpoint"""
        res = self.client.post(ME_URL, {})

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user_profile(self):
        """Test updating user profile for authenticated user"""
        payload = {
            'username': 'new_username',
            'email': 'example@example.com',
            'password': 'test12345'
        }
        res = self.client.patch(ME_URL, payload)

        self.user.refresh_from_db()
        self.assertEqual(self.user.username, payload['username'])
        self.assertEqual(self.user.email, payload['email'])
        self.assertTrue(self.user.check_password(payload['password']))
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_change_active_account(self):
        """Test changing active account for authenticated user"""
        payload = {
            'account_id': self.account1.id
        }
        res = self.client.patch(ACTIVE_ACCOUNT_URL, payload)

        self.active_account.refresh_from_db()
        self.assertEqual(self.active_account.account, self.account1)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_show_active_account(self):
        """Test showing active account for authenticated user"""
        res = self.client.get(ACTIVE_ACCOUNT_URL)
        account = ActiveAccount.objects.get(user=self.user).account

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {
            'account': {
                'id': account.id,
                'name': account.name,
                'balance': str(account.balance)
        }
    })

    def test_list_accounts(self):
        """Test listing accounts for authenticated user"""
        account2 = Account.objects.create(user=self.user, name='Checking', balance=100)

        res = self.client.get(ACCOUNTS_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 3)
        account_names = {account['name'] for account in res.data}
        self.assertIn(self.account1.name, account_names)
        self.assertIn(account2.name, account_names)
        accoutn_ids = {account['id'] for account in res.data}
        self.assertIn(self.account1.id, accoutn_ids)
        self.assertIn(account2.id, accoutn_ids)










