from xml.dom import ValidationErr
from rest_framework import generics, status
from rest_framework import permissions, serializers
from rest_framework.response import Response
from users.models import Owner, Users
from .serializers.user_serializers import UserSerializer, OwnerCreateSerializer
from .serializers.token_verify_serializer import CustomTokenVerifySerializer
from rest_framework_simplejwt.serializers import TokenVerifySerializer


class CreateUser(generics.CreateAPIView):
    serializer_class = UserSerializer
    permission_class = [permissions.AllowAny]


class RegisterAsOwner(generics.CreateAPIView):
    serializer_class = OwnerCreateSerializer
    permission_class = [permissions.IsAuthenticated,]

    def get_user(self, request):
        if "HTTP_AUTHORIZATION" in request.META:  
            try:
                token = request.META.get('HTTP_AUTHORIZATION').split(' ')[1]
            except:
                return 0
            if len(token):
                data = CustomTokenVerifySerializer().validate({'token': token})
                return data.get('user_id')
            return 0
        else:
            return 0

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        user_id = self.get_user(self.request)
        if user_id == 0:
            return Response({"message":"missing token"})
        user = Users.objects.get(id=user_id)
        if serializer.is_valid():
            shop_name=serializer.validated_data.get('shop_name')
            qs = Owner.objects.filter(user=user).filter(shop_name=shop_name)
            if qs.exists():
                msg="You already have a shop by this name"
                return Response({'message':msg})
            serializer.save(user=user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class TestView(generics.GenericAPIView):
    permission_class = [permissions.AllowAny]
    def post(self, request, *args, **kwargs):
        token = request.META.get('HTTP_AUTHORIZATION').split(' ')[1]
        data = CustomTokenVerifySerializer().validate({'token':token})
        print(data['user_id'])
        return Response({"response":"OK"})