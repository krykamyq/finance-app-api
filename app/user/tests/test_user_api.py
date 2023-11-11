"""Test for user api"""
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model

# Define any necessary URLs
# For example:
CREATE_USER_URL = reverse('user:create')


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
        self.assertTrue(user.accounts.exists())

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


