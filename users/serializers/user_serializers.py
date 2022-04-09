from wsgiref.validate import validator
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password
from ..models import User, Shop


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

    class Meta:
        model = Shop
        fields = (
            'shop_name',
            'shop_location',
        )
        extra_kwargs = {
            'shop_name': {'required':True}
        }