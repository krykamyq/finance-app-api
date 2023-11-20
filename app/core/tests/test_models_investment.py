from django.test import TestCase
from django.contrib.auth import get_user_model
from core.models import InvestmentAccount, Asset, InvestmentAsset, InvestmentTransaction, ActiveInvestmentAccount, ActiveAccount
from decimal import Decimal
from datetime import date
from django.core.exceptions import ValidationError





class ModelTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='test_user',
            password='test_password',
            email='test_email@test.com')
        self.investment_account = ActiveInvestmentAccount.objects.get(user=self.user)
        self.account = self.investment_account.investment_account
        self.asset = Asset.objects.create(
            name='test',
            value=80
        )
        self.investment_asset = InvestmentAsset.objects.create(
            asset=self.asset,
            investment_account=self.account
        )


    def test_accoutn_creation(self):
        self.assertEquals(self.account.user, self.user)
        self.assertEquals(self.account.amount_to_invest, 0)
        self.assertEquals(self.account.total_investment, 0)
        self.assertEquals(self.account.balance, 0)
        self.assertEquals(self.user.balance, 0)

    def test_create_asset(self):
        self.assertEquals(self.asset.name, 'test')
        self.assertEquals(self.asset.value, 80)

    def test_create_investment_asset(self):
        self.assertEquals(self.investment_asset.asset, self.asset)
        self.assertEquals(self.investment_asset.investment_account, self.account)
        self.assertEquals(self.investment_asset.quantity_have, 0)
        self.assertEquals(self.investment_asset.total_value, 0)

    def test_create_buy_investment_transaction_with_not_enought_ammount_to_invest(self):
        with self.assertRaises(ValidationError):
            InvestmentTransaction.objects.create(
                asset=self.investment_asset,
                investment_account=self.account,
                quantity=10,
                date = date.today(),
                initial_value=100,
                type_transaction=InvestmentTransaction.type_transactions.BUY
            )
        self.assertEquals(self.investment_asset.quantity_have, 0)
        self.assertEquals(self.investment_asset.total_value, 0)
        self.assertEquals(self.user.balance, 0)

    def test_create_buy_investment_transaction_with_enought_ammount_to_invest(self):
        self.account.amount_to_invest = 1000
        self.account.save()
        InvestmentTransaction.objects.create(
                asset=self.investment_asset,
                investment_account=self.account,
                quantity=10,
                date = date.today(),
                initial_value=100,
                type_transaction=InvestmentTransaction.type_transactions.BUY
            )
        self.assertEquals(self.investment_asset.quantity_have, 10)
        self.assertEquals(self.investment_asset.total_value, 800)
        self.user.refresh_from_db()
        self.assertEquals(self.user.balance, 800)

    def test_create_sell_investment_transaction_with_not_enought_quantity_have(self):
        self.account.amount_to_invest = 1000
        self.account.save()
        InvestmentTransaction.objects.create(
                asset=self.investment_asset,
                investment_account=self.account,
                quantity=10,
                date = date.today(),
                initial_value=100,
                type_transaction=InvestmentTransaction.type_transactions.BUY
            )
        with self.assertRaises(ValidationError):
            InvestmentTransaction.objects.create(
                asset=self.investment_asset,
                investment_account=self.account,
                quantity=11,
                date = date.today(),
                initial_value=100,
                type_transaction=InvestmentTransaction.type_transactions.SELL
            )
        self.assertEquals(self.investment_asset.quantity_have, 10)
        self.assertEquals(self.investment_asset.total_value, 800)
        self.user.refresh_from_db()
        self.assertEquals(self.user.balance, 800)

    def test_create_sell_investment_transaction_with_enought_quantity_have(self):
        self.account.amount_to_invest = 1000
        self.account.save()
        InvestmentTransaction.objects.create(
                asset=self.investment_asset,
                investment_account=self.account,
                quantity=10,
                date = date.today(),
                initial_value=100,
                type_transaction=InvestmentTransaction.type_transactions.BUY
            )

        InvestmentTransaction.objects.create(
                asset=self.investment_asset,
                investment_account=self.account,
                quantity=8,
                date = date.today(),
                initial_value=100,
                type_transaction=InvestmentTransaction.type_transactions.SELL
            )
        self.assertEquals(self.investment_asset.quantity_have, 2)
        self.assertEquals(self.investment_asset.total_value, 160)
        self.assertEquals(self.account.amount_to_invest, 800)
        self.assertEquals(self.account.total_investment, 160)
        self.assertEquals(self.account.balance, 960)
        self.user.refresh_from_db()
        self.assertEquals(self.user.balance, 960)

    def test_update_buy_investment_transaction_with_not_enought_ammount_to_invest(self):
        self.account.amount_to_invest = 1000
        self.account.save()
        transaction =InvestmentTransaction.objects.create(
                asset=self.investment_asset,
                investment_account=self.account,
                quantity=10,
                date = date.today(),
                initial_value=100,
                type_transaction=InvestmentTransaction.type_transactions.BUY
            )
        transaction.quantity = 11  # Zwiększenie ilości o 1
        with self.assertRaises(ValidationError):
            transaction.save()

        self.investment_asset.refresh_from_db()
        self.user.refresh_from_db()
        self.assertEquals(self.investment_asset.quantity_have, 10)
        self.assertEquals(self.investment_asset.total_value, 800)
        self.assertEquals(self.user.balance, 800)

    def test_update_buy_investment_transaction_with_enought_ammount_to_invest(self):
        self.account.amount_to_invest = 1000
        self.account.save()
        transaction =InvestmentTransaction.objects.create(
                asset=self.investment_asset,
                investment_account=self.account,
                quantity=10,
                date = date.today(),
                initial_value=100,
                type_transaction=InvestmentTransaction.type_transactions.BUY
            )
        transaction.quantity = 8  # Zmniejszenie ilosci o 2
        transaction.save()

        self.investment_asset.refresh_from_db()
        self.user.refresh_from_db()

        self.assertEquals(self.investment_asset.quantity_have, 8)
        self.assertEquals(self.investment_asset.total_value, 640)
        self.assertEquals(self.user.balance, 840)

        transaction.quantity = 9 # Zwiekszenie ilosci o 1
        transaction.save()

        self.investment_asset.refresh_from_db()
        self.user.refresh_from_db()

        self.assertEquals(self.investment_asset.quantity_have, 9)
        self.assertEquals(self.investment_asset.total_value, 720)
        self.assertEquals(self.user.balance, 820)


    def test_update_sell_investment_transaction_with_not_enought_quantity_have(self):
        self.account.amount_to_invest = 1000
        self.account.save()
        InvestmentTransaction.objects.create(
                asset=self.investment_asset,
                investment_account=self.account,
                quantity=10,
                date = date.today(),
                initial_value=100,
                type_transaction=InvestmentTransaction.type_transactions.BUY
            )

        transaction = InvestmentTransaction.objects.create(
                asset=self.investment_asset,
                investment_account=self.account,
                quantity=8,
                date = date.today(),
                initial_value=100,
                type_transaction=InvestmentTransaction.type_transactions.SELL
            )
        transaction.quantity = 11 # Zwiększenie ilości o 1
        with self.assertRaises(ValidationError):
            transaction.save()

        self.assertEquals(self.investment_asset.quantity_have, 2)
        self.assertEquals(self.investment_asset.total_value, 160)
        self.assertEquals(self.account.amount_to_invest, 800)
        self.assertEquals(self.account.total_investment, 160)
        self.assertEquals(self.account.balance, 960)
        self.user.refresh_from_db()
        self.assertEquals(self.user.balance, 960)

    def test_update_sell_investment_transaction_with_ennought_quantity_have(self):
        self.account.amount_to_invest = 1000
        self.account.save()
        InvestmentTransaction.objects.create(
                asset=self.investment_asset,
                investment_account=self.account,
                quantity=10,
                date = date.today(),
                initial_value=100,
                type_transaction=InvestmentTransaction.type_transactions.BUY
            )

        transaction = InvestmentTransaction.objects.create(
                asset=self.investment_asset,
                investment_account=self.account,
                quantity=8,
                date = date.today(),
                initial_value=100,
                type_transaction=InvestmentTransaction.type_transactions.SELL
            )
        transaction.quantity = 7
        transaction.save()

        self.assertEquals(self.investment_asset.quantity_have, 3)
        self.assertEquals(self.investment_asset.total_value, 240)
        self.assertEquals(self.account.amount_to_invest, 700)
        self.assertEquals(self.account.total_investment, 240)
        self.assertEquals(self.account.balance, 940)
        self.user.refresh_from_db()
        self.assertEquals(self.user.balance, 940)

        transaction.quantity = 9
        transaction.save()

        self.assertEquals(self.investment_asset.quantity_have, 1)
        self.assertEquals(self.investment_asset.total_value, 80)
        self.assertEquals(self.account.amount_to_invest, 900)
        self.assertEquals(self.account.total_investment, 80)
        self.assertEquals(self.account.balance, 980)
        self.user.refresh_from_db()
        self.assertEquals(self.user.balance, 980)

    def test_update_asset_value(self):
        self.account.amount_to_invest = 1000
        self.account.save()
        InvestmentTransaction.objects.create(
                asset=self.investment_asset,
                investment_account=self.account,
                quantity=10,
                date = date.today(),
                initial_value=100,
                type_transaction=InvestmentTransaction.type_transactions.BUY
            )
        self.asset.value=100
        self.asset.save()
        self.investment_asset.save()
        self.account.save()
        self.investment_asset.refresh_from_db()
        self.account.refresh_from_db()

        self.assertEquals(self.investment_asset.quantity_have, 10)
        self.assertEquals(self.investment_asset.total_value, 1000)
        self.user.refresh_from_db()
        self.assertEquals(self.user.balance, 1000)


    def test_delete_asset(self):
        self.account.amount_to_invest = 1000
        self.account.save()
        InvestmentTransaction.objects.create(
                asset=self.investment_asset,
                investment_account=self.account,
                quantity=10,
                date = date.today(),
                initial_value=100,
                type_transaction=InvestmentTransaction.type_transactions.BUY
            )
        with self.assertRaises(ValidationError):
            self.asset.delete()
        asset2 = Asset.objects.create(name="Asset 2", value=1000)
        self.assertTrue(Asset.objects.filter(id=asset2.id).exists())
        asset2.delete()
        self.assertFalse(Asset.objects.filter(id=asset2.id).exists())

    def test_delete_investment_asset(self):
        self.account.amount_to_invest = 1000
        self.account.save()
        InvestmentTransaction.objects.create(
                asset=self.investment_asset,
                investment_account=self.account,
                quantity=10,
                date = date.today(),
                initial_value=100,
                type_transaction=InvestmentTransaction.type_transactions.BUY
            )
        with self.assertRaises(ValidationError):
            self.investment_asset.delete()
        InvestmentTransaction.objects.create(
            asset=self.investment_asset,
            investment_account=self.account,
            quantity=10,
            date = date.today(),
            initial_value=100,
            type_transaction=InvestmentTransaction.type_transactions.SELL)
        self.investment_asset.delete()
        self.assertFalse(InvestmentAsset.objects.filter(id=self.investment_asset.id).exists())


    def test_delete_investment_account(self):
        self.account.amount_to_invest = 1000
        self.account.save()
        InvestmentTransaction.objects.create(
                asset=self.investment_asset,
                investment_account=self.account,
                quantity=10,
                date = date.today(),
                initial_value=100,
                type_transaction=InvestmentTransaction.type_transactions.BUY
            )
        with self.assertRaises(ValidationError):
            self.account.delete()
        InvestmentTransaction.objects.create(
            asset=self.investment_asset,
            investment_account=self.account,
            quantity=10,
            date = date.today(),
            initial_value=100,
            type_transaction=InvestmentTransaction.type_transactions.SELL)
        self.account.delete()
        self.assertFalse(InvestmentAsset.objects.filter(id=self.investment_asset.id).exists())
        self.assertFalse(InvestmentAccount.objects.filter(id=self.account.id).exists())
        active = ActiveAccount.objects.get(user = self.user).account
        active.refresh_from_db()
        self.assertEquals(active.balance, 1000)
        self.user.refresh_from_db()
        self.assertEquals(self.user.balance, 1000)

    def test_delete_buy_transaction(self):
        self.account.amount_to_invest = 1000
        self.account.save()
        transaction = InvestmentTransaction.objects.create(
                asset=self.investment_asset,
                investment_account=self.account,
                quantity=10,
                date = date.today(),
                initial_value=100,
                type_transaction=InvestmentTransaction.type_transactions.BUY
            )
        transaction.delete()
        self.assertFalse(InvestmentTransaction.objects.filter(id=transaction.id).exists())
        self.account.refresh_from_db()
        self.assertEquals(self.account.amount_to_invest, 1000)

    def test_delete_buy_transaction_if_no_quantity(self):
        self.account.amount_to_invest = 1000
        self.account.save()
        transaction = InvestmentTransaction.objects.create(
                asset=self.investment_asset,
                investment_account=self.account,
                quantity=10,
                date = date.today(),
                initial_value=100,
                type_transaction=InvestmentTransaction.type_transactions.BUY
            )
        InvestmentTransaction.objects.create(
                asset=self.investment_asset,
                investment_account=self.account,
                quantity=10,
                date = date.today(),
                initial_value=100,
                type_transaction=InvestmentTransaction.type_transactions.SELL
            )
        with self.assertRaises(ValidationError):
            transaction.delete()


    def test_delete_sell_transaction(self):
        self.account.amount_to_invest = 1000
        self.account.save()
        InvestmentTransaction.objects.create(
                asset=self.investment_asset,
                investment_account=self.account,
                quantity=10,
                date = date.today(),
                initial_value=100,
                type_transaction=InvestmentTransaction.type_transactions.BUY
            )
        transaction = InvestmentTransaction.objects.create(
                asset=self.investment_asset,
                investment_account=self.account,
                quantity=10,
                date = date.today(),
                initial_value=100,
                type_transaction=InvestmentTransaction.type_transactions.SELL
            )
        transaction.delete()
        self.assertFalse(InvestmentTransaction.objects.filter(id=transaction.id).exists())
        self.account.refresh_from_db()
        self.assertEquals(self.account.amount_to_invest, 0)


    def test_delete_sell_transaction_if_not_enought_ammount(self):
        self.account.amount_to_invest = 1000
        self.account.save()
        InvestmentTransaction.objects.create(
                asset=self.investment_asset,
                investment_account=self.account,
                quantity=10,
                date = date.today(),
                initial_value=100,
                type_transaction=InvestmentTransaction.type_transactions.BUY
            )
        transaction = InvestmentTransaction.objects.create(
                asset=self.investment_asset,
                investment_account=self.account,
                quantity=10,
                date = date.today(),
                initial_value=100,
                type_transaction=InvestmentTransaction.type_transactions.SELL
            )
        InvestmentTransaction.objects.create(
                asset=self.investment_asset,
                investment_account=self.account,
                quantity=10,
                date = date.today(),
                initial_value=100,
                type_transaction=InvestmentTransaction.type_transactions.BUY
            )
        with self.assertRaises(ValidationError):
            transaction.delete()