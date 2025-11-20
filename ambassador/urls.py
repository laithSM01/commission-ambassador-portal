from .views import ProductFrontendAPIView, ProductBackendAPIView

from django.urls import path, include

urlpatterns = [
    path('', include('common.urls')),
    path('products/frontend', ProductFrontendAPIView.as_view()),
    path('products/backend', ProductBackendAPIView.as_view()),
]