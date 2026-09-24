from products.services.context import (
    build_retrieved_products_context,
)
from products.services.search import (
    search_products,
)

RETRIEVED_PRODUCTS_LIMIT = 10


def handle_product_search(store, query_plan):
    search_results = search_products(
        store=store,
        semantic_query=(query_plan.semantic_query),
        filters=query_plan.filters,
        limit=RETRIEVED_PRODUCTS_LIMIT,
    )

    return build_retrieved_products_context(search_results)


def handle_category_overview(store_categories):
    if not store_categories:
        return "No categories are currently available."

    lines = ["Current store categories:"]

    for category in store_categories:
        lines.append(f"- {category['name']} - {category['description']}")

    return "\n".join(lines)


def handle_broad_catalog_request():
    return (
        "Explain that the shown products are only a small sample of the available catalog "
        "Do not present the sample products as the complete catalog "
        "Explain that the catalog contains many products and categories "
        "Tell the customer that showing the entire catalog at once is not practical "
        "Suggest that the customer ask for a specific product or category "
        "Use the available sample products to give the customer an idea of what is available "
        "Be clear that there are many more products than the ones shown "
        "Encourage the customer to narrow the request to get more relevant products "
        "A more specific request will help find the right products "
        "Only call it the complete catalog when all products have been retrieved. "
    )
