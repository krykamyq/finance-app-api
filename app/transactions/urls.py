"""Urls for transactions"""
from django.urls import path
from transactions.views import TransactionList, IncomeViewSet
from rest_framework.routers import DefaultRouter

app_name = 'transactions'

router = DefaultRouter()
router.register(r'Incomes', IncomeViewSet, basename='income')



urlpatterns = [
    path('transactions/', TransactionList.as_view(), name='transaction-list'),

]

urlpatterns += router.urls