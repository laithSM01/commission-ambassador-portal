from django.urls import path, include

from administrator.views import AmbassadorAPIView, ProductGenericAPIView, LinkAPIView, OrderAPIView
from common.views import UserAPIView

"""URL configuration for app project.
    this is why we built a common app :
    so we can include the same thing in the ambassador and administrator urls
"""
urlpatterns = [
    path('', include('common.urls')),
    path('ambassadors', AmbassadorAPIView.as_view()),
    path('products', ProductGenericAPIView.as_view()),
    path('products/<str:pk>', ProductGenericAPIView.as_view()),
    path('users/<str:pk>/links', LinkAPIView.as_view()),
    path('orders', OrderAPIView.as_view()),
]