from rest_framework.authentication import BaseAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed
from .models import User  # Your MongoEngine User Model

class MongoJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        auth_tuple = super().authenticate(request)
        if auth_tuple is None:
            return None
        
        validated_token = auth_tuple[1]
        user_id = validated_token.get("user_id")

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise AuthenticationFailed("User not found")

        return (user, validated_token)
