from django.urls import path
from .views import SeedLotListView, SeedLotDetailView, PlantListView, PlantDetailView, HarvestListView, HarvestDetailView, SeedlingBatchListView, SeedlingBatchDetailView, EventListView, EventDetailView, EventAddView

app_name = 'farm'

urlpatterns = [
    path('seedlots/', SeedLotListView.as_view(), name='seedlot_list'),
    path('seedlots/<uuid:pk>/', SeedLotDetailView.as_view(), name='seedlot_detail'),
    path('plants/', PlantListView.as_view(), name='plant_list'),
    path('plants/<uuid:pk>/', PlantDetailView.as_view(), name='plant_detail'),
    path('harvests/', HarvestListView.as_view(), name='harvest_list'),
    path('harvests/<uuid:pk>/', HarvestDetailView.as_view(), name='harvest_detail'),
    path('seedlingbatches/', SeedlingBatchListView.as_view(), name='seedlingbatch_list'),
    path('seedlingbatches/<uuid:pk>/', SeedlingBatchDetailView.as_view(), name='seedlingbatch_detail'),
    path('events/', EventListView.as_view(), name='event_list'),
    path('events/<uuid:pk>/', EventDetailView.as_view(), name='event_detail'),
    path('events/add/', EventAddView.as_view(), name='event_add'),
]
