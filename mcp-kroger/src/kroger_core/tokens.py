from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from kroger_api.token_storage import load_token, save_token


def apply_token_path(api, token_path: Path) -> Dict[str, Any] | None:
    """Point the Kroger API client at the desired token file and hydrate in-memory token info."""
    api.client.token_file = str(token_path)
    token_info = load_token(str(token_path))
    if token_info:
        api.client.token_info = token_info
    return token_info


def persist_token(api, token_path: Path) -> Dict[str, Any] | None:
    """Persist the current token_info to disk if present."""
    token_info = getattr(api.client, "token_info", None)
    if token_info:
        save_token(token_info, str(token_path))
    return token_info
