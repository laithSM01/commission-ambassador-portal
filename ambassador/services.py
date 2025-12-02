from core.models import Product, Link

import random, string



class ProductService:
    @staticmethod
    def create_product(id , title , description , price , image = None ):
        return Product.objects.create(id=id, title=title, description=description, image=image, price=price)
    
    @staticmethod
    def update_product(product_id, id , title , description , price , image = None):
        product = Product.objects.get(id=product_id)
        product.id = id
        product.title = title
        product.description = description
        product.price = price
        product.image = image
        product.save()
        return product
    
    @staticmethod
    def get_filtered_products(search='', sort=None):
        """
        Business logic only - no pagination
        Returns QuerySet for optimal database performance
        """
        queryset = Product.objects.all()
        
        if search:
            queryset = queryset.filter(title__icontains=search) | queryset.filter(description__icontains=search)

        if sort == 'asc':
            queryset = queryset.order_by('price')
        elif sort == 'desc':
            queryset = queryset.order_by('-price')

        return queryset
    
    @staticmethod
    def get_all_products(search='', sort=None):
        """Backward compatibility - delegates to get_filtered_products"""
        return ProductService.get_filtered_products(search, sort)
    
    @staticmethod
    def get_product_by_id(product_id):
        return Product.objects.get(id=product_id)

class LinkService:
    @staticmethod
    def generate_code():
        while True:
            code = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
            if not Link.objects.filter(code=code).exists():
                return code
    @staticmethod
    def create_link(user, products):
        code = LinkService.generate_code()
        link = Link.objects.create(code=code, user=user)
        link.products.set(products)
        return link