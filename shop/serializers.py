from rest_framework import serializers
from .models import SeedPackage, ProducePackage, PlantPackage


class SeedPackageSerializer(serializers.ModelSerializer):
    class Meta:
        model = SeedPackage
        fields = [
            'id', 'seed_lot', 'quantity', 'quantity_units',
            'date_packaged', 'description', 'customer',
        ]
        read_only_fields = ['id', 'customer']


class ProducePackageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProducePackage
        fields = [
            'id', 'harvest', 'quantity', 'quantity_units',
            'date_packaged', 'description', 'customer',
        ]
        read_only_fields = ['id', 'customer']


class PlantPackageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlantPackage
        fields = [
            'id', 'plants', 'date_packaged', 'quantity',
            'description', 'seedling_batch', 'customer',
        ]
        read_only_fields = ['id', 'customer']
