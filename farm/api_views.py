from rest_framework import viewsets
from seeplahar.api_mixins import CustomerAwareAPIViewMixin
from .models import Location, SeedLot, Planting, Harvest, HarvestContainer, SeedlingBatch, Event
from .serializers import (
    LocationSerializer, SeedLotSerializer, PlantingSerializer,
    HarvestSerializer, HarvestContainerSerializer,
    SeedlingBatchSerializer, EventSerializer,
)


class LocationViewSet(CustomerAwareAPIViewMixin, viewsets.ModelViewSet):
    serializer_class = LocationSerializer

    def get_queryset(self):
        return Location.objects.all()

    def perform_create(self, serializer):
        serializer.save(customer=self.request.user.customer)


class SeedLotViewSet(CustomerAwareAPIViewMixin, viewsets.ModelViewSet):
    serializer_class = SeedLotSerializer

    def get_queryset(self):
        return SeedLot.objects.all()

    def perform_create(self, serializer):
        serializer.save(customer=self.request.user.customer)


class PlantingViewSet(CustomerAwareAPIViewMixin, viewsets.ModelViewSet):
    serializer_class = PlantingSerializer

    def get_queryset(self):
        return Planting.objects.all()

    def perform_create(self, serializer):
        serializer.save(customer=self.request.user.customer)


class HarvestContainerViewSet(CustomerAwareAPIViewMixin, viewsets.ModelViewSet):
    serializer_class = HarvestContainerSerializer

    def get_queryset(self):
        return HarvestContainer.objects.all()

    def perform_create(self, serializer):
        serializer.save(customer=self.request.user.customer)


class HarvestViewSet(CustomerAwareAPIViewMixin, viewsets.ModelViewSet):
    serializer_class = HarvestSerializer

    def get_queryset(self):
        return Harvest.objects.all()

    def perform_create(self, serializer):
        serializer.save(customer=self.request.user.customer)


class SeedlingBatchViewSet(CustomerAwareAPIViewMixin, viewsets.ModelViewSet):
    serializer_class = SeedlingBatchSerializer

    def get_queryset(self):
        return SeedlingBatch.objects.all()

    def perform_create(self, serializer):
        serializer.save(customer=self.request.user.customer)


class EventViewSet(CustomerAwareAPIViewMixin, viewsets.ModelViewSet):
    serializer_class = EventSerializer

    def get_queryset(self):
        return Event.objects.all()

    def perform_create(self, serializer):
        serializer.save(customer=self.request.user.customer)
