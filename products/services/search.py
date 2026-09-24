from decimal import Decimal
from pgvector.django import CosineDistance
from products.models import Category, ProductEmbedding
from products.services.embedding import generate_query_embedding
from products.services.query_planner import SearchFilters


def search_products(store, semantic_query: str, filters: SearchFilters, limit: int = 10):
    queryset = ProductEmbedding.objects.filter(
        product__store=store,
        product__is_active=True,
    )

    # Validate category against the current store.
    if filters.category_id:
        category_exists = Category.objects.filter(
            id=filters.category_id,
            store=store,
        ).exists()

        # Fail closed if Gemini returned an invalid category.
        if not category_exists:
            return ProductEmbedding.objects.none()

        queryset = queryset.filter(
            product__category_id=filters.category_id,
        )

    # Structured price filters.
    if filters.min_price is not None:
        queryset = queryset.filter(product__price__gte=Decimal(str(filters.min_price)))

    if filters.max_price is not None:
        queryset = queryset.filter(product__price__lte=Decimal(str(filters.max_price)))

    # quantity An essential filter, so it will definitely not appear to the customer. A product that is not available
    queryset = queryset.filter(product__stock_quantity__gt=0)

    # Semantic search.
    semantic_query = semantic_query.strip()

    if semantic_query:
        query_embedding = generate_query_embedding(semantic_query)

        queryset = queryset.annotate(
            distance=CosineDistance(
                "embedding",
                query_embedding,
            )
        ).order_by("distance")

    return queryset.select_related(
        "product",
        "product__category",
    )[:limit]
