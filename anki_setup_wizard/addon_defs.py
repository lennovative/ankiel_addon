"""
Catalogue of supported add-ons and their guided-setup steps.

Each entry in ADDON_CATALOG has:
  id            - unique key
  name          - display name
  subtitle      - one-line tagline
  description   - longer description
  category      - key into CATEGORIES
  icon          - emoji icon
  addon_codes   - list of AnkiWeb numeric IDs to install
  requires_account - bool: user needs an external account
  external_url  - link to homepage / AnkiWeb page
  setup_steps   - list of steps; each step has:
      type        "install" | "instruction"
      title       heading text
      description body text (plain, use \n for newlines)
      codes       (install only) list of codes to install
      button_label (instruction only, optional) button text
      button_url   (instruction only, optional) URL to open
"""

from __future__ import annotations

ADDON_CATALOG: dict = {
    # ------------------------------------------------------------------ #
    #  German Medical                                                      #
    # ------------------------------------------------------------------ #
    "ankizin": {
        "id": "ankizin",
        "name": "AnkiZin",
        "subtitle": "Medizinkarten für das deutsche Studium",
        "description": (
            "Umfassendes Kartenset auf Basis der AMBOSS-Bibliothek und des "
            "100-Tage-Lernplans. Enthält eigene Notiztypen und einen "
            "integrierten Lernplan-Manager."
        ),
        "category": "german_medical",
        "icon": "🏥",
        "addon_codes": ["2058530482"],
        "requires_account": False,
        "external_url": "https://www.ankizin.de",
        "setup_steps": [
            {
                "type": "install",
                "title": "AnkiZin Add-on installieren",
                "description": "Das AnkiZin Add-on (Notiztypen + Lernplan-Manager) wird installiert.",
                "codes": ["2058530482"],
            },
            {
                "type": "instruction",
                "title": "AnkiZin Deck herunterladen",
                "description": (
                    "1. Besuche die AnkiZin-Website (Button unten).\n"
                    "2. Lade das aktuelle Deck herunter (.apkg-Datei).\n"
                    "3. Öffne die Datei → Anki importiert Deck + Notiztypen automatisch.\n"
                    "   (alternativ: Datei → Importieren, Strg+Shift+I)"
                ),
                "button_label": "AnkiZin Website öffnen",
                "button_url": "https://www.ankizin.de/wiki/ankizin-deck-installieren/",
            },
            {
                "type": "instruction",
                "title": "Karten aussetzen & Datenbank prüfen",
                "description": (
                    "Nach dem Import:\n\n"
                    "1. Öffne den Karten-Browser (B oder Strg+B).\n"
                    "2. Suche nach:  #Ankizin_v5\n"
                    "3. Alle auswählen (Strg+A) → Rechtsklick → Aussetzen.\n"
                    "4. Suche nach:  !DELETE  → alle auswählen → Löschen.\n"
                    "5. Werkzeuge → Leere Karten löschen → Bestätigen.\n"
                    "6. Werkzeuge → Datenbank überprüfen → Bestätigen.\n\n"
                    "Danach aktivierst du Themen gezielt über Tags (z. B. nach Lernplan-Tag)."
                ),
            },
        ],
    },

    "ankihub": {
        "id": "ankihub",
        "name": "AnkiHub",
        "subtitle": "Kollaborative Deck-Updates",
        "description": (
            "AnkiHub hält deine Decks automatisch aktuell und ermöglicht "
            "gemeinschaftliche Karten-Verbesserungen. Wird für viele "
            "Community-Decks (z. B. AnkiZin) benötigt."
        ),
        "category": "german_medical",
        "icon": "🔄",
        "addon_codes": ["1322529746"],
        "requires_account": True,
        "external_url": "https://www.ankihub.net",
        "setup_steps": [
            {
                "type": "instruction",
                "title": "AnkiHub Account erstellen",
                "description": (
                    "1. Besuche app.ankihub.net/accounts/signup/ (Button unten).\n"
                    "2. Erstelle einen kostenlosen Account.\n"
                    "3. Beantrage eine kostenlose Scholarship:\n"
                    "   app.ankihub.net/scholarship-requirement/\n"
                    "   (Du kannst 0 € eingeben. Freigabe dauert 24–48 h.)"
                ),
                "button_label": "AnkiHub Registrierung öffnen",
                "button_url": "https://app.ankihub.net/accounts/signup/",
            },
            {
                "type": "install",
                "title": "AnkiHub Add-on installieren",
                "description": "Das AnkiHub Add-on wird installiert.",
                "codes": ["1322529746"],
            },
            {
                "type": "instruction",
                "title": "In AnkiHub einloggen",
                "description": (
                    "Nach dem Neustart von Anki:\n\n"
                    "1. Das AnkiHub-Fenster öffnet sich automatisch.\n"
                    "2. Logge dich mit deinen AnkiHub-Zugangsdaten ein.\n"
                    "3. Abonniere gewünschte Decks über das AnkiHub-Menü\n"
                    "   in der Werkzeuge-Leiste."
                ),
            },
        ],
    },

    "amboss": {
        "id": "amboss",
        "name": "AMBOSS",
        "subtitle": "Medizinische Referenz direkt in Anki",
        "description": (
            "Hover über Fachbegriffe in deinen Karten und erhalte sofort "
            "Erklärungen aus der AMBOSS-Bibliothek. Erfordert einen "
            "AMBOSS-Account (kostenpflichtig oder Unizugang)."
        ),
        "category": "german_medical",
        "icon": "📚",
        "addon_codes": ["1044112126"],
        "requires_account": True,
        "external_url": "https://www.amboss.com",
        "setup_steps": [
            {
                "type": "install",
                "title": "AMBOSS Add-on installieren",
                "description": "Das AMBOSS Add-on für Anki wird installiert.",
                "codes": ["1044112126"],
            },
            {
                "type": "instruction",
                "title": "AMBOSS-Account verknüpfen",
                "description": (
                    "Nach dem Neustart:\n\n"
                    "1. Klicke auf das AMBOSS-Icon in der Werkzeuge-Leiste\n"
                    "   (oder Werkzeuge → AMBOSS → Einstellungen).\n"
                    "2. Logge dich mit deinen AMBOSS-Zugangsdaten ein.\n"
                    "3. Das Add-on verbindet sich automatisch.\n\n"
                    "Beim Lernen: Hover über hervorgehobene Begriffe\n"
                    "für sofortige AMBOSS-Pop-ups."
                ),
                "button_label": "AMBOSS Website",
                "button_url": "https://www.amboss.com",
            },
        ],
    },

    "meditricks": {
        "id": "meditricks",
        "name": "Meditricks",
        "subtitle": "Eselsbrücken-Videos direkt in Anki",
        "description": (
            "Zeigt passende Meditricks-Gedächtnisstützen direkt in deinen "
            "Anki-Karten an. Perfekt in Kombination mit dem AnkiZin-Deck. "
            "Erfordert einen Meditricks-Account."
        ),
        "category": "german_medical",
        "icon": "🧠",
        "addon_codes": ["1110557695"],
        "requires_account": True,
        "external_url": "https://www.meditricks.de/anki/",
        "setup_steps": [
            {
                "type": "install",
                "title": "Meditricks Add-on installieren",
                "description": "Das Meditricks Add-on wird installiert.",
                "codes": ["1110557695"],
            },
            {
                "type": "instruction",
                "title": "Meditricks-Account verknüpfen",
                "description": (
                    "Nach dem Neustart:\n\n"
                    "1. Gehe zu Werkzeuge → Meditricks.\n"
                    "2. Logge dich mit deinen Meditricks-Zugangsdaten ein.\n"
                    "3. Die Eselsbrücken erscheinen automatisch in kompatiblen\n"
                    "   AnkiZin-Karten während des Lernens."
                ),
                "button_label": "Meditricks Website",
                "button_url": "https://www.meditricks.de/anki/",
            },
        ],
    },

    # ------------------------------------------------------------------ #
    #  Collaboration                                                        #
    # ------------------------------------------------------------------ #
    "ankicollab": {
        "id": "ankicollab",
        "name": "AnkiCollab",
        "subtitle": "Kollaborative Deck-Plattform",
        "description": (
            "Abonniere und verbessere Anki-Decks gemeinsam mit anderen. "
            "Ideal für uni-spezifische Karten und gemeinsame Korrekturen. "
            "Kostenfrei nutzbar."
        ),
        "category": "collaboration",
        "icon": "🤝",
        "addon_codes": ["1957538407"],
        "requires_account": True,
        "external_url": "https://www.ankicollab.com",
        "setup_steps": [
            {
                "type": "install",
                "title": "AnkiCollab installieren",
                "description": "Das AnkiCollab Add-on wird heruntergeladen und installiert.",
                "codes": ["1957538407"],
            },
            {
                "type": "instruction",
                "title": "AnkiCollab Account erstellen",
                "description": (
                    "1. Besuche ankicollab.com/Login (Button unten).\n"
                    "2. Klicke auf 'Sign Up Here' und erstelle einen\n"
                    "   kostenlosen Account.\n"
                    "3. Bestätige deine E-Mail-Adresse."
                ),
                "button_label": "AnkiCollab.com öffnen",
                "button_url": "https://www.ankicollab.com/Login",
            },
            {
                "type": "instruction",
                "title": "In Anki einloggen",
                "description": (
                    "Nach dem Neustart von Anki:\n\n"
                    "1. Klicke in der Menüleiste auf 'AnkiCollab'.\n"
                    "2. Wähle 'Login' und gib deine Zugangsdaten ein.\n"
                    "3. Nach dem Login erscheint ✓ neben 'AnkiCollab'."
                ),
            },
            {
                "type": "instruction",
                "title": "Deck abonnieren",
                "description": (
                    "1. Besuche ankicollab.com/Decks (Button unten).\n"
                    "2. Suche nach dem gewünschten Deck.\n"
                    "3. Klicke auf den Deck-Namen und kopiere den\n"
                    "   Subscription Key (blauer Text oben).\n"
                    "4. In Anki: AnkiCollab → Edit Subscriptions\n"
                    "   → Key einfügen → 'Add Subscription'.\n\n"
                    "Tipp: Aktiviere 'Update Decks on startup' für\n"
                    "automatische Updates."
                ),
                "button_label": "Decks durchsuchen",
                "button_url": "https://www.ankicollab.com/Decks",
            },
        ],
    },

    # ------------------------------------------------------------------ #
    #  Utility                                                             #
    # ------------------------------------------------------------------ #
    "image_occlusion": {
        "id": "image_occlusion",
        "name": "Image Occlusion Enhanced",
        "subtitle": "Bildbasierte Lernkarten erstellen",
        "description": (
            "Überdecke Teile eines Bildes und teste dich auf das Verdeckte. "
            "Unverzichtbar für Anatomie, Biochemie-Diagramme und alle "
            "visuellen Lerninhalte."
        ),
        "category": "utility",
        "icon": "🖼️",
        "addon_codes": ["1374772155"],
        "requires_account": False,
        "external_url": "https://ankiweb.net/shared/info/1374772155",
        "setup_steps": [
            {
                "type": "install",
                "title": "Image Occlusion Enhanced installieren",
                "description": "Das Add-on wird installiert. Kein weiterer Setup-Schritt nötig.",
                "codes": ["1374772155"],
            },
        ],
    },

    "review_heatmap": {
        "id": "review_heatmap",
        "name": "Review Heatmap",
        "subtitle": "Lernaktivität visualisieren",
        "description": (
            "Zeigt eine GitHub-ähnliche Heatmap deiner täglichen Lernaktivität "
            "im Anki-Hauptfenster. Motivierend und hilfreich für die "
            "Lernplanung."
        ),
        "category": "utility",
        "icon": "📊",
        "addon_codes": ["1771074083"],
        "requires_account": False,
        "external_url": "https://ankiweb.net/shared/info/1771074083",
        "setup_steps": [
            {
                "type": "install",
                "title": "Review Heatmap installieren",
                "description": "Das Add-on wird installiert. Kein weiterer Setup-Schritt nötig.",
                "codes": ["1771074083"],
            },
        ],
    },

    "ankiconnect": {
        "id": "ankiconnect",
        "name": "AnkiConnect",
        "subtitle": "API-Schnittstelle für externe Tools",
        "description": (
            "Ermöglicht externen Programmen (Browser-Erweiterungen, Yomitan, "
            "eigene Skripte) die Kommunikation mit Anki. Wird von vielen "
            "anderen Tools vorausgesetzt."
        ),
        "category": "utility",
        "icon": "🔌",
        "addon_codes": ["2055492159"],
        "requires_account": False,
        "external_url": "https://ankiweb.net/shared/info/2055492159",
        "setup_steps": [
            {
                "type": "install",
                "title": "AnkiConnect installieren",
                "description": "AnkiConnect wird installiert.",
                "codes": ["2055492159"],
            },
            {
                "type": "instruction",
                "title": "AnkiConnect läuft automatisch",
                "description": (
                    "Nach dem Neustart läuft AnkiConnect automatisch\n"
                    "als lokaler Server auf localhost:8765.\n\n"
                    "Keine weitere Konfiguration notwendig.\n"
                    "Einstellungen: Werkzeuge → Add-ons → AnkiConnect\n"
                    "→ Konfiguration (z. B. erlaubte Herkunftsdomains)."
                ),
            },
        ],
    },
}

CATEGORIES: dict = {
    "german_medical": {
        "label": "🏥  Medizinstudium (Deutsch)",
        "description": "Add-ons speziell für das deutsche Medizinstudium",
        "color": "#c0392b",
    },
    "collaboration": {
        "label": "🤝  Kollaboration & Sync",
        "description": "Gemeinsames Arbeiten an und Teilen von Decks",
        "color": "#2980b9",
    },
    "utility": {
        "label": "⚡  Nützliche Tools",
        "description": "Allgemeine Verbesserungen für Anki",
        "color": "#27ae60",
    },
}

PRESETS: dict = {
    "german_medical": {
        "label": "🏥  Medizinstudium (Deutsch)",
        "tooltip": "AnkiZin, AnkiHub, AMBOSS, Meditricks, Image Occlusion, Review Heatmap",
        "addons": ["ankizin", "ankihub", "amboss", "meditricks", "image_occlusion", "review_heatmap"],
    },
    "collab": {
        "label": "🤝  Kollaboration",
        "tooltip": "AnkiCollab + AnkiHub",
        "addons": ["ankicollab", "ankihub"],
    },
    "essential": {
        "label": "⚡  Basis-Tools",
        "tooltip": "Image Occlusion Enhanced, Review Heatmap, AnkiConnect",
        "addons": ["image_occlusion", "review_heatmap", "ankiconnect"],
    },
}
