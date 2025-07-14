from django.urls import path
from .views import GenerateQRCodeView

app_name = 'labels'

urlpatterns = [
    path('qr/<uuid:pk>/', GenerateQRCodeView.as_view(), name='generate_qr'),
]