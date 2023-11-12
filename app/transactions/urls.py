"""Urls for transactions"""
from django.urls import path
from transactions.views import TransactionList

app_name = 'transactions'

urlpatterns = [
    path('transactions/', TransactionList.as_view(), name='transaction-list'),

]