#!/usr/bin/env bash
# Build anki_setup_tool.ankiaddon (distributable zip for Anki 2.1.49+)
set -e

ADDON_DIR="ankiel_setup_tool"
OUT="ankiel_setup_tool.ankiaddon"

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
echo "  -OR- copy the ankiel_setup_tool/ folder into your Anki addons21/ directory."
