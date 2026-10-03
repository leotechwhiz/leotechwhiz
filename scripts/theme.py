"""Shared theme and profile loader for Leo's profile README generators."""

import json
from pathlib import Path

# Paths
REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = REPO_ROOT / "data" / "profile.json"


def load_config():
    """Load the centralized profile.json containing theme and profile data."""
    if not DATA_PATH.exists():
        raise FileNotFoundError(f"Configuration file not found at: {DATA_PATH}")
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


CONFIG = load_config()
THEME = CONFIG.get("theme", {})
PROFILE = CONFIG.get("profile", {})
