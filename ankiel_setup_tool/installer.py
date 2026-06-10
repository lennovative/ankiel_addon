"""
Helpers for checking add-on installation state.

The actual download + installation is delegated to Anki's own
`aqt.addons.download_addons` function (wizard.py), which uses the
correct URL format, headers, and mw.addonManager.install() pipeline.
"""

from __future__ import annotations

import json
import os


def is_addon_installed(code: str, addons_folder: str) -> bool:
    """Return True if the add-on folder exists and contains __init__.py."""
    return os.path.isfile(os.path.join(addons_folder, code, "__init__.py"))


def is_addon_disabled(code: str, addons_folder: str) -> bool:
    """Return True if the add-on is installed but disabled in Anki."""
    meta_path = os.path.join(addons_folder, code, "meta.json")
    try:
        with open(meta_path, encoding="utf-8") as f:
            return bool(json.load(f).get("disabled", False))
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return False
