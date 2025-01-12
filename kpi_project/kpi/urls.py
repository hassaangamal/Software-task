from django.urls import path
from .views import KPIListCreateView, LinkAssetToKPIView, IngestMessageView, UpdateConfigView
from graphene_django.views import GraphQLView
from django.views.decorators.csrf import csrf_exempt


urlpatterns = [
    path('kpis/', KPIListCreateView.as_view(), name='kpi-list-create'),
    path('messages/ingest/', IngestMessageView.as_view(), name='ingest-message'),
    path('kpis/link-asset/', LinkAssetToKPIView.as_view(), name='link-asset-to-kpi'),
    path('config/update/', UpdateConfigView.as_view(), name='update-config'),
    path('graphql/', csrf_exempt(GraphQLView.as_view(graphiql=True))),

]
