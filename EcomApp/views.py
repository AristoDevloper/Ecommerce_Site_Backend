from uuid import UUID

from django.shortcuts import render, get_object_or_404
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
from rest_framework.decorators import api_view
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.models import User
from .utils import get_tokens_for_user, send_email
from rest_framework.decorators import permission_classes 
from django.contrib.auth import authenticate
from rest_framework.throttling import UserRateThrottle
from rest_framework import generics
from rest_framework.pagination import LimitOffsetPagination

# Create your views here.
@api_view(['GET'])  # Allow anyone to access the home view
@permission_classes([AllowAny])  # Allow anyone to access the home view
def home(request):
    return Response({'message': 'Welcome to the E-commerce API!'}, status=status.HTTP_200_OK)


class ProductList(generics.ListCreateAPIView):
    permission_classes = [AllowAny]
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def get_queryset(self):
        queryset = Product.objects.select_related('category').prefetch_related('images').all()

        category_name = self.request.query_params.get('category')
        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')

        if category_name and category_name.lower() != 'all objects':
            queryset = queryset.filter(category__name__iexact=category_name)

        if min_price not in (None, ''):
            queryset = queryset.filter(price__gte=min_price)

        if max_price not in (None, ''):
            queryset = queryset.filter(price__lte=max_price)

        return queryset.order_by('id')


# class ProductList(APIView):
#     permission_classes = [AllowAny]

#     def get(self, request):
#         products = Product.objects.all()

#         paginator = LimitOffsetPagination()
#         result_page = paginator.paginate_queryset(products, request)

#         serializer = ProductSerializer(result_page, many=True)

#         return paginator.get_paginated_response(serializer.data)

# User Registration, Login, Logout, and Password Reset Views
class UserRegistrationView(APIView):
    permission_classes = [AllowAny] 
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            profile = Profile.objects.create(user=user)
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
            # Set the JWT access token in an HTTP-only cookie
            response.set_cookie(
                key='jwt_access_token',
                value=tokens['access'],
                httponly=True,
                secure=False,  # Set to True in production for HTTPS
                samesite='Lax' # Adjust as needed (e.g., 'Strict' or 'None') 
            )
            response.set_cookie(
                key='jwt_refresh_token',
                value=tokens['refresh'],
                httponly=True,
                secure=False,  # Set to True in production for HTTPS in development 
                # you can set it to False as we are using http and will not matter for development
                samesite='Lax'   # Adjust as needed (e.g., 'Strict' or 'None')
            )
            return response
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
# View to handle JWT token refresh
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
                secure=False,  # Set to True in production for HTTPS
                samesite='Lax' # Adjust as needed (e.g., 'Strict' or 'None')
            )
            return response
        except TokenError as err:
            return Response({'error': 'Invalid refresh token'}, status=status.HTTP_401_UNAUTHORIZED)

# View to handle user login
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
            secure=False,  # Set to True in production for HTTPS
            samesite='Lax' # Adjust as needed (e.g., 'Strict' or 'None')
        )

        response.set_cookie(
            key='jwt_refresh_token',
            value=tokens['refresh'],
            httponly=True,
            secure=False,  # Set to True in production for HTTPS
            samesite='Lax'   # Adjust as needed (e.g., 'Strict' or 'None')

        )
        return response

# View to handle user logout
class UserLogoutView(APIView):
    authentication_classes = [CustomJWTAuthentication]

    def post(self, request):
        response = Response({'message': 'User logged out successfully'}, status=status.HTTP_200_OK)
        response.delete_cookie('jwt_access_token')
        response.delete_cookie('jwt_refresh_token')
        return response

# View to handle password reset request
class PasswordResetRequestView(APIView):
    authentication_classes = [CustomJWTAuthentication]

    def post(self, request):
        email = request.data.get('email')
        try:
            user = User.objects.get(email=email)
            # Generate password reset token and send email
            reset_token = default_token_generator.make_token(user)
            reset_link = f'http://localhost:3000/reset-password/{user.id}/{reset_token}/'
            # Send email with reset link

            # (Implementation for sending email would go here)
            return Response({'message': 'Password reset link sent to email','reset_link': reset_link}, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            return Response({'error': 'User with this email does not exist'}, status=status.HTTP_404_NOT_FOUND)
        
class AuthenticationCheckView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        if request.user.is_authenticated:
            return Response({'message': 'User is authenticated'}, status=status.HTTP_200_OK)
        return Response({'message': 'User is not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)

# View to handle password reset confirmation
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

# View to handle user profile retrieval and update
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

# View to handle user profile retrieval and update
class CartView(APIView):
    authentication_classes = [CustomJWTAuthentication]

    def get(self, request):
        cart = Cart.objects.get(user=request.user)
        serializer = CartSerializer(cart)
        cart_items = CartItem.objects.filter(cart=cart)
        cart_items_serializer = CartItemSerializer(cart_items, many=True)
        return Response({
            **serializer.data,
            'items': cart_items_serializer.data
        }, status=status.HTTP_200_OK)

    def post(self, request):
        cart = Cart.objects.get(user=request.user)
        product_id = request.data.get('product_id')
        quantity = request.data.get('quantity', 1)

        try:
            product = Product.objects.get(id=product_id)
            cart_item, created = CartItem.objects.get_or_create(
                cart=cart, 
                product=product, 
                defaults={'quantity': quantity}
                )
            if not created:
                cart_item.quantity += quantity
            else:
                cart_item.quantity = quantity
            cart_item.save()
            if quantity < 0:
                return Response({'message': 'Product quantity updated in cart'}, status=status.HTTP_200_OK)
            return Response({'message': 'Product added to cart'}, status=status.HTTP_200_OK)
        except Product.DoesNotExist:
            return Response({'error': 'Product does not exist'}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request):
        cart = Cart.objects.get(user=request.user)
        product_id = request.data.get('product_id')

        try:
            product = Product.objects.get(id=product_id)
            cart_item = CartItem.objects.filter(cart=cart, product=product).first()
            if cart_item:
                cart_item.delete()
                return Response(status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Product not found in cart'}, status=status.HTTP_404_NOT_FOUND)
        except Product.DoesNotExist:
            return Response({'error': 'Product does not exist'}, status=status.HTTP_404_NOT_FOUND)

# View to handle order placement and retrieval
class OrderView(APIView):
    authentication_classes = [CustomJWTAuthentication]

    def post(self, request):
        if not request.data.get('product_id'):
            cart = Cart.objects.get(user=request.user)
            if not cart.items.exists():
                return Response({'error': 'Cart is empty'}, status=status.HTTP_400_BAD_REQUEST)
            
            order = Order.objects.create(
                user=request.user,
             total_price=sum(item.product.price * item.quantity for item in cart.items.all())
            )
            for item in cart.items.all():
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    quantity=item.quantity,
                    price=item.product.price
                )
            
            cart.items.all().delete()  # Clear the cart after creating the order
            print('Order created from cart')

        # when order is placed directly from the product details page
        elif 'product_id' in request.data:
            product_id = request.data.get('product_id')
            quantity = request.data.get('quantity', 1)
            try:
                product = Product.objects.get(product_id=product_id)
                order = Order.objects.create(
                    user=request.user,
                    total_price=product.price * quantity,
                )
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=quantity,
                    price=product.price
                )
                print('Order created from product details page')
            except Product.DoesNotExist:
                return Response({'error': 'Product does not exist'}, status=status.HTTP_404_NOT_FOUND)
        

        # sending order confirmation email to the user
        send_email(
            subject='Order Confirmation',
            message=f'Hello {request.user.username},\n\nYour order has been placed successfully. Your order ID is {order.id}.\n\nBest regards,\nE-commerce Team',
            recipient_list=[request.user.email]
        )
        return Response({'message': 'Order placed successfully'}, status=status.HTTP_201_CREATED)
    
    def get(self, request):
        orders = Order.objects.filter(user=request.user)
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
# View to handle order details retrieval
class OrderDetailView(APIView):
    authentication_classes = [CustomJWTAuthentication]

    def get(self, request, order_id, product_id):
        order_item = get_object_or_404(
            OrderItem.objects.select_related('order', 'product'),
            order__order_id=order_id,
            product__product_id=product_id,
            order__user=request.user
        )
        serializer = OrderItemSerializer(order_item)
        return Response(serializer.data, status=status.HTTP_200_OK)

# View to handle order status updates
class orderStatusUpdateView(APIView):
    authentication_classes = [CustomJWTAuthentication]

    def put(self, request, order_id):
        new_status = request.data.get('status')
        try:
            order = Order.objects.get(order_id=order_id, user=request.user)
            order.set_status(new_status)
            return Response({'message': f'Order status updated to {new_status}'}, status=status.HTTP_200_OK)
        except Order.DoesNotExist:
            return Response({'error': 'Order does not exist'}, status=status.HTTP_404_NOT_FOUND)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
# View to handle product reviews  
class ReviewView(APIView):
    authentication_classes = [CustomJWTAuthentication]

    def post(self, request):
        product_id = request.data.get('product_id')
        rating = request.data.get('rating')
        comment = request.data.get('comment', '')
        try:
            product = Product.objects.get(product_id=product_id)
            Review.objects.create(
                user=request.user,
                product=product,
                rating=rating,
                comment=comment
            )

            return Response({'message': 'Review submitted successfully'}, status=status.HTTP_201_CREATED)
        except Product.DoesNotExist:
            return Response({'error': 'Product does not exist'}, status=status.HTTP_404_NOT_FOUND)
        
    def get(self, request):
        try:
            product = Product.objects.get(product_id=request.data.get("product_id"))
            reviews = Review.objects.filter(product=product)
            serializer = ReviewSerializer(reviews, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Product.DoesNotExist:
            return Response({'error': 'Product does not exist'}, status=status.HTTP_404_NOT_FOUND)
        
    def delete(self, request):
        review_id = request.data.get('review_id')
        try:
            review = Review.objects.get(id=review_id, user=request.user)
            review.delete()
            return Response({'message': 'Review deleted successfully'}, status=status.HTTP_200_OK)
        except Review.DoesNotExist:
            return Response({'error': 'Review does not exist'}, status=status.HTTP_404_NOT_FOUND)
        
# View to handle wishlist management
class WishlistView(APIView):
    authentication_classes = [CustomJWTAuthentication]

    def post(self, request):
        product_id = request.data.get('product_id')
        try:
            product = Product.objects.get(product_id=product_id)
            Wishlist.objects.create(
                user=request.user,
                product=product
            )
            return Response({'message': 'Product added to wishlist'}, status=status.HTTP_201_CREATED)
        except Product.DoesNotExist:
            return Response({'error': 'Product does not exist'}, status=status.HTTP_404_NOT_FOUND)
        
    def get(self, request):
        wishlist_items = Wishlist.objects.filter(user=request.user)
        serializer = WishlistSerializer(wishlist_items, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def delete(self, request):
        product_id = request.data.get('product_id')
        try:
            product = Product.objects.get(product_id=product_id)
            wishlist_item = Wishlist.objects.filter(user=request.user, product=product).first()
            if wishlist_item:
                wishlist_item.delete()
                return Response({'message': 'Product removed from wishlist'}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Product not found in wishlist'}, status=status.HTTP_404_NOT_FOUND)
        except Product.DoesNotExist:
            return Response({'error': 'Product does not exist'}, status=status.HTTP_404_NOT_FOUND)

# View to handle chat room creation and retrieval  
class ChatRoomView(APIView):
    authentication_classes = [CustomJWTAuthentication]

    def post(self, request):
        store_id = request.data.get("store_id")
        try:
            store = Store.objects.select_related("owner").get(store_id=store_id)
        except Store.DoesNotExist:
            return Response(
                {'error':'Store does not exist!!!'},
                status=status.HTTP_404_NOT_FOUND
            )
        seller = store.owner
        if not seller:
           return Response(
               {'error':'Seller does not exists!!!'},
               status=status.HTTP_404_NOT_FOUND
               )
        
        conversation, created = Conversation.objects.get_or_create(
            user1=seller,
            user2=request.user
            )
        
        if created:
            return Response(
                {
                    "Robot_response" : f"Thank you for contacting {store.name}. How can we help you?",
                    "conversation_id" : conversation.id,
                    "route" : f"/ws/chat/{conversation.id}/",
                    "created" : True
                 }
                )
        
        return Response(
            {
                "conversation_id" : conversation.id,
                "created" : False,
                "route" : f"/ws/chat/{conversation.id}/"
            }
            )

@api_view(['GET'])
@permission_classes([AllowAny])
def storeview(request):
    stores = Store.objects.all()
    serializer = StoreSerializer(stores, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

class ChatMessageView(APIView):
    authentication_classes = [CustomJWTAuthentication]

    def get(self, request, room_id):
        try:
            conversation = Conversation.objects.get(uuid=room_id)
        except Conversation.DoesNotExist:
            return Response({'error': 'Conversation does not exist'}, status=status.HTTP_404_NOT_FOUND)
        
        paginator = LimitOffsetPagination()
        paginator.default_limit = 20  # Set the default limit for pagination
        paginator.max_limit = 50  # Set the maximum limit for pagination
        
        fetched_messages = Message.objects.filter(conversation=conversation).order_by('created_at')
        messages = paginator.paginate_queryset(fetched_messages, request)
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def conversation_list(request):
    conversations = Conversation.objects.filter(user1=request.user) | Conversation.objects.filter(user2=request.user)
    serializer = ConversationSerializer(conversations, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)