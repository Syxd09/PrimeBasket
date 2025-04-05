from django.db import models

class Product(models.Model):
    id = models.AutoField(primary_key=True)
    product = models.CharField(max_length=255)
    category = models.CharField(max_length=100)
    sub_category = models.CharField(max_length=100, blank=True, null=True)
    brand = models.CharField(max_length=100)
    type = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    market_price = models.DecimalField(max_digits=10, decimal_places=2)
    sale_price = models.DecimalField(max_digits=10, decimal_places=2)
    rating = models.FloatField(blank=True, null=True)
    discount = models.FloatField(blank=True, null=True)

class CartItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)