import json
import sys
from pathlib import Path

from mcp.server.fastmcp import FastMCP
from kroger_api.token_storage import load_token

sys.path.append(str(Path(__file__).resolve().parent / "src"))

from kroger_core.client import KrogerService
from kroger_core.config import resolve_location_id, user_token_path
from kroger_core.products import search_and_summarize

mcp = FastMCP(
    name='kroger-api'
)


# Initialize a shared Kroger service for MCP tools
kroger_service = KrogerService()
try:
    kroger_service.ensure_client_credentials()
    print("Successfully obtained token for Kroger API")
except Exception as e:
    print(f"Warning: Could not obtain initial token: {e}")
    print("Token will be obtained on first API call")

@mcp.tool()
def product_search_tool(query: str, limit: int = 5) -> str:
    """Search for products using the Kroger API based on user query. Defaults to returning top 5 results. Results are a JSON string with details such as description, brand, upc, size, and price."""
    try:
        return search_and_summarize(kroger_service, query, limit=limit, location_id=resolve_location_id())
    except Exception as retry_error:
        return json.dumps({
            "error": f"Failed to search products: {str(retry_error)}",
            "query": query
        })

@mcp.tool()
def add_to_cart_tool(upc: str, quantity: int = 1, modality: str = "PICKUP", location_id: str = None) -> str:
    """Add an item to the authenticated user's Kroger cart. Requires prior user auth (cart.basic:write)."""
    # Basic validation
    if not upc or not isinstance(upc, str):
        return json.dumps({"error": "Invalid UPC provided.", "upc": upc})
    try:
        qty_int = int(quantity)
    except Exception:
        return json.dumps({"error": "Quantity must be an integer.", "quantity": quantity})
    if qty_int < 1:
        return json.dumps({"error": "Quantity must be at least 1.", "quantity": quantity})
    
    modality_clean = (modality or "").strip().upper()
    allowed_modalities = {"PICKUP", "DELIVERY"}
    if modality_clean not in allowed_modalities:
        return json.dumps({
            "error": "Invalid modality. Use PICKUP or DELIVERY.",
            "modality": modality
        })

    # Location: prefer env (consistent with product search), fallback to provided location_id
    resolved_location = resolve_location_id(location_id)
    if not resolved_location:
        return json.dumps({"error": "Missing location_id and KROGER_STORE_ID is not set."})

    # Load user token for cart operations
    token_file = user_token_path()
    user_token = load_token(str(token_file))
    if not user_token:
        return json.dumps({
            "error": "User token not found. Run `python utils/auth.py` to authorize with cart.basic:write.",
            "token_file": str(token_file)
        })

    try:
        kroger_service.add_to_cart(
            upc=upc,
            quantity=qty_int,
            modality=modality_clean,
            location_id=resolved_location,
        )
        return json.dumps({
            "status": "success",
            "upc": upc,
            "quantity": qty_int,
            "modality": modality_clean,
            "location_id": resolved_location
        })
    except Exception as e:
        return json.dumps({
            "error": f"Failed to add to cart: {e}"
        })

# Start the server
if __name__ == "__main__":
    mcp.run()
