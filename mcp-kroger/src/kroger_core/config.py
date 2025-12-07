from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


def config_dir() -> Path:
    """Return the configuration directory used for token storage."""
    return Path(os.getenv("KROGER_CONFIG_DIR") or Path(os.getenv("XDG_CONFIG_HOME", Path.home() / ".config")) / "kroger")


def ensure_config_dir() -> Path:
    directory = config_dir()
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def client_token_path() -> Path:
    return ensure_config_dir() / "client_token.json"


def user_token_path() -> Path:
    return ensure_config_dir() / "user_token.json"


def resolve_location_id(explicit: str | None = None) -> str | None:
    return explicit or os.getenv("KROGER_STORE_ID")
