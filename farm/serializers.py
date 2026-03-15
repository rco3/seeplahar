from rest_framework import serializers
from .models import Location, SeedLot, Planting, Harvest, HarvestContainer, SeedlingBatch, Event


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ['id', 'name', 'description', 'parent', 'customer']
        read_only_fields = ['id', 'customer']


class SeedLotSerializer(serializers.ModelSerializer):
    class Meta:
        model = SeedLot
        fields = [
            'id', 'variety', 'name', 'quantity', 'units',
            'date_received', 'vendor', 'description',
            'source_partner', 'source_content_type', 'source_object_id',
            'location', 'customer',
        ]
        read_only_fields = ['id', 'customer']


class PlantingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Planting
        fields = [
            'id', 'variety', 'date', 'location', 'status',
            'quantity', 'type',
            'source_partner', 'source_content_type', 'source_object_id',
            'customer',
        ]
        read_only_fields = ['id', 'customer']


class HarvestContainerSerializer(serializers.ModelSerializer):
    class Meta:
        model = HarvestContainer
        fields = ['id', 'name', 'container_type', 'status', 'location', 'customer']
        read_only_fields = ['id', 'customer']


class HarvestSerializer(serializers.ModelSerializer):
    plants = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Planting.objects.all(),
    )

    class Meta:
        model = Harvest
        fields = [
            'id', 'plants', 'variety', 'date', 'quantity', 'units',
            'description', 'status', 'container',
            'source_partner', 'customer',
        ]
        read_only_fields = ['id', 'customer']


class SeedlingBatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = SeedlingBatch
        fields = [
            'id', 'variety', 'date', 'quantity', 'units',
            'parent_batch', 'vendor',
            'source_partner', 'source_content_type', 'source_object_id',
            'location', 'customer',
        ]
        read_only_fields = ['id', 'customer']


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = [
            'id', 'type', 'date', 'description',
            'content_type', 'object_id',
            'operator', 'customer',
        ]
        read_only_fields = ['id', 'customer']
