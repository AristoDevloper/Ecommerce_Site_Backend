from rest_framework import serializers
from EcomApp.models import Order, OrderItem
from .products import ProductSerializer

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'

class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    order_id = serializers.UUIDField(source='order.order_id', read_only=True)
    seller = serializers.CharField(source='seller.name', read_only=True)
    class Meta:
        model = OrderItem
        fields = ['order_id', 'product', 'quantity', 'price', 'seller']

class OrderFullSerializer(serializers.ModelSerializer):
    items = serializers.SerializerMethodField()
    class Meta:
        model = Order
        fields = '__all__'

    def get_items(self, obj):
        items = obj.orderitem_set.all()
        return OrderItemSerializer(items, many=True).data
