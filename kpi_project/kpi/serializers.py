from rest_framework import serializers
from .models import KPI
from .models import KPI, Asset

class KPISerializer(serializers.ModelSerializer):
    class Meta:
        model = KPI
        fields = ['id', 'name', 'expression', 'description', 'asset']

class AssetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Asset
        fields = ['id', 'asset_id']