# AnKiel Setup Tool

Anki setup wizard for medical students. Installs and configures the right add-ons for your university in one go.

---

## Features

- **University-aware setup** — selects and installs the right add-ons for your location automatically
- **Guided install wizard** — step-by-step instructions for each add-on, including login flows for AMBOSS, AnkiCollab, and others
- **Overview page** — manage all installed add-ons from one place: re-run setup, check for updates, uninstall
- **Auto-start on first launch** — opens automatically when it is the only add-on installed
- **Restart flow** — triggers a clean Anki restart after install and resumes right where it left off

### Supported add-ons

The following add-ons are currently supported. More will be added over time.

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

### From a release file (recommended)

1. Download `ankiel_setup_tool.ankiaddon` from the [latest release](../../releases/latest).
2. In Anki: **Tools → Add-ons → Install from file…** → select the downloaded file.
3. Restart Anki. The tool opens automatically.

### Manual (from source)

```bash
git clone https://github.com/lennovative/ankiel_addon.git
cp -r ankiel_addon/ankiel_setup_tool ~/.local/share/Anki2/addons21/
```

Restart Anki.

---

## Requirements

- Anki **2.1.49** or later (Qt 6 / PyQt6)
- Tested on Linux. macOS and Windows should work but are not yet verified.

---

## Adding a university

Create a file `ankiel_setup_tool/configs/<id>.json`:

```json
{
  "id": "your_uni",
  "name": "Your University",
  "description": "Short description shown in the list",
  "icon": "🎓",
  "basic_addons": ["ankizin", "amboss"],
  "optional_addons": ["ankihub", "ankicollab", "image_occlusion", "review_heatmap", "ankiconnect", "meditricks"]
}
```

The file is picked up automatically — no code changes needed. `basic_addons` are installed automatically after the university is selected; `optional_addons` are offered on the overview page.

Pull requests for additional universities are welcome.

---

## Development

```bash
# Run from repo root — copies the add-on into your local Anki addons folder
cp -r ankiel_setup_tool ~/.local/share/Anki2/addons21/

# Build a distributable .ankiaddon file
bash build_addon.sh
```

The add-on is structured as follows:

```
ankiel_setup_tool/
  __init__.py          startup hooks, toolbar/menu registration
  wizard.py            main QDialog wizard
  addon_defs.py        loads addons.json into ADDON_CATALOG
  config_loader.py     loads university configs and persists state
  installer.py         checks whether an add-on is installed
  configs/
    addons.json        add-on definitions (codes, login specs, setup steps)
    kiel.json          university config for Kiel / UKSH
  locales/
    de.py              all user-visible strings (German)
    __init__.py        exposes T dict for use in wizard.py
  manifest.json        Anki package metadata
```

---

## License

MIT
