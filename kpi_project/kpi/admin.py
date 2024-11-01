from django.contrib import admin
from .models import Asset, KPI


# Register the Asset model
@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display = ('asset_id',)  
    search_fields = ('asset_id',)

# Register the KPI model
@admin.register(KPI)
class KPIAdmin(admin.ModelAdmin):
    list_display = ('name', 'expression', 'description', 'asset')  #
    search_fields = ('name', 'description')  
    list_filter = ('asset',)  
    ordering = ('name',)  