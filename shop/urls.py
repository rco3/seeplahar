from django.urls import path

from seeplahar.views import GenericListView, GenericCreateView, GenericUpdateView, GenericDeleteView
from .models import SeedPackage, ProducePackage, PlantPackage
from .views import SeedPackageDetailView, ProducePackageDetailView, PlantPackageDetailView, SeedPackageCreateView, \
    ProducePackageCreateView, PlantPackageCreateView

app_name = 'shop'

urlpatterns = [
    # SeedPackage URLs
    path('seedpackage/', GenericListView.as_view(model=SeedPackage), name='seedpackage_list'),
    path('seedpackage/<uuid:pk>/', SeedPackageDetailView.as_view(), name='seedpackage_detail'),
    path('seedpackage/create/', SeedPackageCreateView.as_view(), name='seedpackage_create'),
    path('seedpackage/<uuid:pk>/update/', GenericUpdateView.as_view(model=SeedPackage,
                                                                    fields=['seed_lot', 'quantity', 'quantity_units',
                                                                            'date_packaged', 'description', 'photos']),
         name='seedpackage_update'),
    path('seedpackage/<uuid:pk>/delete/', GenericDeleteView.as_view(model=SeedPackage), name='seedpackage_delete'),

    # ProducePackage URLs
    path('producepackage/', GenericListView.as_view(model=ProducePackage), name='producepackage_list'),
    path('producepackage/<uuid:pk>/', ProducePackageDetailView.as_view(), name='producepackage_detail'),
    path('producepackage/create/', ProducePackageCreateView.as_view(), name='producepackage_create'),
    path('producepackage/<uuid:pk>/update/', GenericUpdateView.as_view(model=ProducePackage,
                                                                       fields=['harvest', 'quantity', 'quantity_units',
                                                                               'date_packaged', 'description',
                                                                               'photos']),
         name='producepackage_update'),
    path('producepackage/<uuid:pk>/delete/', GenericDeleteView.as_view(model=ProducePackage),
         name='producepackage_delete'),

    # PlantPackage URLs
    path('plantpackage/', GenericListView.as_view(model=PlantPackage), name='plantpackage_list'),
    path('plantpackage/<uuid:pk>/', PlantPackageDetailView.as_view(), name='plantpackage_detail'),
    path('plantpackage/create/', PlantPackageCreateView.as_view(), name='plantpackage_create'),
    path('plantpackage/<uuid:pk>/update/', GenericUpdateView.as_view(model=PlantPackage,
                                                                     fields=['plants', 'date_packaged', 'quantity',
                                                                             'description', 'seedling_batch',
                                                                             'photos']), name='plantpackage_update'),

    path('plantpackage/<uuid:pk>/delete/', GenericDeleteView.as_view(model=PlantPackage), name='plantpackage_delete'),
]
