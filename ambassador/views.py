import time

from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django_redis import get_redis_connection
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from ambassador.serializer import ProductSerializer, LinkSerializer
from ambassador.services import ProductService, LinkService
from ambassador.pagination import ProductPagination
from django.core.cache import cache

from common.authentication import JWTAuthentication
from core.models import Link, Order


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
    pagination_class = ProductPagination

    def get(self, request):
        search = request.query_params.get('search', '')
        sort = request.query_params.get('sort', None)
        page = request.query_params.get('page', '1')
        per_page = request.query_params.get('per_page', '9')
        
        # Page-specific cache key (much more efficient)
        cache_key = f'products_backend_{search}_{sort}_{page}_{per_page}'
        cached_response = cache.get(cache_key)
        
        if cached_response:
            return Response(cached_response)
        
        # Your simulation delay
        time.sleep(2)
        
        # Get filtered queryset (lazy evaluation - no DB hit yet)
        queryset = ProductService.get_filtered_products(search=search, sort=sort)
        
        # DRF handles pagination efficiently
        paginator = self.pagination_class()
        page_obj = paginator.paginate_queryset(queryset, request, view=self)
        
        if page_obj is not None:
            serializer = ProductSerializer(page_obj, many=True)
            response = paginator.get_paginated_response(serializer.data)
            
            # Cache the paginated response (not the entire dataset)
            cache.set(cache_key, response.data, timeout=60 * 30)
            return response
        
        # Fallback (should not happen with proper pagination)
        serializer = ProductSerializer(queryset, many=True)
        return Response(serializer.data)

class LinkAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        serializer = LinkSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        link = LinkService.create_link(user=user, products=serializer.validated_data['products'])

        return Response({
            'code': link.code,
            'link': link.user.id,
            'products': [p.id for p in link.products.all()]
        })

class StatsAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        links = Link.objects.filter(user_id=user.id)

        return Response([self.format(link) for link in links])

    def format(self, link):
        orders = Order.objects.filter(code=link.code, complete=1)

        return {
            'code': link.code,
            'count': len(orders),
            'revenue': sum(o.ambassador_revenue for o in orders)
        }

class RankingsAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        con = get_redis_connection("default")

        # zrevrangebyscore this helps us sort desc
        rankings = con.zrevrangebyscore('rankings', min=0, max=10000, withscores=True)

        return Response({
            r[0].decode("utf-8"): r[1] for r in rankings
        })