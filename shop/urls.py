
from django.urls import path
from .views import SeedPackageDetailView, ProducePackageDetailView, PlantPackageDetailView

app_name = 'shop'

urlpatterns = [
    path('seedpackage/<uuid:pk>/', SeedPackageDetailView.as_view(), name='seedpackage-detail'),
    path('producepackage/<uuid:pk>/', ProducePackageDetailView.as_view(), name='producepackage-detail'),
    path('plantpackage/<uuid:pk>/', PlantPackageDetailView.as_view(), name='plantpackage-detail'),
]
