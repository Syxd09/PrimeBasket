from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Product, CartItem
from .serializers import ProductSerializer, CartItemSerializer
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

@api_view(['GET'])
def get_products(request):
    category = request.GET.get('category', '').lower()
    brand = request.GET.get('brand', '').lower()
    sort = request.GET.get('sort', '')

    products = Product.objects.all()
    if category and category != 'all categories':
        products = products.filter(category__iexact=category)
    if brand and brand != 'all brands':
        products = products.filter(brand__iexact=brand)
    if sort == 'price_asc':
        products = products.order_by('sale_price')
    elif sort == 'price_desc':
        products = products.order_by('-sale_price')
    elif sort == 'rating_desc':
        products = products.order_by('-rating')

    serializer = ProductSerializer(products[:50], many=True)
    return Response(serializer.data)

@api_view(['GET'])
def search_products(request):
    query = request.GET.get('q', '').lower()
    if not query:
        return Response([])
    
    products = Product.objects.filter(
        product__icontains=query) | Product.objects.filter(
        brand__icontains=query) | Product.objects.filter(
        category__icontains=query) | Product.objects.filter(
        description__icontains=query)
    
    serializer = ProductSerializer(products[:50], many=True)
    return Response(serializer.data)

@api_view(['POST'])
def add_to_cart(request):
    product_id = request.data.get('product_id')
    if not product_id:
        return Response({'error': 'Product ID is required'}, status=400)
    
    product = Product.objects.filter(id=product_id).first()
    if not product:
        return Response({'error': 'Product not found'}, status=404)
    
    cart_item, created = CartItem.objects.get_or_create(product=product)
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    
    serializer = CartItemSerializer(CartItem.objects.all(), many=True)
    return Response(serializer.data)

@api_view(['POST'])
def remove_from_cart(request):
    product_id = request.data.get('product_id')
    if not product_id:
        return Response({'error': 'Product ID is required'}, status=400)
    
    CartItem.objects.filter(product_id=product_id).delete()
    
    serializer = CartItemSerializer(CartItem.objects.all(), many=True)
    return Response(serializer.data)

@api_view(['POST'])
def update_cart_quantity(request):
    product_id = request.data.get('product_id')
    quantity = request.data.get('quantity')
    if not product_id or not quantity:
        return Response({'error': 'Product ID and quantity are required'}, status=400)
    
    cart_item = CartItem.objects.filter(product_id=product_id).first()
    if not cart_item:
        return Response({'error': 'Product not found in cart'}, status=404)
    
    cart_item.quantity = quantity
    cart_item.save()
    
    serializer = CartItemSerializer(CartItem.objects.all(), many=True)
    return Response(serializer.data)