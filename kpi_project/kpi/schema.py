# schema.py
import graphene
from graphene_django import DjangoObjectType
from .models import Asset, KPI, Message
from django.db.models import Q

# Define Types
class AssetType(DjangoObjectType):
    class Meta:
        model = Asset
        fields = ('id', 'asset_id', 'kpis')

class KPIType(DjangoObjectType):
    class Meta:
        model = KPI
        fields = ('id', 'name', 'expression', 'description', 'asset')

class MessageType(DjangoObjectType):
    class Meta:
        model = Message
        fields = ('id', 'asset_id', 'attribute_id', 'timestamp', 'value')

# Queries
class Query(graphene.ObjectType):
    # Asset Queries
    all_assets = graphene.List(AssetType)
    asset_by_id = graphene.Field(AssetType, asset_id=graphene.String())
    
    # KPI Queries
    all_kpis = graphene.List(KPIType)
    kpi_by_name = graphene.Field(KPIType, name=graphene.String())
    kpis_by_asset = graphene.List(KPIType, asset_id=graphene.String())
    
    # Message Queries
    all_messages = graphene.List(MessageType)
    messages_by_asset = graphene.List(MessageType, asset_id=graphene.String())
    messages_by_timerange = graphene.List(
        MessageType,
        start_time=graphene.DateTime(),
        end_time=graphene.DateTime()
    )

    def resolve_all_assets(self, info):
        return Asset.objects.all()

    def resolve_asset_by_id(self, info, asset_id):
        return Asset.objects.get(asset_id=asset_id)

    def resolve_all_kpis(self, info):
        return KPI.objects.all()

    def resolve_kpi_by_name(self, info, name):
        return KPI.objects.get(name=name)

    def resolve_kpis_by_asset(self, info, asset_id):
        return KPI.objects.filter(asset__asset_id=asset_id)

    def resolve_all_messages(self, info):
        return Message.objects.all()

    def resolve_messages_by_asset(self, info, asset_id):
        return Message.objects.filter(asset_id=asset_id)

    def resolve_messages_by_timerange(self, info, start_time, end_time):
        return Message.objects.filter(timestamp__range=[start_time, end_time])

# Mutations
class CreateAsset(graphene.Mutation):
    class Arguments:
        asset_id = graphene.String(required=True)

    asset = graphene.Field(AssetType)

    def mutate(self, info, asset_id):
        asset = Asset.objects.create(asset_id=asset_id)
        return CreateAsset(asset=asset)

class CreateKPI(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        expression = graphene.String(required=True)
        description = graphene.String()
        asset_id = graphene.String(required=True)

    kpi = graphene.Field(KPIType)

    def mutate(self, info, name, expression, asset_id, description=None):
        asset = Asset.objects.get(asset_id=asset_id)
        kpi = KPI.objects.create(
            name=name,
            expression=expression,
            description=description,
            asset=asset
        )
        return CreateKPI(kpi=kpi)

class CreateMessage(graphene.Mutation):
    class Arguments:
        asset_id = graphene.String(required=True)
        attribute_id = graphene.String(required=True)
        timestamp = graphene.DateTime(required=True)
        value = graphene.String(required=True)

    message = graphene.Field(MessageType)

    def mutate(self, info, asset_id, attribute_id, timestamp, value):
        message = Message.objects.create(
            asset_id=asset_id,
            attribute_id=attribute_id,
            timestamp=timestamp,
            value=value
        )
        return CreateMessage(message=message)

class UpdateKPI(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
        name = graphene.String()
        expression = graphene.String()
        description = graphene.String()

    kpi = graphene.Field(KPIType)

    def mutate(self, info, id, **kwargs):
        kpi = KPI.objects.get(pk=id)
        for key, value in kwargs.items():
            if value is not None:
                setattr(kpi, key, value)
        kpi.save()
        return UpdateKPI(kpi=kpi)

class DeleteKPI(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)

    success = graphene.Boolean()

    def mutate(self, info, id):
        try:
            KPI.objects.get(pk=id).delete()
            return DeleteKPI(success=True)
        except KPI.DoesNotExist:
            return DeleteKPI(success=False)

class Mutation(graphene.ObjectType):
    create_asset = CreateAsset.Field()
    create_kpi = CreateKPI.Field()
    create_message = CreateMessage.Field()
    update_kpi = UpdateKPI.Field()
    delete_kpi = DeleteKPI.Field()

schema = graphene.Schema(query=Query, mutation=Mutation)