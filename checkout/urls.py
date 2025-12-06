from django.urls import path
from .views import LinkAPIView, OrderApiView

urlpatterns = [
    path('links/<str:code>', LinkAPIView.as_view()),
    path('orders', OrderApiView.as_view())
]