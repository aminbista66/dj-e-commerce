from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView


class customTokenObtainPairSerializer(TokenObtainPairSerializer):

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        token['name'] = f"{user.first_name} {user.last_name}"
        token['user_id'] = user.id
        token['is_owner'] = user.is_owner

        return token

class customTokenObtainPairView(TokenObtainPairView):
    serializer_class = customTokenObtainPairSerializer