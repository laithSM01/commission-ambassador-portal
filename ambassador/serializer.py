from rest_framework import serializers

from core.models import Product, Link


# class ProductSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Product
#         fields = '__all__'

class ProductSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    title = serializers.CharField(max_length=255)
    description = serializers.CharField()
    image = serializers.CharField(max_length=255)
    price = serializers.DecimalField(max_digits=10, decimal_places=2)

    #  Serializer Only Validates & Transforms Data
    #  Business logic handled in service layer