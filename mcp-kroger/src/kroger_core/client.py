from __future__ import annotations

from kroger_api import KrogerAPI

from . import config
from .tokens import apply_token_path


class KrogerService:
    """Shared Kroger API facade usable by MCP tools and CLI commands."""

    def __init__(self):
        self.api = KrogerAPI()

    def ensure_client_credentials(self, scope: str = "product.compact") -> None:
        client_token = config.client_token_path()
        apply_token_path(self.api, client_token)
        client_token.parent.mkdir(parents=True, exist_ok=True)
        self.api.authorization.get_token_with_client_credentials(scope)

    def search_products(self, term: str, *, limit: int = 5, location_id: str | None = None):
        self.ensure_client_credentials()
        resolved_location = config.resolve_location_id(location_id)
        return self.api.product.search_products(term=term, location_id=resolved_location, limit=limit)

    def add_to_cart(
        self,
        *,
        upc: str,
        quantity: int = 1,
        modality: str = "PICKUP",
        location_id: str | None = None,
    ) -> None:
        user_token_file = config.user_token_path()
        token_info = apply_token_path(self.api, user_token_file)
        if not token_info:
            raise RuntimeError(
                "User token not found. Run `python utils/auth.py` or the CLI auth flow to generate cart credentials."
            )

        resolved_location = config.resolve_location_id(location_id)
        payload_items = [
            {
                "upc": upc,
                "quantity": quantity,
                "modality": modality,
            }
        ]

        def _attempt():
            return self.api.cart.add_to_cart(payload_items)

        try:
            _attempt()
            return
        except Exception as initial_error:
            refresh_token = token_info.get("refresh_token") if isinstance(token_info, dict) else None
            if not refresh_token:
                raise
            try:
                self.api.authorization.refresh_token(refresh_token)
                apply_token_path(self.api, user_token_file)
                _attempt()
            except Exception as retry_error:
                raise RuntimeError(f"Failed to add to cart after refresh: {retry_error}") from initial_error
