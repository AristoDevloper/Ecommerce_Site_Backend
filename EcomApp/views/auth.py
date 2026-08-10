from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

from EcomApp.models import Profile, Cart
from EcomApp.serializers import UserSerializer, ProfileSerializer
from EcomApp.utils import get_tokens_for_user, send_email
from EcomApp.customjwtauthentication import CustomJWTAuthentication

class UserRegistrationView(APIView):
    permission_classes = [AllowAny] 
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            full_name = f"{user.first_name} {user.last_name}".strip()
            profile = Profile.objects.create(user=user, display_name=full_name if full_name else user.username)
            tokens = get_tokens_for_user(user)
            if user:
                cart = Cart.objects.create(user=user)
                send_email(
                    subject='Welcome to E-commerce Site',
                    message=f'Hello {user.username},\n\nThank you for registering on our E-commerce site. We are excited to have you on board!\n\nBest regards,\nE-commerce Team',
                    recipient_list=[user.email]
                )
            response = Response({
                'user': serializer.data,
                'message': 'User registered successfully',
            }, status=status.HTTP_201_CREATED)
            response.set_cookie(
                key='jwt_access_token',
                value=tokens['access'],
                httponly=True,
                secure=True,
                samesite='None'
            )
            response.set_cookie(
                key='jwt_refresh_token',
                value=tokens['refresh'],
                httponly=True,
                secure=True,
                samesite='None'
            )
            return response
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class TokenRefreshView(APIView):
    permission_classes = [AllowAny]
    
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
                secure=True,
                samesite='None'
            )
            return response
        except TokenError:
            return Response({'error': 'Invalid refresh token'}, status=status.HTTP_401_UNAUTHORIZED)

class UserLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        if not email or not password:
            return Response({'error': 'Email and password are required'}, status=status.HTTP_400_BAD_REQUEST)

        if request.user.is_authenticated:
            return Response({'message': 'User is already logged in'}, status=status.HTTP_200_OK)

        try:
            user_obj = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            return Response({'error': 'Invalid email or password'}, status=status.HTTP_401_UNAUTHORIZED)

        user = authenticate(request, username=user_obj.username, password=password)
        if user is None:
            return Response({'error': 'Invalid email or password'}, status=status.HTTP_401_UNAUTHORIZED)
        
        tokens = get_tokens_for_user(user)
        response = Response({
            'message': 'User logged in successfully',
        }, status=status.HTTP_200_OK)

        response.set_cookie(
            key='jwt_access_token',
            value=tokens['access'],
            httponly=True,
            secure=True,
            samesite='None'
        )
        response.set_cookie(
            key='jwt_refresh_token',
            value=tokens['refresh'],
            httponly=True,
            secure=True,
            samesite='None'
        )
        return response

class UserLogoutView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        response = Response({'message': 'User logged out successfully'}, status=status.HTTP_200_OK)
        
        cookie_keys = ['jwt_access_token', 'jwt_refresh_token']
        for key in cookie_keys:
            response.set_cookie(
                key=key,
                value='',
                max_age=0,
                expires='Thu, 01 Jan 1970 00:00:00 GMT',
                path='/',
                httponly=True,
                secure=True,
                samesite='None'
            )
            response.set_cookie(
                key=key,
                value='',
                max_age=0,
                expires='Thu, 01 Jan 1970 00:00:00 GMT',
                path='/',
                httponly=True,
                secure=False,
                samesite='Lax'
            )
            response.delete_cookie(key, path='/')

        refresh_token = request.COOKIES.get('jwt_refresh_token')
        if refresh_token:
            try:
                refresh = RefreshToken(refresh_token)
                refresh.blacklist()
            except TokenError:
                pass

        return response

class PasswordResetRequestView(APIView):
    authentication_classes = [CustomJWTAuthentication]

    def post(self, request):
        email = request.data.get('email')
        try:
            user = User.objects.get(email=email)
            reset_token = default_token_generator.make_token(user)
            reset_link = f'http://localhost:3000/reset-password/{user.id}/{reset_token}/'
            return Response({'message': 'Password reset link sent to email','reset_link': reset_link}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'error': 'User with this email does not exist'}, status=status.HTTP_404_NOT_FOUND)
        
class AuthenticationCheckView(APIView):
    permission_classes = [AllowAny]

    def _auth_check_response(self, request):
        if request.user.is_authenticated:
            role = 'customer'
            if hasattr(request.user, 'profile'):
                role = request.user.profile.role
            return Response({
                'message': 'User is authenticated',
                'role': role,
                'is_staff': request.user.is_staff,
                'is_superuser': request.user.is_superuser
            }, status=status.HTTP_200_OK)
        return Response({'message': 'User is not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)

    def post(self, request):
        return self._auth_check_response(request)

    def get(self, request):
        return self._auth_check_response(request)

class PasswordResetConfirmView(APIView):
    authentication_classes = [CustomJWTAuthentication]

    def post(self, request, user_id, token):
        new_password = request.data.get('new_password')
        try:
            user = User.objects.get(id=user_id)
            if not default_token_generator.check_token(user, token):
                return Response({'error': 'Invalid or expired token'}, status=status.HTTP_400_BAD_REQUEST)
            user.set_password(new_password)
            user.save()
            return Response({'message': 'Password reset successful'}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'error': 'User does not exist'}, status=status.HTTP_404_NOT_FOUND)

class UserProfileView(APIView):
    authentication_classes = [CustomJWTAuthentication]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def patch(self, request):
        if not request.data:
            return Response({'error': 'No data provided for update'}, status=status.HTTP_400_BAD_REQUEST)

        address = request.data.get('address')
        phone_number = request.data.get('phone_number')
        name = request.data.get('display_name')
        try: 
            profile = Profile.objects.get(user=request.user)
            if address:
                profile.address = address
            if phone_number:
                profile.phone_number = phone_number
            if name:
                profile.display_name = name
            profile.save()
            serializer = ProfileSerializer(profile)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Profile.DoesNotExist:
            return Response({'error': 'Profile does not exist'}, status=status.HTTP_404_NOT_FOUND)
