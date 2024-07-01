from django.urls import path
from seeplahar.views.generic import GenericListView, GenericDetailView, GenericCreateView, GenericUpdateView, GenericDeleteView
from .models import SeedLot, Planting, Harvest, SeedlingBatch, Event
from .views import GenerateQRCodeView, IntakeView, EventCreateView, EventUpdateView

app_name = 'farm'

urlpatterns = [
    # SeedLot URLs
    path('seedlots/', GenericListView.as_view(model=SeedLot), name='seedlot_list'),
    path('seedlots/<uuid:pk>/', GenericDetailView.as_view(model=SeedLot), name='seedlot_detail'),
    path('seedlots/add/', GenericCreateView.as_view(model=SeedLot, fields=['variety', 'name', 'quantity', 'units', 'date_received', 'origin', 'description', 'source_partner', 'source']), name='seedlot_create'),
    path('seedlots/<uuid:pk>/update/', GenericUpdateView.as_view(model=SeedLot, fields=['variety', 'name', 'quantity', 'units', 'date_received', 'origin', 'description', 'source_partner', 'source']), name='seedlot_update'),
    path('seedlots/<uuid:pk>/delete/', GenericDeleteView.as_view(model=SeedLot), name='seedlot_delete'),

    # Planting URLs
    path('plants/', GenericListView.as_view(model=Planting), name='planting_list'),
    path('plants/<uuid:pk>/', GenericDetailView.as_view(model=Planting), name='planting_detail'),
    path('plants/add/', GenericCreateView.as_view(model=Planting, fields=['source_partner', 'variety', 'date', 'location', 'status', 'source_content_type', 'source_object_id']), name='planting_create'),
    path('plants/<uuid:pk>/update/', GenericUpdateView.as_view(model=Planting, fields=['source_partner', 'variety', 'date', 'location', 'status', 'source_content_type', 'source_object_id']), name='planting_update'),
    path('plants/<uuid:pk>/delete/', GenericDeleteView.as_view(model=Planting), name='planting_delete'),

    # Harvest URLs
    path('harvests/', GenericListView.as_view(model=Harvest), name='harvest_list'),
    path('harvests/<uuid:pk>/', GenericDetailView.as_view(model=Harvest), name='harvest_detail'),
    path('harvests/add/', GenericCreateView.as_view(model=Harvest, fields=['plants', 'date', 'quantity', 'units', 'description', 'source_partner']), name='harvest_create'),
    path('harvests/<uuid:pk>/update/', GenericUpdateView.as_view(model=Harvest, fields=['plants', 'date', 'quantity', 'units', 'description', 'source_partner']), name='harvest_update'),
    path('harvests/<uuid:pk>/delete/', GenericDeleteView.as_view(model=Harvest), name='harvest_delete'),

    # SeedlingBatch URLs
    path('seedlingbatches/', GenericListView.as_view(model=SeedlingBatch), name='seedlingbatch_list'),
    path('seedlingbatches/<uuid:pk>/', GenericDetailView.as_view(model=SeedlingBatch), name='seedlingbatch_detail'),
    path('seedlingbatches/add/', GenericCreateView.as_view(model=SeedlingBatch, fields=['seed_lot', 'date', 'quantity', 'units', 'location', 'status', 'parent_batch', 'source', 'variety']), name='seedlingbatch_create'),
    path('seedlingbatches/<uuid:pk>/update/', GenericUpdateView.as_view(model=SeedlingBatch, fields=['seed_lot', 'date', 'quantity', 'units', 'location', 'status', 'parent_batch', 'source', 'variety']), name='seedlingbatch_update'),
    path('seedlingbatches/<uuid:pk>/delete/', GenericDeleteView.as_view(model=SeedlingBatch), name='seedlingbatch_delete'),

    # Event URLs
    path('events/', GenericListView.as_view(model=Event), name='event_list'),
    path('events/<uuid:pk>/', GenericDetailView.as_view(model=Event), name='event_detail'),
    path('events/add/', EventCreateView.as_view(), name='event_create'),
    path('events/<uuid:pk>/update/', EventUpdateView.as_view(), name='event_update'),
    path('events/<uuid:pk>/delete/', GenericDeleteView.as_view(model=Event), name='event_delete'),

    # Special views
    path('generate_qr/<uuid:pk>/', GenerateQRCodeView.as_view(), name='generate_qr'),
    path('intake/', IntakeView.as_view(), name='intake'),
]