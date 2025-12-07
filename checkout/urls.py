from django.urls import path
from .views import LinkAPIView, OrderApiView, OrderConfirmAPIView

urlpatterns = [
    path('links/<str:code>', LinkAPIView.as_view()),
    path('orders', OrderApiView.as_view()),
    path('orders/confirm', OrderConfirmAPIView.as_view()),
]