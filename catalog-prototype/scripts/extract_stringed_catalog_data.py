#!/usr/bin/env python3

import csv
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import unquote

ROOT = Path("/Users/lpdmusic/Documents/New project")
EXTRACT_DIR = ROOT / "stringed-local-idml"
SPREADS_DIR = EXTRACT_DIR / "Spreads"
STORIES_DIR = EXTRACT_DIR / "Stories"
LINKS_DIR = ROOT / "NEW CATALOG Folder" / "Links"
OUTPUT_CSV = ROOT / "stringed-catalog-data.csv"

PRICE_RE = re.compile(r"\$[\d,]+(?:\.\d{2})?")
LINK_RE = re.compile(r'LinkResourceURI="file:[^"]*/Links/([^"]+)"')


def clean_text(text: str) -> str:
    text = text.replace("\ufeff", " ")
    text = text.replace("\u2028", " ")
    text = text.replace("\u2029", " ")
    text = text.replace("\u00a0", " ")
    text = text.replace("\n", " ")
    text = text.replace("•", "• ")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def decode_style(style: str) -> str:
    return unquote(style).split(":")[-1].strip()


def parse_topic(topic: str):
    decoded = unquote(topic or "")
    parts = [part for part in decoded.split("Topicn") if part]
    if len(parts) >= 2:
        return parts[-2].strip(), parts[-1].strip()
    return "", ""


def parse_story(story_path: Path):
    root = ET.parse(story_path).getroot()
    data = {
        "sku": "",
        "product_name": "",
        "description": "",
        "colors": "",
        "map_price": "",
        "net_price": "",
        "brand": "",
        "subcategory": "",
        "topic": "",
    }

    for node in root.iter():
        tag = node.tag.split("}")[-1]
        if tag == "PageReference":
            topic = node.attrib.get("ReferencedTopic", "")
            if topic and not data["topic"]:
                data["topic"] = topic
                brand, subcategory = parse_topic(topic)
                data["brand"] = brand
                data["subcategory"] = subcategory
        elif tag == "CharacterStyleRange":
            style = decode_style(node.attrib.get("AppliedCharacterStyle", ""))
            parts = []
            for child in node:
                child_tag = child.tag.split("}")[-1]
                if child_tag == "Content":
                    parts.append(child.text or "")
                elif child_tag == "Br":
                    parts.append("\n")
            text = clean_text("".join(parts))
            if not text:
                continue

            if style == "MODEL #" and not data["sku"]:
                data["sku"] = text
            elif style == "Model NAME":
                data["product_name"] = clean_text(f"{data['product_name']} {text}")
            elif style == "COLORS":
                data["colors"] = clean_text(text.replace("Colors:", "").strip())
            elif style == "MAP Price":
                price = PRICE_RE.search(text)
                if price:
                    data["map_price"] = price.group(0)
            elif style == "NET Price":
                price = PRICE_RE.search(text)
                if price:
                    data["net_price"] = price.group(0)
            elif "Description" in style:
                data["description"] = clean_text(f"{data['description']} {text}")

    if not data["sku"] or not data["net_price"]:
        return None

    data["product_name"] = clean_text(data["product_name"])
    data["description"] = clean_text(data["description"])
    return data


def parse_bounds(elem):
    transform = elem.attrib.get("ItemTransform", "").split()
    tx = ty = 0.0
    if len(transform) >= 6:
        try:
            tx = float(transform[4])
            ty = float(transform[5])
        except ValueError:
            pass
    points = []
    for node in elem.iter():
        if node.tag.split("}")[-1] != "PathPointType":
            continue
        try:
            px, py = map(float, node.attrib.get("Anchor", "").split())
        except ValueError:
            continue
        points.append((px, py))
    if not points:
        return tx, ty
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    return ((min(xs) + max(xs)) / 2.0) + tx, ((min(ys) + max(ys)) / 2.0) + ty


def cluster_rows(items, threshold=90):
    rows = []
    for item in sorted(items, key=lambda entry: entry["y"]):
        if not rows or abs(item["y"] - rows[-1][0]["y"]) > threshold:
            rows.append([item])
        else:
            rows[-1].append(item)
    for row in rows:
        row.sort(key=lambda entry: entry["x"])
    return rows


def spread_page_name(root):
    spread = next((child for child in root if child.tag.split("}")[-1] == "Spread"), None)
    if spread is None:
        return ""
    for child in spread:
        if child.tag.split("}")[-1] == "Page":
            return child.attrib.get("Name", "")
    return ""


def collect_story_image_map():
    story_meta = {}
    for spread_path in sorted(SPREADS_DIR.glob("*.xml")):
        root = ET.parse(spread_path).getroot()
        page = spread_page_name(root)
        parent_map = {child: parent for parent in root.iter() for child in parent}
        textframes = []
        images = []

        for elem in root.iter():
            tag = elem.tag.split("}")[-1]
            if tag == "TextFrame":
                story_id = elem.attrib.get("ParentStory", "")
                if not story_id:
                    continue
                x, y = parse_bounds(elem)
                textframes.append({"story_id": story_id, "x": x, "y": y, "page": page})
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
                        "source_image_name": unquote(Path(uri).name),
                        "x": x,
                        "y": y,
                        "page": page,
                    }
                )

        text_rows = cluster_rows(textframes)
        image_rows = cluster_rows(images)
        for row_index, text_row in enumerate(text_rows):
            image_row = image_rows[row_index] if row_index < len(image_rows) else []
            for col_index, frame in enumerate(text_row):
                story_meta[frame["story_id"]] = {
                    "page": frame["page"],
                    "source_image_name": image_row[col_index]["source_image_name"] if col_index < len(image_row) else "",
                }
    return story_meta


def main():
    story_image_map = collect_story_image_map()
    rows = []
    for story_path in sorted(STORIES_DIR.glob("Story_*.xml")):
        story_id = story_path.stem.replace("Story_", "")
        data = parse_story(story_path)
        if not data:
            continue
        meta = story_image_map.get(story_id, {})
        image_name = meta.get("source_image_name", "")
        image_path = str(LINKS_DIR / image_name) if image_name else ""
        rows.append(
            {
                "sort_order": "",
                "page": meta.get("page", ""),
                "story_id": story_id,
                "brand": data["brand"],
                "top_category": "Fretted Instruments",
                "subcategory": data["subcategory"],
                "sku": data["sku"],
                "product_name": data["product_name"],
                "description": data["description"],
                "colors": data["colors"],
                "map_price": data["map_price"],
                "net_price": data["net_price"],
                "net_price_if_buy_6_or_more": "",
                "net_price_if_buy_12_or_more": "",
                "source_image_name": image_name,
                "source_image_path": image_path,
            }
        )

    rows.sort(key=lambda row: (int(row["page"]) if row["page"].isdigit() else 9999, row["story_id"]))

    with OUTPUT_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "sort_order",
                "page",
                "story_id",
                "brand",
                "top_category",
                "subcategory",
                "sku",
                "product_name",
                "description",
                "colors",
                "map_price",
                "net_price",
                "net_price_if_buy_6_or_more",
                "net_price_if_buy_12_or_more",
                "source_image_name",
                "source_image_path",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote {len(rows)} rows to {OUTPUT_CSV}")


if __name__ == "__main__":
    main()
