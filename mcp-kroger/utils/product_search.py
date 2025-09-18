import json


def clean_product_search(search_result):
    """Cleans and formats the product search results from Kroger API call. Simple framework for now, that could break with API changes.
    """
    try:
        # Expect a dict with top-level "data" list from the Kroger API
        products = search_result.get("data", [])

        # Build a JSON-friendly summary of results
        items = []
        for product in products:
            if not isinstance(product, dict):
                continue

            description = product.get("description", "Unknown")
            brand = product.get("brand", "N/A")
            upc = product.get("upc")

            size_val = None
            regular = None
            promo = None
            prod_items = product.get("items") or []
            if isinstance(prod_items, list) and prod_items:
                first_item = prod_items[0]
                if isinstance(first_item, dict):
                    size_val = first_item.get("size")
                    price = first_item.get("price") or {}
                    if isinstance(price, dict):
                        regular = price.get("regular")
                        promo = price.get("promo")

            items.append({
                "description": description,
                "brand": brand,
                "upc": upc,
                "size": size_val,
                "price": {
                    "regular": regular,
                    "promo": promo
                }
            })

        return json.dumps({"items": items})
    except Exception as e:
        print(f"See error, API might have changed: {e}")
        return json.dumps({"items": []})
