import decimal

from django.db import transaction
from rest_framework import status, exceptions
from rest_framework.response import Response
from rest_framework.views import APIView

from core.models import Order, Product, OrderItem, Link
from .serializers import CheckoutLinkSerializer
from .services import CheckoutService

from django.core.mail import send_mail


class LinkAPIView(APIView):

    """Get link details for checkout"""
    def get(self, request, code=''):
        link = CheckoutService.get_link_by_code(code)
        if not link:
            return Response(
                {'error': 'Link not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = CheckoutLinkSerializer(link)
        return Response(serializer.data)

class OrderApiView(APIView):

    def post(self, request):
        """Create a new order - only handle HTTP layer"""
        try:
            # Delegate business logic to service
            order, payment = CheckoutService.create_order(request.data)
            
            # Get approval URL from PayPal payment
            approval_url = None
            for link in payment.links:
                if link.rel == "approval_url":
                    approval_url = link.href
                    break
            
            return Response({
                'id': payment.id,
                'approval_url': approval_url
            }, status=status.HTTP_201_CREATED)
            
        except ValueError as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            return Response({
                'error': 'An error occurred while processing your order'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class OrderConfirmAPIView(APIView):
    def post(self, request):
        order = Order.objects.filter(transaction_id=request.data['source']).first()
        if not order:
            raise exceptions.APIException('Order not found!')

        order.complete = 1
        order.save()

        # Admin Email
        send_mail(
            subject='An Order has been completed',
            message='Order #' + str(order.id) + 'with a total of $' + str(order.admin_revenue) + ' has been completed!',
            from_email='from@email.com',
            recipient_list=['admin@admin.com']
        )

        send_mail(
            subject='An Order has been completed',
            message='You earned $' + str(order.ambassador_revenue) + ' from the link #' + order.code,
            from_email='from@email.com',
            recipient_list=[order.ambassador_email]
        )

        return Response({
            'message': 'success'
        })