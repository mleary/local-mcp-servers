import os 

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

load_and_validate_env(["KROGER_CLIENT_ID", "KROGER_CLIENT_SECRET", "KROGER_REDIRECT_URI"])

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



### testing 

products = kroger.product.search_products(
            term="1% milk",
            location_id=os.getenv("KROGER_STORE_ID"),
            limit=5
            )