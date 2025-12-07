import os

from dotenv import load_dotenv
from kroger_api.auth import authenticate_user, switch_to_client_credentials
from kroger_api.utils.env import load_and_validate_env

from kroger_core.config import client_token_path, ensure_config_dir, user_token_path

load_dotenv()
ensure_config_dir()

# Direct the Kroger SDK to use stable token locations
os.environ["KROGER_USER_TOKEN_FILE"] = str(user_token_path())
os.environ["KROGER_CLIENT_TOKEN_FILE"] = str(client_token_path())

load_and_validate_env(["KROGER_CLIENT_ID", "KROGER_CLIENT_SECRET", "KROGER_REDIRECT_URI"])

# User auth first (cart.basic:write), then pivot back to client credentials for search
kroger = authenticate_user(scopes="cart.basic:write profile.compact")
kroger, user_token_info, user_token_file = switch_to_client_credentials(kroger, scope="product.compact")
