from rest_framework import serializers
from .models import Taxon, Variety, Characteristic, CharacteristicValue


class CharacteristicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Characteristic
        fields = ['id', 'name', 'customer']
        read_only_fields = ['id', 'customer']


class CharacteristicValueSerializer(serializers.ModelSerializer):
    class Meta:
        model = CharacteristicValue
        fields = ['id', 'characteristic', 'value', 'taxon', 'variety']


class TaxonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Taxon
        fields = ['id', 'name', 'species_name', 'type', 'description', 'customer']
        read_only_fields = ['id', 'customer']


class VarietySerializer(serializers.ModelSerializer):
    class Meta:
        model = Variety
        fields = ['id', 'name', 'taxon', 'description', 'customer']
        read_only_fields = ['id', 'customer']
