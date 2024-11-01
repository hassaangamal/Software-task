from django.urls import path
from .views import KPIListCreateView, LinkAssetToKPIView, IngestMessageView, UpdateConfigView

urlpatterns = [
    path('kpis/', KPIListCreateView.as_view(), name='kpi-list-create'),
    path('messages/ingest/', IngestMessageView.as_view(), name='ingest-message'),
    path('kpis/link-asset/', LinkAssetToKPIView.as_view(), name='link-asset-to-kpi'),
    path('config/update/', UpdateConfigView.as_view(), name='update-config'),
]
