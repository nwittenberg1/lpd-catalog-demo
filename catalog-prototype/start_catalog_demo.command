#!/bin/zsh

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT_DIR="$SCRIPT_DIR"
URL="http://127.0.0.1:8000/catalog-prototype/index.html"

if ! lsof -iTCP:8000 -sTCP:LISTEN >/dev/null 2>&1; then
  nohup python3 "$ROOT_DIR/serve_catalog.py" --host 127.0.0.1 --port 8000 >/tmp/lpd-catalog-demo.log 2>&1 &
  sleep 1
fi

open "$URL"
