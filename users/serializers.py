from rest_framework import serializers
from .models import Partner, Customer


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['id', 'name', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class PartnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Partner
        fields = ['id', 'name', 'is_active', 'created_at', 'updated_at', 'customer']
        read_only_fields = ['id', 'created_at', 'updated_at', 'customer']
