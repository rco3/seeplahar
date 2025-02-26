# media/urls.py
from django.urls import path
from . import views

app_name = 'media'

urlpatterns = [
    path('add_photo/<str:object_type>/<uuid:object_id>/',
         views.add_photo, name='add_photo'),
    path('get_photos/<str:object_type>/<uuid:object_id>/',
         views.get_photos, name='get_photos'),
    path('delete_photo/<uuid:photo_id>/',
         views.delete_photo, name='delete_photo'),
]