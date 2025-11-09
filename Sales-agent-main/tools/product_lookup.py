def lookup_product(query: str):
    products = {
        "detergent": {"price": 120, "stock": 45},
        "shampoo": {"price": 85, "stock": 23},
        "soap": {"price": 35, "stock": 100}
    }

    for name, info in products.items():
        if name in query.lower():
            return f"{name.capitalize()} - ₹{info['price']} (Stock: {info['stock']})"
    return "Product not found."
