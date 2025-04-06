import os
import pandas as pd
from django.core.management.base import BaseCommand
from shop.models import Product

class Command(BaseCommand):
    help = "Load products from CSV"

    def handle(self, *args, **kwargs):
        # Get the directory of this script
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        
        # Construct the path to the CSV file (must be inside the repo)
        csv_file_path = os.path.join(BASE_DIR, "datab.csv")

        # Check if file exists before proceeding
        if not os.path.exists(csv_file_path):
            self.stderr.write(self.style.ERROR(f"CSV file not found: {csv_file_path}"))
            return

        # Load the CSV file
        df = pd.read_csv(csv_file_path, encoding="utf-8")

        # Insert products into the database
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
                rating=row.get("rating", None),
            )

        self.stdout.write(self.style.SUCCESS("Successfully loaded products"))
