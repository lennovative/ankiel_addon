"""
AnKiel Setup Tool
=================
A one-stop wizard for installing and configuring popular Anki add-ons like
AnkiZin, AnkiHub, AMBOSS, ...

Adds:  toolbar button + Tools → AnKiel Setup Tool

Requires Anki 2.1.49+ (Qt6/PyQt6).
"""

import os

from aqt import gui_hooks, mw
from aqt.qt import QAction, QDialog, QMessageBox, QTimer

_REOPEN_FLAG = os.path.join(os.path.dirname(__file__), ".reopen_wizard")

# ---------------------------------------------------------------------------
# Startup popup suppression
# ---------------------------------------------------------------------------
# When Anki is restarted via the wizard we want to jump straight back into
# AnKiel without other addons showing their own login/greeting dialogs.
#
# We patch QDialog.exec with a Python function.  To call the real C++ exec
# we must first *delete* our override — assigning the original SIP descriptor
# back doesn't work in PyQt6 because the wrapper doesn't round-trip through
# a plain Python variable (you get "first argument of unbound method").
# Deleting the override lets Python fall through to the C++ method directly.
#
# For QMessageBox callers that assert clickedButton() is not None, we click
# the first non-HelpRole button via a zero-delay timer before exec runs.
# For plain QDialog subclasses we just reject and return 0.

_suppression_active = False


def _suppress_startup_popups() -> None:
    global _suppression_active
    if not os.path.exists(_REOPEN_FLAG):
        return

    _suppression_active = True

    def _click_safe(msg: QMessageBox) -> None:
        btns = msg.buttons()
        for btn in btns:
            try:
                if msg.buttonRole(btn) != QMessageBox.ButtonRole.HelpRole:
                    btn.click()
                    return
            except Exception:
                pass
        msg.reject()

    def _patched_exec(self):  # type: ignore[misc]
        # Delete our Python-level override so self.exec() hits C++.
        try:
            del QDialog.exec  # type: ignore[attr-defined]
        except (AttributeError, TypeError):
            pass

        try:
            if isinstance(self, QMessageBox):
                QTimer.singleShot(0, lambda: _click_safe(self))
                return self.exec()  # real C++ exec; closed by timer
            else:
                self.reject()
                return 0
        finally:
            if _suppression_active:
                try:
                    QDialog.exec = _patched_exec  # type: ignore[method-assign]
                except Exception:
                    pass

    QDialog.exec = _patched_exec  # type: ignore[method-assign]


def _restore_startup_suppression() -> None:
    global _suppression_active
    if _suppression_active:
        _suppression_active = False
        try:
            del QDialog.exec  # type: ignore[attr-defined]
        except (AttributeError, TypeError):
            pass


_suppress_startup_popups()


# ---------------------------------------------------------------------------
# Wizard helpers
# ---------------------------------------------------------------------------

def _show_wizard(post_restart: bool = False) -> None:
    _restore_startup_suppression()
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


def _on_toolbar_init(links: list, toolbar) -> None:
    links.append(
        toolbar.create_link(
            cmd="ankiel_setup",
            label="AnKiel",
            func=lambda: _show_wizard(),
            tip="AnKiel Setup Tool öffnen",
            id="ankiel-setup-btn",
        )
    )


def _register_menu() -> None:
    action = QAction("AnKiel Setup Tool", mw)
    action.triggered.connect(_show_wizard)
    mw.form.menuTools.addAction(action)

    if os.path.exists(_REOPEN_FLAG):
        try:
            os.remove(_REOPEN_FLAG)
        except OSError:
            pass
        _show_wizard(post_restart=True)


gui_hooks.main_window_did_init.append(_register_menu)
gui_hooks.top_toolbar_did_init_links.append(_on_toolbar_init)
