from rest_framework import serializers
from core.models import Product, Link


class CheckoutProductSerializer(serializers.Serializer):
    """Only fields checkout needs for products"""
    id = serializers.IntegerField(read_only=True)
    title = serializers.CharField(max_length=255)
    description = serializers.CharField()
    image = serializers.CharField(max_length=255)
    price = serializers.DecimalField(max_digits=10, decimal_places=2)
    
    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Price must be greater than 0")
        return value


class CheckoutLinkSerializer(serializers.Serializer):
    """Only fields checkout needs for links"""
    id = serializers.IntegerField(read_only=True)
    products = CheckoutProductSerializer(many=True, read_only=True)
    
    def validate_code(self, value):
        try:
            Link.objects.get(code=value)
            return value
        except Link.DoesNotExist:
            raise serializers.ValidationError("Invalid link code")