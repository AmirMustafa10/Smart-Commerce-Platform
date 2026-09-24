def build_retrieved_products_context(results) -> str:
    results = list(results)

    if not results:
        return "No matching products were found."

    products = []

    for index, result in enumerate(results, start=1):
        product = result.product

        category_name = product.category.name if product.category_id else "Unknown"

        product_data = [
            f"Product {index}:",
            f"Name: {product.name}",
            f"Category: {category_name}",
            f"Price: {product.price}",
            f"Discounted price: {product.final_price or 'None'}",
            f"Stock quantity: {product.stock_quantity}",
            f"Description: {product.description or 'No description'}",
        ]

        products.append("\n".join(product_data))

    return "\n\n".join(products)
