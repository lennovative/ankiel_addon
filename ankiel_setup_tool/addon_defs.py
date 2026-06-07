"""Load addon catalogue and categories from configs/addons.json."""
from __future__ import annotations

import json
import os

_ADDONS_JSON = os.path.join(os.path.dirname(__file__), "configs", "addons.json")


def _load() -> tuple[dict, dict]:
    with open(_ADDONS_JSON, encoding="utf-8") as f:
        data = json.load(f)
    return data["addons"], data["categories"]


ADDON_CATALOG, CATEGORIES = _load()
