import math
from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.core.cache import cache
from django.db.models import Q, F, FloatField
from django.db.models.functions import Coalesce
from django.contrib.postgres.search import TrigramSimilarity
from .models import Product, CartItem
from .serializers import ProductSerializer, CartItemSerializer


def _get_session_key(request):
    if not request.session.session_key:
        request.session.create()
    return request.session.session_key


def _clean_json_floats(data):
    if isinstance(data, list):
        return [_clean_json_floats(v) for v in data]
    if isinstance(data, dict):
        return {k: _clean_json_floats(v) for k, v in data.items()}
    if isinstance(data, float):
        return round(data, 2) if not math.isnan(data) else None
    return data


class ProductPagination(PageNumberPagination):
    page_size = 24
    max_page_size = 100
    page_size_query_param = "page_size"


@api_view(["GET"])
def get_products(request):
    cache_key = f"products_{request.GET.urlencode()}"
    cached = cache.get(cache_key)
    if cached:
        return Response(cached)

    try:
        queryset = Product.objects.all().only(
            "id", "product", "category", "brand", "sale_price", "rating", "discount"
        )

        category = request.GET.get("category")
        if category:
            queryset = queryset.filter(category__iexact=category)

        brand = request.GET.get("brand")
        if brand:
            queryset = queryset.filter(brand__iexact=brand)

        sort_map = {
            "price_asc": "sale_price",
            "price_desc": "-sale_price",
            "rating": "-rating",
            "discount": "-discount",
        }
        sort = request.GET.get("sort")
        if sort in sort_map:
            queryset = queryset.order_by(sort_map[sort])

        paginator = ProductPagination()
        page = paginator.paginate_queryset(queryset, request)

        serializer = ProductSerializer(page, many=True)
        response_data = {
            "count": queryset.count(),
            "next": paginator.get_next_link(),
            "previous": paginator.get_previous_link(),
            "results": _clean_json_floats(serializer.data),
        }

        cache.set(cache_key, response_data, 300)
        return Response(response_data)

    except Exception as e:
        return Response({"error": str(e)}, status=500)


@api_view(["GET"])
def get_single_product(request, product_id):
    cache_key = f"product_{product_id}"
    cached_data = cache.get(cache_key)

    if cached_data:
        return Response(cached_data)

    try:
        product = Product.objects.only(
            "id", "product", "category", "brand", "description", "sale_price", "rating"
        ).get(id=product_id)

        similar = (
            Product.objects.filter(category=product.category)
            .exclude(id=product.id)
            .annotate(similarity=TrigramSimilarity("product", product.product))
            .order_by("-similarity")[:5]
            .only("id", "product", "sale_price", "rating")
        )

        recommended = (
            Product.objects.filter(Q(brand=product.brand) | Q(discount__gte=15))
            .exclude(id=product.id)
            .annotate(score=Coalesce(F("rating"), 0.0) * 2 + F("discount"))
            .order_by("-score")[:5]
            .only("id", "product", "sale_price", "rating", "discount")
        )

        serializer = ProductSerializer(product)
        similar_serializer = ProductSerializer(similar, many=True)
        recommended_serializer = ProductSerializer(recommended, many=True)

        response_data = {
            "product": _clean_json_floats(serializer.data),
            "similar_products": similar_serializer.data,
            "recommended_products": recommended_serializer.data,
        }

        cache.set(cache_key, response_data, 300)
        return Response(response_data)

    except Product.DoesNotExist:
        return Response({"error": "Product not found"}, status=404)


@api_view(["GET"])
def search_products(request):
    query = request.GET.get("q", "").strip().lower()

    if not query:
        return Response({"error": "Search query is required"}, status=400)

    cache_key = f"search_{query}"
    cached_data = cache.get(cache_key)

    if cached_data:
        return Response(cached_data)

    try:
        exact_matches = Product.objects.filter(
            Q(product__icontains=query)
            | Q(category__icontains=query)
            | Q(description__icontains=query)
            | Q(brand__icontains=query)
        )

        fuzzy_matches = (
            Product.objects.annotate(similarity=TrigramSimilarity("product", query))
            .filter(similarity__gt=0.2)
            .order_by("-similarity")
        )

        all_results = list(set(exact_matches) | set(fuzzy_matches))

        serializer = ProductSerializer(all_results[:50], many=True)

        response_data = {
            "query": query,
            "results": serializer.data,
            "count": len(all_results),
        }

        cache.set(cache_key, response_data, 300)
        return Response(response_data)

    except Exception as e:
        return Response({"error": str(e)}, status=500)


@api_view(["GET"])
def get_cart(request):
    session_key = _get_session_key(request)
    cache_key = f"cart_{session_key}"
    cached_data = cache.get(cache_key)

    if cached_data:
        return Response(cached_data)

    try:
        items = CartItem.objects.filter(session_key=session_key).select_related(
            "product"
        )
        serializer = CartItemSerializer(items, many=True)
        response_data = _clean_json_floats(serializer.data)

        cache.set(cache_key, response_data, 300)
        return Response(response_data)

    except Exception as e:
        return Response({"error": str(e)}, status=500)


@api_view(["POST"])
def add_to_cart(request):
    try:
        session_key = _get_session_key(request)
        product_id = int(request.data["product_id"])
        quantity = int(request.data.get("quantity", 1))

        if quantity < 1 or quantity > 10:
            return Response({"error": "Quantity must be between 1-10"}, status=400)

        product = Product.objects.only("id").get(id=product_id)

        item, created = CartItem.objects.get_or_create(
            session_key=session_key, product=product, defaults={"quantity": quantity}
        )

        if not created:
            item.quantity = min(item.quantity + quantity, 10)
            item.save()

        return get_cart(request)

    except (ValueError, KeyError):
        return Response({"error": "Invalid product ID"}, status=400)
    except Product.DoesNotExist:
        return Response({"error": "Product not found"}, status=404)


@api_view(["POST"])
def remove_from_cart(request):
    try:
        session_key = _get_session_key(request)
        product_id = int(request.data["product_id"])
        CartItem.objects.filter(session_key=session_key, product_id=product_id).delete()
        return get_cart(request)

    except (ValueError, KeyError):
        return Response({"error": "Invalid product ID"}, status=400)


@api_view(["POST"])
def update_cart_quantity(request):
    try:
        session_key = _get_session_key(request)
        product_id = int(request.data["product_id"])
        quantity = int(request.data["quantity"])

        if quantity < 1 or quantity > 10:
            return Response({"error": "Quantity must be between 1-10"}, status=400)

        item = CartItem.objects.filter(
            session_key=session_key, product_id=product_id
        ).first()
        if not item:
            return Response({"error": "Product not found in cart"}, status=404)

        item.quantity = quantity
        item.save()
        return get_cart(request)

    except (ValueError, KeyError):
        return Response({"error": "Invalid product ID"}, status=400)
