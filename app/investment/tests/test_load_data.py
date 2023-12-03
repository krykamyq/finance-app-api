"""Test UpdateStockDataView and AssetList"""

from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model


UPDATE_STOCK_DATA_URL = reverse('investment:update_stock_data')
ASSET_LIST_URL = reverse('investment:assets_list')


class PublicInvestmentApiTests(APITestCase):
    """Test the publicly available investment API"""

    def test_login_required_for_update_stock_data(self):
        """Test that login is required for updating stock data"""
        res = self.client.get(UPDATE_STOCK_DATA_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_retrieve_assets(self):
        """Test retrieving assets"""
        res = self.client.get(ASSET_LIST_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)


class PrivateInvestmentApiTests(APITestCase):
    """Test the authorized user investment API"""

    def setUp(self):
        self.user = get_user_model().objects.create_superuser(username='test', password='test', email='test@example.com')
        self.client.force_authenticate(self.user)


"""
    def test_update_stock_data(self):

        res = self.client.get(UPDATE_STOCK_DATA_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_update_stock_data_unauthorized(self):

        self.client.force_authenticate(None)
        res = self.client.get(UPDATE_STOCK_DATA_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
"""