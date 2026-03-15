from rest_framework import viewsets
from seeplahar.api_mixins import CustomerAwareAPIViewMixin
from .models import Taxon, Variety, Characteristic
from .serializers import TaxonSerializer, VarietySerializer, CharacteristicSerializer


class TaxonViewSet(CustomerAwareAPIViewMixin, viewsets.ModelViewSet):
    serializer_class = TaxonSerializer

    def get_queryset(self):
        return Taxon.objects.all()

    def perform_create(self, serializer):
        serializer.save(customer=self.request.user.customer)


class VarietyViewSet(CustomerAwareAPIViewMixin, viewsets.ModelViewSet):
    serializer_class = VarietySerializer

    def get_queryset(self):
        return Variety.objects.all()

    def perform_create(self, serializer):
        serializer.save(customer=self.request.user.customer)


class CharacteristicViewSet(CustomerAwareAPIViewMixin, viewsets.ModelViewSet):
    serializer_class = CharacteristicSerializer

    def get_queryset(self):
        return Characteristic.objects.all()

    def perform_create(self, serializer):
        serializer.save(customer=self.request.user.customer)
