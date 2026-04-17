#!/bin/zsh

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
STAMP="$(date +%Y-%m-%d)"
OUTPUT_ZIP="$PROJECT_ROOT/LPD-Catalog-Demo-$STAMP.zip"
TEMP_DIR="$PROJECT_ROOT/.portable-demo-staging"

rm -rf "$TEMP_DIR"
mkdir -p "$TEMP_DIR/LPD-Catalog-Demo"

cp -R "$PROJECT_ROOT/catalog-prototype" "$TEMP_DIR/LPD-Catalog-Demo/"
cp -R "$PROJECT_ROOT/Photos" "$TEMP_DIR/LPD-Catalog-Demo/"

rm -f "$OUTPUT_ZIP"
cd "$TEMP_DIR" || exit 1
/usr/bin/zip -r "$OUTPUT_ZIP" "LPD-Catalog-Demo" >/dev/null

rm -rf "$TEMP_DIR"
open -R "$OUTPUT_ZIP"
