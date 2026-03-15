"""
API URL configuration for Seeplahar.

All endpoints live under /api/ and require JWT (or session) auth.

Auth:
    POST /api/auth/token/          – obtain token pair
    POST /api/auth/token/refresh/  – refresh access token

Resolve:
    GET  /api/resolve/<uuid>/      – identify an object by UUID across all models

Resources (full CRUD via ModelViewSet):
    /api/locations/
    /api/seedlots/
    /api/plantings/
    /api/harvests/
    /api/harvestcontainers/
    /api/seedlingbatches/
    /api/events/
    /api/taxa/
    /api/varieties/
    /api/characteristics/
    /api/seedpackages/
    /api/producepackages/
    /api/plantpackages/
    /api/partners/
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from farm.api_views import (
    LocationViewSet, SeedLotViewSet, PlantingViewSet,
    HarvestViewSet, HarvestContainerViewSet,
    SeedlingBatchViewSet, EventViewSet,
)
from taxon.api_views import TaxonViewSet, VarietyViewSet, CharacteristicViewSet
from shop.api_views import SeedPackageViewSet, ProducePackageViewSet, PlantPackageViewSet
from users.api_views import PartnerViewSet
from .api_resolve import ResolveView

router = DefaultRouter()
router.register('locations', LocationViewSet, basename='location')
router.register('seedlots', SeedLotViewSet, basename='seedlot')
router.register('plantings', PlantingViewSet, basename='planting')
router.register('harvests', HarvestViewSet, basename='harvest')
router.register('harvestcontainers', HarvestContainerViewSet, basename='harvestcontainer')
router.register('seedlingbatches', SeedlingBatchViewSet, basename='seedlingbatch')
router.register('events', EventViewSet, basename='event')
router.register('taxa', TaxonViewSet, basename='taxon')
router.register('varieties', VarietyViewSet, basename='variety')
router.register('characteristics', CharacteristicViewSet, basename='characteristic')
router.register('seedpackages', SeedPackageViewSet, basename='seedpackage')
router.register('producepackages', ProducePackageViewSet, basename='producepackage')
router.register('plantpackages', PlantPackageViewSet, basename='plantpackage')
router.register('partners', PartnerViewSet, basename='partner')

urlpatterns = [
    path('auth/token/', TokenObtainPairView.as_view(), name='api-token-obtain'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='api-token-refresh'),
    path('resolve/<uuid:pk>/', ResolveView.as_view(), name='api-resolve'),
    path('', include(router.urls)),
]
