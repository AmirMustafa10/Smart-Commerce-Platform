from celery import shared_task
from products.models import Product, ProductEmbedding
from products.services.embedding import (
    EMBEDDING_MODEL,
    build_product_embedding_text,
    generate_embedding,
)


@shared_task
def sync_product_embedding_task(product_id):
    """
    Generate or update the embedding for a Product.

    This task is triggered after a Product is successfully saved.
    """

    product = Product.objects.select_related("category").filter(pk=product_id).first()

    if not product:
        return "Product not found"

    content = build_product_embedding_text(product)

    existing_embedding = ProductEmbedding.objects.filter(product_id=product_id).first()

    # Avoid unnecessary Gemini API calls when the semantic
    # content and embedding model have not changed.
    if (
        existing_embedding
        and existing_embedding.model_name == EMBEDDING_MODEL
        and existing_embedding.content == content
    ):
        return "Embedding already up to date"

    embedding = generate_embedding(content)

    ProductEmbedding.objects.update_or_create(
        product=product,
        defaults={
            "content": content,
            "embedding": embedding,
            "model_name": EMBEDDING_MODEL,
        },
    )

    return "Embedding synchronized"
