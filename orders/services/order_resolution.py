import re
from dataclasses import dataclass
from products.models import Product
from products.services.query_planner import SearchFilters
from products.services.search import search_products


@dataclass(slots=True)
class ProductResolution:
    product: Product | None
    candidates: list[Product]
    reason: str = ""


def _normalize_text(value: str) -> str:
    """
    Converts text to lowercase, removes symbols and punctuation while keeping Arabic and English letters and numbers, and replaces multiple spaces with one space.
    """

    value = (value or "").casefold()

    value = re.sub(
        r"[^a-z0-9\u0600-\u06ff]+",
        " ",
        value,
    )

    return " ".join(value.split())


def _get_specific_tokens(value: str) -> list[str]:
    """
    Extracts specific tokens such as model numbers, codes, and standalone numbers from the normalized text, while ignoring words made only of letters.
    """

    tokens = _normalize_text(value).split()

    return [
        token
        for token in tokens
        if (re.search(r"[a-z]", token) and re.search(r"\d", token)) or token.isdigit()
    ]


def _build_product_search_text(product: Product) -> str:
    category_name = ""

    if product.category_id:
        category_name = product.category.name or ""

    return _normalize_text(
        " ".join(
            [
                product.name or "",
                product.sku or "",
                product.description or "",
                category_name,
            ]
        )
    )


def _find_exact_product(customer, semantic_query: str) -> Product | None:
    """
    Try deterministic exact matching before semantic search.

    Priority:
    1. Exact SKU
    2. Exact product name
    """

    normalized_query = _normalize_text(semantic_query)

    if not normalized_query:
        return None

    product = Product.objects.filter(
        store_id=customer.store_id,
        is_active=True,
        sku__iexact=semantic_query.strip(),
    ).first()

    if product:
        return product

    product = Product.objects.filter(
        store_id=customer.store_id,
        is_active=True,
        name__iexact=semantic_query.strip(),
    ).first()

    if product:
        return product

    normalized_products = Product.objects.filter(
        store_id=customer.store_id,
        is_active=True,
    ).select_related("category")

    for product in normalized_products:
        if _normalize_text(product.name) == normalized_query:
            return product

    return None


def _resolve_from_candidates(semantic_query: str, results) -> ProductResolution:
    """
    Refines the products found by semantic search to find one exact product match.

    It uses simple rules in this order:

    1. Returns the result directly if there are 0 or 1 products.
    2. Checks for exact or partial matches in the product name or SKU.
    3. Checks that important details, such as model numbers or storage capacity, match.
    4. If there is still more than one possible match, returns all candidates.
    """

    products = [result.product for result in results]

    if not products:
        return ProductResolution(
            product=None,
            candidates=[],
            reason=("No matching product was found."),
        )

    if len(products) == 1:
        return ProductResolution(
            product=products[0],
            candidates=products,
        )

    normalized_query = _normalize_text(semantic_query)

    # -----------------------------------------------------
    # Strong full-text match against product name / SKU.
    # -----------------------------------------------------

    strong_matches = []

    for product in products:
        normalized_name = _normalize_text(product.name)

        normalized_sku = _normalize_text(product.sku or "")

        if normalized_query and normalized_query in normalized_name:
            strong_matches.append(product)
            continue

        if normalized_query and normalized_query == normalized_sku:
            strong_matches.append(product)

    if len(strong_matches) == 1:
        return ProductResolution(
            product=strong_matches[0],
            candidates=strong_matches,
        )

    # -----------------------------------------------------
    # Specific model/storage tokens.
    #
    # Example:
    # "Samsung A25 128GB"
    #
    # Specific tokens:
    # A25, 128GB
    # -----------------------------------------------------

    specific_tokens = _get_specific_tokens(semantic_query)

    if specific_tokens:

        token_matches = []

        for product in products:
            searchable_text = _build_product_search_text(product)

            if all(token in searchable_text for token in specific_tokens):
                token_matches.append(product)

        if len(token_matches) == 1:
            return ProductResolution(
                product=token_matches[0],
                candidates=token_matches,
            )

    return ProductResolution(
        product=None,
        candidates=products,
        reason=("Multiple products may match the customer's request."),
    )


def resolve_product_for_order(
    customer, semantic_query: str, filters: SearchFilters | None = None, limit: int = 5
) -> ProductResolution:
    """
    Resolve a customer product request into one concrete Product.

    Resolution order:

        Exact SKU / Name
            ↓
        Hybrid semantic search
            ↓
        Strong textual matching
            ↓
        Specific model/storage token matching
            ↓
        Clarification if still ambiguous
    """

    semantic_query = (semantic_query or "").strip()

    if not semantic_query:
        return ProductResolution(
            product=None,
            candidates=[],
            reason=("No product description was provided."),
        )

    exact_product = _find_exact_product(
        customer=customer,
        semantic_query=semantic_query,
    )

    if exact_product:
        return ProductResolution(
            product=exact_product,
            candidates=[exact_product],
        )

    if filters is None:
        filters = SearchFilters()

    search_results = list(
        search_products(
            store=customer.store,
            semantic_query=semantic_query,
            filters=filters,
            limit=limit,
        )
    )

    return _resolve_from_candidates(
        semantic_query=semantic_query,
        results=search_results,
    )
