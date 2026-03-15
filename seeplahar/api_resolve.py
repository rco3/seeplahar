"""
GET /api/resolve/<uuid>/

Returns JSON describing which entity the UUID belongs to, scoped to the
authenticated user's customer.  Useful for QR-scan kiosk clients that receive
a UUID and need to know what kind of object it is before deciding what to do.

Response (200):
    {
        "type":    "seedlot",
        "app":     "farm",
        "id":      "<uuid>",
        "name":    "Andorian Blue Peas Batch 1",
        "api_url": "/api/seedlots/<uuid>/"
    }

Response (404): object not found for this customer.
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from farm.models import SeedLot, Planting, Harvest, SeedlingBatch, HarvestContainer, Location
from taxon.models import Taxon, Variety
from users.models import Partner
from seeplahar.api_mixins import CustomerAwareAPIViewMixin

# (model_class, type_slug, app_label, api_basename)
_REGISTRY = [
    (SeedLot,          'seedlot',          'farm',  'seedlots'),
    (Planting,         'planting',         'farm',  'plantings'),
    (Harvest,          'harvest',          'farm',  'harvests'),
    (SeedlingBatch,    'seedlingbatch',    'farm',  'seedlingbatches'),
    (HarvestContainer, 'harvestcontainer', 'farm',  'harvestcontainers'),
    (Location,         'location',         'farm',  'locations'),
    (Taxon,            'taxon',            'taxon', 'taxa'),
    (Variety,          'variety',          'taxon', 'varieties'),
    (Partner,          'partner',          'users', 'partners'),
]


class ResolveView(CustomerAwareAPIViewMixin, APIView):
    def get(self, request, pk):
        for model_class, type_slug, app_label, api_basename in _REGISTRY:
            try:
                obj = model_class.objects.get(pk=pk)
                return Response({
                    'type':    type_slug,
                    'app':     app_label,
                    'id':      str(obj.pk),
                    'name':    str(obj),
                    'api_url': f'/api/{api_basename}/{obj.pk}/',
                })
            except model_class.DoesNotExist:
                continue
        return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
