from .serializers.token_verify_serializer import CustomTokenVerifySerializer

def get_user(request):
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