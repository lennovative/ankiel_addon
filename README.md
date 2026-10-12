# AnKiel Setup Tool

Einrichtungsassistent für Anki, entwickelt fürs Medizinstudium an deutschen Universitäten. Nach Auswahl des Standorts installiert das Tool die passenden Add-ons und begleitet Kontoerstellung, Login und Konfiguration.

> [English version below](#ankiel-setup-tool-1)

---

## Funktionen

- Wähle deine Universität – die passenden Add-ons werden nach deiner Bestätigung installiert
- Schritt-für-Schritt-Anleitung für jedes Add-on, inklusive Account-Anmeldung
- Übersicht aller Add-ons: Updates prüfen, Anleitungen erneut öffnen, deinstallieren

### Unterstützte Add-ons

- [Ankizin](https://www.ankizin.de)
- [AMBOSS](https://www.amboss.com)
- [AnkiCollab](https://www.ankicollab.com)
- [AnkiHub](https://www.ankihub.net)
- [Meditricks](https://www.meditricks.de/anki/)
- [Image Occlusion Enhanced](https://ankiweb.net/shared/info/1374772155)
- [Review Heatmap](https://ankiweb.net/shared/info/1771074083)
- [AnkiConnect](https://ankiweb.net/shared/info/2055492159)

---

## Installation

1. `ankiel_setup_tool.ankiaddon` vom [neuesten Release](../../releases/latest) herunterladen.
2. In Anki: **Extras → Erweiterungen → Aus Datei installieren...** → heruntergeladene Datei auswählen.
3. Anki neu starten. Das Tool öffnet sich automatisch.

**Voraussetzung:** Anki 2.1.49 oder neuer.

---
---

# AnKiel Setup Tool

Setup wizard for Anki, built for medical students at German universities. After selecting a location, the tool installs the matching add-ons and walks through account creation, login, and configuration for each of them.

---

## Features

- Select your university – the matching add-ons are installed once you confirm
- Step-by-step instructions for each add-on, including account login where needed
- Overview of all add-ons: check for updates, reopen setup guides, uninstall

### Supported add-ons

- [Ankizin](https://www.ankizin.de)
- [AMBOSS](https://www.amboss.com)
- [AnkiCollab](https://www.ankicollab.com)
- [AnkiHub](https://www.ankihub.net)
- [Meditricks](https://www.meditricks.de/anki/)
- [Image Occlusion Enhanced](https://ankiweb.net/shared/info/1374772155)
- [Review Heatmap](https://ankiweb.net/shared/info/1771074083)
- [AnkiConnect](https://ankiweb.net/shared/info/2055492159)

---

## Installation

1. Download `ankiel_setup_tool.ankiaddon` from the [latest release](../../releases/latest).
2. In Anki: **Tools → Add-ons → Install from file...** → select the downloaded file.
3. Restart Anki. The tool opens automatically.

**Requirement:** Anki 2.1.49 or later.

---
---

# Development

```bash
# Copy add-on into local Anki addons folder
cp -r ankiel_setup_tool ~/.local/share/Anki2/addons21/

# Build a distributable .ankiaddon file
bash build_addon.sh
```

---

## Adding a university

Create `ankiel_setup_tool/configs/<id>.json`:

```json
{
  "id": "your_uni",
  "name": "Your University",
  "description": "Short description shown in the list",
  "icon": "🎓",
  "basic_addons": ["ankizin", "ankicollab"],
  "optional_addons": ["amboss", "image_occlusion", "review_heatmap", "ankiconnect", "meditricks"]
}
```

The file is picked up automatically. `basic_addons` are listed for confirmation after the university is selected and installed once the user agrees; `optional_addons` are offered on the overview page.

---

## Adding an add-on

Add an entry to `ankiel_setup_tool/configs/addons.json` under `"addons"`:

```json
"my_addon": {
  "id": "my_addon",
  "name": "My Add-on",
  "subtitle": "One-line description",
  "description": "Longer description shown on the card.",
  "category": "tools",
  "icon": "🔌",
  "addon_codes": ["1234567890"],
  "requires_account": false,
  "external_url": "https://example.com",
  "setup_steps": []
}
```

Available categories are defined in the `"categories"` block of the same file (`deck_platforms`, `learning`, `tools`).

**Setup steps** are shown in the guided wizard after installation — plain instruction objects, no type field:

```json
"setup_steps": [
  {
    "title": "Step title",
    "description": "What the user should do.",
    "button_label": "Open website",
    "button_url": "https://example.com"
  }
]
```

**If the add-on requires a login**, add a top-level `"login"` block. The wizard automatically inserts it as the first step in the setup flow:

```json
"login": {
  "title": "Log in",
  "description": "Log in with your account.",
  "skip_if_logged_in": true,
  "button_label": "Sign up",
  "button_url": "https://example.com/signup",
  "login_module": "1234567890.dialogs",
  "login_dialog_class": "LoginDialog",
  "auth_module": "1234567890.auth",
  "is_logged_in_attr": "auth_manager.is_logged_in"
}
```

If `requires_account` is true but no `"login"` block is present, the add-on is treated as handling login externally (e.g. through its own menu). The wizard shows an "external login" badge but no login button.

Optionally add a `"post_login_hook"` inside the `"login"` block to trigger a UI refresh in the add-on after a successful login:

```json
"post_login_hook": {
  "module": "1234567890.menu",
  "function": "update_ui_for_login_state"
}
```

Hooks call `function` in the add-on's already loaded `module`. `function` may be a dotted path to a method (e.g. `"some_service.start"`), and an optional `"kwargs"` object is passed as keyword arguments.

**If the newest version is not on AnkiWeb** (e.g. AMBOSS), add a `"download_url"` pointing to the `.ankiaddon` file. `addon_codes` then holds the package (folder) name from that file's `manifest.json`, and `"replaces"` lists older installs (e.g. the AnkiWeb code) that are removed after a successful install, keeping their config. The update check compares that file with the installed version and never downgrades an add-on that updated itself:

```json
"addon_codes": ["0amboss_addon"],
"download_url": "https://integrations-cdn.amboss.com/amboss-de-v0.11.2.ankiaddon",
"replaces": ["1044112126"]
```

`download_url` then only decides the version for new installs; bumping it is optional if the add-on updates itself.

**If the add-on has its own updater**, add an `"update_hook"` so "Auf Updates prüfen" hands the check to it instead of using AnkiWeb or `download_url`. With `"requires_login": true` this only happens while the user is logged in (checked via the `"login"` block); otherwise, and whenever the add-on isn't loaded yet, the built-in check runs:

```json
"update_hook": {
  "module": "0amboss_addon.addon",
  "function": "update_notification_service.start",
  "kwargs": {"interactive": true},
  "requires_login": true
}
```

Once added to `addons.json`, the add-on can be referenced by its `id` in any university config's `optional_addons` list.

---
---