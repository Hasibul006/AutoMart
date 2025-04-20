from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

class User(AbstractUser):
    ROLE_CHOICES = [
        ('user', 'User'),
        ('admin', 'Admin'),
    ]
    role = models.CharField(max_length=5, choices=ROLE_CHOICES, default='user')
    fullname = models.CharField(max_length=150, default='')

class Category(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50, unique=True)
    image = models.ImageField(upload_to='category_images/', null=True, blank=True)


class Product(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='product_images/', null=True, blank=True)
    description = models.TextField(max_length=500, null=True)
    price = models.DecimalField(max_digits=20, decimal_places=2)
    stock = models.PositiveIntegerField()
    company = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

class Cart(models.Model):
    id = models.AutoField(primary_key=True)
    checkout = models.BooleanField(default=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=0)
    added_at = models.DateTimeField(auto_now_add=True)

    def get_total_price(self):
        return self.product.price * self.quantity
    
    
class Order(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    fullname = models.CharField(max_length=100, default='')
    email = models.EmailField(max_length=100, default='')
    phone = models.CharField(max_length=20, default='')
    address = models.CharField(max_length=200, default='')
    payment_method = models.CharField(max_length=20, default='')
    total_price = models.DecimalField(max_digits=1000, decimal_places=2, default=0)
    ordered_at = models.DateTimeField(auto_now_add=True)

class OrderItem(models.Model):
    id = models.AutoField(primary_key=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=0)
    price = models.DecimalField(max_digits=1000,decimal_places=2, default=0)