"""Urls for investment"""
from django.urls import path
from investment.views import AssetList, UpdateStockDataView, AccountViewsets, ActiveInvestmentAccountView
from rest_framework.routers import DefaultRouter

app_name = 'investment'


router = DefaultRouter()
router.register(r'InvestmentsAccounts', AccountViewsets, basename='account-investment')

urlpatterns = [
    path('api/assets/', AssetList.as_view(), name='load_assets'),
    path('api/update_stock_data/', UpdateStockDataView.as_view(), name='update_stock_data'),
    path('active-account/', ActiveInvestmentAccountView.as_view(), name='active-account'),
]

urlpatterns += router.urls