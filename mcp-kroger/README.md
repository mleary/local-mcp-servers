
## mcp-kroger

A simple MCP server for Kroger product search and grocery tools. This subdirectory contains the MCP server code for interacting with Kroger's API, designed to be used as a backend for local MCP workflows or with compatible front-end clients.

![MCP Kroger Example Screenshot](assets/mcp-kroger-example.png)

* Screenshot from a sample product search.

## Features
- `search_products(query)`: Search for products by keyword.


## Requirements
- Python `3.12` (see `.python-version` if present).
- Kroger API credentials stored locally (not committed).
- Package manager: `uv` (preferred) or `pip`.

## Quick Start

1. **Install Python 3.12**  
	(Check `.python-version` for the required version.)

2. **Set up Kroger API Credentials**  
	> **Note:** You will need to register for Kroger API access and obtain your client ID and client secret. Store credentials securely and do not commit them.

	Run:
	```sh
	python utils/auth.py
	```
	This creates your local credentials file (should be .gitignored).

3. **Configure Environment**  
	- Copy `.env.example` to `.env` (if provided)
	- Set your values for:
	  - `KROGER_CLIENT_ID=your_client_id`
	  - `KROGER_CLIENT_SECRET=your_client_secret`
	  - `ZIP_CODE=your_zip_code`

4. **Install Dependencies**  
	- Preferred:
	  ```sh
	  uv sync
	  ```
	- Or fallback:
	  ```sh
	  pip install -r requirements.txt
	  ```

5. **Run the Server**  
	```sh
	python server.py
	```

## Configuration
- API credentials and zip code are set in your `.env` file.
- You can override by passing arguments to the tools or by editing `.env`.


## Project Files
- `server.py`: Main server
- `utils/auth.py`: Kroger API authentication helper
- `utils/product_search.py`: Product search logic
- `utils/kroger_mcp_api.py`: Kroger MCP API integration
- `.env.example`: Example env file (if present)

## Troubleshooting
- **Missing credentials**: Check `.env` and your credentials file.
- **Token expired**: Run `python utils/auth.py` again.

## TODO
* this is basic functionality, need to add ability to put items in cart
* Improve documentation and error handling