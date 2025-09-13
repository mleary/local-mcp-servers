# Kroger MCP Server

A Model Context Protocol (MCP) server that provides grocery shopping functionality for Kroger stores. This server allows you to search for grocery items and manage a shopping cart.

## Features

- **Search Grocery Items**: Search for products across different categories
- **Shopping Cart Management**: Add items to cart, view cart contents, and clear cart
- **Store Configuration**: Configure your preferred Kroger store
- **Mock Implementation**: Uses mock data for initial development and testing

## Setup

1. **Install Dependencies**:
   ```bash
   cd mcp-kroger
   pip install -r requirements.txt
   ```

2. **Configuration**:
   ```bash
   cp .env.example .env
   # Edit .env with your store preferences
   ```

3. **Run the Server**:
   ```bash
   python server.py
   ```

## Available Tools

### Core Shopping Tools

- **`search_grocery_items(items: List[str])`**: Search for grocery items
- **`add_to_cart(product_id: str, quantity: int)`**: Add products to shopping cart
- **`view_cart()`**: View current cart contents and total
- **`clear_cart()`**: Remove all items from cart

### Store Information

- **`get_store_info()`**: Get information about the configured store

## Example Usage

1. **Search for items**:
   ```json
   search_grocery_items(["milk", "bread", "eggs"])
   ```

2. **Add items to cart**:
   ```json
   add_to_cart("1001", 2)  // Add 2 gallons of milk
   ```

3. **View cart**:
   ```json
   view_cart()
   ```

## Integration with Claude Desktop

Add this configuration to your Claude Desktop MCP settings:

```json
{
  "mcpServers": {
    "kroger-grocery-helper": {
      "command": "/path/to/python",
      "args": ["/path/to/mcp-kroger/server.py"],
      "transport": "stdio"
    }
  }
}
```

## Future Enhancements

- Integration with actual Kroger API
- Real-time pricing and availability
- Store location services
- Order placement functionality
- Nutritional information
- Recipe-based shopping lists

## Development Notes

This is currently a mock implementation designed for iterative development. The mock grocery database includes common items across several categories to demonstrate the functionality.