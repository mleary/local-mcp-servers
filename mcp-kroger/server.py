import os
import json

from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv
from kroger_api import KrogerAPI
from kroger_api.token_storage import load_token, save_token
from kroger_api.utils.env import load_and_validate_env

mcp = FastMCP(
    name='kroger-api'
)

# Load environment variables from .env file
load_dotenv()

#load_and_validate_env(["KROGER_CLIENT_ID", "KROGER_CLIENT_SECRET", "KROGER_REDIRECT_URI"])

# Initialize KrogerAPI client
kroger = KrogerAPI()


# Get new token -- could imrpove this to check if token is expired first
token_file = "kroger_token.json"
token_info = load_token(token_file) 

if token_info:
    print("Found existing client token, testing if it's valid...")
    
    # Test if the token is valid
    kroger.client.token_info = token_info
    is_valid = kroger.test_current_token()
    
    if is_valid:
        print("Token is valid, no need to get a new one")
    else:
        print("Token is invalid, getting a new one...")
        token_info = kroger.authorization.get_token_with_client_credentials("product.compact")
        print("New token obtained")
else:
    print("No existing token found, getting a new one...")
    token_info = kroger.authorization.get_token_with_client_credentials("product.compact")
    print("New token obtained")

@mcp.tool()
def search_for_product(search_query: str) -> str:
    products = kroger.product.search_products(
            term=search_query,
            location_id=os.getenv("KROGER_STORE_ID"),
            limit=5
            )
    # Build a JSON-friendly summary of results
    items = []
    for product in products.get("data", []):
        description = product.get("description", "Unknown")
        brand = product.get("brand", "N/A")
        upc = product.get("upc")

        size_val = None
        regular = None
        promo = None
        if "items" in product and product["items"]:
            first_item = product["items"][0]
            size_val = first_item.get("size")
            price = first_item.get("price") or {}
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



# products = kroger.product.search_products(
#             term="1% milk",
#             location_id=os.getenv("KROGER_STORE_ID"),
#             limit=5
#             )