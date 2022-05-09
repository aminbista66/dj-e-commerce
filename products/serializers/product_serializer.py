from dataclasses import field
from rest_framework import serializers
from rest_framework.response import Response
from ..models import Product, ProductImage
from users.models import Shop


class ProductImageUploadSerializer(serializers.Serializer):
    images = serializers.ListField(child=serializers.FileField(allow_empty_file=False, use_url=False), allow_empty=False)


class ProductSerializer(serializers.ModelSerializer):
    shop_name = serializers.CharField(source='shop.shop_name')
    images = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = Product
        fields = (
            'slug',
            'title',
            'description',
            'price',
            'discount',
            'quantity',
            'shop_name',
            'images',
        )
        extra_kwargs = {
            'shop_name': {'required': True}
        }
    def get_images(self, obj):
        images = ProductImage.objects.filter(product__slug=obj.slug).values()
        return images
        
