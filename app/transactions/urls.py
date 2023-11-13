"""Urls for transactions"""
from django.urls import path
from transactions.views import TransactionList, IncomeViewSet, ExpenseViewSet, TransferAPIView, BudgetViewSet
from rest_framework.routers import DefaultRouter

app_name = 'transactions'

router = DefaultRouter()
router.register(r'Incomes', IncomeViewSet, basename='income')
router.register(r'Expenses', ExpenseViewSet, basename='expense')
router.register(r'Budgets', BudgetViewSet, basename='budget')



urlpatterns = [
    path('transactions/', TransactionList.as_view(), name='transaction-list'),
    path('transfer/', TransferAPIView.as_view(), name='transfer'),

]

urlpatterns += router.urls