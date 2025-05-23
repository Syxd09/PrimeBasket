from django.urls import path
from .views import get_products, search_products, add_to_cart, remove_from_cart, update_cart_quantity

urlpatterns = [
    path('products/', get_products),
    path('search/', search_products),
    path('cart/add/', add_to_cart),
    path('cart/remove/', remove_from_cart),
    path('cart/update/', update_cart_quantity),
]