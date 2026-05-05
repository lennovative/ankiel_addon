#!/usr/bin/env bash
# Build anki_setup_wizard.ankiaddon (distributable zip for Anki 2.1.49+)
set -e

ADDON_DIR="anki_setup_wizard"
OUT="anki_setup_wizard.ankiaddon"

cd "$(dirname "$0")"

rm -f "$OUT"
cd "$ADDON_DIR"
zip -r "../$OUT" . \
    --exclude "*.pyc" \
    --exclude "__pycache__/*" \
    --exclude ".DS_Store"
cd ..

echo "Built: $OUT  ($(du -sh "$OUT" | cut -f1))"
echo ""
echo "To install in Anki:"
echo "  Tools → Add-ons → Install from file… → select $OUT"
echo "  -OR- copy the anki_setup_wizard/ folder into your Anki addons21/ directory."
