#!/usr/bin/env python3

import csv
import re
import subprocess
from pathlib import Path

IDML_PATH = Path("/Users/lpdmusic/Documents/New project/NEW CATALOG Folder/HARMONICAS & BOOKS UPDATED.idml")
LINKS_DIR = Path("/Users/lpdmusic/Documents/New project/NEW CATALOG Folder/Links")
EXTRACT_DIR = Path("/tmp/harmbooks-local-idml")
OUTPUT_DIR = Path("/Users/lpdmusic/Documents/New project/harmbooks-normalized-sample")
MANIFEST_PATH = OUTPUT_DIR / "manifest.csv"

CANVAS_SIZE = 2048
INNER_BOX_MAX = 1720
PAD_COLOR = "FFFFFF"


def extract_idml():
    EXTRACT_DIR.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["unzip", "-o", "-q", str(IDML_PATH), "-d", str(EXTRACT_DIR)],
        check=True,
    )


def linked_filenames():
    pattern = re.compile(r'LinkResourceURI="file:[^"]*/Links/([^"]+)"')
    names = []
    for spread in sorted((EXTRACT_DIR / "Spreads").glob("*.xml")):
        text = spread.read_text(errors="ignore")
        for match in pattern.finditer(text):
            name = match.group(1).replace("%20", " ")
            if name not in names:
                names.append(name)
    return names


def png_name(source_name: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", Path(source_name).stem.lower()).strip("-")
    return f"{slug}.png" if slug else "image.png"


def normalize_image(source: Path, output: Path):
    output.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [
            "sips",
            "-s",
            "format",
            "png",
            "-s",
            "dpiWidth",
            "72",
            "-s",
            "dpiHeight",
            "72",
            "--resampleHeightWidthMax",
            str(INNER_BOX_MAX),
            "--padToHeightWidth",
            str(CANVAS_SIZE),
            str(CANVAS_SIZE),
            "--padColor",
            PAD_COLOR,
            str(source),
            "--out",
            str(output),
        ],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def dimensions(path: Path):
    result = subprocess.run(
        ["sips", "-g", "pixelWidth", "-g", "pixelHeight", str(path)],
        check=True,
        capture_output=True,
        text=True,
    )
    width = height = ""
    for line in result.stdout.splitlines():
        if "pixelWidth:" in line:
            width = line.split(":")[-1].strip()
        if "pixelHeight:" in line:
            height = line.split(":")[-1].strip()
    return width, height


def main():
    extract_idml()
    names = linked_filenames()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    rows = []
    for name in names:
        source = LINKS_DIR / name
        if not source.exists():
            rows.append(
                {
                    "source_name": name,
                    "source_path": str(source),
                    "output_path": "",
                    "status": "missing",
                }
            )
            continue

        output = OUTPUT_DIR / png_name(name)
        normalize_image(source, output)
        width, height = dimensions(output)
        rows.append(
            {
                "source_name": name,
                "source_path": str(source),
                "output_path": str(output),
                "status": "normalized",
                "output_width": width,
                "output_height": height,
            }
        )

    with MANIFEST_PATH.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "source_name",
                "source_path",
                "output_path",
                "status",
                "output_width",
                "output_height",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)

    normalized = sum(1 for row in rows if row["status"] == "normalized")
    missing = sum(1 for row in rows if row["status"] == "missing")
    print(f"Normalized {normalized} files")
    print(f"Missing {missing} files")
    print(f"Output folder: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
