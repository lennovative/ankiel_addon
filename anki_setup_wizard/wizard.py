"""
Main wizard dialog for the Anki Setup Wizard add-on.

Pages (QStackedWidget indices):
  0  Select   – per-addon checkboxes
  1  Install  – download/install progress log
  2  Steps    – guided setup instructions per add-on
  3  Done     – summary + restart reminder
"""

from __future__ import annotations

from typing import Dict, List, Optional, Tuple

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

PAGE_SELECT = 0
PAGE_INSTALL = 1
PAGE_STEPS = 2
PAGE_DONE = 3

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
# Addon card widget
# ===========================================================================

class _AddonCard(QFrame):
    """Clickable card with checkbox for one add-on."""

    def __init__(self, addon_data: dict, addons_folder: str, parent: QWidget = None) -> None:
        super().__init__(parent)
        self._addon_data = addon_data
        self.setFrameShape(_FRAME_STYLED)
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

        self._checkbox = QCheckBox()
        self._checkbox.setFixedSize(22, 22)
        row.addWidget(self._checkbox)

        icon_lbl = QLabel(addon_data.get("icon", "📦"))
        icon_lbl.setStyleSheet("font-size:26px;min-width:34px;max-width:34px;")
        row.addWidget(icon_lbl)

        txt = QVBoxLayout()
        txt.setSpacing(1)
        name_lbl = QLabel(
            f"<b>{addon_data['name']}</b>"
            f"  <span style='color:#7f8c8d;font-size:10px;'>#{addon_data['addon_codes'][0]}</span>"
        )
        name_lbl.setStyleSheet("font-size:13px;")
        subtitle_lbl = QLabel(addon_data.get("subtitle", ""))
        subtitle_lbl.setStyleSheet("color:#7f8c8d;font-size:11px;")
        desc_lbl = QLabel(addon_data["description"])
        desc_lbl.setWordWrap(True)
        desc_lbl.setStyleSheet("color:#555;font-size:11px;margin-top:2px;")
        txt.addWidget(name_lbl)
        txt.addWidget(subtitle_lbl)
        txt.addWidget(desc_lbl)
        row.addLayout(txt, stretch=1)

        badges = QVBoxLayout()
        badges.setSpacing(4)
        badges.setAlignment(_ALIGN_TOP | _ALIGN_RIGHT)

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
            badges.addWidget(b)
        if addon_data.get("requires_account"):
            b2 = QLabel("Account nötig")
            b2.setStyleSheet(
                "background:#fef9e7;color:#9a7d0a;padding:2px 7px;"
                "border-radius:9px;font-size:10px;"
            )
            badges.addWidget(b2)
        badges.addStretch()
        row.addLayout(badges)

    def mousePressEvent(self, event) -> None:  # type: ignore[override]
        cb_pos = self._checkbox.mapFromParent(event.pos())
        if not self._checkbox.rect().contains(cb_pos):
            self._checkbox.setChecked(not self._checkbox.isChecked())
        super().mousePressEvent(event)

    def is_checked(self) -> bool:
        return self._checkbox.isChecked()

    def set_checked(self, v: bool) -> None:
        self._checkbox.setChecked(v)

    def addon_id(self) -> str:
        return self._addon_data["id"]


# ===========================================================================
# Main wizard
# ===========================================================================

class AnkiSetupWizard(QDialog):

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Anki Setup Wizard")
        self.setMinimumSize(720, 560)
        self.resize(760, 640)

        self._addons_folder: str = mw.addonManager.addonsFolder()
        self._selected_ids: List[str] = []
        self._install_results: Dict[str, bool] = {}
        # maps AnkiWeb numeric code → our addon_id key
        self._code_to_addon: Dict[int, str] = {}

        self._step_queue: List[Tuple[str, dict]] = []
        self._step_idx: int = -1
        self._current_step_url: Optional[str] = None

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        self._build_header(outer)

        self._stack = QStackedWidget()
        outer.addWidget(self._stack, stretch=1)

        self._stack.addWidget(self._build_select_page())   # 0
        self._stack.addWidget(self._build_install_page())  # 1
        self._stack.addWidget(self._build_steps_page())    # 2
        self._stack.addWidget(self._build_done_page())     # 3

        self._build_nav_bar(outer)
        self._go_to(PAGE_SELECT)

    # -----------------------------------------------------------------------
    # Header
    # -----------------------------------------------------------------------

    def _build_header(self, parent: QVBoxLayout) -> None:
        hdr = QFrame()
        hdr.setStyleSheet(
            "QFrame{background:qlineargradient("
            "x1:0,y1:0,x2:1,y2:0,stop:0 #1a252f,stop:1 #2980b9);"
            "min-height:60px;max-height:60px;}"
        )
        hl = QHBoxLayout(hdr)
        hl.setContentsMargins(22, 0, 22, 0)
        title = QLabel("🎓  Anki Setup Wizard")
        title.setStyleSheet("color:white;font-size:19px;font-weight:bold;")
        sub = QLabel("Add-ons installieren und einrichten")
        sub.setStyleSheet("color:#85c1e9;font-size:11px;")
        col = QVBoxLayout()
        col.setSpacing(2)
        col.addWidget(title)
        col.addWidget(sub)
        hl.addLayout(col)
        hl.addStretch()
        parent.addWidget(hdr)

    # -----------------------------------------------------------------------
    # Pages
    # -----------------------------------------------------------------------

    def _build_select_page(self) -> QWidget:
        page = QWidget()
        vl = QVBoxLayout(page)
        vl.setContentsMargins(18, 12, 18, 8)
        vl.setSpacing(6)

        top = QLabel(
            "<b style='font-size:14px;'>Add-ons auswählen</b>"
            "  <span style='color:#7f8c8d;font-size:11px;'>"
            "– Klicke auf eine Karte, um sie auszuwählen</span>"
        )
        vl.addWidget(top)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(_FRAME_NONE)

        inner = QWidget()
        il = QVBoxLayout(inner)
        il.setContentsMargins(2, 2, 2, 2)
        il.setSpacing(3)

        self._addon_cards: List[_AddonCard] = []

        for cat_id, cat_info in CATEGORIES.items():
            cat_lbl = QLabel(cat_info["label"])
            cat_lbl.setStyleSheet(
                f"color:{cat_info['color']};font-weight:bold;"
                "font-size:12px;padding:6px 2px 1px 2px;"
            )
            il.addWidget(cat_lbl)
            for addon_id, addon_data in ADDON_CATALOG.items():
                if addon_data.get("category") != cat_id:
                    continue
                card = _AddonCard(addon_data, self._addons_folder)
                il.addWidget(card)
                self._addon_cards.append(card)

        il.addStretch()
        scroll.setWidget(inner)
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

        self._btn_next = QPushButton("Installieren →")
        self._btn_next.setStyleSheet(_BTN_PRIMARY)
        self._btn_next.clicked.connect(self._on_next)
        hl.addWidget(self._btn_next)

        parent.addWidget(bar)

    def _go_to(self, page: int) -> None:
        self._stack.setCurrentIndex(page)
        self._update_nav()

    def _update_nav(self) -> None:
        page = self._stack.currentIndex()
        self._btn_back.setVisible(page == PAGE_SELECT)
        self._btn_back.setEnabled(False)  # only one page before install; nowhere to go back to
        self._btn_skip.setVisible(page == PAGE_STEPS)

        if page == PAGE_DONE:
            self._btn_next.setText("Schließen ✓")
            self._btn_next.setEnabled(True)
        elif page == PAGE_STEPS:
            self._btn_next.setText("Nächster Schritt →")
            self._btn_next.setEnabled(True)
        elif page == PAGE_INSTALL:
            self._btn_next.setText("Installiere…")
            self._btn_next.setEnabled(False)
        else:
            self._btn_next.setText("Installieren →")
            self._btn_next.setEnabled(True)

    # -----------------------------------------------------------------------
    # Navigation actions
    # -----------------------------------------------------------------------

    def _on_back(self) -> None:
        pass  # back button only shows on SELECT; nowhere to go back to

    def _on_next(self) -> None:
        page = self._stack.currentIndex()
        if page == PAGE_DONE:
            self.accept()
        elif page == PAGE_SELECT:
            ids = [c.addon_id() for c in self._addon_cards if c.is_checked()]
            if not ids:
                tooltip("Bitte wähle mindestens ein Add-on aus.")
                return
            self._selected_ids = ids
            self._start_install()
        elif page == PAGE_STEPS:
            self._advance_step()

    # -----------------------------------------------------------------------
    # Installation via Anki's own download_addons
    # -----------------------------------------------------------------------

    def _start_install(self) -> None:
        self._go_to(PAGE_INSTALL)
        self._install_log.clear()
        self._install_results = {}
        self._code_to_addon = {}

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
        """Called by Anki's download_addons when all downloads + installs are done."""
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
            else:
                errmsg = getattr(result, "errmsg", None) or getattr(result, "exception", str(result))
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
        self._step_queue = []
        for aid in self._selected_ids:
            addon = ADDON_CATALOG.get(aid, {})
            for step in addon.get("setup_steps", []):
                if step.get("type") == "instruction":
                    self._step_queue.append((aid, step))

        self._step_idx = -1
        if self._step_queue:
            self._advance_step()
        else:
            self._show_done()

    # -----------------------------------------------------------------------
    # Step-by-step guidance
    # -----------------------------------------------------------------------

    def _advance_step(self) -> None:
        self._step_idx += 1
        if self._step_idx >= len(self._step_queue):
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

    # -----------------------------------------------------------------------
    # Completion
    # -----------------------------------------------------------------------

    def _show_done(self) -> None:
        installed = [
            ADDON_CATALOG[aid]["name"]
            for aid in self._selected_ids
            if self._install_results.get(aid)
        ]
        failed = [
            ADDON_CATALOG[aid]["name"]
            for aid in self._selected_ids
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
