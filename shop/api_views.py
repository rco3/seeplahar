from rest_framework import viewsets
from seeplahar.api_mixins import CustomerAwareAPIViewMixin
from .models import SeedPackage, ProducePackage, PlantPackage
from .serializers import SeedPackageSerializer, ProducePackageSerializer, PlantPackageSerializer


class SeedPackageViewSet(CustomerAwareAPIViewMixin, viewsets.ModelViewSet):
    serializer_class = SeedPackageSerializer

    def get_queryset(self):
        return SeedPackage.objects.all()

    def perform_create(self, serializer):
        serializer.save(customer=self.request.user.customer)


class ProducePackageViewSet(CustomerAwareAPIViewMixin, viewsets.ModelViewSet):
    serializer_class = ProducePackageSerializer

    def get_queryset(self):
        return ProducePackage.objects.all()

    def perform_create(self, serializer):
        serializer.save(customer=self.request.user.customer)


class PlantPackageViewSet(CustomerAwareAPIViewMixin, viewsets.ModelViewSet):
    serializer_class = PlantPackageSerializer

    def get_queryset(self):
        return PlantPackage.objects.all()

    def perform_create(self, serializer):
        serializer.save(customer=self.request.user.customer)
