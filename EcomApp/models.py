from django.db import models
from django.contrib.auth.models import User
import uuid
from django.core.validators import MinValueValidator
from django.db.models import CheckConstraint, Q

# Create your models here.

# Models for E-commerce application

# Category model to categorize products
class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
    

# Product model to represent products in the store
class Product(models.Model):
    product_id = models.UUIDField(default=uuid.uuid4,editable=False,unique=True,db_index=True,null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10,decimal_places=2)
    stock = models.IntegerField()

    def __str__(self):
        return self.name
    

class ProductImage(models.Model):
    product = models.ForeignKey('Product', related_name='images', on_delete=models.CASCADE)
    image_url = models.URLField(max_length=200)

    def __str__(self):
        return f"Image for {self.product.name}"
    

# Store model to represent different stores in the marketplace
class Store(models.Model):
    store_id = models.UUIDField(default=uuid.uuid4,unique=True,editable=False,db_index=True, null=True)
    name = models.CharField(max_length=100)
    owner = models.OneToOneField(User,on_delete=models.CASCADE)

    def __str__(self):
        return self.name

# StoreProduct model to represent the relationship between stores and products with price
class StoreProduct(models.Model):
    store = models.ForeignKey(Store,on_delete=models.CASCADE)
    product = models.ForeignKey(Product,on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.product.name} in {self.store.name}"


# Profile model to extend the default User model with additional information
class Profile(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    address = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=20)
    role = models.CharField(max_length=20,default='customer')

    def __str__(self):
        return self.user.username
    

# Cart model to represent a user's shopping cart
class Cart(models.Model):
    cart_id = models.URLField(default=uuid.uuid4,unique=True,editable=False,db_index=True,null=True)
    user = models.OneToOneField(User,on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username}'s Cart"
    
# CartItem model to represent items in the shopping cart
class CartItem(models.Model):
    cart = models.ForeignKey(Cart,on_delete=models.CASCADE,related_name='items')
    product = models.ForeignKey(Product,on_delete=models.CASCADE)
    quantity = models.IntegerField(validators=[MinValueValidator(1)])

    def __str__(self):
        return f"{self.product.name} - {self.quantity}"

    class Meta:
        constraints = [
            models.CheckConstraint(condition=Q(quantity__gte=1), name='quantity_positive')
        ]
    
# Wishlist model to represent products that users have added to their wishlist
class Wishlist(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    product = models.ForeignKey(Product,on_delete=models.CASCADE,null=True, blank=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.product.name}"
    
class OrderStatus(models.TextChoices):
    PENDING = 'PENDING', 'Pending'
    SHIPPED = 'SHIPPED', 'Shipped'
    DELIVERED = 'DELIVERED', 'Delivered'
    CANCELLED = 'CANCELLED', 'Cancelled'

# Order model to represent an order placed by a customer
class Order(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    total_price = models.DecimalField(max_digits=10,decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    order_id = models.UUIDField(default=uuid.uuid4,null=True, editable=False, unique=True,db_index=True)
    status = models.CharField(max_length=20, choices=OrderStatus.choices, default=OrderStatus.PENDING)

    def __str__(self):
        return f"Order {self.order_id} by {self.user.username}"
    
    def set_status(self,new_status):
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

# OrderItem model to represent items/ products in an order
class OrderItem(models.Model):
    order = models.ForeignKey(Order,on_delete=models.CASCADE)
    product = models.ForeignKey(Product,on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10,decimal_places=2)
    seller = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='sold_items',null=True, blank=True)

    def __str__(self):
        return f"{self.product.name} - {self.quantity}"

# Payment Methods to be chosed by the user for purchasing the products 
class PaymentMethod(models.TextChoices):
    CREDIT_CARD = 'CREDIT_CARD', 'Credit_Card'
    KHALTI = 'KHALTI', 'Khalti'
    ESEWA = 'ESEWA', 'eSewa'
    CASH_ON_DELIVERY = 'CASH_ON_DELIVERY', 'Cash_on_Delivery'

# Payment model to represent payment details for an order
class Payment(models.Model):
    order = models.OneToOneField(Order,on_delete=models.CASCADE)
    payment_method = models.CharField(max_length=50, choices=PaymentMethod.choices)
    payment_status = models.CharField(max_length=20)
    transaction_id = models.CharField(max_length=100)
    
    def __str__(self):
        return f"Payment for Order {self.order.order_id}"


# Review model to represent customer reviews for products
class Review(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name='reviews')
    product = models.ForeignKey(Product,on_delete=models.CASCADE,related_name='reviews')
    rating = models.IntegerField() # Add validation for rating (e.g., 1-5)
    comment = models.TextField()

    def __str__(self):
        return f"Review by {self.user.username} for {self.product.name}"

# Conversation room for users(buyers and sellers) to chat with each other
class Conversation(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4,unique=True,editable=False,db_index=True, null=True)
    user1 = models.ForeignKey(User, related_name='conversations_as_user1', on_delete=models.CASCADE)
    user2 = models.ForeignKey(User, related_name='conversations_as_user2', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Conversation between {self.user1.username} and {self.user2.username}"

# Message model to represent messages in a conversation between users
class Message(models.Model):
    conversation = models.ForeignKey(Conversation,related_name='messages', on_delete=models.CASCADE)
    sender = models.ForeignKey(User,on_delete=models.CASCADE, related_name='send_messages')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.sender.username} in {self.conversation}"