import json
import os
from typing import List, Dict, Any, Optional

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

# Initialize MCP server
mcp = FastMCP(name='kroger-grocery-helper')

# Load environment variables from .env file
load_dotenv()

# Configuration
STORE_ID = os.getenv("KROGER_STORE_ID", "70100146")  # Default store ID
CONTEXT_FILE_PATH = os.getenv("CONTEXT_FILE_PATH", "./grocery_context.json")

# Mock grocery database - in a real implementation, this would be API calls
MOCK_GROCERY_DATABASE = {
    "milk": [
        {"id": "1001", "name": "Great Value 1% Lowfat Milk", "size": "1 gallon", "price": 3.28, "brand": "Great Value"},
        {"id": "1002", "name": "Great Value 2% Reduced Fat Milk", "size": "1 gallon", "price": 3.28, "brand": "Great Value"},
        {"id": "1003", "name": "Great Value Whole Milk", "size": "1 gallon", "price": 3.28, "brand": "Great Value"},
        {"id": "1004", "name": "Horizon Organic 1% Lowfat Milk", "size": "1/2 gallon", "price": 4.98, "brand": "Horizon"},
    ],
    "bread": [
        {"id": "2001", "name": "Wonder Bread Classic White", "size": "20 oz", "price": 1.98, "brand": "Wonder"},
        {"id": "2002", "name": "Nature's Own 100% Whole Wheat", "size": "20 oz", "price": 2.78, "brand": "Nature's Own"},
        {"id": "2003", "name": "Dave's Killer Bread 21 Whole Grains", "size": "27 oz", "price": 4.98, "brand": "Dave's Killer"},
    ],
    "eggs": [
        {"id": "3001", "name": "Great Value Large White Eggs", "size": "12 count", "price": 2.32, "brand": "Great Value"},
        {"id": "3002", "name": "Eggland's Best Large White Eggs", "size": "12 count", "price": 3.98, "brand": "Eggland's Best"},
        {"id": "3003", "name": "Organic Valley Large Brown Eggs", "size": "12 count", "price": 5.48, "brand": "Organic Valley"},
    ],
    "bananas": [
        {"id": "4001", "name": "Bananas", "size": "per lb", "price": 0.58, "brand": "Fresh"},
        {"id": "4002", "name": "Organic Bananas", "size": "per lb", "price": 0.98, "brand": "Organic"},
    ],
    "apples": [
        {"id": "5001", "name": "Gala Apples", "size": "3 lb bag", "price": 3.98, "brand": "Fresh"},
        {"id": "5002", "name": "Honeycrisp Apples", "size": "3 lb bag", "price": 5.98, "brand": "Fresh"},
        {"id": "5003", "name": "Granny Smith Apples", "size": "3 lb bag", "price": 3.98, "brand": "Fresh"},
    ]
}

# Cart to store items
shopping_cart = []

def load_context_mapping() -> Dict[str, str]:
    """Load context mapping from JSON file."""
    try:
        if os.path.exists(CONTEXT_FILE_PATH):
            with open(CONTEXT_FILE_PATH, 'r') as f:
                return json.load(f)
        else:
            # Default context mapping
            default_context = {
                "milk": "1% milk",
                "butter": "unsalted butter",
                "cheese": "cheddar cheese",
                "yogurt": "plain greek yogurt",
                "chicken": "boneless skinless chicken breast",
                "ground beef": "80/20 ground beef",
                "rice": "white rice",
                "pasta": "spaghetti pasta",
                "oil": "olive oil",
                "salt": "table salt"
            }
            # Create the file with default values
            with open(CONTEXT_FILE_PATH, 'w') as f:
                json.dump(default_context, f, indent=2)
            return default_context
    except Exception as e:
        print(f"Error loading context mapping: {e}")
        return {}

def apply_context(item: str, context_mapping: Dict[str, str]) -> str:
    """Apply context mapping to transform generic item names to specific ones."""
    return context_mapping.get(item.lower(), item)

def search_products(query: str) -> List[Dict[str, Any]]:
    """Search for products in the mock database."""
    query = query.lower().strip()
    results = []
    
    # Direct key match
    if query in MOCK_GROCERY_DATABASE:
        results.extend(MOCK_GROCERY_DATABASE[query])
    
    # Partial matching
    for category, products in MOCK_GROCERY_DATABASE.items():
        if query in category or category in query:
            results.extend(products)
        else:
            # Search within product names
            for product in products:
                if query in product["name"].lower():
                    results.append(product)
    
    # Remove duplicates
    seen = set()
    unique_results = []
    for product in results:
        if product["id"] not in seen:
            seen.add(product["id"])
            unique_results.append(product)
    
    return unique_results

@mcp.tool()
def search_grocery_items(items: List[str]) -> str:
    """
    Search for grocery items at the configured Kroger store.
    
    Args:
        items: List of grocery items to search for
        
    Returns:
        JSON string containing search results for each item
    """
    try:
        context_mapping = load_context_mapping()
        results = {}
        
        for item in items:
            # Apply context mapping
            specific_item = apply_context(item, context_mapping)
            
            # Search for products
            products = search_products(specific_item)
            
            results[item] = {
                "search_term": specific_item,
                "products_found": len(products),
                "products": products[:5]  # Limit to top 5 results
            }
        
        return json.dumps(results, indent=2)
        
    except Exception as e:
        return json.dumps({"error": str(e)})

@mcp.tool()
def add_to_cart(product_id: str, quantity: int = 1) -> str:
    """
    Add a specific product to the shopping cart.
    
    Args:
        product_id: The ID of the product to add
        quantity: Number of items to add (default: 1)
        
    Returns:
        JSON string confirming the addition
    """
    try:
        # Find the product in our database
        product = None
        for category, products in MOCK_GROCERY_DATABASE.items():
            for p in products:
                if p["id"] == product_id:
                    product = p.copy()
                    break
            if product:
                break
        
        if not product:
            return json.dumps({"error": f"Product with ID {product_id} not found"})
        
        # Add quantity to product info
        product["quantity"] = quantity
        product["total_price"] = round(product["price"] * quantity, 2)
        
        # Check if product already in cart
        for item in shopping_cart:
            if item["id"] == product_id:
                item["quantity"] += quantity
                item["total_price"] = round(item["price"] * item["quantity"], 2)
                return json.dumps({
                    "success": True,
                    "message": f"Updated quantity for {product['name']}",
                    "new_quantity": item["quantity"],
                    "total_price": item["total_price"]
                })
        
        # Add new item to cart
        shopping_cart.append(product)
        
        return json.dumps({
            "success": True,
            "message": f"Added {quantity}x {product['name']} to cart",
            "item": product
        })
        
    except Exception as e:
        return json.dumps({"error": str(e)})

@mcp.tool()
def view_cart() -> str:
    """
    View current shopping cart contents.
    
    Returns:
        JSON string containing cart contents and total
    """
    try:
        if not shopping_cart:
            return json.dumps({"message": "Cart is empty", "items": [], "total": 0})
        
        total = sum(item["total_price"] for item in shopping_cart)
        
        return json.dumps({
            "items": shopping_cart,
            "item_count": len(shopping_cart),
            "total_items": sum(item["quantity"] for item in shopping_cart),
            "total_price": round(total, 2)
        }, indent=2)
        
    except Exception as e:
        return json.dumps({"error": str(e)})

@mcp.tool()
def clear_cart() -> str:
    """
    Clear all items from the shopping cart.
    
    Returns:
        JSON string confirming cart is cleared
    """
    try:
        global shopping_cart
        items_removed = len(shopping_cart)
        shopping_cart = []
        
        return json.dumps({
            "success": True,
            "message": f"Cleared {items_removed} items from cart",
            "cart": []
        })
        
    except Exception as e:
        return json.dumps({"error": str(e)})

@mcp.tool()
def update_context_mapping(item: str, specific_description: str) -> str:
    """
    Update the context mapping for grocery items.
    
    Args:
        item: Generic item name (e.g., "milk")
        specific_description: Specific description (e.g., "1% milk")
        
    Returns:
        JSON string confirming the update
    """
    try:
        context_mapping = load_context_mapping()
        context_mapping[item.lower()] = specific_description
        
        with open(CONTEXT_FILE_PATH, 'w') as f:
            json.dump(context_mapping, f, indent=2)
        
        return json.dumps({
            "success": True,
            "message": f"Updated context mapping: '{item}' -> '{specific_description}'"
        })
        
    except Exception as e:
        return json.dumps({"error": str(e)})

@mcp.tool()
def view_context_mapping() -> str:
    """
    View current context mapping for grocery items.
    
    Returns:
        JSON string containing all context mappings
    """
    try:
        context_mapping = load_context_mapping()
        return json.dumps(context_mapping, indent=2)
        
    except Exception as e:
        return json.dumps({"error": str(e)})

@mcp.tool()
def get_store_info() -> str:
    """
    Get information about the configured Kroger store.
    
    Returns:
        JSON string containing store information
    """
    return json.dumps({
        "store_id": STORE_ID,
        "store_name": "Kroger Marketplace",
        "address": "123 Main St, Anytown, USA",
        "phone": "(555) 123-4567",
        "hours": "6:00 AM - 12:00 AM daily"
    })

if __name__ == "__main__":
    mcp.run()