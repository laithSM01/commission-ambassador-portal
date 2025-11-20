import time

from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from ambassador.serializer import ProductSerializer
from ambassador.services import ProductService
from django.core.cache import cache


class ProductFrontendAPIView(APIView):

    @method_decorator(cache_page(60 * 60 * 2, key_prefix='product-frontend'))
    def get(self, request):
        products = ProductService.get_all_products()
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            # Use validated data in service layer
            product = ProductService.create_product(**serializer.validated_data)
            response_serializer = ProductSerializer(product)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ProductBackendAPIView(APIView):

    def get(self, _):
        products = cache.get('products_backend')
        if not products:
            time.sleep(2)
            products = ProductService.get_all_products()
            cache.set('products_backend', products, timeout=60 * 30)  # 30 min

        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)