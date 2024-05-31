from django.urls import path
from .views import PlantDetailView, SeedLotDetailView, SeedlingBatchDetailView, HarvestDetailView, EventAddView

app_name = 'farm'

urlpatterns = [
    path('plant/<uuid:pk>/', PlantDetailView.as_view(), name='plant-detail'),
    path('seedlot/<uuid:pk>/', SeedLotDetailView.as_view(), name='seedlot-detail'),
    path('seedlingbatch/<uuid:pk>/', SeedlingBatchDetailView.as_view(), name='seedlingbatch-detail'),
    path('harvest/<uuid:pk>/', HarvestDetailView.as_view(), name='harvest-detail'),
    path('event/add/<uuid:pk>/', EventAddView.as_view(), name='event-add'),
]