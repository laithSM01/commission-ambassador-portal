from core.models import Product


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
    def get_all_products():
        return Product.objects.all()
    
    @staticmethod
    def get_product_by_id(product_id):
        return Product.objects.get(id=product_id)