from django.db import models
from django.utils.timezone import now

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

    class Meta:
        indexes = [
            models.Index(fields=['product']),
            models.Index(fields=['category']),
            models.Index(fields=['brand']),
        ]

class CartItem(models.Model):
    session_key = models.CharField(max_length=40, blank=True, null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True, default=now)

    class Meta:
        unique_together = ('session_key', 'product')
