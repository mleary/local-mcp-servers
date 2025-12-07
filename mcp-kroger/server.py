import os
import json
from pathlib import Path

from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv
import kroger_api.token_storage as token_storage

# Import your new MCP-compatible wrapper
from utils.kroger_mcp_api import MCPKrogerAPI
from utils.product_search import clean_product_search

mcp = FastMCP(
    name='kroger-api'
)


# Load environment variables from .env file
load_dotenv()

# Initialize the MCP-compatible Kroger API wrapper
kroger_wrapper = MCPKrogerAPI()

# The wrapper handles token management internally, so we just need to get the initial token
print("Initializing Kroger API with MCP-compatible token storage...")

try:
    # Try to get a client credentials token
    token_info = kroger_wrapper.api.authorization.get_token_with_client_credentials("product.compact")
    print("Successfully obtained token for Kroger API")
except Exception as e:
    print(f"Warning: Could not obtain initial token: {e}")
    print("Token will be obtained on first API call")

# Access the actual API through the wrapper
kroger = kroger_wrapper.api

DEFAULT_USER_TOKEN_FILENAME = ".kroger_token_user.json"


def _token_file_candidates():
    """Ordered list of places to look for the user token file."""
    env_path = os.getenv("KROGER_USER_TOKEN_FILE")
    repo_root = Path(__file__).resolve().parent

    candidates = []
    if env_path:
        candidates.append(Path(env_path).expanduser())

    candidates.extend([
        repo_root / DEFAULT_USER_TOKEN_FILENAME,
        Path.cwd() / DEFAULT_USER_TOKEN_FILENAME,
        kroger_wrapper.token_dir / DEFAULT_USER_TOKEN_FILENAME,
    ])

    return candidates


def _resolve_user_token_file():
    """Pick the first existing token path, or fall back to the highest-priority guess."""
    candidates = _token_file_candidates()
    for path in candidates:
        if path.is_file():
            return path
    return candidates[0] if candidates else Path.cwd() / DEFAULT_USER_TOKEN_FILENAME

@mcp.tool()
def product_search_tool(query: str, limit: int = 5) -> str:
    """Search for products using the Kroger API based on user query. Defaults to returning top 5 results. Results are a JSON string with details such as description, brand, upc, size, and price."""
    try:
        products = kroger.product.search_products(
            term=query,
            location_id=os.getenv("KROGER_STORE_ID"),
            limit=limit
        )
        return clean_product_search(products)
    except Exception as e:
        # If token expired, try to refresh
        try:
            print(f"API call failed, attempting to refresh token: {e}")
            token_info = kroger.authorization.get_token_with_client_credentials("product.compact")
            # Retry the search
            products = kroger.product.search_products(
                term=query,
                location_id=os.getenv("KROGER_STORE_ID"),
                limit=limit
            )
            return clean_product_search(products)
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
    resolved_location = os.getenv("KROGER_STORE_ID") or location_id
    if not resolved_location:
        return json.dumps({"error": "Missing location_id and KROGER_STORE_ID is not set."})

    # Load user token for cart operations
    token_path = _resolve_user_token_file()
    user_token = token_storage.load_token(str(token_path))
    if not user_token:
        return json.dumps({
            "error": "User token not found. Run `python utils/auth.py` to authorize with cart.basic:write.",
            "token_file": str(token_path),
            "searched_paths": [str(p) for p in _token_file_candidates()]
        })

    kroger.client.token_file = str(token_path)
    kroger.client.token_info = user_token

    payload_items = [{
        "upc": upc,
        "quantity": qty_int,
        "modality": modality_clean
    }]

    def _attempt_add():
        return kroger.cart.add_to_cart(payload_items)

    try:
        _attempt_add()
        return json.dumps({
            "status": "success",
            "upc": upc,
            "quantity": qty_int,
            "modality": modality_clean,
            "location_id": resolved_location
        })
    except Exception as e:
        # Attempt token refresh once if possible
        refresh_token = user_token.get("refresh_token") if isinstance(user_token, dict) else None
        if refresh_token:
            try:
                kroger.authorization.refresh_token(refresh_token)
                kroger.client.token_info = token_storage.load_token(str(token_path)) or kroger.client.token_info
                _attempt_add()
                return json.dumps({
                    "status": "success",
                    "upc": upc,
                    "quantity": qty_int,
                    "modality": modality_clean,
                    "location_id": resolved_location,
                    "note": "Token was refreshed before adding to cart."
                })
            except Exception as retry_error:
                return json.dumps({
                    "error": f"Failed to add to cart after refresh: {retry_error}",
                    "details": str(e)
                })
        return json.dumps({
            "error": f"Failed to add to cart: {e}"
        })

# Start the server
if __name__ == "__main__":
    mcp.run()
