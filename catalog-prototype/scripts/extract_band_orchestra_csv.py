#!/usr/bin/env python3

import csv
import re
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT = Path("/Users/lpdmusic/Documents/New project")
IDML_PATH = ROOT / "NEW CATALOG Folder" / "BAND & ORCHESTRA UPDATED.idml"
OUTPUT_CSV = ROOT / "band-orchestra-catalog-data.csv"
QA_CSV = ROOT / "band-orchestra-catalog-data-qa-report.csv"

FIELDNAMES = [
    "sort_order",
    "page",
    "story_id",
    "brand",
    "top_category",
    "subcategory",
    "sku",
    "product_name",
    "description",
    "notes",
    "colors",
    "list_price",
    "map_price",
    "net_price",
    "net_price_if_buy_4_or_more",
    "net_price_if_buy_6_or_more",
    "net_price_if_buy_12_or_more",
    "source_image_name",
    "source_image_path",
]

SPREAD_MAP = {
    "Spreads/Spread_u237c.xml": ("Stands, Mutes, & Reeds", "255-256"),
    "Spreads/Spread_u2457.xml": ("Stands, Mutes, & Reeds", "257-258"),
    "Spreads/Spread_u26d8.xml": ("Mouthpieces", "259-260"),
    "Spreads/Spread_u29ef.xml": ("Caps, Ligatures, & Endplugs", "258-259"),
    "Spreads/Spread_u2be4.xml": ("Straps", "260-261"),
    "Spreads/Spread_u2e80.xml": ("Straps", "260-261"),
    "Spreads/Spread_u31a2.xml": ("Lyres", "261"),
    "Spreads/Spread_u355d.xml": ("Instrument Care", "262-263"),
    "Spreads/Spread_u38a4.xml": ("Instrument Care", "262-263"),
    "Spreads/Spread_u3ac3.xml": ("Instrument Care", "264-265"),
    "Spreads/Spread_u3d99.xml": ("Instrument Care", "264-265"),
    "Spreads/Spread_u3f54.xml": ("Violin Sets & Bags", "266"),
    "Spreads/Spread_u41d5.xml": ("Strings, Bows, & Hangers", "267-268"),
    "Spreads/Spread_u43c6.xml": ("Strings, Bows, & Hangers", "267-268"),
    "Spreads/Spread_u4620.xml": ("Parts", "269"),
    "Spreads/Spread_u4930.xml": ("Percussion & Recorders", "270"),
    "Spreads/Spread_u4ba2.xml": ("Music Stands", "271-272"),
    "Spreads/Spread_u4e47.xml": ("Music Stands", "271-272"),
    "Spreads/Spread_u5027.xml": ("Stand Lights, Folders, & Batons", "273"),
    "Spreads/Spread_u50f3.xml": ("Stand Lights, Folders, & Batons", "273"),
    "Spreads/Spread_u52aa.xml": ("Stand Lights, Folders, & Batons", "273"),
}

IGNORE_TEXT_EXACT = {
    "TABLE OF CONTENTS",
    "BAND & ORCHESTRA",
    "STRAPS",
    "STANDS, MUTES, & REEDS",
    "CAPS, LIGATURES, & ENDPLUGS",
    "MOUTHPIECES",
    "LYRES",
    "INSTRUMENT CARE",
    "VIOLIN SETS & BAGS",
    "STRINGS, BOWS, & HANGERS",
    "PARTS",
    "PERCUSSION & RECORDERS",
    "MUSIC STANDS",
    "STAND LIGHTS, FOLDERS, & BATONS",
    "Woodwind",
    "Brass",
    "Drum",
}

IGNORE_SKUS = {
    "LIST",
    "NET",
    "MAP",
    "MOUTHPIECES",
    "PARTS",
    "STRAPS",
    "LYRES",
    "LIGHT",
    "LIGHTS",
    "FOLDER",
    "WINDOW",
}

BRAND_KEYWORDS = [
    ("PLASTICOVER BY D’ADDARIO", "D'Addario"),
    ("PLASTICOVER BY D'ADDARIO", "D'Addario"),
    ("D’ADDARIO", "D'Addario"),
    ("D'ADDARIO", "D'Addario"),
    ("MIGHTY BRIGHT", "Mighty Bright"),
    ("ROCHE THOMAS", "Roche Thomas"),
    ("EASTAR", "Eastar"),
    ("JUNO", "Juno"),
    ("JONES", "Jones"),
    ("KUN", "Kun"),
    ("HAMILTON", "Hamilton"),
    ("GROVER", "Grover"),
    ("AMERICAN PLATING", "American Plating"),
]


def walk_text(elem):
    out = []
    for node in elem.iter():
        tag = node.tag.split("}")[-1]
        if tag == "Content" and node.text:
            out.append(node.text)
        elif tag == "Br":
            out.append("\n")
    text = " ".join(out)
    text = text.replace("\u00a0", " ")
    text = re.sub(r"\s+", " ", text).strip()
    return text


def infer_brand(text, sku):
    upper = text.upper()
    for needle, brand in BRAND_KEYWORDS:
        if needle in upper:
            return brand
    if sku.startswith("JS"):
        return "JamStands"
    if sku.startswith("OS"):
        return "On-Stage"
    if sku.startswith("KB"):
        return "Hamilton"
    if sku.startswith("TR") or sku.startswith("HC"):
        return "Hamilton"
    if sku.startswith("AP"):
        return "American Plating"
    if sku.startswith("B3") or sku.startswith("BT") or sku.startswith("BC") or sku.startswith("BFH"):
        return "Blessing"
    if sku.startswith("VO") or sku.startswith("BJ") or sku.startswith("BO"):
        return "Ultra-Pure"
    if sku.startswith("SR") or sku.startswith("CC") or sku.startswith("AB") or sku.startswith("IM"):
        return "Cecilio"
    return ""


def normalize_money(token):
    token = token.strip()
    if token.endswith("¢"):
        token = token[:-1]
    token = token.replace("$", "")
    if token.startswith("."):
        token = f"0{token}"
    return token


def clean_desc(desc):
    desc = desc.strip(" -–•")
    desc = re.sub(r"\s+", " ", desc)
    return desc.strip()


def looks_like_noise(text):
    if not text:
        return True
    if text in IGNORE_TEXT_EXACT:
        return True
    if text.isdigit():
        return True
    if "www.lpdmusic.com" in text.lower():
        return True
    if "FREE Freight" in text:
        return True
    return False


def extract_segments(text):
    normalized = text.replace("–", "-").replace("—", "-")
    normalized = normalized.replace("Clari net", "Clarinet")
    normalized = normalized.replace("TrUMPeT", "Trumpet")
    normalized = normalized.replace("REEDS", "Reeds")
    pattern = re.compile(
        r"(?P<sku>[A-Z0-9][A-Z0-9/\-+]{1,})\s+"
        r"(?P<desc>.*?)\s+"
        r"(?:(?P<label>LIST|MAP)\s+)?"
        r"\$?(?P<price1>\d+(?:\.\d+)?|\.\d+)"
        r"\s+(?:NET\s+)?\$?(?P<price2>\d+(?:\.\d+)?|\.\d+)"
        r"(?:\s+(?P<bulk_label>\d+\+)\s+\$?(?P<bulk_price>\d+(?:\.\d+)?|\.\d+))?",
        re.IGNORECASE,
    )
    rows = []
    for match in pattern.finditer(normalized):
        sku = match.group("sku").upper()
        if sku in IGNORE_SKUS or not any(ch.isdigit() for ch in sku):
            continue
        if sku.isdigit() and len(sku) <= 3:
            continue
        desc = clean_desc(match.group("desc"))
        if not desc:
            continue
        price1 = normalize_money(match.group("price1"))
        price2 = normalize_money(match.group("price2"))
        label = (match.group("label") or "LIST").upper()
        bulk_label = match.group("bulk_label") or ""
        bulk_price = normalize_money(match.group("bulk_price") or "")
        row = {
            "sku": sku,
            "product_name": clean_desc(desc.split(" Available", 1)[0]),
            "description": desc if len(desc) > 12 else "",
            "list_price": price1 if label == "LIST" else "",
            "map_price": price1 if label == "MAP" else "",
            "net_price": price2,
            "net_price_if_buy_4_or_more": bulk_price if bulk_label == "4+" else "",
            "net_price_if_buy_6_or_more": bulk_price if bulk_label == "6+" else "",
            "net_price_if_buy_12_or_more": bulk_price if bulk_label == "12+" else "",
            "notes": normalized,
        }
        rows.append(row)
    return rows


def first_sku(text):
    for token in re.findall(r"\b[A-Z0-9][A-Z0-9/\-+]{1,}\b", text):
        if token in IGNORE_SKUS:
            continue
        if any(ch.isdigit() for ch in token):
            if token.isdigit() and len(token) <= 3:
                continue
            return token.upper()
    return ""


def story_rows(story_id, text, subcategory, page, sort_order):
    extracted = extract_segments(text)
    if extracted:
        rows = []
        for item in extracted:
            rows.append(
                {
                    "sort_order": str(sort_order),
                    "page": page,
                    "story_id": story_id,
                    "brand": infer_brand(text, item["sku"]),
                    "top_category": "Band & Orchestra",
                    "subcategory": subcategory,
                    "sku": item["sku"],
                    "product_name": item["product_name"],
                    "description": item["description"],
                    "notes": item["notes"],
                    "colors": "",
                    "list_price": item["list_price"],
                    "map_price": item["map_price"],
                    "net_price": item["net_price"],
                    "net_price_if_buy_4_or_more": item["net_price_if_buy_4_or_more"],
                    "net_price_if_buy_6_or_more": item["net_price_if_buy_6_or_more"],
                    "net_price_if_buy_12_or_more": item["net_price_if_buy_12_or_more"],
                    "source_image_name": "",
                    "source_image_path": "",
                }
            )
        return rows

    sku = first_sku(text)
    if not sku:
        return []

    list_match = re.search(r"LIST\s+\$?(\d+(?:\.\d+)?|\.\d+)", text, re.IGNORECASE)
    map_match = re.search(r"MAP\s+\$?(\d+(?:\.\d+)?|\.\d+)", text, re.IGNORECASE)
    net_match = re.search(r"NET\s+\$?(\d+(?:\.\d+)?|\.\d+)", text, re.IGNORECASE)
    bulk4 = re.search(r"4\+\s+\$?(\d+(?:\.\d+)?|\.\d+)", text)
    bulk6 = re.search(r"6\+\s+\$?(\d+(?:\.\d+)?|\.\d+)", text)
    bulk12 = re.search(r"12\+\s+\$?(\d+(?:\.\d+)?|\.\d+)", text)

    product_name = clean_desc(text.split(" LIST ", 1)[0].split(" MAP ", 1)[0])
    if product_name.startswith(f"{sku} "):
        product_name = product_name[len(sku) :].strip()

    return [
        {
            "sort_order": str(sort_order),
            "page": page,
            "story_id": story_id,
            "brand": infer_brand(text, sku),
            "top_category": "Band & Orchestra",
            "subcategory": subcategory,
            "sku": sku,
            "product_name": product_name or sku,
            "description": text,
            "notes": text,
            "colors": "",
            "list_price": normalize_money(list_match.group(1)) if list_match else "",
            "map_price": normalize_money(map_match.group(1)) if map_match else "",
            "net_price": normalize_money(net_match.group(1)) if net_match else "",
            "net_price_if_buy_4_or_more": normalize_money(bulk4.group(1)) if bulk4 else "",
            "net_price_if_buy_6_or_more": normalize_money(bulk6.group(1)) if bulk6 else "",
            "net_price_if_buy_12_or_more": normalize_money(bulk12.group(1)) if bulk12 else "",
            "source_image_name": "",
            "source_image_path": "",
        }
    ]


def load_story_texts(zip_file):
    story_text = {}
    for name in zip_file.namelist():
        if not name.startswith("Stories/Story_"):
            continue
        story_id = name.split("Story_")[1].split(".xml")[0]
        story_text[story_id] = walk_text(ET.fromstring(zip_file.read(name)))
    return story_text


def main():
    rows = []
    qa_rows = []
    sort_order = 1

    with zipfile.ZipFile(IDML_PATH) as z:
        story_text = load_story_texts(z)
        for spread_name, (subcategory, page) in SPREAD_MAP.items():
            xml = z.read(spread_name).decode("utf-8", errors="ignore")
            story_ids = re.findall(r'ParentStory="([^"]+)"', xml)
            seen = []
            for story_id in story_ids:
                if story_id in seen:
                    continue
                seen.append(story_id)
                text = story_text.get(story_id, "").strip()
                if looks_like_noise(text):
                    continue
                story_rows_found = story_rows(story_id, text, subcategory, page, sort_order)
                if story_rows_found:
                    rows.extend(story_rows_found)
                    sort_order += 1
                else:
                    qa_rows.append(
                        {
                            "page": page,
                            "subcategory": subcategory,
                            "story_id": story_id,
                            "issue": "Unparsed story text",
                            "raw_text": text,
                        }
                    )

    with OUTPUT_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)

    with QA_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["page", "subcategory", "story_id", "issue", "raw_text"])
        writer.writeheader()
        writer.writerows(qa_rows)

    print(f"Wrote {len(rows)} starter rows to {OUTPUT_CSV}")
    print(f"Wrote {len(qa_rows)} QA rows to {QA_CSV}")


if __name__ == "__main__":
    main()
