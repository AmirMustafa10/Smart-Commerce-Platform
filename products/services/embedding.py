import os
from google import genai
from google.genai import types
from products.models import Product, ProductEmbedding

EMBEDDING_MODEL = "gemini-embedding-2"
EMBEDDING_DIMENSIONS = 768

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def build_product_embedding_text(product: Product) -> str:
    category_name = product.category.name if product.category_id else ""

    return (
        f"title: {product.name} | "
        f"text: Category: {category_name}. "
        f"Description: {product.description or ''}"
    )


def generate_embedding(text: str) -> list[float]:
    response = client.models.embed_content(
        model=EMBEDDING_MODEL,
        contents=text,
        config=types.EmbedContentConfig(
            output_dimensionality=EMBEDDING_DIMENSIONS,
        ),
    )

    return response.embeddings[0].values


def generate_query_embedding(query: str) -> list[float]:
    formatted_query = f"task: search result | query: {query}"
    return generate_embedding(formatted_query)


def create_or_update_product_embedding(product: Product) -> ProductEmbedding:
    content = build_product_embedding_text(product)
    embedding = generate_embedding(content)

    product_embedding, _ = ProductEmbedding.objects.update_or_create(
        product=product,
        defaults={
            "content": content,
            "embedding": embedding,
            "model_name": EMBEDDING_MODEL,
        },
    )

    return product_embedding
