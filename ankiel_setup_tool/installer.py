"""
Helpers for checking add-on installation state.

The actual download + installation is delegated to Anki's own
`aqt.addons.download_addons` function (wizard.py), which uses the
correct URL format, headers, and mw.addonManager.install() pipeline.
"""

from __future__ import annotations

import os


def is_addon_installed(code: str, addons_folder: str) -> bool:
    """Return True if the add-on folder exists and contains __init__.py."""
    return os.path.isfile(os.path.join(addons_folder, code, "__init__.py"))
