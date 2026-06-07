"""
Main wizard dialog for the AnKiel add-on.

Pages (QStackedWidget indices):
  0  Uni     – town / university selection
  1  Install – download/install progress log  (reused for basics and extras)
  2  Select  – full overview: basics (read-only) + optional checkboxes
  3  Steps   – guided setup instructions per add-on
  4  Done    – summary + restart reminder
  5  Update  – update-check page shown before re-running setup steps
"""

from __future__ import annotations

import datetime
import json
import os
from typing import Any, Dict, List, Optional, Tuple

from aqt import mw
from aqt.addons import InstallOk, download_addons
from aqt.qt import (
    QCheckBox,
    QDesktopServices,
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QStackedWidget,
    QTextBrowser,
    QUrl,
    QVBoxLayout,
    QWidget,
    Qt,
)
from aqt.utils import tooltip

from .addon_defs import ADDON_CATALOG, CATEGORIES
from .config_loader import list_towns, load_state, save_state
from .installer import is_addon_installed

# ---------------------------------------------------------------------------
# Qt 5 / 6 compatibility shim
# ---------------------------------------------------------------------------
try:
    _ALIGN_CENTER = Qt.AlignmentFlag.AlignCenter
    _ALIGN_TOP = Qt.AlignmentFlag.AlignTop
    _ALIGN_RIGHT = Qt.AlignmentFlag.AlignRight
    _FRAME_STYLED = QFrame.Shape.StyledPanel
    _FRAME_NONE = QFrame.Shape.NoFrame
except AttributeError:
    _ALIGN_CENTER = Qt.AlignCenter  # type: ignore[attr-defined]
    _ALIGN_TOP = Qt.AlignTop  # type: ignore[attr-defined]
    _ALIGN_RIGHT = Qt.AlignRight  # type: ignore[attr-defined]
    _FRAME_STYLED = QFrame.StyledPanel  # type: ignore[attr-defined]
    _FRAME_NONE = QFrame.NoFrame  # type: ignore[attr-defined]

PAGE_UNI = 0
PAGE_INSTALL = 1
PAGE_SELECT = 2
PAGE_STEPS = 3
PAGE_DONE = 4
PAGE_UPDATE = 5

# ---------------------------------------------------------------------------
# Shared styles
# ---------------------------------------------------------------------------
_BTN_PRIMARY = (
    "QPushButton{"
    " background:#2980b9;color:white;padding:8px 22px;"
    " border-radius:5px;font-weight:bold;font-size:12px;}"
    "QPushButton:hover{background:#3498db;}"
    "QPushButton:disabled{background:#95a5a6;}"
)
_BTN_SECONDARY = (
    "QPushButton{"
    " background:#ecf0f1;color:#2c3e50;padding:8px 22px;"
    " border-radius:5px;font-size:12px;border:1px solid #bdc3c7;}"
    "QPushButton:hover{background:#d5dbdb;}"
    "QPushButton:disabled{color:#aab;}"
)
_BTN_GREEN = (
    "QPushButton{"
    " background:#27ae60;color:white;padding:7px 18px;"
    " border-radius:5px;font-size:12px;}"
    "QPushButton:hover{background:#2ecc71;}"
)
_BTN_SETUP = (
    "QPushButton{"
    " background:#2980b9;color:white;padding:2px 7px;"
    " border-radius:4px;font-size:10px;font-weight:bold;}"
    "QPushButton:hover{background:#3498db;}"
)
_BTN_UNINSTALL = (
    "QPushButton{"
    " background:#e74c3c;color:white;padding:2px 7px;"
    " border-radius:4px;font-size:10px;font-weight:bold;}"
    "QPushButton:hover{background:#c0392b;}"
)
_LOG_STYLE = (
    "QTextBrowser{"
    " background:#1e1e2e;color:#cdd6f4;"
    " font-family:monospace;font-size:12px;"
    " border:1px solid #45475a;border-radius:4px;}"
)
_STEPS_STYLE = (
    "QTextBrowser{"
    " background:#f8f9fa;color:#2c3e50;"
    " font-size:13px;border:1px solid #dee2e6;border-radius:4px;"
    " padding:8px;}"
)




# ===========================================================================
# Town card widget
# ===========================================================================

class _TownCard(QFrame):
    """Clickable selection card for a town / university."""

    def __init__(self, town_data: dict, on_select, parent: QWidget = None) -> None:
        super().__init__(parent)
        self._town_data = town_data
        self._on_select = on_select
        self._selected = False
        self.setFrameShape(_FRAME_STYLED)
        self._apply_style()
        try:
            self.setCursor(Qt.CursorShape.PointingHandCursor)
        except AttributeError:
            self.setCursor(Qt.PointingHandCursor)  # type: ignore[attr-defined]

        row = QHBoxLayout(self)
        row.setContentsMargins(14, 10, 14, 10)
        row.setSpacing(12)

        icon_lbl = QLabel(town_data.get("icon", "🎓"))
        icon_lbl.setStyleSheet("font-size:28px;min-width:36px;max-width:36px;")
        row.addWidget(icon_lbl)

        txt = QVBoxLayout()
        txt.setSpacing(2)
        name_lbl = QLabel(f"<b>{town_data['name']}</b>")
        name_lbl.setStyleSheet("font-size:13px;")
        desc_lbl = QLabel(town_data.get("description", ""))
        desc_lbl.setWordWrap(True)
        desc_lbl.setStyleSheet("color:#555;font-size:11px;")
        txt.addWidget(name_lbl)
        txt.addWidget(desc_lbl)
        row.addLayout(txt, stretch=1)

    def _apply_style(self) -> None:
        if self._selected:
            self.setStyleSheet(
                "_TownCard{background:#ebf5fb;border:2px solid #2980b9;"
                "border-radius:8px;margin:2px 0;}"
            )
        else:
            self.setStyleSheet(
                "_TownCard{background:#fff;border:2px solid #dee2e6;"
                "border-radius:8px;margin:2px 0;}"
                "_TownCard:hover{border-color:#85c1e9;}"
            )

    def mousePressEvent(self, event) -> None:  # type: ignore[override]
        self._on_select(self._town_data["id"])
        super().mousePressEvent(event)

    def set_selected(self, v: bool) -> None:
        self._selected = v
        self._apply_style()

    def town_id(self) -> str:
        return self._town_data["id"]


# ===========================================================================
# Addon card widget
# ===========================================================================

class _AddonCard(QFrame):
    """Clickable card for one add-on.

    read_only=True : already-installed card (no checkbox, not selectable).
    on_check_changed : called when the checkbox state changes.
    on_setup         : if provided, a 'Setup →' button is shown.
    on_uninstall     : if provided, a red 'Deinstallieren' button is shown.
    """

    def __init__(
        self,
        addon_data: dict,
        addons_folder: str,
        read_only: bool = False,
        on_check_changed=None,
        on_setup=None,
        on_uninstall=None,
        login_type: Optional[str] = None,
        on_login=None,
        parent: QWidget = None,
    ) -> None:
        super().__init__(parent)
        self._addon_data = addon_data
        self._read_only = read_only
        self.setFrameShape(_FRAME_STYLED)

        if read_only:
            self.setStyleSheet(
                "_AddonCard{background:#f0faf4;border:1px solid #a9dfbf;"
                "border-radius:8px;margin:2px 0;}"
            )
        else:
            self.setStyleSheet(
                "_AddonCard{background:#fff;border:2px solid #dee2e6;border-radius:8px;margin:2px 0;}"
                "_AddonCard:hover{border-color:#3498db;}"
            )
            try:
                self.setCursor(Qt.CursorShape.PointingHandCursor)
            except AttributeError:
                self.setCursor(Qt.PointingHandCursor)  # type: ignore[attr-defined]

        row = QHBoxLayout(self)
        row.setContentsMargins(12, 9, 12, 9)
        row.setSpacing(10)

        if read_only:
            self._checkbox = None
        else:
            self._checkbox = QCheckBox()
            self._checkbox.setFixedSize(22, 22)
            if on_check_changed:
                self._checkbox.stateChanged.connect(on_check_changed)
            row.addWidget(self._checkbox)

        icon_lbl = QLabel(addon_data.get("icon", "📦"))
        icon_lbl.setStyleSheet("font-size:26px;min-width:34px;max-width:34px;")
        row.addWidget(icon_lbl)

        txt = QVBoxLayout()
        txt.setSpacing(1)

        # Title row: name + inline badges
        name_row = QHBoxLayout()
        name_row.setSpacing(6)
        name_lbl = QLabel(
            f"<b>{addon_data['name']}</b>"
            f"  <span style='color:#7f8c8d;font-size:10px;'>#{addon_data['addon_codes'][0]}</span>"
        )
        name_lbl.setStyleSheet("font-size:13px;")
        name_row.addWidget(name_lbl)

        if read_only:
            b = QLabel("✓ Installiert")
            b.setStyleSheet(
                "background:#d5f5e3;color:#1e8449;padding:2px 7px;"
                "border-radius:9px;font-size:10px;"
            )
            name_row.addWidget(b)
        else:
            already = all(
                is_addon_installed(str(c), addons_folder)
                for c in addon_data.get("addon_codes", [])
            )
            if already:
                b = QLabel("✓ Installiert")
                b.setStyleSheet(
                    "background:#d5f5e3;color:#1e8449;padding:2px 7px;"
                    "border-radius:9px;font-size:10px;"
                )
                name_row.addWidget(b)

        if addon_data.get("requires_account"):
            b2 = QLabel("Account nötig")
            b2.setStyleSheet(
                "background:#fef9e7;color:#9a7d0a;padding:2px 7px;"
                "border-radius:9px;font-size:10px;"
            )
            name_row.addWidget(b2)

        if login_type == "external":
            login_note = addon_data.get("login", {}).get("note", "")
            b3 = QLabel("Externer Login")
            b3.setStyleSheet(
                "background:#eaecee;color:#566573;padding:2px 7px;"
                "border-radius:9px;font-size:10px;"
            )
            if login_note:
                b3.setToolTip(login_note)
            name_row.addWidget(b3)
        elif login_type == "logged_in":
            b3 = QLabel("✓ Angemeldet")
            b3.setStyleSheet(
                "background:#d5f5e3;color:#1e8449;padding:2px 7px;"
                "border-radius:9px;font-size:10px;"
            )
            name_row.addWidget(b3)

        name_row.addStretch()
        txt.addLayout(name_row)

        subtitle_lbl = QLabel(addon_data.get("subtitle", ""))
        subtitle_lbl.setStyleSheet("color:#7f8c8d;font-size:11px;")
        desc_lbl = QLabel(addon_data["description"])
        desc_lbl.setWordWrap(True)
        desc_lbl.setStyleSheet("color:#555;font-size:11px;margin-top:2px;")
        txt.addWidget(subtitle_lbl)
        txt.addWidget(desc_lbl)
        row.addLayout(txt, stretch=1)

        # Right column: buttons only
        if on_setup or on_uninstall or on_login:
            btns = QVBoxLayout()
            btns.setSpacing(4)
            btns.setAlignment(_ALIGN_TOP | _ALIGN_RIGHT)
            if on_login:
                login_btn = QPushButton("Anmelden")
                login_btn.setStyleSheet(_BTN_SETUP)
                login_btn.clicked.connect(on_login)
                btns.addWidget(login_btn)
            if on_setup:
                setup_btn = QPushButton("Setup →")
                setup_btn.setStyleSheet(_BTN_SETUP)
                setup_btn.clicked.connect(on_setup)
                btns.addWidget(setup_btn)
            if on_uninstall:
                uninstall_btn = QPushButton("Deinstallieren")
                uninstall_btn.setStyleSheet(_BTN_UNINSTALL)
                uninstall_btn.clicked.connect(on_uninstall)
                btns.addWidget(uninstall_btn)
            btns.addStretch()
            row.addLayout(btns)

    def mousePressEvent(self, event) -> None:  # type: ignore[override]
        if self._read_only:
            super().mousePressEvent(event)
            return
        cb_pos = self._checkbox.mapFromParent(event.pos())
        if not self._checkbox.rect().contains(cb_pos):
            self._checkbox.setChecked(not self._checkbox.isChecked())
        super().mousePressEvent(event)

    def is_checked(self) -> bool:
        if self._read_only:
            return False
        return self._checkbox.isChecked()

    def set_checked(self, v: bool) -> None:
        if self._read_only:
            return
        self._checkbox.setChecked(v)

    def addon_id(self) -> str:
        return self._addon_data["id"]


# ===========================================================================
# Main wizard
# ===========================================================================

class AnkiSetupWizard(QDialog):

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("AnKiel")
        self.setMinimumSize(820, 720)
        self.resize(860, 700)

        self._addons_folder: str = mw.addonManager.addonsFolder()

        # Town selection
        self._selected_town_id: Optional[str] = None
        self._town_config: dict = {}
        self._town_cards: List[_TownCard] = []

        # Install state
        self._install_phase: str = ""
        self._all_installed_ids: List[str] = []
        self._newly_installed_ids: List[str] = []
        self._selected_ids: List[str] = []
        self._install_results: Dict[str, bool] = {}
        self._code_to_addon: Dict[int, str] = {}

        # Overview cards
        self._addon_cards: List[_AddonCard] = []

        # Step-through state
        self._step_queue: List[Tuple[str, dict]] = []
        self._step_idx: int = -1
        self._current_step_url: Optional[str] = None
        self._setup_mode: str = "install"  # "install" | "manual"

        # Update-check state
        self._update_addon_id: str = ""
        self._update_mod_before: Dict[str, int] = {}

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        self._build_header(outer)

        self._stack = QStackedWidget()
        outer.addWidget(self._stack, stretch=1)

        self._stack.addWidget(self._build_uni_page())     # 0  PAGE_UNI
        self._stack.addWidget(self._build_install_page()) # 1  PAGE_INSTALL
        self._stack.addWidget(self._build_select_page())  # 2  PAGE_SELECT
        self._stack.addWidget(self._build_steps_page())   # 3  PAGE_STEPS
        self._stack.addWidget(self._build_done_page())    # 4  PAGE_DONE
        self._stack.addWidget(self._build_update_page())  # 5  PAGE_UPDATE

        self._build_nav_bar(outer)
        self._go_to(PAGE_UNI)
        self._apply_saved_state()

    # -----------------------------------------------------------------------
    # Saved state
    # -----------------------------------------------------------------------

    def _apply_saved_state(self) -> None:
        saved = load_state().get("selected_town")
        if saved:
            self._on_town_selected(saved)

    # -----------------------------------------------------------------------
    # Header
    # -----------------------------------------------------------------------

    def _build_header(self, parent: QVBoxLayout) -> None:
        hdr = QFrame()
        hdr.setStyleSheet(
            "QFrame{background:qlineargradient("
            "x1:0,y1:0,x2:1,y2:0,stop:0 #1a252f,stop:1 #2980b9);"
            "min-height:10px;max-height:200px;}"
        )
        hl = QHBoxLayout(hdr)
        hl.setContentsMargins(20, 10, 20, 10)
        title = QLabel("AnKiel Setup")
        title.setStyleSheet("color:white;font-size:19px;font-weight:bold;")
        sub = QLabel("Add-ons installieren und einrichten")
        sub.setStyleSheet("color:#85c1e9;font-size:11px;")
        col = QVBoxLayout()
        col.setSpacing(1)
        col.addWidget(title)
        col.addWidget(sub)
        hl.addLayout(col)
        hl.addStretch()
        parent.addWidget(hdr)

    # -----------------------------------------------------------------------
    # Pages
    # -----------------------------------------------------------------------

    def _build_uni_page(self) -> QWidget:
        page = QWidget()
        vl = QVBoxLayout(page)
        vl.setContentsMargins(18, 12, 18, 8)
        vl.setSpacing(6)

        top = QLabel(
            "<b style='font-size:14px;'>Hochschule auswählen</b>"
            "  <span style='color:#7f8c8d;font-size:11px;'>"
            "– Wähle deine Uni oder deinen Standort</span>"
        )
        vl.addWidget(top)

        hint = QLabel(
            "Add-ons für deinen Standort werden automatisch installiert."
        )
        hint.setStyleSheet("color:#7f8c8d;font-size:11px;padding-bottom:4px;")
        vl.addWidget(hint)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(_FRAME_NONE)

        inner = QWidget()
        il = QVBoxLayout(inner)
        il.setContentsMargins(2, 2, 2, 2)
        il.setSpacing(6)

        for town in list_towns():
            card = _TownCard(town, on_select=self._on_town_selected)
            il.addWidget(card)
            self._town_cards.append(card)

        il.addStretch()
        scroll.setWidget(inner)
        vl.addWidget(scroll, stretch=1)
        return page

    def _on_town_selected(self, town_id: str) -> None:
        self._selected_town_id = town_id
        for card in self._town_cards:
            card.set_selected(card.town_id() == town_id)
        save_state({"selected_town": town_id})

    def _build_install_page(self) -> QWidget:
        page = QWidget()
        vl = QVBoxLayout(page)
        vl.setContentsMargins(26, 18, 26, 14)
        vl.setSpacing(10)

        self._install_status_lbl = QLabel("<b>Installiere Add-ons…</b>")
        self._install_status_lbl.setStyleSheet("font-size:14px;")
        vl.addWidget(self._install_status_lbl)

        self._install_progress = QProgressBar()
        self._install_progress.setStyleSheet(
            "QProgressBar{height:18px;border-radius:4px;border:1px solid #bdc3c7;}"
            "QProgressBar::chunk{background:#2980b9;border-radius:4px;}"
        )
        vl.addWidget(self._install_progress)

        self._install_log = QTextBrowser()
        self._install_log.setStyleSheet(_LOG_STYLE)
        vl.addWidget(self._install_log, stretch=1)
        return page

    def _build_select_page(self) -> QWidget:
        page = QWidget()
        vl = QVBoxLayout(page)
        vl.setContentsMargins(18, 12, 18, 8)
        vl.setSpacing(6)

        top = QLabel(
            "<b style='font-size:14px;'>Übersicht & weitere Add-ons</b>"
            "  <span style='color:#7f8c8d;font-size:11px;'>"
            "– optionale Add-ons auswählen</span>"
        )
        vl.addWidget(top)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(_FRAME_NONE)

        self._select_inner = QWidget()
        self._select_inner_layout = QVBoxLayout(self._select_inner)
        self._select_inner_layout.setContentsMargins(2, 2, 2, 2)
        self._select_inner_layout.setSpacing(3)

        scroll.setWidget(self._select_inner)
        vl.addWidget(scroll, stretch=1)

        btn_row = QHBoxLayout()
        all_btn = QPushButton("Alle auswählen")
        all_btn.setStyleSheet(_BTN_SECONDARY)
        all_btn.clicked.connect(lambda: [c.set_checked(True) for c in self._addon_cards])
        none_btn = QPushButton("Keine")
        none_btn.setStyleSheet(_BTN_SECONDARY)
        none_btn.clicked.connect(lambda: [c.set_checked(False) for c in self._addon_cards])
        btn_row.addWidget(all_btn)
        btn_row.addWidget(none_btn)
        btn_row.addStretch()
        vl.addLayout(btn_row)
        return page

    def _populate_addon_overview(self, basic_ids: List[str], optional_ids: List[str]) -> None:
        layout = self._select_inner_layout
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        self._addon_cards = []

        if basic_ids:
            section_lbl = QLabel("✅  Basics – automatisch installiert")
            section_lbl.setStyleSheet(
                "color:#1e8449;font-weight:bold;font-size:12px;padding:6px 2px 2px 2px;"
            )
            layout.addWidget(section_lbl)
            for aid in basic_ids:
                addon_data = ADDON_CATALOG.get(aid)
                if not addon_data:
                    continue
                login_type, on_login = self._make_login_callback(aid, addon_data)
                card = _AddonCard(
                    addon_data, self._addons_folder,
                    read_only=True,
                    on_setup=self._make_setup_callback(aid, addon_data),
                    login_type=login_type,
                    on_login=on_login,
                )
                layout.addWidget(card)
                self._addon_cards.append(card)

        if optional_ids:
            section_lbl2 = QLabel("➕  Weitere Add-ons (optional)")
            section_lbl2.setStyleSheet(
                "color:#2980b9;font-weight:bold;font-size:12px;padding:12px 2px 2px 2px;"
            )
            layout.addWidget(section_lbl2)

            for cat_id, cat_info in CATEGORIES.items():
                addons_in_cat = [
                    (aid, ADDON_CATALOG[aid])
                    for aid in optional_ids
                    if ADDON_CATALOG.get(aid, {}).get("category") == cat_id
                ]
                if not addons_in_cat:
                    continue
                cat_lbl = QLabel(cat_info["label"])
                cat_lbl.setStyleSheet(
                    f"color:{cat_info['color']};font-weight:bold;"
                    "font-size:11px;padding:4px 2px 1px 10px;"
                )
                layout.addWidget(cat_lbl)
                for aid, addon_data in addons_in_cat:
                    already = all(
                        is_addon_installed(str(c), self._addons_folder)
                        for c in addon_data.get("addon_codes", [])
                    )
                    on_uninstall = self._make_uninstall_callback(aid) if already else None
                    login_type, on_login = self._make_login_callback(aid, addon_data) if already else (None, None)
                    card = _AddonCard(
                        addon_data, self._addons_folder,
                        read_only=already,
                        on_check_changed=self._update_install_btn,
                        on_setup=self._make_setup_callback(aid, addon_data) if already else None,
                        on_uninstall=on_uninstall,
                        login_type=login_type,
                        on_login=on_login,
                    )
                    layout.addWidget(card)
                    self._addon_cards.append(card)

        layout.addStretch()

    def _make_setup_callback(self, addon_id: str, addon_data: dict):
        """Return a callback that opens the update+setup page, or None if no steps exist."""
        has_steps = any(
            s.get("type") in ("instruction", "login")
            for s in addon_data.get("setup_steps", [])
        )
        if not has_steps:
            return None
        def _cb(_checked=False, _aid=addon_id):
            self._open_update_page(_aid)
        return _cb

    def _make_uninstall_callback(self, addon_id: str):
        def _cb(_checked=False, _aid=addon_id):
            self._uninstall_addon(_aid)
        return _cb

    def _check_is_logged_in(self, auth_module: str, attr_path: str) -> bool:
        """Check login state via the addon's own auth_manager (requires addon to be loaded)."""
        import sys
        if not auth_module or not attr_path:
            return False
        mod = sys.modules.get(auth_module)
        if not mod:
            return False
        obj: Any = mod
        for attr in attr_path.split("."):
            obj = getattr(obj, attr, None)
            if obj is None:
                return False
        try:
            return bool(obj())
        except Exception:
            return False

    def _make_login_callback(self, _addon_id: str, addon_data: dict):
        """Return (card_login_type, callback) or (None, None) if no login spec."""
        login = addon_data.get("login", {})
        login_type = login.get("type")
        if not login_type:
            return None, None
        if login_type == "external":
            return "external", None
        elif login_type == "native":
            logged_in = self._check_is_logged_in(
                login.get("auth_module", ""),
                login.get("is_logged_in_attr", ""),
            )
            if logged_in:
                return "logged_in", None
            def _cb_native(_checked=False, _data=addon_data):
                self._open_native_login_for_card(_data)
            return "native", _cb_native
        elif login_type == "browser":
            url = login.get("url", "")
            def _cb_browser(_checked=False, _url=url):
                QDesktopServices.openUrl(QUrl(_url))
            return "browser", _cb_browser
        return None, None

    def _open_native_login_for_card(self, addon_data: dict) -> None:
        """Open the addon's own login dialog and refresh the overview afterward."""
        import sys
        login = addon_data.get("login", {})
        mod = sys.modules.get(login.get("login_module", ""))
        if not mod:
            tooltip(
                "Das Add-on ist noch nicht geladen. "
                "Starte Anki neu und öffne den Setup erneut."
            )
            return
        dlg_class = getattr(mod, login.get("login_dialog_class", ""), None)
        if not dlg_class:
            return
        dlg_class(mw).exec()
        self._back_to_overview()

    def _uninstall_addon(self, addon_id: str) -> None:
        import shutil
        from aqt.utils import askUser

        addon = ADDON_CATALOG.get(addon_id, {})
        name = addon.get("name", addon_id)

        if not askUser(f"Möchtest du '{name}' wirklich deinstallieren?"):
            return

        for code in addon.get("addon_codes", []):
            addon_path = os.path.join(self._addons_folder, str(code))
            if os.path.isdir(addon_path):
                shutil.rmtree(addon_path)

        self._back_to_overview()

    def _build_steps_page(self) -> QWidget:
        page = QWidget()
        vl = QVBoxLayout(page)
        vl.setContentsMargins(26, 16, 26, 14)
        vl.setSpacing(6)

        self._steps_addon_lbl = QLabel()
        self._steps_addon_lbl.setStyleSheet("font-size:16px;font-weight:bold;")
        vl.addWidget(self._steps_addon_lbl)

        self._steps_progress_lbl = QLabel()
        self._steps_progress_lbl.setStyleSheet("color:#7f8c8d;font-size:11px;")
        vl.addWidget(self._steps_progress_lbl)

        self._steps_title_lbl = QLabel()
        self._steps_title_lbl.setStyleSheet("font-size:14px;font-weight:bold;margin-top:6px;")
        vl.addWidget(self._steps_title_lbl)

        self._steps_desc = QTextBrowser()
        self._steps_desc.setStyleSheet(_STEPS_STYLE)
        vl.addWidget(self._steps_desc, stretch=1)

        self._steps_url_btn = QPushButton("Link öffnen")
        self._steps_url_btn.setStyleSheet(_BTN_GREEN)
        self._steps_url_btn.clicked.connect(self._open_step_url)
        self._steps_url_btn.hide()
        vl.addWidget(self._steps_url_btn)

        self._steps_login_btn = QPushButton("🔑  Login-Fenster öffnen")
        self._steps_login_btn.setStyleSheet(_BTN_PRIMARY)
        self._steps_login_btn.clicked.connect(self._on_steps_login_click)
        self._steps_login_btn.hide()
        vl.addWidget(self._steps_login_btn)

        self._steps_login_status = QLabel()
        self._steps_login_status.setStyleSheet("font-size:12px;padding:2px 0;")
        self._steps_login_status.hide()
        vl.addWidget(self._steps_login_status)
        return page

    def _build_done_page(self) -> QWidget:
        page = QWidget()
        vl = QVBoxLayout(page)
        vl.setContentsMargins(40, 30, 40, 20)
        vl.setSpacing(14)
        vl.setAlignment(_ALIGN_CENTER)

        icon_lbl = QLabel("✅")
        icon_lbl.setStyleSheet("font-size:56px;")
        icon_lbl.setAlignment(_ALIGN_CENTER)
        vl.addWidget(icon_lbl)

        vl.addWidget(QLabel("<h2>Einrichtung abgeschlossen!</h2>"))

        self._done_summary_lbl = QLabel()
        self._done_summary_lbl.setWordWrap(True)
        self._done_summary_lbl.setAlignment(_ALIGN_CENTER)
        self._done_summary_lbl.setStyleSheet("font-size:13px;color:#555;")
        vl.addWidget(self._done_summary_lbl)

        restart_lbl = QLabel(
            "⚠️  <b>Starte Anki neu</b>, damit alle installierten Add-ons aktiv werden."
        )
        restart_lbl.setWordWrap(True)
        restart_lbl.setAlignment(_ALIGN_CENTER)
        restart_lbl.setStyleSheet(
            "background:#fef9e7;color:#856404;padding:12px;"
            "border-radius:6px;font-size:12px;"
        )
        vl.addWidget(restart_lbl)
        vl.addStretch()
        return page

    def _build_update_page(self) -> QWidget:
        page = QWidget()
        vl = QVBoxLayout(page)
        vl.setContentsMargins(26, 16, 26, 14)
        vl.setSpacing(10)

        self._update_addon_lbl = QLabel()
        self._update_addon_lbl.setStyleSheet("font-size:16px;font-weight:bold;")
        vl.addWidget(self._update_addon_lbl)

        self._update_version_lbl = QLabel()
        self._update_version_lbl.setStyleSheet("color:#7f8c8d;font-size:11px;")
        vl.addWidget(self._update_version_lbl)

        self._update_check_btn = QPushButton("🔍  Auf Updates prüfen")
        self._update_check_btn.setStyleSheet(_BTN_PRIMARY)
        self._update_check_btn.setFixedWidth(220)
        self._update_check_btn.clicked.connect(self._check_for_updates)
        vl.addWidget(self._update_check_btn)

        self._update_log = QTextBrowser()
        self._update_log.setStyleSheet(_LOG_STYLE)
        vl.addWidget(self._update_log, stretch=1)

        hint = QLabel(
            "💡 Nach einer Aktualisierung muss Anki neu gestartet werden, "
            "damit das Update aktiv wird."
        )
        hint.setWordWrap(True)
        hint.setStyleSheet("color:#7f8c8d;font-size:11px;")
        vl.addWidget(hint)
        return page

    # -----------------------------------------------------------------------
    # Nav bar
    # -----------------------------------------------------------------------

    def _build_nav_bar(self, parent: QVBoxLayout) -> None:
        bar = QFrame()
        bar.setStyleSheet("QFrame{background:#f4f6f7;border-top:1px solid #d5d8dc;}")
        hl = QHBoxLayout(bar)
        hl.setContentsMargins(20, 8, 20, 8)

        self._btn_back = QPushButton("← Zurück")
        self._btn_back.setStyleSheet(_BTN_SECONDARY)
        self._btn_back.clicked.connect(self._on_back)
        hl.addWidget(self._btn_back)
        hl.addStretch()

        self._btn_skip = QPushButton("Überspringen")
        self._btn_skip.setStyleSheet(_BTN_SECONDARY)
        self._btn_skip.clicked.connect(self._advance_step)
        self._btn_skip.hide()
        hl.addWidget(self._btn_skip)

        self._btn_next = QPushButton("Weiter →")
        self._btn_next.setStyleSheet(_BTN_PRIMARY)
        self._btn_next.clicked.connect(self._on_next)
        hl.addWidget(self._btn_next)

        parent.addWidget(bar)

    def _go_to(self, page: int) -> None:
        self._stack.setCurrentIndex(page)
        self._update_nav()

    def _update_nav(self) -> None:
        page = self._stack.currentIndex()

        self._btn_back.setVisible(page in (PAGE_SELECT, PAGE_UPDATE))
        self._btn_back.setEnabled(page in (PAGE_SELECT, PAGE_UPDATE))

        self._btn_skip.setVisible(page == PAGE_STEPS)

        if page == PAGE_DONE:
            self._btn_next.setText("Zur Übersicht")
            self._btn_next.setEnabled(True)
        elif page == PAGE_STEPS:
            self._btn_next.setText("Nächster Schritt →")
            self._btn_next.setEnabled(True)
        elif page == PAGE_INSTALL:
            self._btn_next.setText("Installiere…")
            self._btn_next.setEnabled(False)
        elif page == PAGE_SELECT:
            self._btn_next.setText("Installieren →")
            self._btn_next.setEnabled(False)
        elif page == PAGE_UPDATE:
            self._btn_next.setText("Setup →")
            self._btn_next.setEnabled(True)
        else:  # PAGE_UNI
            self._btn_next.setText("Weiter →")
            self._btn_next.setEnabled(True)

    # -----------------------------------------------------------------------
    # Navigation actions
    # -----------------------------------------------------------------------

    def _on_back(self) -> None:
        page = self._stack.currentIndex()
        if page == PAGE_UPDATE:
            self._go_to(PAGE_SELECT)
        else:
            self._go_to(PAGE_UNI)

    def _update_install_btn(self, *_) -> None:
        self._btn_next.setEnabled(any(c.is_checked() for c in self._addon_cards))

    def _on_next(self) -> None:
        page = self._stack.currentIndex()
        if page == PAGE_DONE:
            self._back_to_overview()
        elif page == PAGE_UNI:
            if not self._selected_town_id:
                tooltip("Bitte wähle eine Hochschule aus.")
                return
            self._start_basic_install()
        elif page == PAGE_SELECT:
            ids = [c.addon_id() for c in self._addon_cards if c.is_checked()]
            if not ids:
                return
            self._install_phase = "extras"
            self._selected_ids = ids
            self._all_installed_ids.extend(ids)
            self._run_install()
        elif page == PAGE_UPDATE:
            self._run_setup_for_addon(self._update_addon_id)
        elif page == PAGE_STEPS:
            self._advance_step()

    # -----------------------------------------------------------------------
    # Update-check page
    # -----------------------------------------------------------------------

    def _open_update_page(self, addon_id: str) -> None:
        """Show the update-check page before running setup steps."""
        self._update_addon_id = addon_id
        addon = ADDON_CATALOG.get(addon_id, {})
        icon = addon.get("icon", "📦")
        name = addon.get("name", addon_id)

        self._update_addon_lbl.setText(f"{icon}  {name}")

        # Try to read installed version date from meta.json
        version_text = ""
        for code in addon.get("addon_codes", []):
            meta_path = os.path.join(self._addons_folder, str(code), "meta.json")
            try:
                with open(meta_path, encoding="utf-8") as f:
                    mod = json.load(f).get("mod", 0)
                if mod:
                    dt = datetime.datetime.fromtimestamp(mod).strftime("%d.%m.%Y")
                    version_text = f"Installiert am: {dt}"
            except (FileNotFoundError, json.JSONDecodeError, OSError):
                pass

        self._update_version_lbl.setText(version_text)
        self._update_log.clear()
        self._update_check_btn.setEnabled(True)
        self._go_to(PAGE_UPDATE)

    def _check_for_updates(self) -> None:
        addon = ADDON_CATALOG.get(self._update_addon_id, {})
        codes = addon.get("addon_codes", [])

        # Record current mod times so we can detect a real update afterward
        self._update_mod_before = {}
        for code in codes:
            meta_path = os.path.join(self._addons_folder, str(code), "meta.json")
            try:
                with open(meta_path, encoding="utf-8") as f:
                    self._update_mod_before[str(code)] = json.load(f).get("mod", 0)
            except (FileNotFoundError, json.JSONDecodeError, OSError):
                self._update_mod_before[str(code)] = 0

        self._update_log.clear()
        self._update_log.append("⏳  Prüfe auf Updates…")
        self._update_check_btn.setEnabled(False)

        download_addons(
            parent=self,
            mgr=mw.addonManager,
            ids=[int(c) for c in codes],
            on_done=self._on_update_check_done,
        )

    def _on_update_check_done(self, log: list) -> None:
        self._update_check_btn.setEnabled(True)
        any_updated = False

        for entry_id, result in log:
            code = str(entry_id)
            if isinstance(result, InstallOk):
                meta_path = os.path.join(self._addons_folder, code, "meta.json")
                try:
                    with open(meta_path, encoding="utf-8") as f:
                        new_mod = json.load(f).get("mod", 0)
                    old_mod = self._update_mod_before.get(code, 0)
                    if new_mod > old_mod:
                        dt = datetime.datetime.fromtimestamp(new_mod).strftime("%d.%m.%Y")
                        self._update_log.append(f"✅  Update installiert  (Stand: {dt})")
                        self._update_version_lbl.setText(f"Installiert am: {dt}")
                        any_updated = True
                    else:
                        self._update_log.append("✅  Bereits auf dem neuesten Stand")
                except (FileNotFoundError, json.JSONDecodeError, OSError):
                    self._update_log.append("✅  Download abgeschlossen")
            else:
                errmsg = (
                    getattr(result, "errmsg", None)
                    or getattr(result, "exception", None)
                    or str(result)
                )
                self._update_log.append(f"❌  Fehler: {errmsg}")

        if any_updated:
            self._update_log.append(
                "\n⚠️  Starte Anki neu, damit das Update aktiv wird."
            )

    # -----------------------------------------------------------------------
    # Installation – phase 1: basics (automatic after town selection)
    # -----------------------------------------------------------------------

    def _start_basic_install(self) -> None:
        from .config_loader import load_town
        self._town_config = load_town(self._selected_town_id or "")
        basic_ids = self._town_config.get("basic_addons", [])

        self._install_phase = "basics"
        self._install_results = {}
        self._selected_ids = basic_ids
        self._all_installed_ids = list(basic_ids)
        self._run_install()

    # -----------------------------------------------------------------------
    # Shared install runner
    # -----------------------------------------------------------------------

    def _run_install(self) -> None:
        self._go_to(PAGE_INSTALL)
        self._install_log.clear()
        self._code_to_addon = {}
        self._newly_installed_ids = []

        codes_to_download: List[int] = []

        for addon_id in self._selected_ids:
            addon = ADDON_CATALOG.get(addon_id, {})
            name = addon.get("name", addon_id)
            icon = addon.get("icon", "📦")
            needs_dl = False
            for code in addon.get("addon_codes", []):
                self._code_to_addon[int(code)] = addon_id
                if not is_addon_installed(str(code), self._addons_folder):
                    codes_to_download.append(int(code))
                    needs_dl = True
            if needs_dl:
                self._install_log.append(f"⏳  {icon} {name}  –  wird heruntergeladen…")
            else:
                self._install_log.append(f"ℹ️   {icon} {name}  –  bereits installiert")
                self._install_results[addon_id] = True

        total = len(codes_to_download)
        self._install_progress.setMaximum(max(total, 1))
        self._install_progress.setValue(0)
        self._install_status_lbl.setText(
            f"<b>Lade {total} Paket(e) herunter…</b>" if total else "<b>Nichts zu installieren.</b>"
        )

        if codes_to_download:
            download_addons(
                parent=self,
                mgr=mw.addonManager,
                ids=codes_to_download,
                on_done=self._on_downloads_done,
            )
        else:
            self._finish_install()

    def _on_downloads_done(self, log: list) -> None:
        done = 0
        for entry_id, result in log:
            addon_id = self._code_to_addon.get(entry_id)
            addon = ADDON_CATALOG.get(addon_id or "", {})
            name = addon.get("name", str(entry_id))
            icon = addon.get("icon", "📦")

            if isinstance(result, InstallOk):
                self._install_log.append(f"   ✅  {icon} {name}  –  installiert")
                if addon_id:
                    self._install_results[addon_id] = True
                    self._newly_installed_ids.append(addon_id)
            else:
                errmsg = (
                    getattr(result, "errmsg", None)
                    or getattr(result, "exception", None)
                    or str(result)
                )
                self._install_log.append(f"   ❌  {icon} {name}  –  Fehler: {errmsg}")
                if addon_id:
                    self._install_results[addon_id] = False
            done += 1
            self._install_progress.setValue(done)

        ok = sum(1 for v in self._install_results.values() if v)
        fail = len(self._install_results) - ok
        self._install_status_lbl.setText(
            f"<b>Fertig: {ok} installiert"
            + (f", {fail} Fehler" if fail else "")
            + "</b>"
        )
        self._finish_install()

    def _finish_install(self) -> None:
        self._go_to_steps_then_overview()

    # -----------------------------------------------------------------------
    # Step routing
    # -----------------------------------------------------------------------

    def _go_to_steps_then_overview(self) -> None:
        """Show setup steps for freshly installed addons, then go to overview.
        Skips straight to overview if nothing was freshly downloaded."""
        self._setup_mode = "install"

        if not self._newly_installed_ids:
            self._back_to_overview()
            return

        self._step_queue = []
        for aid in self._newly_installed_ids:
            addon = ADDON_CATALOG.get(aid, {})
            for step in addon.get("setup_steps", []):
                if step.get("type") in ("instruction", "login"):
                    self._step_queue.append((aid, step))

        self._step_idx = -1
        if self._step_queue:
            self._advance_step()
        else:
            self._show_done()

    def _run_setup_for_addon(self, addon_id: str) -> None:
        """Run the instruction steps for one addon (manual re-run from Setup button)."""
        addon = ADDON_CATALOG.get(addon_id, {})
        steps = [
            step for step in addon.get("setup_steps", [])
            if step.get("type") in ("instruction", "login")
        ]
        if not steps:
            return
        self._setup_mode = "manual"
        self._step_queue = [(addon_id, step) for step in steps]
        self._step_idx = -1
        self._advance_step()

    def _back_to_overview(self) -> None:
        basic_ids = self._town_config.get("basic_addons", [])
        optional_ids = self._town_config.get("optional_addons", [])
        self._populate_addon_overview(basic_ids, optional_ids)
        self._go_to(PAGE_SELECT)

    # -----------------------------------------------------------------------
    # Step-by-step guidance
    # -----------------------------------------------------------------------

    def _advance_step(self) -> None:
        self._step_idx += 1
        if self._step_idx >= len(self._step_queue):
            if self._setup_mode == "manual":
                self._back_to_overview()
            else:
                self._show_done()
            return

        addon_id, step = self._step_queue[self._step_idx]
        addon = ADDON_CATALOG[addon_id]

        addon_steps = [(i, s) for i, (aid, s) in enumerate(self._step_queue) if aid == addon_id]
        pos_in_addon = next(
            p + 1 for p, (i, _) in enumerate(addon_steps) if i == self._step_idx
        )

        self._steps_addon_lbl.setText(f"{addon.get('icon', '')}  {addon['name']}")
        self._steps_progress_lbl.setText(
            f"Schritt {pos_in_addon} / {len(addon_steps)}"
            f"  •  Gesamt {self._step_idx + 1} / {len(self._step_queue)}"
        )
        self._steps_title_lbl.setText(step["title"])
        self._steps_desc.setPlainText(step.get("description", ""))

        if step.get("type") == "login":
            # Auto-skip if already logged in
            if step.get("skip_if_logged_in") and self._check_is_logged_in(
                step.get("auth_module", ""), step.get("is_logged_in_attr", "")
            ):
                self._advance_step()
                return
            self._steps_url_btn.hide()
            self._steps_login_btn.show()
            self._steps_login_status.hide()
        else:
            self._steps_login_btn.hide()
            self._steps_login_status.hide()
            url = step.get("button_url")
            self._current_step_url = url
            if url:
                self._steps_url_btn.setText(step.get("button_label", "Link öffnen"))
                self._steps_url_btn.show()
            else:
                self._steps_url_btn.hide()

        self._go_to(PAGE_STEPS)

    def _open_step_url(self) -> None:
        if self._current_step_url:
            QDesktopServices.openUrl(QUrl(self._current_step_url))

    def _on_steps_login_click(self) -> None:
        import sys
        _, step = self._step_queue[self._step_idx]
        mod = sys.modules.get(step.get("login_module", ""))
        if not mod:
            self._steps_login_status.setText(
                "⚠️  Add-on noch nicht geladen – starte Anki neu und öffne den Setup erneut."
            )
            self._steps_login_status.setStyleSheet("color:#e67e22;font-size:12px;padding:2px 0;")
            self._steps_login_status.show()
            return
        dlg_class = getattr(mod, step.get("login_dialog_class", ""), None)
        if dlg_class:
            dlg_class(mw).exec()
        logged_in = self._check_is_logged_in(
            step.get("auth_module", ""), step.get("is_logged_in_attr", "")
        )
        if logged_in:
            self._steps_login_status.setText("✅  Angemeldet!")
            self._steps_login_status.setStyleSheet("color:#27ae60;font-size:12px;padding:2px 0;")
        else:
            self._steps_login_status.setText("Noch nicht angemeldet.")
            self._steps_login_status.setStyleSheet("color:#7f8c8d;font-size:12px;padding:2px 0;")
        self._steps_login_status.show()

    # -----------------------------------------------------------------------
    # Completion
    # -----------------------------------------------------------------------

    def _show_done(self) -> None:
        installed = [
            ADDON_CATALOG[aid]["name"]
            for aid in self._newly_installed_ids
            if self._install_results.get(aid)
        ]
        failed = [
            ADDON_CATALOG[aid]["name"]
            for aid in self._newly_installed_ids
            if not self._install_results.get(aid)
        ]
        parts: List[str] = []
        if installed:
            parts.append(f"<b>Installiert:</b> {', '.join(installed)}")
        if failed:
            parts.append(
                f"<span style='color:#c0392b;'><b>Fehler bei:</b> {', '.join(failed)}</span>"
            )
        self._done_summary_lbl.setText("<br>".join(parts))
        self._go_to(PAGE_DONE)
