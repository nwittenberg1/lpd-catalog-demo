#!/usr/bin/env python3

import csv
import json
from pathlib import Path

MANIFEST = Path("/Users/lpdmusic/Documents/New project/harmbooks-normalized-sample/manifest.csv")
OUTPUT = Path("/Users/lpdmusic/Documents/New project/catalog-prototype/data/harmbooks-preview-data.js")


def title_from_filename(name: str) -> str:
    stem = Path(name).stem
    words = stem.replace("_", " ").replace("-", " ").split()
    return " ".join(word[:1].upper() + word[1:] for word in words)


def main():
    rows = []
    with MANIFEST.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            if row.get("status") != "normalized":
                continue
            output_path = row.get("output_path", "")
            rows.append(
                {
                    "title": title_from_filename(row.get("source_name", "")),
                    "sourceName": row.get("source_name", ""),
                    "imageUrl": output_path,
                }
            )

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text("window.HARMBOOKS_PREVIEW = " + json.dumps(rows, indent=2) + ";\n", encoding="utf-8")
    print(f"Wrote {len(rows)} preview rows to {OUTPUT}")


if __name__ == "__main__":
    main()
