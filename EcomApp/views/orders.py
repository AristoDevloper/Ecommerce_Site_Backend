from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from EcomApp.models import Order, OrderItem, Product, Cart
from EcomApp.serializers import OrderSerializer, OrderFullSerializer, OrderItemSerializer
from EcomApp.utils import send_email
from EcomApp.customjwtauthentication import CustomJWTAuthentication

class OrderView(APIView):
    authentication_classes = [CustomJWTAuthentication]

    def post(self, request):
        if not request.data.get('product_id'):
            cart_id = request.data.get('cart_id')
            if cart_id:
                try:
                    cart = Cart.objects.get(user=request.user, cart_id=cart_id)
                except Cart.DoesNotExist:
                    return Response({'error': 'Invalid cart ID'}, status=status.HTTP_400_BAD_REQUEST)
            else:
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
                item.product.stock -= item.quantity
                item.product.save(update_fields=['stock'])
            
            cart.items.all().delete()

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
                product.stock -= quantity
                product.save(update_fields=['stock'])
            except Product.DoesNotExist:
                return Response({'error': 'Product does not exist'}, status=status.HTTP_404_NOT_FOUND)
        
        send_email(
            subject='Order Confirmation',
            message=f'Hello {request.user.username},\n\nYour order has been placed successfully. Your order ID is {order.id}.\n\nBest regards,\nE-commerce Team',
            recipient_list=[request.user.email]
        )
        return Response({'message': 'Order placed successfully'}, status=status.HTTP_201_CREATED)
    
    def get(self, request):
        orders = Order.objects.filter(user=request.user).order_by('-created_at')
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class OrderFullDetailView(APIView):
    authentication_classes = [CustomJWTAuthentication]

    def get(self, request, order_id):
        order = get_object_or_404(Order, order_id=order_id, user=request.user)
        serializer = OrderFullSerializer(order)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
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
