"""Test for user api"""
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model

from core.models import ActiveAccount

# Define any necessary URLs
# For example:
CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')

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




