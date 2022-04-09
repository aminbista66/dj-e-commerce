from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework import permissions, serializers
from rest_framework.response import Response
from rest_framework_simplejwt.serializers import TokenVerifySerializer
from rest_framework.mixins import UpdateModelMixin

from users.models import Shop, User
from .serializers.user_serializers import UserSerializer, OwnerCreateSerializer
from .get_user import get_user


class CreateUser(generics.CreateAPIView):
    serializer_class = UserSerializer
    permission_class = [permissions.AllowAny]


class RegisterAsOwner(generics.GenericAPIView, UpdateModelMixin):
    permission_class = [permissions.IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        user = User.objects.get(id=get_user(request))
        user.is_owner = True
        user.save()
        return Response({"Message":"Registerd Successfully"})


class CreateShop(generics.CreateAPIView):
    serializer_class = OwnerCreateSerializer
    permission_class = [permissions.IsAuthenticated,]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        user_id = get_user(self.request)
        if user_id == 0:
            return Response({"message":"missing token"})
        user = User.objects.get(id=user_id)
        if not user.is_owner:
            return Response({"message":"you must register as a owner"})
        if serializer.is_valid():
            shop_name=serializer.validated_data.get('shop_name')
            qs = Shop.objects.filter(owner=user).filter(shop_name=shop_name)
            if qs.exists():
                msg="You already have a shop by this name"
                return Response({'message':msg})
            serializer.save(owner=user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class TestView(generics.GenericAPIView):
    def get(self, request, *args, **kwargs):
        user = User.objects.get(id=2)
        print(user.is_owner)
        return Response({"message":f"{user.is_owner}"})