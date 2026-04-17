#!/usr/bin/env python3
from __future__ import annotations

import argparse
import io
import json
import mimetypes
import os
import zipfile
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse


PROJECT_ROOT = Path(__file__).resolve().parent.parent
CATALOG_ROOT = PROJECT_ROOT / "catalog-prototype"
PHOTOS_ROOT = PROJECT_ROOT / "Photos"


def resolve_source_path(raw_path: str) -> Path | None:
    if not raw_path:
        return None
    decoded = Path(unquote(raw_path))
    if decoded.is_absolute():
        candidate = decoded.resolve()
    else:
        candidate = (CATALOG_ROOT / decoded).resolve()

    allowed_roots = [PROJECT_ROOT.resolve(), PHOTOS_ROOT.resolve(), CATALOG_ROOT.resolve()]
    if any(root == candidate or root in candidate.parents for root in allowed_roots):
        return candidate
    return None


def resolve_asset_reference(source_path: str, image_url: str) -> Path | None:
    source_candidate = resolve_source_path(source_path)
    if source_candidate is not None:
        return source_candidate

    raw_url = str(image_url or "").strip()
    if not raw_url:
        return None

    cleaned = raw_url
    if cleaned.startswith("../"):
        cleaned = cleaned[3:]
    if cleaned.startswith("./"):
        cleaned = cleaned[2:]
    if cleaned.startswith("/"):
        cleaned = cleaned[1:]

    candidate = (PROJECT_ROOT / cleaned).resolve()
    allowed_roots = [PROJECT_ROOT.resolve(), PHOTOS_ROOT.resolve(), CATALOG_ROOT.resolve()]
    if any(root == candidate or root in candidate.parents for root in allowed_roots):
        return candidate
    return None


class CatalogHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(PROJECT_ROOT), **kwargs)

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/":
            self.send_response(HTTPStatus.FOUND)
            self.send_header("Location", "/catalog-prototype/index.html")
            self.end_headers()
            return

        if parsed.path == "/api/health":
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(b'{"ok":true}')
            return

        if parsed.path == "/api/source-image":
            params = parse_qs(parsed.query)
            raw_path = params.get("path", [""])[0]
            source_path = resolve_source_path(raw_path)

            if source_path is None or not source_path.exists() or not source_path.is_file():
                self.send_error(HTTPStatus.NOT_FOUND, "Source image not found")
                return

            mime_type, _ = mimetypes.guess_type(str(source_path))
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", mime_type or "application/octet-stream")
            self.send_header("Content-Length", str(source_path.stat().st_size))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            with source_path.open("rb") as handle:
                self.wfile.write(handle.read())
            return

        self.path = parsed.path
        return super().do_GET()

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path != "/api/export-dealer-list":
            self.send_error(HTTPStatus.NOT_FOUND, "Endpoint not found")
            return

        try:
            content_length = int(self.headers.get("Content-Length", "0"))
            payload = json.loads(self.rfile.read(content_length) or b"{}")
        except Exception:
            self.send_error(HTTPStatus.BAD_REQUEST, "Invalid JSON payload")
            return

        stamp = str(payload.get("stamp") or "").strip() or "dealer-list"
        csv_text = str(payload.get("csvText") or "")
        csv_name = str(payload.get("fileName") or f"dealer-list-{stamp}.csv")
        assets = payload.get("assets") or []

        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", compression=zipfile.ZIP_DEFLATED) as zip_file:
            zip_file.writestr(csv_name, csv_text)

            for asset in assets:
                file_name = Path(str(asset.get("fileName") or "")).name
                source_path = resolve_asset_reference(
                    str(asset.get("sourceImageUrl") or ""),
                    str(asset.get("imageUrl") or ""),
                )
                if not file_name or source_path is None or not source_path.exists() or not source_path.is_file():
                    continue
                zip_file.write(source_path, arcname=f"Images/{file_name}")

        zip_bytes = zip_buffer.getvalue()
        download_name = f"LPD-Dealer-List-{stamp}.zip"
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "application/zip")
        self.send_header("Content-Length", str(len(zip_bytes)))
        self.send_header("Content-Disposition", f'attachment; filename="{download_name}"')
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(zip_bytes)


def main() -> None:
    parser = argparse.ArgumentParser(description="Serve the LPD catalog prototype with local export helpers.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", default=8000, type=int)
    args = parser.parse_args()

    server = ThreadingHTTPServer((args.host, args.port), CatalogHandler)
    print(f"Serving catalog at http://{args.host}:{args.port}/catalog-prototype/index.html")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
