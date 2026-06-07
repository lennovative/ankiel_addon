"""Load town/university config files from the configs/ directory."""
from __future__ import annotations

import json
import os

_CONFIGS_DIR = os.path.join(os.path.dirname(__file__), "configs")


def list_towns() -> list[dict]:
    """Return all town configs (sorted by name), excluding addons.json."""
    towns = []
    for fname in os.listdir(_CONFIGS_DIR):
        if fname.endswith(".json") and fname != "addons.json":
            path = os.path.join(_CONFIGS_DIR, fname)
            with open(path, encoding="utf-8") as f:
                towns.append(json.load(f))
    return sorted(towns, key=lambda t: t.get("name", ""))


def load_town(town_id: str) -> dict:
    path = os.path.join(_CONFIGS_DIR, f"{town_id}.json")
    with open(path, encoding="utf-8") as f:
        return json.load(f)


_STATE_FILE = os.path.join(os.path.dirname(__file__), "user_state.json")


def load_state() -> dict:
    try:
        with open(_STATE_FILE, encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def save_state(state: dict) -> None:
    with open(_STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)
