from django.db import models
from django.contrib.auth.models import User
import uuid

class OrderStatus(models.TextChoices):
    PENDING = 'PENDING', 'Pending'
    SHIPPED = 'SHIPPED', 'Shipped'
    DELIVERED = 'DELIVERED', 'Delivered'
    CANCELLED = 'CANCELLED', 'Cancelled'

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    order_id = models.UUIDField(default=uuid.uuid4, null=True, editable=False, unique=True, db_index=True)
    status = models.CharField(max_length=20, choices=OrderStatus.choices, default=OrderStatus.PENDING)

    def __str__(self):
        return f"Order {self.order_id} by {self.user.username}"
    
    def set_status(self, new_status):
        allowed_transitions = {
            OrderStatus.PENDING: [OrderStatus.SHIPPED, OrderStatus.CANCELLED],
            OrderStatus.SHIPPED: [OrderStatus.DELIVERED],
            OrderStatus.DELIVERED: [],
            OrderStatus.CANCELLED: []
        }

        if new_status in allowed_transitions.get(self.status, []):
            self.status = new_status
            self.save()
        else:
            raise ValueError("Invalid status transition")

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey('EcomApp.Product', on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    seller = models.ForeignKey('EcomApp.Store', on_delete=models.CASCADE, related_name='sold_items', null=True, blank=True)

    def __str__(self):
        return f"{self.product.name} - {self.quantity}"

class PaymentMethod(models.TextChoices):
    CREDIT_CARD = 'CREDIT_CARD', 'Credit_Card'
    KHALTI = 'KHALTI', 'Khalti'
    ESEWA = 'ESEWA', 'eSewa'
    CASH_ON_DELIVERY = 'CASH_ON_DELIVERY', 'Cash_on_Delivery'

class Payment(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    payment_method = models.CharField(max_length=50, choices=PaymentMethod.choices)
    payment_status = models.CharField(max_length=20)
    transaction_id = models.CharField(max_length=100)
    
    def __str__(self):
        return f"Payment for Order {self.order.order_id}"
