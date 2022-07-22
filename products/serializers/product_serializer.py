from dataclasses import field
from rest_framework import serializers
from rest_framework.response import Response
from ..models import Product, ProductImage, Review
from users.models import Shop, User
from statistics import mean


class ProductImageUploadSerializer(serializers.Serializer):
    images = serializers.ListField(child=serializers.FileField(
        allow_empty_file=False, use_url=False), allow_empty=False)


class ProductSerializer(serializers.ModelSerializer):
    shop_name = serializers.CharField(source='shop.shop_name')
    images = serializers.SerializerMethodField(read_only=True)
    net_price = serializers.SerializerMethodField(read_only=True)
    rating = serializers.SerializerMethodField(read_only=True)
    reviews = serializers.SerializerMethodField(read_only=True)
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
            'net_price',
            'rating',
            'reviews'
        )
        extra_kwargs = {
            'shop_name': {'required': True}
        }

    def get_images(self, obj):
        images = ProductImage.objects.filter(product__slug=obj.slug).values()
        return images

    def get_net_price(self, obj):
        return round(obj._total_price)

    def get_rating(self, obj):
        reviews = Review.objects.filter(product__slug=obj.slug)
        stars = [i.stars for i in reviews]
        if self.custom_mean(stars) != None: 
            return self.custom_mean(stars)
    
    def get_reviews(self, obj):
        reviews = Review.objects.filter(product__slug=obj.slug).values()
        return reviews

    def custom_mean(self, l):
        if len(l) == 0:
            return
        return sum(l) / len(l)

class UserPublicData(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'first_name',
            'last_name',
        )
        
class ReviewSerializer(serializers.ModelSerializer):
    reviewby = UserPublicData(source="user", read_only=True)
    class Meta:
        model = Review
        fields = (
            'reviewby',
            'feedback',
            'stars'
        )

