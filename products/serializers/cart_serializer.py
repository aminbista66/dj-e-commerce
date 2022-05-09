from rest_framework import serializers

from ..models import CartProduct, ProductImage

class CartReadSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.title')
    images = serializers.SerializerMethodField(read_only=True)
    shop_name = serializers.CharField(source='shop.shop_name')
    class Meta:
        model = CartProduct
        fields = (
            'slug',
            'product_name',
            'product',
            'user',
            'shop',
            'shop_name',
            'is_ordered',
            'is_delivered',
            'quantity',
            'images',
        )
    def get_images(self, obj):
        images = ProductImage.objects.filter(product__slug=obj.product.slug).values()
        return images

class CartSummarySerializer(serializers.Serializer):
    total_amount = serializers.FloatField()
    total_quantity = serializers.IntegerField()
    total_discount_percent = serializers.FloatField()
    total_discount_amount = serializers.FloatField()
    net_amount = serializers.FloatField()



