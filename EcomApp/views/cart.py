from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from EcomApp.models import Cart, CartItem, Product
from EcomApp.serializers import CartSerializer, CartItemSerializer
from EcomApp.customjwtauthentication import CustomJWTAuthentication

class CartView(APIView):
    authentication_classes = [CustomJWTAuthentication]

    def get(self, request):
        cart = Cart.objects.get(user=request.user)
        serializer = CartSerializer(cart)
        cart_items = CartItem.objects.select_related('product').filter(cart=cart)
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
            product = Product.objects.get(product_id=product_id)
            cart_item, created = CartItem.objects.get_or_create(
                cart=cart, 
                product=product, 
                defaults={'quantity': quantity}
                )
            if not created:
                cart_item.quantity += quantity
            else:
                cart_item.quantity = quantity

            if cart_item.quantity <= 0:
                cart_item.delete()
                return Response({'message': 'Product removed from cart'}, status=status.HTTP_200_OK)
            else:
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
            product = Product.objects.get(product_id=product_id)
            cart_item = CartItem.objects.filter(cart=cart, product=product).first()
            if cart_item:
                cart_item.delete()
                return Response(status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Product not found in cart'}, status=status.HTTP_404_NOT_FOUND)
        except Product.DoesNotExist:
            return Response({'error': 'Product does not exist'}, status=status.HTTP_404_NOT_FOUND)
