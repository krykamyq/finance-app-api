from django.test import TestCase
from django.contrib.auth import get_user_model
from core.models import InvestmentAccount, Asset, InvestmentAsset, InvestmentTransaction, ActiveInvestmentAccount
from decimal import Decimal
from datetime import date


class InvestmentAccountModelTest(TestCase):

    def test_create_investment_account(self):
        user = get_user_model().objects.create_user(username='testuser', email='test@example.com', password='testpass123')
        account = InvestmentAccount.objects.create(
            user=user,
            name='testaccount',
            amount_to_invest=Decimal('100.00'),
            total_investment=Decimal('150.00')
        )

        self.assertEqual(account.user, user)
        self.assertEqual(account.amount_to_invest, Decimal('100.00'))
        self.assertEqual(account.total_investment, Decimal('150.00'))
        self.assertEqual(account.actual_balance(), Decimal('250.00'))

class AssetModelTest(TestCase):

    def test_create_asset(self):
        asset = Asset.objects.create(
            name='Test Asset',
            value=Decimal('200.00'),
            type_asset='Stock'
        )

        self.assertEqual(asset.name, 'Test Asset')
        self.assertEqual(asset.value, Decimal('200.00'))
        self.assertEqual(asset.type_asset, 'Stock')


class InvestmentAssetModelTest(TestCase):

    def test_investment_asset_total_value(self):
        user = get_user_model().objects.create_user(username='testuser', email='test@example.com', password='testpass123')
        investment_account = InvestmentAccount.objects.create(user=user, name='testaccount')
        asset = Asset.objects.create(name='Test Asset', value=Decimal('50.00'))
        investment_asset = InvestmentAsset.objects.create(
            investment_account=investment_account,
            asset=asset,
            quantity_have=Decimal('2')
        )

        self.assertEqual(investment_asset.total_value(), Decimal('100.00'))

class InvestmentTransactionModelTest(TestCase):

    def test_create_transaction_and_update_asset_quantity(self):
        user = get_user_model().objects.create_user(username='testuser', email='test@example.com', password='testpass123')
        investment_account = InvestmentAccount.objects.create(user=user)
        asset = Asset.objects.create(name='Test Asset', value=Decimal('50.00'))
        investment_asset = InvestmentAsset.objects.create(
            investment_account=investment_account,
            asset=asset,
            quantity_have=Decimal('2')
        )

        transaction = InvestmentTransaction.objects.create(
            investment_account=investment_account,
            asset=investment_asset,
            quantity=Decimal('1'),
            date=date.today(),
            initial_value=Decimal('50.00'),
            type_transaction='buy'
        )

        investment_asset.refresh_from_db()

        self.assertEqual(transaction.quantity, Decimal('1'))
        self.assertEqual(investment_asset.quantity_have, Decimal('3'))

class ActiveInvestmentAccountModelTest(TestCase):

    def test_create_active_investment_account(self):
        # Create and save a User instance
        user = get_user_model().objects.create_user(username='testuser', email='test@example.com', password='testpass123')

        # Create and save an InvestmentAccount instance
        investment_account = InvestmentAccount.objects.create(
            user=user,
            # Set other necessary fields of InvestmentAccount
        )

        # Now that investment_account is saved, create ActiveInvestmentAccount
        active_investment_account = ActiveInvestmentAccount.objects.create(
            user=user,
            investment_account=investment_account
        )

        # Perform your assertions here
        self.assertEqual(active_investment_account.user, user)
        self.assertEqual(active_investment_account.investment_account, investment_account)



