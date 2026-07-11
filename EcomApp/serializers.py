from rest_framework import serializers
from .models import *
from django.contrib.auth.models import User

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = '__all__'

class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Product
        fields = '__all__'

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user
    
class ProfileSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()
    name = serializers.CharField(source='display_name')
    class Meta:
        model = Profile
        fields = ['id','user','address', 'phone_number', 'role' ,'name']

class CartSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Cart
        fields = ['cart_id']

class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    class Meta:
        model = CartItem
        fields = '__all__'

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'

class OrderFullSerializer(serializers.ModelSerializer):
    items = serializers.SerializerMethodField()
    class Meta:
        model = Order
        fields = '__all__'

    def get_items(self, obj):
        items = obj.orderitem_set.all()
        return OrderItemSerializer(items, many=True).data

class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    order_id = serializers.UUIDField(source='order.order_id', read_only=True)
    seller = serializers.CharField(source='seller.name', read_only=True)
    class Meta:
        model = OrderItem
        fields = ['order_id', 'product', 'quantity', 'price', 'seller']

class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = '__all__'


class WishlistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wishlist
        fields = '__all__'

class MessageSerializer(serializers.ModelSerializer):
    sender_username = serializers.CharField(source='sender.username', read_only=True)
    sender_id = serializers.IntegerField(source='sender.id', read_only=True)
    class Meta:
        model = Message
        fields = ['id', 'conversation', 'sender', 'sender_id', 'sender_username', 'content', 'created_at']

class StoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = '__all__'

class StoreProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = StoreProduct
        fields = '__all__'

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = '__all__'

class ConversationSerializer(serializers.ModelSerializer):
    user1_username = serializers.CharField(source='user1.username', read_only=True)
    user2_username = serializers.CharField(source='user2.username', read_only=True)
    user1_id = serializers.IntegerField(source='user1.id', read_only=True)
    user2_id = serializers.IntegerField(source='user2.id', read_only=True)
    last_message = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = ['id', 'uuid', 'user1', 'user1_id', 'user1_username', 'user2', 'user2_id', 'user2_username', 'created_at', 'last_message']

    def get_last_message(self, obj):
        last = obj.messages.order_by('-created_at').first()
        if last:
            return {
                'content': last.content,
                'sender_username': last.sender.username,
                'created_at': last.created_at.isoformat()
            }
        return None
