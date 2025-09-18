import os
import sys
import json

from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv

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


# Start the server
if __name__ == "__main__":
    mcp.run()