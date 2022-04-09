from rest_framework_simplejwt.serializers import TokenVerifySerializer
from rest_framework import serializers
from rest_framework_simplejwt.tokens import UntypedToken
from  jwt import decode as jwt_decode
from django.conf import settings

class CustomTokenVerifySerializer(TokenVerifySerializer):
    token = serializers.CharField()

    def validate(self, attrs):
        token = attrs["token"]
        data = jwt_decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        return data