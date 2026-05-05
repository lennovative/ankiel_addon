"""
Anki Setup Wizard
=================
A one-stop wizard for installing and configuring popular Anki add-ons,
with a focus on German medical students (AnkiZin, AnkiHub, AMBOSS, …).

Adds:  Tools → Anki Setup Wizard

Requires Anki 2.1.49+ (Qt6/PyQt6).
"""

from aqt import gui_hooks, mw
from aqt.qt import QAction


def _show_wizard() -> None:
    try:
        from .wizard import AnkiSetupWizard
        dlg = AnkiSetupWizard(mw)
        dlg.exec()
    except Exception as exc:  # noqa: BLE001
        from aqt.utils import showWarning
        showWarning(
            f"Anki Setup Wizard konnte nicht geöffnet werden:\n\n{exc}",
            title="Anki Setup Wizard – Fehler",
        )
        raise


def _register_menu() -> None:
    """Called once the main window is fully initialised."""
    action = QAction("Anki Setup Wizard", mw)
    action.triggered.connect(_show_wizard)
    mw.form.menuTools.addAction(action)


# gui_hooks.main_window_did_init fires after the deck list is shown,
# which guarantees mw.form.menuTools exists.
gui_hooks.main_window_did_init.append(_register_menu)
