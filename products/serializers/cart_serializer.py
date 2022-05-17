from rest_framework import serializers
from ..models import CartProduct, ProductImage, Review

class CartReadSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.title')
    images = serializers.SerializerMethodField(read_only=True)
    shop_name = serializers.CharField(source='shop.shop_name')
    price = serializers.SerializerMethodField(read_only=True)
    stock = serializers.SerializerMethodField(read_only=True)
    product_slug = serializers.CharField(source='product.slug')
    rating = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = CartProduct
        fields = (
            'slug',
            'product_name',
            'product_slug',
            'user',
            'shop',
            'shop_name',
            'is_ordered',
            'is_delivered',
            'quantity',
            'images',
            'price',
            'stock',
            'rating'
        )
    def get_images(self, obj):
        images = ProductImage.objects.filter(product__slug=obj.product.slug).values()
        return images
    def get_price(self, obj):
        return round(obj._total_price)
    def get_stock(self, obj):
        return obj.product.quantity
    def get_rating(self, obj):
        reviews = Review.objects.filter(product__slug=obj.product.slug)
        stars = [i.stars for i in reviews]
        if self.custom_mean(stars) != None: 
            return self.custom_mean(stars)
    def custom_mean(self, l):
        if len(l) == 0:
            return
        return sum(l) / len(l)

class CartSummarySerializer(serializers.Serializer):
    total_amount = serializers.FloatField()
    total_quantity = serializers.IntegerField()
    total_discount_percent = serializers.FloatField()
    total_discount_amount = serializers.FloatField()
    net_amount = serializers.FloatField()

class CartWriteSerializer(serializers.Serializer):
    quantity = serializers.IntegerField()

