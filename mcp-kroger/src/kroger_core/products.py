from __future__ import annotations

import json
from typing import Any, Dict, List

from .client import KrogerService


def summarize_products(search_result: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
    """Normalize search results to a concise, JSON-friendly shape."""
    products = search_result.get("data", []) if isinstance(search_result, dict) else []
    items: List[Dict[str, Any]] = []
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

        items.append(
            {
                "description": description,
                "brand": brand,
                "upc": upc,
                "size": size_val,
                "price": {
                    "regular": regular,
                    "promo": promo,
                },
            }
        )

    return {"items": items}


def search_and_summarize(service: KrogerService, term: str, *, limit: int = 5, location_id: str | None = None) -> str:
    results = service.search_products(term=term, limit=limit, location_id=location_id)
    return json.dumps(summarize_products(results))
