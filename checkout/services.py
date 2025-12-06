from decimal import Decimal
from typing import Optional
from core.models import Link, Order, OrderItem, Product
import decimal
from django.db import transaction
from django.conf import settings
import paypalrestsdk


class CheckoutService:
    """Service layer for checkout operations"""
    
    @staticmethod
    def get_link_by_code(code: str) -> Optional[Link]:
        """Get link by code for checkout"""
        try:
            return Link.objects.select_related('user').prefetch_related('products').get(code=code)
        except Link.DoesNotExist:
            return None
    
    @staticmethod
    def create_order_instance(order_data, link):
        """Create an order instance from provided data and link"""
        order = Order()
        order.code = link.code
        order.user_id = link.user.id
        order.ambassador_email = link.user.email
        order.first_name = order_data['first_name']
        order.last_name = order_data['last_name']
        order.email = order_data['email']
        order.address = order_data['address']
        order.country = order_data['country']
        order.city = order_data['city']
        order.zip = order_data['zip']
        order.save()
        return order
    
    @staticmethod
    def create_order_items(order, data):
        """Create order items and return line items for PayPal"""
        line_items = []
        for item in data['products']:
                product = Product.objects.filter(pk=item['product_id']).first()
                quantity = decimal.Decimal(item['quantity'])

                order_item = OrderItem()
                order_item.order = order
                order_item.product_title = product.title
                order_item.price = product.price
                order_item.quantity = quantity
                order_item.ambassador_revenue = decimal.Decimal(.1) * product.price * quantity
                order_item.admin_revenue = decimal.Decimal(.9) * product.price * quantity
                order_item.save()

                # Build line items for PayPal
                line_items.append({
                    'name': product.title,
                    'description': product.description,
                    'quantity': str(quantity),
                    'price': str(product.price),
                    'currency': 'USD'
                })
        return line_items

    @staticmethod
    def create_paypal_payment(line_items):
        """Create PayPal payment"""
        # Configure PayPal SDK
        paypalrestsdk.configure({
            "mode": settings.PAYPAL_MODE,
            "client_id": settings.PAYPAL_CLIENT_ID,
            "client_secret": settings.PAYPAL_CLIENT_SECRET
        })
        
        # Calculate total
        total = sum(Decimal(item['price']) * Decimal(item['quantity']) for item in line_items)
        
        payment = paypalrestsdk.Payment({
            "intent": "sale",
            "payer": {
                "payment_method": "paypal"
            },
            "redirect_urls": {
                "return_url": settings.PAYPAL_SUCCESS_URL,
                "cancel_url": settings.PAYPAL_CANCEL_URL
            },
            "transactions": [{
                "item_list": {
                    "items": line_items
                },
                "amount": {
                    "total": str(total),
                    "currency": settings.PAYPAL_CURRENCY
                },
                "description": "Order payment"
            }]
        })
        
        if payment.create():
            return payment
        else:
            raise Exception(payment.error)

    @staticmethod
    @transaction.atomic
    def create_order(order_data):
        try:
            link = Link.objects.filter(code=order_data['code']).first()
            if not link:
                raise ValueError('Invalid code!')

            order = CheckoutService.create_order_instance(order_data, link)
            line_items = CheckoutService.create_order_items(order, order_data)

            payment = CheckoutService.create_paypal_payment(line_items)
            order.transaction_id = payment.id
            order.save()

            return order, payment
        except Exception as e:
            transaction.rollback()
            raise e
        