import math
from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.postgres.search import TrigramSimilarity
from rapidfuzz import process, fuzz
from .models import Product, CartItem
from .serializers import ProductSerializer, CartItemSerializer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np


# ✅ Get all products with filters & sorting
@api_view(["GET"])
def get_products(request):
    category = request.GET.get("category", "").strip().lower()
    brand = request.GET.get("brand", "").strip().lower()
    sort = request.GET.get("sort", "").strip()

    products = Product.objects.all()

    # Apply category filter
    if category and category != "all categories":
        products = products.filter(category__iexact=category)

    # Apply brand filter
    if brand and brand != "all brands":
        products = products.filter(brand__iexact=brand)

    # Apply sorting
    if sort == "price_asc":
        products = products.order_by("sale_price")
    elif sort == "price_desc":
        products = products.order_by("-sale_price")
    elif sort == "rating_desc":
        products = products.order_by("-rating")

    # Serialize and clean JSON output
    serializer = ProductSerializer(products[:500], many=True)
    serialized_data = _clean_json_floats(serializer.data)

    return Response(serialized_data)


# ✅ Search products with improved fuzzy matching
@api_view(["GET"])
def search_products(request):
    query = request.GET.get("q", "").strip().lower()
    if not query:
        return Response([])

    # Direct matches (case insensitive)
    products = Product.objects.filter(
        product__icontains=query
    ) | Product.objects.filter(
        brand__icontains=query
    ) | Product.objects.filter(
        category__icontains=query
    ) | Product.objects.filter(
        description__icontains=query
    )

    # Use Trigram Similarity to improve search results
    fuzzy_matches = Product.objects.annotate(
        similarity=TrigramSimilarity("product", query)
    ).filter(similarity__gt=0.2).order_by("-similarity")

    # Combine results and remove duplicates
    all_results = list(set(products) | set(fuzzy_matches))

    # Serialize and clean JSON output
    serializer = ProductSerializer(all_results[:50], many=True)
    serialized_data = _clean_json_floats(serializer.data)

    return Response(serialized_data)

@api_view(["GET"])
def get_single_product(request, product_id):
    product = Product.objects.filter(id=product_id).first()
    if not product:
        return Response({"error": "Product not found"}, status=404)

    # Get similar products (Example: based on category)
    similar_products = Product.objects.filter(category=product.category).exclude(id=product.id)[:5]
    
    # Get recommended products (Example: based on brand)
    recommended_products = Product.objects.filter(brand=product.brand).exclude(id=product.id)[:5]

    serializer = ProductSerializer(product)
    similar_serializer = ProductSerializer(similar_products, many=True)
    recommended_serializer = ProductSerializer(recommended_products, many=True)

    return Response({
        "product": serializer.data,
        "similar_products": similar_serializer.data,
        "recommended_products": recommended_serializer.data,
    })



# ✅ Get similar products based on text similarity & category
def _get_similar_products(product):
    all_products = Product.objects.exclude(id=product.id)
    
    # Create a list of descriptions for TF-IDF
    descriptions = [p.description for p in all_products]
    descriptions.insert(0, product.description)

    # Convert text to numerical features using TF-IDF
    vectorizer = TfidfVectorizer(stop_words="english")
    tfidf_matrix = vectorizer.fit_transform(descriptions)

    # Compute cosine similarity between the target product & all others
    similarity_scores = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()

    # Get top 5 most similar products
    similar_indices = similarity_scores.argsort()[-5:][::-1]
    similar_items = [all_products[i] for i in similar_indices]

    serializer = ProductSerializer(similar_items, many=True)
    return _clean_json_floats(serializer.data)


# ✅ Get recommended products based on user behavior & category
def _get_recommended_products(product):
    # Get other products from the same category & brand
    recommendations = Product.objects.filter(category=product.category).exclude(id=product.id)

    # Prioritize top-rated and most-sold products
    recommendations = recommendations.order_by("-rating")[:5]

    serializer = ProductSerializer(recommendations, many=True)
    return _clean_json_floats(serializer.data)


# ✅ Add product to cart
@api_view(["POST"])
def add_to_cart(request):
    product_id = request.data.get("product_id")
    if not product_id:
        return Response({"error": "Product ID is required"}, status=400)

    product = Product.objects.filter(id=product_id).first()
    if not product:
        return Response({"error": "Product not found"}, status=404)

    cart_item, created = CartItem.objects.get_or_create(product=product)
    if not created:
        cart_item.quantity += 1
        cart_item.save()

    return _get_cart_response()


# ✅ Remove product from cart
@api_view(["POST"])
def remove_from_cart(request):
    product_id = request.data.get("product_id")
    if not product_id:
        return Response({"error": "Product ID is required"}, status=400)

    CartItem.objects.filter(product_id=product_id).delete()
    return _get_cart_response()


# ✅ Update cart quantity
@api_view(["POST"])
def update_cart_quantity(request):
    product_id = request.data.get("product_id")
    quantity = request.data.get("quantity")
    if not product_id or quantity is None:
        return Response({"error": "Product ID and quantity are required"}, status=400)

    cart_item = CartItem.objects.filter(product_id=product_id).first()
    if not cart_item:
        return Response({"error": "Product not found in cart"}, status=404)

    cart_item.quantity = max(1, int(quantity))  # Ensure minimum quantity is 1
    cart_item.save()

    return _get_cart_response()


# ✅ Helper function: Clean NaN/Infinity values in JSON response
def _clean_json_floats(data):
    for product in data:
        for key in ["market_price", "sale_price", "rating"]:
            if key in product and isinstance(product[key], float):
                if math.isnan(product[key]) or math.isinf(product[key]):
                    product[key] = None  # Replace NaN/Infinity with None
    return data


# ✅ Helper function: Get cart items response
def _get_cart_response():
    serializer = CartItemSerializer(CartItem.objects.all(), many=True)
    return Response(serializer.data)
