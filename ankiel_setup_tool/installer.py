"""
Helpers for checking add-on installation state.

AnkiWeb downloads are delegated to Anki's own `aqt.addons.download_addons`
function (wizard.py), which uses the correct URL format, headers, and
mw.addonManager.install() pipeline.

Add-ons whose newest version is not on AnkiWeb (e.g. AMBOSS) define a
`download_url` in addons.json and are installed via `install_from_url`.
"""

from __future__ import annotations

import io
import json
import os
import zipfile

from anki.httpclient import HttpClient
from aqt.addons import DownloadError, InstallError, InstallOk


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


def installed_mod(code: str, addons_folder: str) -> int:
    """Return the 'mod' timestamp from the add-on's meta.json (0 if unknown)."""
    meta_path = os.path.join(addons_folder, code, "meta.json")
    try:
        with open(meta_path, encoding="utf-8") as f:
            return int(json.load(f).get("mod", 0) or 0)
    except (FileNotFoundError, json.JSONDecodeError, OSError, ValueError):
        return 0


def _download(url: str) -> bytes | DownloadError:
    try:
        with HttpClient() as client:
            resp = client.get(url)
            if resp.status_code != 200:
                return DownloadError(status_code=resp.status_code)
            return client.stream_content(resp)
    except Exception as exc:  # noqa: BLE001
        return DownloadError(exception=exc)


def _package_mod(data: bytes) -> int:
    """Return the 'mod' timestamp from an .ankiaddon's manifest.json (0 if missing)."""
    try:
        with zipfile.ZipFile(io.BytesIO(data)) as zfile:
            return int(json.loads(zfile.read("manifest.json")).get("mod", 0) or 0)
    except (KeyError, ValueError, zipfile.BadZipFile):
        return 0


def _replace_legacy(mgr, package: str, legacy_codes: list) -> None:
    """Remove superseded installs (e.g. the AnkiWeb copy of AMBOSS), keeping their config.

    Anki's conflict handling has already disabled them during install; this
    mirrors what the add-on's own updater does on a package-name change.
    """
    for old in legacy_codes:
        old = str(old)
        if old == package or not os.path.isdir(mgr.addonsFolder(old)):
            continue
        try:
            config = mgr.getConfig(old)
            if config is not None:
                mgr.writeConfig(package, config)
            mgr.deleteAddon(old)
        except Exception:  # noqa: BLE001
            pass


def install_from_url(
    mgr, addon: dict, min_mod: int = 0
) -> InstallOk | InstallError | DownloadError | None:
    """Download addon['download_url'] and install it.

    Returns None without installing if the download is not newer than
    *min_mod*, so an add-on that already updated itself is never downgraded.
    Runs in a background thread, like Anki's own downloader.
    """
    data = _download(addon["download_url"])
    if isinstance(data, DownloadError):
        return data
    if min_mod and _package_mod(data) <= min_mod:
        return None
    try:
        result = mgr.install(io.BytesIO(data))
    except Exception as exc:  # noqa: BLE001
        return DownloadError(exception=exc)
    if isinstance(result, InstallOk):
        _replace_legacy(mgr, str(addon["addon_codes"][0]), addon.get("replaces", []))
    return result
