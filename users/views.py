from xmlrpc.client import ResponseError
from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework import permissions, serializers
from rest_framework.response import Response
from rest_framework.mixins import UpdateModelMixin
from products.views import Order

from users.models import Address, Shop, User
from  products.models import CartProduct, Orders
from .serializers.user_serializers import UserSerializer, OwnerCreateSerializer, AddressSerializer, UserPublicData
from .serializers.order_serializer import OrderSerializer
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
        return Response({"Message": "Registerd Successfully"})

class RevokeAsOwner(generics.GenericAPIView):
    permission_class = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = User.objects.get(id=get_user(request))
        if not user.is_owner:
            return Response({"message":"You are not registered as owner"}, status=404)
        user.is_owner = False
        user.save()
        return Response({"message":"Ownership revoked"}, status=200)


class CreateShop(generics.CreateAPIView):
    serializer_class = OwnerCreateSerializer
    permission_class = [permissions.IsAuthenticated, ]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        user_id = get_user(self.request)
        if user_id == 0:
            return Response({"message": "missing token or user not found"})
        user = User.objects.get(id=user_id)
        if not user.is_owner:
            return Response({"message": "you must register as a owner"})
        if serializer.is_valid():
            shop_name = serializer.validated_data.get('shop_name')
            qs = Shop.objects.filter(owner=user).filter(shop_name=shop_name)
            if qs.exists():
                msg = "You already have a shop by this name"
                return Response({'message': msg})
            serializer.save(owner=user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class ListShop(generics.ListAPIView):
    permission_class = [permissions.AllowAny]
    serializer_class = OwnerCreateSerializer
    queryset = Shop.objects.all()

class DetailShop(generics.RetrieveAPIView):
    permission_class = [permissions.AllowAny]
    serializer_class = OwnerCreateSerializer
    queryset = Shop.objects.all()

class DeleteShop(generics.DestroyAPIView):
    permission_class = [permissions.IsAuthenticated]
    serializer_class = OwnerCreateSerializer
    queryset = Shop.objects.all()


    def get_queryset(self):
        user_id = get_user(self.request)
        user = User.objects.get(id=user_id)
        if user.is_superuser:
            return self.queryset
        qs = self.queryset.filter(owner=user)
        return qs

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({"message":"successfully deleted"},status=status.HTTP_204_NO_CONTENT)

class UpdateShop(generics.UpdateAPIView):
    permission_class = [permissions.IsAuthenticated]
    serializer_class = OwnerCreateSerializer
    queryset = Shop.objects.all()

    def get_queryset(self):
        user_id = get_user(self.request)
        user = User.objects.get(id=user_id)
        if user.is_superuser:
            return self.queryset
        qs = self.queryset.filter(owner=user)
        return qs

class AddAddress(generics.CreateAPIView):
    serializer_class = AddressSerializer
    permission_class = [permissions.IsAuthenticated, ]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            if get_user(request) == 0:
                return Response({"message":'token missing'})
            city, area, postal_code, zip_code = serializer.validated_data['city'], serializer.validated_data[
                'area'], serializer.validated_data['postal_code'], serializer.validated_data['zip_code']
            address_data = Address.objects.filter(user=get_user(request)).filter(
                city=city, area=area, postal_code=postal_code, zip_code=zip_code)
            if address_data.filter(user=get_user(request)).exists():
                return Response({"message": "address already exists."})
            user = User.objects.get(id=get_user(request))
            serializer.save(user=user)

        return Response({"message": 'Address Added'})

class ListAddress(generics.ListAPIView):
    permission_class = [permissions.IsAuthenticated]
    serializer_class = AddressSerializer

    def get_queryset(self):
        user = User.objects.get(id=get_user(self.request))
        qs = Address.objects.filter(user=user)
        return qs

class UpdateAddress(generics.UpdateAPIView):
    permission_class = [permissions.IsAuthenticated]
    serializer_class = AddressSerializer

    def get_queryset(self):
        user = User.objects.get(id=get_user(self.request))
        qs = Address.objects.filter(user=user)
        return qs

class AddressDetail(generics.RetrieveAPIView):
    permission_class = [permissions.IsAuthenticated]
    serializer_class = AddressSerializer
    queryset = Address.objects.all()

    def get_queryset(self):
        user = User.objects.get(id=get_user(self.request))
        qs = Address.objects.filter(user=user)
        return qs


class DeleteAddress(generics.DestroyAPIView):
    permission_class = [permissions.IsAuthenticated]
    serializer_class = AddressSerializer


    def get_queryset(self):
        user = User.objects.get(id=get_user(self.request))
        qs = Address.objects.filter(user=user)
        return qs

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({"message":"successfully deleted"},status=status.HTTP_204_NO_CONTENT)

class UserPublicDataView(generics.GenericAPIView):
    serializer_class = UserPublicData
    permission_class = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user_id = get_user(self.request)

        qs = User.objects.get(id=user_id)
        data = self.get_serializer(qs).data
        return Response(data, status=200)

class OrderHistory(generics.GenericAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user_id = get_user(request)

        qs = Orders.objects.filter(user__id = user_id)
        if qs.exists():
            data = self.get_serializer(qs, many=True).data
            return Response(data, status=200)
        return Response({"message": "No Orders."}, status=404)


