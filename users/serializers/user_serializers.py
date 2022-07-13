from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password
from ..models import User, Shop, Address
from rest_framework.permissions import DjangoModelPermissions
from products.models import Product

class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required = True,
        validators = [UniqueValidator(queryset=User.objects.all())]
    )
    password = serializers.CharField(
        required=True, write_only=True, validators=[validate_password])
    password2 = serializers.CharField(
        required=True, write_only=True
    )
    is_owner = serializers.BooleanField(
        write_only=True,
        required=True
    )
    class Meta:
        model = User
        fields = (
            'email',
            'first_name',
            'last_name',
            'password',
            'password2',
            'is_owner',)
        extra_kwargs = {
            'first_name':{'required':True},
            'last_name':{'required':True}
        }
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({'password': 'password didnot match'})
        return super().validate(attrs)

    def create(self, validated_data):
        user = User.objects.create(
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            email=validated_data['email']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

class OwnerCreateSerializer(serializers.ModelSerializer):
    products = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Shop
        fields = (
            'id',
            'shop_name',
            'shop_location',
            'products',
        )
        extra_kwargs = {
            'shop_name': {'required':True}
        }
    def get_products(self, obj):
        qs = Product.objects.filter(shop__id=obj.id).values()
        return qs

class AddressSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Address
        fields = (
            'id',
            'city',
            'area',
            'postal_code',
            'zip_code',
        )

class UserPublicData(serializers.ModelSerializer):
    addresses = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = User
        fields = (
            'first_name',
            'last_name',
            'email',
            'addresses',
            'is_owner'
        )
    def get_addresses(self, obj):
        data = Address.objects.filter(user__id=obj.id).values()
        return data

