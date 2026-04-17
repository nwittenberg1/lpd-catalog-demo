#!/usr/bin/env python3

import csv
import json
import re
import unicodedata
from pathlib import Path

from extract_xlsx import build_records, parse_xlsx_rows

SOURCE_XLSX = Path("/Users/lpdmusic/Downloads/SKUs Present in Catalog.xlsx")
IMAGE_ROOT = Path("/tmp/danelectro-rebuild/DANELECTRO")
OUT_DIR = Path("/Users/lpdmusic/Documents/New project/catalog-prototype")
DATA_OUTPUT = OUT_DIR / "data/catalog-products.js"
PRODUCTS_CSV = OUT_DIR / "exports/products.csv"
FINISHES_CSV = OUT_DIR / "exports/finishes.csv"
REPORT_CSV = OUT_DIR / "exports/match-report.csv"
GENERIC_WORDS = {"danelectro", "electric", "guitar", "guitars"}


def normalize(text: str) -> str:
    text = (text or "").replace("™", " ")
    text = unicodedata.normalize("NFKD", text)
    text = text.replace("’", "'").replace("‘", "'")
    text = text.lower().replace("semi-hollow", "semi hollow")
    text = text.replace("�??", " ")
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return " ".join(text.split())


def family_phrase(name: str) -> str:
    tokens = [token for token in normalize(name).split() if token not in GENERIC_WORDS]
    return " ".join(tokens)


def image_url(path: Path) -> str:
    rel = path.relative_to(IMAGE_ROOT)
    return "./images-source/" + "/".join(part.replace(" ", "%20") for part in rel.parts)


def extract_finish(image_name: str, phrase: str) -> str:
    stem = normalize(Path(image_name).stem)
    stem = re.sub(r"^danelectro\s+", "", stem)
    finish = stem.replace(phrase, "", 1).strip() if phrase and phrase in stem else stem
    if not finish:
        return "Default"
    return " ".join(word.capitalize() for word in finish.split())


def token_score(left: str, right: str) -> float:
    left_tokens = set(left.split())
    right_tokens = set(right.split())
    if not left_tokens:
        return 0.0
    return len(left_tokens & right_tokens) / len(left_tokens)


def match_images(record):
    folder = IMAGE_ROOT / record["category"]
    phrase = family_phrase(record["productName"])
    if not folder.exists():
        return [], "unmatched"

    exact = []
    fallback = []
    for path in sorted(folder.iterdir()):
        if not path.is_file() or path.name.startswith(".") or "__MACOSX" in str(path):
            continue
        stem = normalize(path.stem)
        stem = re.sub(r"^danelectro\s+", "", stem)
        if phrase and phrase in stem:
            exact.append(path)
            continue
        score = token_score(phrase, stem)
        if score >= 0.84:
            fallback.append((score, path))

    if exact:
        return exact, "exact-phrase"
    if fallback:
        return [path for _, path in sorted(fallback, reverse=True)], "token-fallback"
    return [], "unmatched"


def write_csv(path: Path, rows, fieldnames):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main():
    products = build_records(parse_xlsx_rows(SOURCE_XLSX))
    product_rows = []
    finish_rows = []
    report_rows = []
    preview_rows = []

    for record in products:
        matches, match_type = match_images(record)
        finishes = []
        for index, path in enumerate(matches, start=1):
            finish = extract_finish(path.name, family_phrase(record["productName"]))
            finishes.append({"finish": finish, "imageFile": path.name, "imageUrl": image_url(path)})
            finish_rows.append(
                {
                    "SKU": record["sku"],
                    "Product Name": record["productName"],
                    "Finish": finish,
                    "Image File": path.name,
                    "Image Folder": path.parent.name,
                    "Image Path": str(path),
                    "Sort Order": index,
                }
            )

        product_rows.append(
            {
                "SKU": record["sku"],
                "Brand": record["brand"],
                "Product Name": record["productName"],
                "Section": record["section"],
                "Category": record["category"],
                "MAP": record["map"],
                "LIST": record["list"],
                "NET": record["net"],
                "Image Match Type": match_type,
                "Finish Count": len(finishes),
            }
        )

        report_rows.append(
            {
                "SKU": record["sku"],
                "Product Name": record["productName"],
                "Category": record["category"],
                "Match Type": match_type,
                "Finish Count": len(finishes),
                "Matched Files": " | ".join(path.name for path in matches),
            }
        )

        preview_rows.append({**record, "matchType": match_type, "finishes": finishes})

    DATA_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    DATA_OUTPUT.write_text("window.CATALOG_PRODUCTS = " + json.dumps(preview_rows, indent=2) + ";\n", encoding="utf-8")
    write_csv(PRODUCTS_CSV, product_rows, ["SKU", "Brand", "Product Name", "Section", "Category", "MAP", "LIST", "NET", "Image Match Type", "Finish Count"])
    write_csv(FINISHES_CSV, finish_rows, ["SKU", "Product Name", "Finish", "Image File", "Image Folder", "Image Path", "Sort Order"])
    write_csv(REPORT_CSV, report_rows, ["SKU", "Product Name", "Category", "Match Type", "Finish Count", "Matched Files"])

    print(f"Wrote {len(product_rows)} product rows")
    print(f"Wrote {len(finish_rows)} finish rows")


if __name__ == "__main__":
    main()
