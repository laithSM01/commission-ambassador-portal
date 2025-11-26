from django.core.cache import cache


class ProductService:
    @staticmethod
    def clear_cache():
        """Clear all product-related cache entries"""
        for key in cache.keys('*'):
            if 'products_frontend' in key:
                cache.delete(key)
        cache.delete('products_backend')