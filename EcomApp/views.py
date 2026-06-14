from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework import status
from .models import *
from .serializers import *
from .customjwtauthentication import CustomJWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import AuthenticationFailed, TokenError
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework.decorators import api_view, permission_classes, authentication_classes

def get_tokens_for_user(user):
    if not user.is_active:
        raise AuthenticationFailed('User is not active.')

    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

# Create your views here.
@api_view(['GET'])
@permission_classes([IsAuthenticated])  # Allow anyone to access the home view
def home(request):
    return Response({'message': 'Welcome to the E-commerce API!'}, status=status.HTTP_200_OK)


class ProductList(APIView):
    def get(self, request):
        products = Product.objects.all()
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]  # Allow anyone to create a user, but restrict other actions to authenticated users
    authentication_classes = [CustomJWTAuthentication]  # Use custom JWT authentication for this viewset

class UserRegistrationView(APIView):
    permission_classes = [AllowAny]  # Allow anyone to access the registration view
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            tokens = get_tokens_for_user(user)
            response = Response({
                'user': serializer.data,
                'message': 'User registered successfully',
            }, status=status.HTTP_201_CREATED)
            # Set the JWT access token in an HTTP-only cookie
            response.set_cookie(
                key='jwt_access_token',
                value=tokens['access'],
                httponly=True,
                secure=True,  # Set to True in production for HTTPS
                samesite='Lax', # Adjust as needed (e.g., 'Strict' or 'None')
                # path='api/'  
            )
            response.set_cookie(
                key='jwt_refresh_token',
                value=tokens['refresh'],
                httponly=True,
                secure=True,  # Set to True in production for HTTPS in development 
                # you can set it to False as we are using http and will not matter for development
                samesite='Lax',   # Adjust as needed (e.g., 'Strict' or 'None')
                path='token/refresh/'  
            )
            return response
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class TokenRefreshView(APIView):
    permission_classes = [AllowAny]  # Allow anyone to access the token refresh view
    def post(self, request):
        refresh_token = request.COOKIES.get('jwt_refresh_token')

        if not refresh_token:
            return Response({'error': 'Refresh token not provided'}, status=status.HTTP_401_UNAUTHORIZED)
        
        try:
            refresh = RefreshToken(refresh_token)
            new_access_token = str(refresh.access_token)

            response = Response({'access': new_access_token}, status=status.HTTP_200_OK)
            response.set_cookie(
                key='jwt_access_token',
                value=new_access_token,
                httponly=True,
                secure=True,  # Set to True in production for HTTPS
                samesite='Lax', # Adjust as needed (e.g., 'Strict' or 'None')
                path='/api/'  
            )
            return response
        except TokenError as err:
            return Response({'error': 'Invalid refresh token'}, status=status.HTTP_401_UNAUTHORIZED)

