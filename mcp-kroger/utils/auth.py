from dotenv import load_dotenv
from kroger_api import KrogerAPI
from kroger_api.auth import authenticate_user, switch_to_client_credentials
from kroger_api.utils.env import load_and_validate_env

load_and_validate_env(["KROGER_CLIENT_ID", "KROGER_CLIENT_SECRET", "KROGER_REDIRECT_URI"])

kroger = authenticate_user(scopes="cart.basic:write profile.compact")

kroger, user_token_info, user_token_file = switch_to_client_credentials(kroger, scope="product.compact")