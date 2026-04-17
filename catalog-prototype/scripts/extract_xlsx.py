#!/usr/bin/env python3

import re
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

NS = {"main": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}


def parse_xlsx_rows(path: Path):
    with zipfile.ZipFile(path) as archive:
        shared_strings = []
        if "xl/sharedStrings.xml" in archive.namelist():
            root = ET.fromstring(archive.read("xl/sharedStrings.xml"))
            for item in root.findall("main:si", NS):
                shared_strings.append("".join(node.text or "" for node in item.iterfind(".//main:t", NS)))

        sheet = ET.fromstring(archive.read("xl/worksheets/sheet1.xml"))
        rows = []
        for row in sheet.findall(".//main:sheetData/main:row", NS):
            cells = {}
            for cell in row.findall("main:c", NS):
                reference = cell.attrib.get("r", "")
                match = re.match(r"([A-Z]+)", reference)
                if not match:
                    continue
                column = match.group(1)
                value_type = cell.attrib.get("t")
                value_node = cell.find("main:v", NS)
                value = "" if value_node is None else value_node.text or ""
                if value_type == "s" and value:
                    value = shared_strings[int(value)]
                elif value_type == "inlineStr":
                    inline = cell.find("main:is", NS)
                    value = "" if inline is None else "".join(node.text or "" for node in inline.iterfind(".//main:t", NS))
                cells[column] = value
            rows.append(cells)
        return rows


def build_records(rows):
    header_row = rows[0]
    headers = {column: value.strip() for column, value in header_row.items() if value and value.strip()}
    records = []
    for row in rows[1:]:
        record = {}
        for column, header_name in headers.items():
          record[header_name] = row.get(column, "").strip()
        if not any(record.values()):
            continue
        records.append(
            {
                "brand": record.get("Brand", ""),
                "productName": record.get("Product Name", ""),
                "sku": record.get("SKU", ""),
                "section": record.get("Section", ""),
                "category": record.get("Category", ""),
                "map": record.get("MAP", ""),
                "list": record.get("LIST", ""),
                "net": record.get("NET", ""),
            }
        )
    return records
