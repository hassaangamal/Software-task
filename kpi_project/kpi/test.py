from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from .models import KPI, Asset, Message
from datetime import datetime
import json
import os
from django.conf import settings

class IngestMessageViewTests(APITestCase):
    def setUp(self):
        # Create a temporary config.json for testing
        self.config_path = os.path.join(settings.BASE_DIR, 'config.json')
        with open(self.config_path, 'w') as f:
            json.dump({'equation': 'ATTR + 5'}, f)

    # def tearDown(self):
    #     # Clean up the temporary config file
    #     if os.path.exists(self.config_path):
    #         os.remove(self.config_path)

    def test_valid_message_ingestion(self):
        url = reverse('ingest-message')
        data = {
            "asset_id": "asset123",
            "attribute_id": "attr123",
            "timestamp": "2024-01-01T12:00:00Z[UTC]",
            "value": "10"
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Message.objects.count(), 1)
        self.assertEqual(response.data['value'], '15')  # 10 + 5 from equation
        self.assertEqual(response.data['attribute_id'], 'output_attr123')

    def test_invalid_message_format(self):
        url = reverse('ingest-message')
        data = {
            "asset_id": "asset123",
            # missing required fields
            "timestamp": "2024-01-01T12:00:00Z[UTC]"
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Message.objects.count(), 0)

class KPIListCreateViewTests(APITestCase):
    def setUp(self):
        # Create a default asset for KPIs
        self.asset = Asset.objects.create(asset_id="test_asset_1")

    def test_create_kpi(self):
        url = reverse('kpi-list-create')
        data = {
            "name": "Test KPI",
            "expression": "value > 100",
            "description": "Test Description",
            "asset": self.asset.id
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(KPI.objects.count(), 1)
        kpi = KPI.objects.get()
        self.assertEqual(kpi.name, 'Test KPI')
        self.assertEqual(kpi.expression, 'value > 100')

    def test_create_kpi_duplicate_name(self):
        # Create first KPI
        KPI.objects.create(
            name="Test KPI",
            expression="value > 100",
            asset=self.asset
        )

        # Try to create second KPI with same name
        url = reverse('kpi-list-create')
        data = {
            "name": "Test KPI",
            "expression": "value > 200",
            "description": "Another Description",
            "asset": self.asset.id
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(KPI.objects.count(), 1)

    def test_list_kpis(self):
        # Create test KPIs
        KPI.objects.create(
            name="KPI 1",
            expression="value > 100",
            description="Desc 1",
            asset=self.asset
        )
        KPI.objects.create(
            name="KPI 2",
            expression="value < 50",
            description="Desc 2",
            asset=self.asset
        )

        url = reverse('kpi-list-create')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]['name'], 'KPI 1')
        self.assertEqual(response.data[1]['name'], 'KPI 2')

class LinkAssetToKPIViewTests(APITestCase):
    def setUp(self):
        self.asset1 = Asset.objects.create(asset_id="asset_1")
        self.asset2 = Asset.objects.create(asset_id="asset_2")
        self.kpi = KPI.objects.create(
            name="Test KPI",
            expression="value > 100",
            description="Test Description",
            asset=self.asset1
        )

    def test_successful_linking(self):
        url = reverse('link-asset-to-kpi')
        data = {
            "kpi_id": self.kpi.id,
            "asset_id": self.asset2.id
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.kpi.refresh_from_db()
        self.assertEqual(self.kpi.asset, self.asset2)

    def test_invalid_kpi_id(self):
        url = reverse('link-asset-to-kpi')
        data = {
            "kpi_id": 999,  # Non-existent KPI
            "asset_id": self.asset2.id
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_invalid_asset_id(self):
        url = reverse('link-asset-to-kpi')
        data = {
            "kpi_id": self.kpi.id,
            "asset_id": 999  # Non-existent asset
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_missing_fields(self):
        url = reverse('link-asset-to-kpi')
        data = {
            "kpi_id": self.kpi.id
            # missing asset_id
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

class UpdateConfigViewTests(APITestCase):
    def setUp(self):
        self.config_path = os.path.join(settings.BASE_DIR, 'config.json')
        with open(self.config_path, 'w') as f:
            json.dump({'equation': 'ATTR + 5'}, f)

    def tearDown(self):
        if os.path.exists(self.config_path):
            os.remove(self.config_path)

    def test_valid_equation_update(self):
        url = reverse('update-config')
        data = {
            "equation": "ATTR * 2"
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        with open(self.config_path, 'r') as f:
            config = json.load(f)
            self.assertEqual(config['equation'], "ATTR * 2")

    def test_invalid_equation(self):
        url = reverse('update-config')
        data = {
            "equation": "INVALID ++ EQUATION"
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_missing_equation(self):
        url = reverse('update-config')
        data = {}  # Empty data
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    