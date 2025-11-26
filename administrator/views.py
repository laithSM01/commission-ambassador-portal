from django.shortcuts import render
from rest_framework import mixins, generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from administrator.serializers import ProductSerializer, LinkSerializer, OrderSerializer
from administrator.services import ProductService
from common.authentication import JWTAuthentication
from common.serializers import UserSerializer
from core.models import User, Product, Link, Order
from django.core.cache import cache


class AmbassadorAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, _):
        ambassadors = User.objects.filter(is_ambassador=True)
        serializer = UserSerializer(ambassadors, many=True) # there was no need for ambassador serializer
        return Response(serializer.data)

class ProductGenericAPIView(
    generics.GenericAPIView, mixins.RetrieveModelMixin, mixins.ListModelMixin, mixins.CreateModelMixin,
    mixins.UpdateModelMixin, mixins.DestroyModelMixin
):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def get(self, request, pk=None):
        if pk:
            return self.retrieve(request, pk)

        return self.list(request)

    def post(self, request):
        response = self.create(request)
        ProductService.clear_cache()
        return response

    def put(self, request, pk=None):
        response = self.partial_update(request, pk)
        ProductService.clear_cache()
        return response

    def delete(self, request, pk=None):
        response = self.destroy(request, pk)
        ProductService.clear_cache()
        return response

class LinkAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, pk = None):
        links = Link.objects.filter(user_id=pk)
        serializer = LinkSerializer(links, many=True)
        return Response(serializer.data)

class OrderAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, pk=None):
        order = Order.object.filter(complete = True)
        serializer = OrderSerializer(order, many=True)
        return Response(serializer.data)