"""Urls for investment"""
from django.urls import path
from investment.views import AssetList, UpdateStockDataView

urlpatterns = [
    path('api/assets/', AssetList.as_view(), name='load_assets'),
    path('api/update_stock_data/', UpdateStockDataView.as_view(), name='update_stock_data'),
]