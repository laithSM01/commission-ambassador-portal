from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class ProductPagination(PageNumberPagination):
    page_size = 9
    page_size_query_param = 'per_page'
    max_page_size = 100
    
    def get_paginated_response(self, data):
        """Custom response format to match your current API"""
        return Response({
            'data': data,
            'meta': {
                'total': self.page.paginator.count,
                'page': self.page.number,
                'last_page': self.page.paginator.num_pages,
                'per_page': self.get_page_size(self.request),
                'has_next': self.page.has_next(),
                'has_previous': self.page.has_previous()
            }
        })