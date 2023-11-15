import requests
from django.conf import settings
from core.models import Asset
from datetime import datetime

def update_asset_data(data):
    for asset in data['results']:
        value = asset['c'] # Adjust this based on the actual response structure
        Asset.objects.update_or_create(
            name=asset['T'],
            defaults={'value': value, 'type_asset': 'Stock'}
        )

def fetch_and_update_stock_data():
    api_url = f"https://api.polygon.io/v2/aggs/grouped/locale/us/market/stocks/2023-01-09?adjusted=true"
    params = {
        'apiKey': settings.POLYGON_IO_API_KEY,
        'adjusted': True,
        'date': datetime.now().strftime("%Y-%m-%d")
    }

    response = requests.get(api_url, params=params)
    if response.status_code == 200:
        data = response.json()
        update_asset_data(data)
    else:
        # Handle errors
        print("Failed to fetch data: ", response.text)