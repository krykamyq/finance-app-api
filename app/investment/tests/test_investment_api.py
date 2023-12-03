from rest_framework.test import APITestCase
from rest_framework.reverse import reverse
from rest_framework import status
from django.contrib.auth import get_user_model
from core.models import ActiveInvestmentAccount, InvestmentAccount



class AccountViewSetTestCase(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='test', password='test', email='test@example.com')
        self.client.force_authenticate(self.user)
        self.account = ActiveInvestmentAccount.objects.get(user=self.user).investment_account
        self.account2 = InvestmentAccount.objects.create(user=self.user, name='test')

    def test_get_accounts(self):
        url = reverse('investment:account-investment-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)


    def test_get_account_detail(self):
        url = reverse('investment:account-investment-detail', kwargs={'pk': self.account.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], self.account.name)
        self.assertEqual(response.data['id'], self.account.id)

    def test_create_account(self):
        url = reverse('investment:account-investment-list')
        data = {'name': 'test'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], data['name'])

    def test_update_account(self):
        url = reverse('investment:account-investment-detail', kwargs={'pk': self.account.id})
        data = {'name': 'test'}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], data['name'])

    def test_delete_account(self):
        url = reverse('investment:account-investment-detail', kwargs={'pk': self.account.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(ActiveInvestmentAccount.objects.count(), 0)

    def test_get_accounts_unauthenticated(self):
        self.client.force_authenticate(None)
        url = reverse('investment:account-investment-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_account_unauthenticated(self):
        self.client.force_authenticate(None)
        url = reverse('investment:account-investment-list')
        data = {'name': 'test'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_active_investment_account(self):
        url = reverse('investment:active-investment-account')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['investment_account']['name'], self.account.name)

    def test_change_active_investment_account(self):
        url = reverse('investment:active-investment-account')
        data = {'investment_account_id': int(self.account2.id)}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
