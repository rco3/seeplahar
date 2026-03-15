from rest_framework import viewsets
from seeplahar.api_mixins import CustomerAwareAPIViewMixin
from .models import Partner
from .serializers import PartnerSerializer


class PartnerViewSet(CustomerAwareAPIViewMixin, viewsets.ModelViewSet):
    serializer_class = PartnerSerializer

    def get_queryset(self):
        return Partner.objects.all()

    def perform_create(self, serializer):
        serializer.save(customer=self.request.user.customer)
