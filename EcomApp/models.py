from django.db import models
from django.contrib.auth.models import User
import uuid

# Create your models here.

# Models for E-commerce application

# Category model to categorize products
class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
    

# Product model to represent products in the store
class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10,decimal_places=2)
    stock = models.IntegerField()

    def __str__(self):
        return self.name
    

# Store model to represent different stores in the marketplace
class Store(models.Model):
    name = models.CharField(max_length=100)
    owner = models.ForeignKey(User,on_delete=models.CASCADE)

    def __str__(self):
        return self.name

# StoreProduct model to represent the relationship between stores and products with price
class StoreProduct(models.Model):
    store = models.ForeignKey(Store,on_delete=models.CASCADE)
    product = models.ForeignKey(Product,on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10,decimal_places=2)

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
    user = models.ForeignKey(User,on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username}'s Cart"
    
# CartItem model to represent items in the shopping cart
class CartItem(models.Model):
    cart = models.ForeignKey(Cart,on_delete=models.CASCADE)
    product = models.ForeignKey(Product,on_delete=models.CASCADE)
    quantity = models.IntegerField()

    def __str__(self):
        return f"{self.product.name} - {self.quantity}"
    
# WhiteList model to represent products that users have added to their wishlist
class WhiteList(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    product = models.ForeignKey(Product,on_delete=models.CASCADE,null=True, blank=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.product.name}"
    

# Order model to represent an order placed by a customer
class Order(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    total_price = models.DecimalField(max_digits=10,decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    order_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True,db_index=True)

    def __str__(self):
        return f"Order {self.order_id} by {self.user.username}"

# OrderItem model to represent items/ products in an order
class OrderItem(models.Model):
    order = models.ForeignKey(Order,on_delete=models.CASCADE)
    product = models.ForeignKey(Product,on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10,decimal_places=2)

    def __str__(self):
        return f"{self.product.name} - {self.quantity}"

# Payment Methods to be chosed by the user for purchasing the products 
class PaymentMethod(models.TextChoices):
    CREDIT_CARD = 'CREDIT_CARD', 'Credit Card'
    PAYPAL = 'PAYPAL', 'PayPal'
    ESEWA = 'ESEWA', 'eSewa'
    CASH_ON_DELIVERY = 'CASH_ON_DELIVERY', 'Cash on Delivery'

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
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    product = models.ForeignKey(Product,on_delete=models.CASCADE)
    rating = models.IntegerField()
    comment = models.TextField()

    def __str__(self):
        return f"Review by {self.user.username} for {self.product.name}"

# Conversation room for users(buyers and sellers) to chat with each other
class Conversation(models.Model):
    user1 = models.ForeignKey(User, related_name='conversations_as_user1', on_delete=models.CASCADE)
    user2 = models.ForeignKey(User, related_name='conversations_as_user2', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Conversation between {self.user1.username} and {self.user2.username}"

# Message model to represent messages in a conversation between users
class Message(models.Model):
    conversation = models.ForeignKey(Conversation,related_name='messages', on_delete=models.CASCADE)
    sender = models.ForeignKey(User,on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.sender.username} in {self.conversation}"