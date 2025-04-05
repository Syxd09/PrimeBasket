import pandas as pd
from django.core.management.base import BaseCommand
from shop.models import Product

class Command(BaseCommand):
    help = "Load products from CSV"

    def handle(self, *args, **kwargs):
        df = pd.read_csv('d:/Python/Django_Project/Prime_basket_app_with_matheen/PrimeBasket/djangojwt/shop/management/commands/datab.csv', encoding='utf-8')
        for _, row in df.iterrows():
            Product.objects.create(
                category=row.get("category", ""),
                sub_category=row.get("sub_category", ""),
                brand=row.get("brand", ""),
                product=row.get("product", ""),
                type=row.get("type", ""),
                description=row.get("description", ""),
                market_price=row.get("market_price", 0),
                sale_price=row.get("sale_price", 0),
                rating=row.get("rating", None)
            )
        self.stdout.write(self.style.SUCCESS("Successfully loaded products"))
