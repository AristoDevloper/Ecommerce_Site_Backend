import rest_framework_simplejwt.authentication
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError

class CustomJWTAuthentication(rest_framework_simplejwt.authentication.JWTAuthentication):
    def authenticate(self,request):
        # get the tokens from http only cookie
        token = request.COOKIES.get('jwt_access_token')
        if not token:
            return None
        try:
            validated_token = self.get_validated_token(token)
            user=self.get_user(validated_token)
            return (user, validated_token)
        except (InvalidToken, TokenError) as e:
            return None
        