"""
AnKiel Setup Tool
=================
A one-stop wizard for installing and configuring popular Anki add-ons like
AnkiZin, AnkiHub, AMBOSS, ...

Adds:  Tools → AnKiel Setup Tool

Requires Anki 2.1.49+ (Qt6/PyQt6).
"""

import os

from aqt import gui_hooks, mw
from aqt.qt import QAction

_REOPEN_FLAG = os.path.join(os.path.dirname(__file__), ".reopen_wizard")


def _show_wizard(post_restart: bool = False) -> None:
    try:
        from .wizard import AnkiSetupWizard
        dlg = AnkiSetupWizard(mw, post_restart=post_restart)
        dlg.exec()
    except Exception as exc:  # noqa: BLE001
        from aqt.utils import showWarning
        showWarning(
            f"AnKiel Setup Tool konnte nicht geöffnet werden:\n\n{exc}",
            title="AnKiel Setup Tool – Fehler",
        )
        raise


def _register_menu() -> None:
    """Called once the main window is fully initialised."""
    action = QAction("AnKiel Setup Tool", mw)
    action.triggered.connect(_show_wizard)
    mw.form.menuTools.addAction(action)

    if os.path.exists(_REOPEN_FLAG):
        try:
            os.remove(_REOPEN_FLAG)
        except OSError:
            pass
        _show_wizard(post_restart=True)


# gui_hooks.main_window_did_init fires after the deck list is shown,
# which guarantees mw.form.menuTools exists.
gui_hooks.main_window_did_init.append(_register_menu)
