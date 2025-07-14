from django.urls import path
from .views import GenerateQRCodeView, TestLabelView, PrintLabelView

app_name = 'labels'

urlpatterns = [
    path('qr/<uuid:pk>/', GenerateQRCodeView.as_view(), name='generate_qr'),
    path('test/<uuid:pk>/', TestLabelView.as_view(), name='test_label'),
    path('print/<str:app_label>/<str:model_name>/<uuid:pk>/', PrintLabelView.as_view(), name='print_label'),
]