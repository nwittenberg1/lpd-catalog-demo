#!/usr/bin/env python3

import csv
import re
import subprocess
import xml.etree.ElementTree as ET
from collections import defaultdict
from pathlib import Path
from urllib.parse import unquote

IDML_PATH = Path("/Users/lpdmusic/Documents/New project/NEW CATALOG Folder/HARMONICAS & BOOKS UPDATED.idml")
EXTRACT_DIR = Path("/tmp/harmbooks-local-idml")
SPREADS_DIR = EXTRACT_DIR / "Spreads"
STORIES_DIR = EXTRACT_DIR / "Stories"
MANIFEST_PATH = Path("/Users/lpdmusic/Documents/New project/harmbooks-normalized-sample/manifest.csv")
OUTPUT_PATH = Path("/Users/lpdmusic/Documents/New project/harmbooks-catalog-data.csv")

PRICE_RE = re.compile(r"\$[\d,]+(?:\.\d{2})?")


def extract_idml():
    EXTRACT_DIR.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["unzip", "-o", "-q", str(IDML_PATH), "-d", str(EXTRACT_DIR)],
        check=True,
    )


def clean_text(text: str) -> str:
    text = text.replace("\ufeff", " ")
    text = text.replace("\u2028", " ")
    text = text.replace("\u2029", " ")
    text = text.replace("\u00a0", " ")
    text = text.replace("\n", " ")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def style_suffix(style: str) -> str:
    decoded = unquote(style)
    return decoded.split(":")[-1].strip()


def iter_story_runs(story_path: Path):
    root = ET.parse(story_path).getroot()
    for node in root.iter():
        if node.tag.split("}")[-1] != "CharacterStyleRange":
            continue
        style = style_suffix(node.attrib.get("AppliedCharacterStyle", ""))
        parts = []
        for child in node:
            tag = child.tag.split("}")[-1]
            if tag == "Content":
                parts.append(child.text or "")
            elif tag == "Br":
                parts.append("\n")
        text = clean_text("".join(parts))
        if text or style:
            yield style, text


def blank_record():
    return {
        "product_name": "",
        "sku": "",
        "list_price": "",
        "map_price": "",
        "net_price": "",
        "description": "",
        "notes": "",
    }


def postprocess_story_records(records):
    if not records:
        return []

    merged = []
    for record in records:
        if (
            merged
            and not merged[-1]["sku"]
            and merged[-1]["product_name"]
            and record["sku"]
            and not record["product_name"]
        ):
            record["product_name"] = merged[-1]["product_name"]
            record["description"] = clean_text(f"{merged[-1]['description']} {record['description']}")
            record["notes"] = clean_text(f"{merged[-1]['notes']} {record['notes']}")
            merged.pop()
        merged.append(record)

    story_name = next((record["product_name"] for record in merged if record["product_name"]), "")
    for record in merged:
        if story_name and not record["product_name"]:
            record["product_name"] = story_name

    cleaned = []
    for record in merged:
        useful = any(
            [
                record["product_name"],
                record["description"],
                record["list_price"],
                record["map_price"],
                record["net_price"],
                record["notes"],
            ]
        )
        if record["sku"] and not useful:
            continue
        if useful or record["sku"]:
            cleaned.append(record)
    return cleaned


def finalize_record(records, current):
    if not current:
        return None
    if not (current["sku"] or current["product_name"]):
        return None
    current["description"] = clean_text(current["description"])
    current["notes"] = clean_text(current["notes"])
    records.append(current.copy())
    return None


def parse_story_records(story_id: str):
    story_path = STORIES_DIR / f"Story_{story_id}.xml"
    if not story_path.exists():
        return []

    records = []
    current = None
    pending_name = ""
    price_target = ""

    for style, text in iter_story_runs(story_path):
        if style == "MODEL #":
            if text:
                if current and (current["sku"] or current["product_name"]):
                    current = finalize_record(records, current)
                current = blank_record()
                current["sku"] = text
                if pending_name and not current["product_name"]:
                    current["product_name"] = pending_name
                    pending_name = ""
                price_target = ""
            continue

        if style == "Model NAME":
            if not text:
                continue
            if current and current["sku"] and not current["product_name"]:
                current["product_name"] = text
            elif current and current["product_name"] and not current["net_price"] and not current["list_price"] and not current["map_price"]:
                current["notes"] = clean_text(f"{current['notes']} {text}")
            else:
                pending_name = text
            continue

        if current is None:
            current = blank_record()
            if pending_name:
                current["product_name"] = pending_name
                pending_name = ""

        upper = text.upper()
        prices = PRICE_RE.findall(text)

        if "LIST" in upper:
            price_target = "list_price"
            if prices:
                current["list_price"] = prices[0]
        elif "MAP" in upper:
            price_target = "map_price"
            if prices:
                current["map_price"] = prices[0]
        elif style == "NET Price" and "NET" in upper:
            price_target = "net_price"
            if prices:
                current["net_price"] = prices[0]
        elif prices and price_target:
            if not current[price_target]:
                current[price_target] = prices[0]
        elif style == "Description" and text:
            current["description"] = clean_text(f"{current['description']} {text}")
        elif text and style not in {"MAP Price", "NET Price"}:
            current["notes"] = clean_text(f"{current['notes']} {text}")

    finalize_record(records, current)
    records = [record for record in records if record["sku"] or record["product_name"]]
    return postprocess_story_records(records)


def parse_bounds(item):
    x = y = 0.0
    transform = item.attrib.get("ItemTransform", "")
    parts = transform.split()
    if len(parts) >= 6:
        try:
            x = float(parts[4])
            y = float(parts[5])
        except ValueError:
            pass
    points = []
    for node in item.iter():
        if node.tag.split("}")[-1] != "PathPointType":
            continue
        try:
            px, py = map(float, node.attrib.get("Anchor", "").split())
        except ValueError:
            continue
        points.append((px, py))
    if not points:
        return x, y
    xs = [point[0] for point in points]
    ys = [point[1] for point in points]
    center_x = ((min(xs) + max(xs)) / 2.0) + x
    center_y = ((min(ys) + max(ys)) / 2.0) + y
    return center_x, center_y


def cluster_rows(items, threshold=80):
    rows = []
    for item in sorted(items, key=lambda entry: entry["y"]):
        if not rows or abs(item["y"] - rows[-1][0]["y"]) > threshold:
            rows.append([item])
        else:
            rows[-1].append(item)
    for row in rows:
        row.sort(key=lambda entry: entry["x"])
    return rows


def iter_product_textframes():
    story_records = {}
    story_index = {}

    for spread_path in sorted(SPREADS_DIR.glob("*.xml")):
        root = ET.parse(spread_path).getroot()
        page = ""
        page_node = next((child for child in root if child.tag.split("}")[-1] == "Spread"), None)
        if page_node is not None:
            for child in page_node:
                if child.tag.split("}")[-1] == "Page":
                    page = child.attrib.get("Name", "")
                    break

        textframes = []
        images = []
        parent_map = {child: parent for parent in root.iter() for child in parent}
        for elem in root.iter():
            tag = elem.tag.split("}")[-1]
            if tag == "TextFrame":
                story_id = elem.attrib.get("ParentStory", "")
                records = parse_story_records(story_id)
                if not records:
                    continue
                x, y = parse_bounds(elem)
                textframes.append({"story_id": story_id, "x": x, "y": y, "page": page})
                story_records.setdefault(story_id, records)
            elif tag == "Link":
                uri = elem.attrib.get("LinkResourceURI", "")
                if not uri:
                    continue
                owner = parent_map.get(parent_map.get(elem))
                if owner is None:
                    continue
                x, y = parse_bounds(owner)
                images.append(
                    {
                        "source_name": unquote(Path(uri).name),
                        "x": x,
                        "y": y,
                        "page": page,
                    }
                )

        text_rows = cluster_rows(textframes)
        image_rows = cluster_rows(images)

        sequence = 0
        for row_index, text_row in enumerate(text_rows):
            image_row = image_rows[row_index] if row_index < len(image_rows) else []
            for col_index, frame in enumerate(text_row):
                story_index[frame["story_id"]] = {
                    "page": frame["page"],
                    "sequence": sequence,
                    "image": image_row[col_index]["source_name"] if col_index < len(image_row) else "",
                }
                sequence += 1

    return story_records, story_index


def load_manifest():
    mapping = {}
    with MANIFEST_PATH.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            mapping[row["source_name"]] = row
    return mapping


def main():
    extract_idml()
    manifest = load_manifest()
    story_records, story_index = iter_product_textframes()

    rows = []
    for story_id, records in story_records.items():
        meta = story_index.get(story_id, {})
        image_name = meta.get("image", "")
        manifest_row = manifest.get(image_name, {})
        for record_number, record in enumerate(records, start=1):
            rows.append(
                {
                    "sort_order": "",
                    "page": meta.get("page", ""),
                    "story_id": story_id,
                    "story_record": record_number,
                    "brand": "",
                    "top_category": "Harmonicas, Books & Novelties",
                    "subcategory": "",
                    "sku": record["sku"],
                    "product_name": record["product_name"],
                    "description": record["description"],
                    "notes": record["notes"],
                    "list_price": record["list_price"],
                    "map_price": record["map_price"],
                    "net_price": record["net_price"],
                    "source_image_name": image_name,
                    "normalized_image_path": manifest_row.get("output_path", ""),
                }
            )

    rows.sort(key=lambda row: (int(row["page"]) if row["page"].isdigit() else 9999, row["story_id"], row["story_record"]))

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_PATH.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "sort_order",
                "page",
                "story_id",
                "story_record",
                "brand",
                "top_category",
                "subcategory",
                "sku",
                "product_name",
                "description",
                "notes",
                "list_price",
                "map_price",
                "net_price",
                "source_image_name",
                "normalized_image_path",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote {len(rows)} rows to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
