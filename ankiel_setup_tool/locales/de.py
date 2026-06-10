STRINGS = {
    # Window / header
    "window_title": "AnKiel",
    "header_title": "AnKiel Setup",
    "header_subtitle": "Add-ons installieren und einrichten",

    # Uni page
    "uni_heading": "Hochschule auswählen",
    "uni_subheading": "Wähle deine Uni oder deinen Standort",
    "uni_hint": "Add-ons für deinen Standort werden automatisch installiert.",
    "uni_search_placeholder": "🔍  Suchen…",

    # Install step template (generated dynamically, not stored in addons.json)
    "step_install_title": "{name} installieren",
    "step_install_description": "Das Add-on {name} wird heruntergeladen und installiert.",

    # Install page — status labels
    "install_status_default": "Installiere Add-ons…",
    "install_status_downloading": "Lade {count} Paket(e) herunter…",
    "install_status_nothing": "Nichts zu installieren.",
    "install_status_done_ok": "Fertig: {ok} installiert",
    "install_status_done_errors": ", {fail} Fehler",

    # Install page — log entries
    "install_log_downloading": "⏳  {icon} {name}  –  wird heruntergeladen…",
    "install_log_already": "ℹ️   {icon} {name}  –  bereits installiert",
    "install_log_ok": "   ✅  {icon} {name}  –  installiert",
    "install_log_error": "   ❌  {icon} {name}  –  Fehler: {errmsg}",

    # Select page
    "select_heading": "Übersicht & weitere Add-ons",
    "select_subheading": "Add-ons verwalten, anmelden & weitere installieren",
    "select_btn_all": "Alle auswählen",
    "select_btn_none": "Keine",
    "select_section_basics": "✅  Basics – automatisch installiert",
    "select_section_optional": "➕  Weitere Add-ons (optional)",

    # Addon card — badges
    "badge_installed": "✓ Installiert",
    "badge_disabled": "⚠ Deaktiviert",
    "badge_account_needed": "Account nötig",
    "badge_external_login": "Externer Login",
    "badge_logged_in": "✓ Angemeldet",

    # Addon card — buttons
    "btn_card_login": "Anmelden",
    "btn_card_setup": "Anleitung",
    "btn_card_update": "Updates prüfen",
    "btn_card_uninstall": "Deinstallieren",

    # Steps page
    "steps_progress": "Schritt {pos} / {total}",
    "steps_progress_overall": "  •  Gesamt {current} / {total}",
    "steps_url_btn_default": "Link öffnen",

    # Done page
    "done_title": "Installation abgeschlossen!",
    "done_restart_note": "Neu installierte Add-ons sind erst nach einem Neustart aktiv.",
    "done_restart_btn": "Anki neu starten",
    "done_installed": "<b>Installiert:</b> {names}",
    "done_failed": "<span style='color:#c0392b;'><b>Fehler bei:</b> {names}</span>",

    # Update page
    "update_check_btn": "🔍 Auf Updates prüfen",
    "update_installed_date": "Version vom: {date}",
    "update_last_checked": "Zuletzt geprüft: {date}",
    "update_never_checked": "Noch nicht geprüft",
    "update_installed_by_ankiel": "Aktuelle Version installiert am: {date}",
    "update_checking": "⏳  Prüfe auf Updates…",
    "update_log_updated": "✅  Update installiert  (Stand: {date})",
    "update_log_current": "✅  Bereits auf dem neuesten Stand (Version: {date})",
    "update_log_update_found": "⬇  Update gefunden ({old_date} → {new_date}) – wird heruntergeladen…",
    "update_log_downloaded": "✅  Download abgeschlossen",
    "update_log_error": "❌  Fehler: {errmsg}",
    "update_log_restart": "⚠️  Starte Anki neu, damit das Update aktiv wird.",
    "update_hint": "💡 Nach einer Aktualisierung muss Anki neu gestartet werden, damit das Update aktiv wird.",

    # Nav bar — button labels
    "nav_back": "← Zurück",
    "nav_skip": "Überspringen",
    "nav_login": "🔑 Anmelden",
    "nav_next": "Weiter →",
    "nav_overview": "Zur Übersicht",
    "nav_next_step": "Nächster Schritt →",
    "nav_installing": "Installiere…",
    "nav_install": "Installieren →",

    # Messages / tooltips
    "tooltip_addon_disabled": (
        "Dieses Add-on ist in Anki deaktiviert.\n"
        "Zum Reaktivieren: Extras → Erweiterungen →\n"
        "Aktivieren/Deaktivieren → Anki neu starten."
    ),
    "msg_select_uni": "Bitte wähle eine Hochschule aus.",
    "msg_confirm_uninstall": "Möchtest du '{name}' wirklich deinstallieren?",
    "msg_addon_not_loaded": "Das Add-on ist noch nicht geladen. Starte Anki neu.",
    "msg_addon_not_loaded_nav": "⚠️  Add-on noch nicht geladen – starte Anki neu.",
    "msg_logged_in": "✅  Angemeldet!",
    "msg_not_logged_in": "Noch nicht angemeldet.",
}
