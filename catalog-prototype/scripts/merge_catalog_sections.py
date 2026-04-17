#!/usr/bin/env python3

import csv
import json
from collections import defaultdict
from pathlib import Path
import re
import unicodedata
import zipfile

ROOT = Path("/Users/lpdmusic/Documents/New project/catalog-prototype")
DATA_JS = ROOT / "data" / "catalog-products.js"
HARM_CSV = Path("/Users/lpdmusic/Documents/New project/harmbooks-catalog-data.csv")
STRINGED_CSV = Path("/Users/lpdmusic/Documents/New project/stringed-catalog-data.csv")
KEYBOARD_CSV = Path("/Users/lpdmusic/Documents/New project/keyboard-catalog-data.csv")
PERCUSSION_CSV = Path("/Users/lpdmusic/Documents/New project/percussion-catalog-data.csv")
BAND_ORCHESTRA_CSV = Path("/Users/lpdmusic/Documents/New project/band-orchestra-catalog-data.csv")
SOURCE_DANELECTRO_ZIP = Path("/Users/lpdmusic/Documents/OTHER/SHOPIFY/PRODUCT IMAGES/DANELECTRO.zip")
DANELECTRO_IMAGE_ROOT = ROOT / "images-source" / "DANELECTRO"
CATALOG_LINKS_ROOT = Path("/Users/lpdmusic/Library/CloudStorage/Dropbox/Catalogs/LPD CATALOG 2026/CATALOG 2026/NEW CATALOG Folder/Links")
PERCUSSION_PHOTO_ROOT = Path("/Users/lpdmusic/Documents/New project/Photos/Percussion")
BAND_ORCHESTRA_PHOTO_ROOT = Path("/Users/lpdmusic/Documents/New project/Photos/Band & Orchestra")
MERGED_PRODUCTS_CSV = ROOT / "exports" / "products.csv"
MERGED_FINISHES_CSV = ROOT / "exports" / "finishes.csv"
MERGE_QA_CSV = ROOT / "exports" / "merge-qa-report.csv"
PHOTO_LIBRARY_MANIFEST_CSV = ROOT / "exports" / "photo-library-manifest.csv"
SECTION_ORDER = [
    "Fretted Instruments",
    "Amplifiers & Effects",
    "Accessories",
    "Percussion",
    "Keyboards",
    "Band & Orchestra",
    "Pro Audio",
    "Harmonicas, Books & Novelties",
]
GENERIC_WORDS = {"danelectro", "electric"}
SPECIAL_FINISH_IMAGES = {
    "D57": [
        ("Limo Black", "danelectro_d57_black.png", str(Path("/Users/lpdmusic/Documents/New project/Photos/Fretted Instruments/danelectro_d57_black.png"))),
        ("Jade", "danelectro_d57_jade.png", str(Path("/Users/lpdmusic/Documents/New project/Photos/Fretted Instruments/danelectro_d57_jade.png"))),
    ],
    "STOCK 59": [
        ("Black", "danelectro_stock-59_black.png", str(Path("/Users/lpdmusic/Documents/New project/Photos/Fretted Instruments/danelectro_stock-59_black.png"))),
        ("Cream", "danelectro_stock-59_cream.png", str(Path("/Users/lpdmusic/Documents/New project/Photos/Fretted Instruments/danelectro_stock-59_cream.png"))),
        ("Red", "danelectro_stock-59_red.png", str(Path("/Users/lpdmusic/Documents/New project/Photos/Fretted Instruments/danelectro_stock-59_red.png"))),
        ("Aqua", "danelectro_stock-59_aqua.png", str(Path("/Users/lpdmusic/Documents/New project/Photos/Fretted Instruments/danelectro_stock-59_aqua.png"))),
        ("Vintage Aqua", "danelectro_stock-59_vintage-aqua.png", str(Path("/Users/lpdmusic/Documents/New project/Photos/Fretted Instruments/danelectro_stock-59_vintage-aqua.png"))),
    ],
    "D59M-PLUS": [
        ("Keen Green", "danelectro_d59m-plus_keen-green.png", str(Path("/Users/lpdmusic/Documents/New project/Photos/Fretted Instruments/danelectro_d59m-plus_keen-green.png"))),
        ("Ice Grey", "danelectro_d59m-plus_ice-grey.png", str(Path("/Users/lpdmusic/Documents/New project/Photos/Fretted Instruments/danelectro_d59m-plus_ice-grey.png"))),
        ("Red", "danelectro_d59m-plus_red.png", str(Path("/Users/lpdmusic/Documents/New project/Photos/Fretted Instruments/danelectro_d59m-plus_red.png"))),
        ("Copper", "danelectro_d59m-plus_copper.png", str(Path("/Users/lpdmusic/Documents/New project/Photos/Fretted Instruments/danelectro_d59m-plus_copper.png"))),
        ("Go Go Blue", "danelectro_d59m-plus_go-go-blue.png", str(Path("/Users/lpdmusic/Documents/New project/Photos/Fretted Instruments/danelectro_d59m-plus_go-go-blue.png"))),
        ("Baby Blue", "danelectro_d59m-plus_baby-blue.png", str(Path("/Users/lpdmusic/Documents/New project/Photos/Fretted Instruments/danelectro_d59m-plus_baby-blue.png"))),
        ("Black", "danelectro_d59m-plus_black.png", str(Path("/Users/lpdmusic/Documents/New project/Photos/Fretted Instruments/danelectro_d59m-plus_black.png"))),
    ],
    "D59M-PLUS-MF": [
        ("Blue Metalflake", "danelectro_d59m-plus-mf_blue-metalflake.png", str(Path("/Users/lpdmusic/Documents/New project/Photos/Fretted Instruments/danelectro_d59m-plus-mf_blue-metalflake.png"))),
        ("Silver Metalflake", "danelectro_d59m-plus-mf_silver-metalflake.png", str(Path("/Users/lpdmusic/Documents/New project/Photos/Fretted Instruments/danelectro_d59m-plus-mf_silver-metalflake.png"))),
        ("Orange Metalflake", "danelectro_d59m-plus-mf_orange-metalflake.png", str(Path("/Users/lpdmusic/Documents/New project/Photos/Fretted Instruments/danelectro_d59m-plus-mf_orange-metalflake.png"))),
        ("Red Metalflake", "danelectro_d59m-plus-mf_red-metalflake.png", str(Path("/Users/lpdmusic/Documents/New project/Photos/Fretted Instruments/danelectro_d59m-plus-mf_red-metalflake.png"))),
    ],
    "59XT": [
        ("Dark Aqua", "danelectro_59xt_aqua.png", str(Path("/Users/lpdmusic/Documents/New project/Photos/Fretted Instruments/danelectro_59xt_aqua.png"))),
        ("Black", "danelectro_59xt_black.png", str(Path("/Users/lpdmusic/Documents/New project/Photos/Fretted Instruments/danelectro_59xt_black.png"))),
        ("Silver", "danelectro_59xt_silver.png", str(Path("/Users/lpdmusic/Documents/New project/Photos/Fretted Instruments/danelectro_59xt_silver.png"))),
        ("Dark Burgundy", "danelectro_59xt_burgundy.png", str(Path("/Users/lpdmusic/Documents/New project/Photos/Fretted Instruments/danelectro_59xt_burgundy.png"))),
        ("Vintage Cream", "danelectro_59xt_vintage-cream.png", str(Path("/Users/lpdmusic/Documents/New project/Photos/Fretted Instruments/danelectro_59xt_vintage-cream.png"))),
    ],
    "DPBS": [
        ("Black", "danelectro_dpbs_black.png", str(Path("/Users/lpdmusic/Documents/New project/Photos/Fretted Instruments/danelectro_dpbs_black.png"))),
        ("White", "danelectro_dpbs_white.png", str(Path("/Users/lpdmusic/Documents/New project/Photos/Fretted Instruments/danelectro_dpbs_white.png"))),
    ],
    "D59X12": [
        ("Black", "danelectro_d59x12_black.png", str(Path("/Users/lpdmusic/Documents/New project/Photos/Fretted Instruments/danelectro_d59x12_black.png"))),
        ("Blood Red", "danelectro_d59x12_blood-red.png", str(Path("/Users/lpdmusic/Documents/New project/Photos/Fretted Instruments/danelectro_d59x12_blood-red.png"))),
        ("Vintage Cream", "danelectro_d59x12_vintage-cream.png", str(Path("/Users/lpdmusic/Documents/New project/Photos/Fretted Instruments/danelectro_d59x12_vintage-cream.png"))),
        ("Ice Grey", "danelectro_d59x12_ice-grey.png", str(Path("/Users/lpdmusic/Documents/New project/Photos/Fretted Instruments/danelectro_d59x12_ice-grey.png"))),
        ("Red Burst", "danelectro_d59x12_red-burst.png", str(Path("/Users/lpdmusic/Documents/New project/Photos/Fretted Instruments/danelectro_d59x12_red-burst.png"))),
    ],
    "D56VBAR": [
        ("Black", "danelectro_d56vbar_black.png", str(Path("/Users/lpdmusic/Documents/New project/Photos/Fretted Instruments/danelectro_d56vbar_black.png"))),
        ("Vintage White", "danelectro_d56vbar_vintage-white.png", str(Path("/Users/lpdmusic/Documents/New project/Photos/Fretted Instruments/danelectro_d56vbar_vintage-white.png"))),
        ("Red", "danelectro_d56vbar_metallic-red.png", str(Path("/Users/lpdmusic/Documents/New project/Photos/Fretted Instruments/danelectro_d56vbar_metallic-red.png"))),
        ("Aqua", "danelectro_d56vbar_aqua.png", str(Path("/Users/lpdmusic/Documents/New project/Photos/Fretted Instruments/danelectro_d56vbar_aqua.png"))),
    ],
    "D56BAR": [
        ("Black", "danelectro_d56bar_black.png", str(Path("/Users/lpdmusic/Documents/New project/Photos/Fretted Instruments/danelectro_d56bar_black.png"))),
        ("Red", "danelectro_d56bar_red.png", str(Path("/Users/lpdmusic/Documents/New project/Photos/Fretted Instruments/danelectro_d56bar_red.png"))),
        ("Red Burst", "danelectro_d56bar_red-burst.png", str(Path("/Users/lpdmusic/Documents/New project/Photos/Fretted Instruments/danelectro_d56bar_red-burst.png"))),
    ],
    "PGG-259": [
        ("Black", "pgg259_bk_Pignose_product_1800x1800.png"),
        ("White", "pgg259_wh_Pignose_product_1800x1800 (1).png"),
    ],
    "PGG-200PL": [
        ("Pink Paisley", "pgg200pl_pkpl_Pignose_product_1800x1800.png"),
        ("Blue Paisley", "pgg200pl_blpl_Pignose_product_1800x1800.png"),
        ("Black Paisley", "pgg200pl_bkpl_Pignose_product_1800x1800.png"),
    ],
    "PGG-200": [
        ("Brown Sunburst", "PGG-200_BS.png"),
        ("Black", "PGG-200_BK.png"),
        ("Candy Apple Red", "PGG-200-CA.png"),
        ("Metallic Blue", "PGG-200_mbl_Pignose.png"),
    ],
    "PGB-200": [
        ("Brown Sunburst", "PGB-200_bs_Pignose.png"),
    ],
    "313-MK2": [
        ("Sunburst", "Aria 313mk2_opsb.jpg"),
        ("Natural", "aria 313mk2_opn.jpg"),
    ],
    "313-MKII/5": [
        ("Sunburst", "Aria 313mk2_5_opsb.jpeg"),
        ("Natural", "Aria 313mk2_5_opn.jpeg"),
    ],
    "313-BB/5-DETROIT": [
        ("Bourbon Barrel", "313bb_5_product_1800x1800.png"),
    ],
    "313-BB-DETROIT": [
        ("Bourbon Barrel", "313bb_bb_product_1800x1800.png"),
    ],
    "313-JP-DETROIT (FRETLESS)": [
        ("Sunburst", "313jp-front.jpeg"),
    ],
    "RSB-618/4": [
        ("Black", "rsb618_4_bk.jpeg"),
        ("White", "aria rsb618_4_wh.jpeg"),
    ],
    "IGB-STD/5-MBK": [
        ("Metallic Black", "igb-std-5-mbk.png"),
    ],
    "J-B": [
        ("SVW (See-Through Vintage White)", "Aria jet_b_svw.jpeg"),
        ("BK (Black)", "Aria jet_b_bk.jpeg"),
        ("3TS (3 Tone Sunburst)", "Aria jet_b_3ts.jpeg"),
    ],
    "STB-JB": [
        ("Black", "aria stb_jb_bk.jpeg"),
        ("3 Tone Sunburst", "Aria stb_jb_3ts.jpeg"),
        ("White", "aria stb_jb_wh.jpeg"),
    ],
    "STB-JB/TT": [
        ("Black", "stbjb_tt_bk.jpg"),
        ("Sunburst", "stbjb_tt_3ts.jpg"),
    ],
    "STB-PBB-WH": [
        ("White w/Rosewood", "aria stbpb_b_wh.jpeg"),
        ("White w/Maple", "stbpb-m-wh.jpeg"),
    ],
    "STB-PB": [
        ("3 Tone Sunburst", "stbpb_3ts_201512.jpg"),
        ("Black", "stbpb_bk_201701.jpg"),
        ("White", "Aria stbpb maple white.jpg"),
    ],
    "SB-700": [
        ("Gold Wing", "gold wing no bg.png"),
    ],
    "SB-ONE": [
        ("Black", "sb_one_bk_product_1800x1800.jpg"),
        ("Candy Apple Red", "sb_one_ca_product_1800x1800.jpg"),
        ("Silver", "sb_one_slv_product_1800x1800.jpg"),
    ],
    "J-B’ TONE": [
        ("Black", "j_btone_bk_product_1800x1800_2023.png"),
        ("Sunburst", "Aria jet baritone 3ts.jpg"),
    ],
    "212-MK2": [
        ("Pink", "212-MK2-Bowery pink.jpg"),
        ("Black", "212mk2_bk_Aria.png"),
        ("Brown Sunburst", "212-MK2-Bowery brown sunburst.webp"),
    ],
    "615-MK2": [
        ("Marble White", "Aria 615_mk2_mbwh.png"),
        ("Turquoise Blue", "aria 615_mk2_tqbl.png"),
    ],
    "615-WJ-BK": [
        ("Black", "Aria 615wj_bk.jpeg"),
    ],
    "615-GH": [
        ("Brown", "aria 615gh.png"),
    ],
    "718MKII-OPWH": [
        ("Black", "718mk2_opbk_product_1800x1800-1.png"),
        ("White", "Aria 718mk2_opwh white.jpeg"),
    ],
    "714-MK2": [
        ("Turquoise Blue", "714mk2_tqbl_hotrod_product_1800x1800_20230823.jpg"),
        ("Ruby Red", "714mk2_rbrd_hotrod_product_1800x1800_20230829.jpg"),
        ("Black Diamond", "714mk2_bkdm_hotrod_product_1800x1800_20230829.jpg"),
    ],
    "714-JH-FULLERTON": [
        ("Marble White", "aria 714_jh.jpg"),
    ],
    "714-STD-FULLERTON": [
        ("3 Tone Sunburst", "Aria-714std-3ts-brighter.png"),
        ("Black", "714std_bk_vert.png"),
        ("Vintage White", "Aria 714 white cutout.png"),
    ],
    "714-DG-FULLERTON": [
        ("Black", "714dg_bk_hotrod_product_1800x1800.png"),
    ],
    "PE-590AF": [
        ("Aged Cherry Sunburst", "PE590AF.jpg"),
    ],
    "PE-590STD": [
        ("Aged Cherry Sunburst", "pe590std_agcs_product_1800x1800.png"),
    ],
    "PE-F80": [
        ("Black Top", "pef80-bktp.png"),
    ],
    "PE-350PF": [
        ("Aged Black", "aria pe350pf_agbk.jpg"),
    ],
    "PE-350PG": [
        ("Aged Lemon Drop", "aria pe350pg_agld.jpg"),
    ],
    "PE-350STD": [
        ("Brown Sunburst", "Aria pe350std_agvs.jpg"),
        ("Black", "Aria pe350std_agbk.jpg"),
        ("Cherry Sunburst", "Aria pe350std_agcs.jpg"),
    ],
    "PE-350CST": [
        ("Aged Black", "Aria pe350cst_agbk.jpg"),
        ("Aged White", "Aria pe350cst_agwh.jpg"),
    ],
    "MAC DLX": [
        ("Stained Brown", "aria macdlx_stbr.jpeg"),
        ("Stained Black", "Aria mac dlx_stbk.jpg"),
    ],
    "MAC-STD": [
        ("Metallic Red Shade", "MAC-STD-upright.jpg", str(ROOT / "processed-images" / "aria" / "MAC-STD-upright.jpg")),
    ],
    "DM206": [
        ("Black Retro", "dm206_bk_retro_product_1800x18002301.png"),
        ("Vintage White", "aria dm206_vw.jpeg"),
        ("3 Tone Sunburst", "aria dm206_3ts.jpeg"),
    ],
    "DMB-206": [
        ("Vintage White", "dmb206_vw_retro_bass_product_1800x1800_2301.png"),
        ("3 Tone Sunburst", "dmb206_3ts_retro_bass_product_1800x1800_2301.png"),
        ("Black", "dmb206_bk_retro_bass_product_1800x1800_2301.png"),
    ],
    "IGB-STD": [
        ("Metallic Red Shade", "igb-std-mrs.png"),
        ("Metallic Black", "igb-std-mbk.jpg"),
    ],
    "TEG-TL": [
        ("Natural", "aria-615.png"),
        ("Metallic Ice Blue", "615tl_mib_full.png"),
        ("White with Tortoise Shell Pickguard", "TEG-TL-white_w__tortoise_shell_pickguard.png"),
    ],
    "TEG-002M": [
        ("3 Tone Sunburst", "TEG-002_3TS_front_Aria.png"),
        ("Black", "TEG-002_BK_front_Aria.png"),
        ("Ivory", "TEG-002_IV_front_Aria.png"),
        ("Black w/ Red Tortoise Pickguard", "Aria teg002_ttbk.jpeg"),
        ("Candy Apple Red", "TEG-002_CA_front_Aria.png"),
    ],
    "STG-MINI": [
        ("3 Tone Sunburst", "stgmini_3ts_product_1800x1800.png"),
        ("Black", "stgmini_bk_product_1800x1800.png"),
        ("Kawaii Pink", "stgmini_kwpk_product_1800x1800.png"),
    ],
    "STG-003": [
        ("3 Tone Sunburst", "stg003_3ts_2016.jpg"),
        ("Black", "stg003_bk_2016.jpg"),
        ("Candy Apple Red", "stg003_ca_2016.jpg"),
        ("Metal Blue", "stg003_mbl_2016.jpg"),
        ("White", "stg003_wh_2016.jpg"),
        ("Green", "Aria STG-003 SFGR_.png"),
        ("Sonic Blue", "Aria STG-003 SNBL.png"),
    ],
    "STG-003-LEFTY": [
        ("3 Tone Sunburst", "stg003_3ts_L_product_1800x1800.png"),
        ("Black", "stg003_L_bk_product_1800x1800.png"),
    ],
    "STG-003SPL": [
        ("Black/Maple Fingerboard", "stg003_spl_bk.jpg"),
        ("Vintage White", "stg003_spl_vw.jpg"),
        ("3 Tone Sunburst", "stg003_spl_3ts.jpg"),
    ],
    "J-1": [
        ("Black", "Aria jet1 black.jpg"),
        ("Candy Apple Red", "Aria jet1 red.jpg"),
        ("See Through Vintage White", "Aria jet1 white.jpg"),
    ],
    "J-2": [
        ("Candy Apple Red", "Aria jet 2 body red.jpg"),
    ],
    "ARIA-151LIL": [
        ("Orange Sunburst", "aria 151_mtos.jpg"),
        ("Tobacco Sunburst", "aria 151_mtts.jpg"),
        ("Natural", "aria 151_mtn.jpg"),
        ("Black", "aria151_mtbk.jpg"),
    ],
    "ARIA-131DP": [
        ("Muddy Brown", "aria131dp_mubr_201602.jpg"),
    ],
    "ARIA-131": [
        ("Natural", "aria131_mtn_201511.jpg"),
    ],
    "ARIA-111": [
        ("Cherry Burst", "aria111_mtcs_201512.jpg"),
    ],
    "ARIA-101DP": [
        ("Muddy Brown", "aria111dp_mubr_201602.jpg"),
    ],
    "ARIA-101UP": [
        ("Red", "aria 101up_strd.jpg"),
        ("Green", "aria 101up_stgr.jpg"),
        ("Blue", "aria 101up_stbl.jpg"),
    ],
    "ARIA-131UP": [
        ("Red", "aria 131up_strd.jpg"),
        ("Blue", "aria 131up_stbl.jpg"),
        ("Green", "aria 131up_stgr.jpg"),
        ("Black", "aria131up_stbk.jpg"),
    ],
    "ARIA-111DP": [
        ("Muddy Brown", "aria111dp_mubr_201602.jpg"),
    ],
    "ARIA-111DP-L": [
        ("Muddy Brown", "aria111dp_mubr_201602.jpg"),
    ],
    "ARIA-101": [
        ("Tobacco Burst", "aria101_ts.png", str(ROOT / "processed-images" / "aria" / "aria101_ts.png")),
    ],
    "A-35CE": [
        ("Default", "a35ce_product_1800x1800.png"),
    ],
    "FEB-F2M": [
        ("Stained Brown", "FEB Brown.jpeg"),
        ("Stained Black", "Aria FEBF2FL Blk.jpeg"),
    ],
    "FEB-F2/FL": [
        ("Stained Brown", "FEB Brown.jpeg"),
        ("Stained Black", "Aria FEBF2FL Blk.jpeg"),
    ],
    "FET-F2": [
        ("Stained Brown", "fetf2_stbr_product_1800x1800.png"),
    ],
    "GUITARLELE": [
        ("Default", "GUITARLELE.png"),
    ],
    "GC39-PRO-SLIM-Q": [
        ("Default", "GC-39 PRO SLIM Q.png"),
    ],
    "GA38-ROCKANDROSES": [
        ("Default", "GA-38-ROCK&ROSES.png"),
    ],
    "U23-ROCK&ROSES": [
        ("Default", "Flower&RollBamboo.jpeg"),
    ],
    "U23-FAIRY": [
        ("Default", "U23-THE-FAIRY-CONCERT-Bamboo.png"),
    ],
    "U-30-SAPELE-Q": [
        ("Default", "U-30 SAPELE.png"),
    ],
}

_PHOTO_LIBRARY_INDEX = None
_PERCUSSION_IMAGE_INDEX = None


def load_photo_library_index():
    global _PHOTO_LIBRARY_INDEX
    if _PHOTO_LIBRARY_INDEX is not None:
        return _PHOTO_LIBRARY_INDEX

    by_sku_finish_source = {}
    by_sku_finish = {}
    if PHOTO_LIBRARY_MANIFEST_CSV.exists():
        with PHOTO_LIBRARY_MANIFEST_CSV.open(newline="", encoding="utf-8") as handle:
            for row in csv.DictReader(handle):
                sku = (row.get("sku") or "").strip().upper()
                finish = normalize(row.get("finish") or "")
                source_image = (row.get("source_image") or "").strip()
                new_image = (row.get("new_image") or "").strip()
                if not sku or not new_image:
                    continue
                by_sku_finish_source[(sku, finish, source_image)] = row
                by_sku_finish.setdefault((sku, finish), row)

    _PHOTO_LIBRARY_INDEX = {
        "by_sku_finish_source": by_sku_finish_source,
        "by_sku_finish": by_sku_finish,
    }
    return _PHOTO_LIBRARY_INDEX


def use_photo_library_paths(sku, finishes):
    photo_index = load_photo_library_index()
    for finish in finishes:
        finish_name = normalize(finish.get("finish") or "")
        image_url = (finish.get("imageUrl") or "").strip()
        photo_row = photo_index["by_sku_finish_source"].get((sku, finish_name, image_url))
        if not photo_row:
            photo_row = photo_index["by_sku_finish"].get((sku, finish_name))
        if not photo_row:
            continue
        new_image = photo_row["new_image"]
        finish["imageFile"] = Path(new_image).name
        finish["imageUrl"] = new_image
    return finishes


def normalize_code(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", str(text or "").lower())


def load_percussion_image_index():
    global _PERCUSSION_IMAGE_INDEX
    if _PERCUSSION_IMAGE_INDEX is not None:
        return _PERCUSSION_IMAGE_INDEX

    by_sku = defaultdict(list)
    if PERCUSSION_PHOTO_ROOT.exists():
        for path in sorted(PERCUSSION_PHOTO_ROOT.iterdir()):
            if not path.is_file() or path.name.startswith("."):
                continue
            parts = path.stem.split("_")
            if len(parts) < 2:
                continue
            by_sku[normalize_code(parts[1])].append(path)

    _PERCUSSION_IMAGE_INDEX = by_sku
    return _PERCUSSION_IMAGE_INDEX


def percussion_image_matches(sku: str):
    return load_percussion_image_index().get(normalize_code(sku), [])


def bulk_price_fields():
    return [
        ("netBulk4", "net_price_if_buy_4_or_more"),
        ("netBulk5", "net_price_if_buy_5_or_more"),
        ("netBulk6", "net_price_if_buy_6_or_more"),
        ("netBulk10", "net_price_if_buy_10_or_more"),
        ("netBulk12", "net_price_if_buy_12_or_more"),
        ("netBulk20", "net_price_if_buy_20_or_more"),
        ("netBulk24", "net_price_if_buy_24_or_more"),
        ("netBulk36", "net_price_if_buy_36_or_more"),
    ]


def parsed_bulk_prices(row):
    return {target: parse_money(row.get(source, "")) for target, source in bulk_price_fields()}


def percussion_row_image_paths(row):
    image_path = (row.get("source_image_path") or "").strip()
    image_name = (row.get("source_image_name") or "").strip()
    if image_path and image_name:
        return image_name, image_path, "csv-linked"

    matches = percussion_image_matches(row.get("sku", ""))
    if matches:
        chosen = matches[0]
        return chosen.name, str(chosen), "variant-image"

    return "", "", ""


def grouped_family_products(rows, row_image_path_resolver):
    grouped = {}

    for row in rows:
        family_id = (row.get("product_family_id") or "").strip()
        key = family_id or f"sku::{row.get('sku', '').strip().upper()}"
        grouped.setdefault(key, []).append(row)

    products = []

    for family_key, family_rows in grouped.items():
        image_pool = []
        exact_images_by_sku = {}
        for row in family_rows:
            image_name, image_path, match_type = row_image_path_resolver(row)
            if image_path:
                exact_images_by_sku[row.get("sku", "").strip().upper()] = {
                    "imageFile": image_name,
                    "imageUrl": image_path,
                    "matchType": match_type,
                }
                if image_path not in image_pool:
                    image_pool.append(image_path)

        shared_image_path = image_pool[0] if len(image_pool) == 1 else (image_pool[0] if image_pool else "")
        shared_image_file = Path(shared_image_path).name if shared_image_path else ""
        default_row = family_rows[0]
        variants = []

        for row in family_rows:
            sku = row.get("sku", "").strip().upper()
            exact_image = exact_images_by_sku.get(sku, {})
            image_url = exact_image.get("imageUrl") or shared_image_path
            image_file = exact_image.get("imageFile") or shared_image_file
            match_type = exact_image.get("matchType") or ("family-shared-image" if shared_image_path else "")
            variant = {
                "label": (row.get("variant") or "").strip() or "Default",
                "sku": sku,
                "list": parse_money(row.get("list_price", "")),
                "map": parse_money(row.get("map_price", "")),
                "net": parse_money(row.get("net_price", "")),
                "imageFile": image_file,
                "imageUrl": image_url,
                "matchType": match_type or "csv-import",
            }
            variant.update(parsed_bulk_prices(row))
            variants.append(variant)

        default_variant = variants[0]
        notes = default_row.get("notes", "").strip() or default_row.get("colors", "").strip()
        product = {
            "brand": default_row.get("brand", "").strip(),
            "productName": normalize_product_name(default_row.get("product_name", "").strip(), default_variant["sku"]),
            "sku": default_variant["sku"],
            "section": default_row.get("top_category", "").strip(),
            "category": default_row.get("subcategory", "").strip() or "Uncategorized",
            "map": default_variant.get("map", ""),
            "list": default_variant.get("list", ""),
            "net": default_variant.get("net", ""),
            "netBulk4": default_variant.get("netBulk4", ""),
            "netBulk5": default_variant.get("netBulk5", ""),
            "netBulk6": default_variant.get("netBulk6", ""),
            "netBulk10": default_variant.get("netBulk10", ""),
            "netBulk12": default_variant.get("netBulk12", ""),
            "netBulk20": default_variant.get("netBulk20", ""),
            "netBulk24": default_variant.get("netBulk24", ""),
            "netBulk36": default_variant.get("netBulk36", ""),
            "matchType": "csv-import",
            "description": default_row.get("description", "").strip(),
            "notes": notes,
            "finishes": [],
            "variants": variants,
        }
        products.append(product)

    return products


def percussion_grouped_products(rows):
    return grouped_family_products(rows, percussion_row_image_paths)


def band_orchestra_row_image_paths(row):
    image_path = (row.get("source_image_path") or "").strip()
    image_name = (row.get("source_image_name") or "").strip()
    if image_path and image_name:
        return image_name, image_path, "csv-linked"
    return "", "", ""

def load_catalog_products():
    raw = DATA_JS.read_text(encoding="utf-8")
    prefix = "window.CATALOG_PRODUCTS = "
    if not raw.startswith(prefix):
        raise RuntimeError("Unexpected catalog-products.js format")
    payload = raw[len(prefix):].rstrip().rstrip(";")
    return json.loads(payload)


def parse_money(value: str) -> str:
    text = str(value or "").strip()
    if not text:
        return ""
    text = text.replace("$", "").replace(",", "")
    try:
        return f"{float(text):.2f}".rstrip("0").rstrip(".")
    except ValueError:
        return ""


def normalize(text: str) -> str:
    text = (text or "").replace("™", " ")
    text = text.replace("ΓÇÿ", "'").replace("ΓÇÖ", "'").replace("ΓÇ", " ")
    text = unicodedata.normalize("NFKD", text)
    text = text.replace("’", "'").replace("‘", "'")
    text = text.replace("�??", " ")
    text = text.lower().replace("semi-hollow", "semi hollow")
    text = text.replace("longorn", "longhorn")
    text = re.sub(r"[^a-z0-9+]+", " ", text)
    return " ".join(text.split())


def smart_title(text: str) -> str:
    def transform_simple(word: str) -> str:
        cleaned = re.sub(r"^[^A-Za-z0-9]+|[^A-Za-z0-9+]+$", "", word)
        if not cleaned:
            return word
        if re.search(r"[A-Za-z]", cleaned) and cleaned.upper() == cleaned:
            return word.upper()
        has_digit = any(char.isdigit() for char in cleaned)
        has_plus = "+" in cleaned
        no_vowels = not re.search(r"[aeiou]", cleaned, flags=re.IGNORECASE)
        has_trailing_code = bool(re.search(r"\d+[A-Za-z]+$", cleaned))
        is_short_code = len(cleaned) <= 3 and no_vowels
        is_code_word = has_plus or (has_digit and no_vowels) or has_trailing_code or is_short_code
        if is_code_word:
            return word.upper()
        short_code = len(cleaned) <= 3
        should_keep_upper = has_plus or (has_digit and short_code) or (short_code and no_vowels)
        if should_keep_upper:
            return word.upper()
        return word[:1].upper() + word[1:].lower()

    def transform_word(word: str) -> str:
        cleaned = re.sub(r"^[^A-Za-z0-9]+|[^A-Za-z0-9+]+$", "", word)
        if not cleaned:
            return word
        if "-" in word:
            pieces = word.split("-")
            if len(pieces) >= 2 and any(char.isdigit() for char in cleaned):
                if all(re.fullmatch(r"[A-Za-z0-9+]+", piece or "") for piece in pieces):
                    return "-".join(transform_simple(piece) for piece in pieces)
            if len(pieces) >= 2 and all(re.fullmatch(r"[A-Za-z0-9+]+", piece or "") for piece in pieces):
                return "-".join(transform_simple(piece) for piece in pieces)
        return transform_simple(word)

    parts = re.split(r"(\s+)", str(text or ""))
    return "".join(transform_word(part) if not part.isspace() else part for part in parts).strip()


def normalize_product_name(raw_name: str, sku: str) -> str:
    name = " ".join(str(raw_name or "").split())
    return name or str(sku or "").strip().upper()


def family_phrase(name: str) -> str:
    tokens = [token for token in normalize(name).split() if token not in GENERIC_WORDS]
    return " ".join(tokens)


def color_values(row):
    text = (row.get("notes", "") or row.get("colors", "") or "").strip()
    if not text:
        return []
    text = re.sub(r"\s+and\s+", ",", text, flags=re.IGNORECASE)
    text = text.replace("&", ",")
    return [part.strip() for part in text.split(",") if part.strip()]


def color_matches_finish(color: str, finish: str) -> bool:
    def expand_terms(text: str) -> set[str]:
        normalized = normalize(text)
        values = {normalized}
        substitutions = [
            ("dark aqua", "aqua"),
            ("vintage aqua", "aqua"),
            ("seafoam", "seafoam green"),
            ("seafoam green", "seafoam"),
            ("dark burgundy", "burgundy"),
            ("limo black", "black"),
            ("black metal flake", "black metalflake"),
            ("metal flake", "metalflake"),
            ("metalflake", "metal flake"),
            ("red metal flake", "red metalflake"),
            ("silver metal flake", "silver metalflake"),
            ("orange metal flake", "orange metalflake"),
            ("blue metal flake", "blue metalflake"),
            ("metallic red", "red"),
            ("red", "metallic red"),
        ]
        pending = [normalized]
        while pending:
            current = pending.pop()
            for old, new in substitutions:
                if old in current:
                    candidate = " ".join(current.replace(old, new).split())
                    if candidate not in values:
                        values.add(candidate)
                        pending.append(candidate)
        return {value for value in values if value}

    color_norm = normalize(color)
    finish_norm = normalize(finish)
    if not color_norm or not finish_norm:
        return False
    if "metalflake" in finish_norm and "metalflake" not in color_norm:
        return False
    if "metalflake" in color_norm and "metalflake" not in finish_norm:
        return False
    color_terms = expand_terms(color)
    finish_terms = expand_terms(finish)
    return any(left in right or right in left for left in color_terms for right in finish_terms)


def token_score(left: str, right: str) -> float:
    left_tokens = set(left.split())
    right_tokens = set(right.split())
    if not left_tokens:
        return 0.0
    return len(left_tokens & right_tokens) / len(left_tokens)


def extract_finish(image_name: str, phrase: str) -> str:
    stem = normalize(Path(image_name).stem)
    stem = re.sub(r"^danelectro\s+", "", stem)
    stem = re.sub(r"^stock\s+", "", stem)
    finish = stem.replace(phrase, "", 1).strip() if phrase and phrase in stem else stem
    finish = re.sub(r"^(c y|cy)\s+", "", finish)
    if not finish:
        return "Default"
    finish = finish.replace("gogo", "go go")
    return " ".join(word.capitalize() for word in finish.split())


def ensure_danelectro_images():
    if DANELECTRO_IMAGE_ROOT.exists():
        return
    DANELECTRO_IMAGE_ROOT.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(SOURCE_DANELECTRO_ZIP) as archive:
        for member in archive.infolist():
            if member.is_dir():
                continue
            if "__MACOSX/" in member.filename:
                continue
            if not member.filename.startswith("DANELECTRO/"):
                continue
            archive.extract(member, DANELECTRO_IMAGE_ROOT.parent)


def danelectro_image_url(path: Path) -> str:
    return str(path)


def danelectro_match_images(row):
    ensure_danelectro_images()
    phrase = family_phrase(row.get("product_name", ""))
    category = row.get("subcategory", "").strip()

    category_folder = DANELECTRO_IMAGE_ROOT / category if category else None
    other_folders = [folder for folder in DANELECTRO_IMAGE_ROOT.iterdir() if folder.is_dir() and folder != category_folder]
    normalized_name = normalize(row.get("product_name", ""))
    color_list = color_values(row)

    def collect_matches(folders, enforce_lefty=True, match_phrase=phrase):
        exact = []
        fallback = []
        is_lefty = "lefty" in normalized_name
        for folder in folders:
            if not folder.exists():
                continue
            for path in sorted(folder.iterdir()):
                if not path.is_file() or path.name.startswith("."):
                    continue
                stem = normalize(path.stem)
                stem = re.sub(r"^danelectro\s+", "", stem)
                stem_is_lefty = "lefty" in stem
                if enforce_lefty and is_lefty != stem_is_lefty and ("lefty" in normalized_name or "lefty" in stem):
                    continue
                if match_phrase and match_phrase in stem:
                    exact.append(path)
                    continue
                score = token_score(match_phrase, stem)
                if score >= 0.84:
                    fallback.append((score, path))
        matches = exact or [path for _, path in sorted(fallback, key=lambda item: (item[0], item[1].name), reverse=True)]
        unique = []
        seen = set()
        for path in matches:
            key = path.name
            if key in seen:
                continue
            seen.add(key)
            unique.append(path)
        return unique

    def filter_by_colors(paths):
        if not color_list:
            return paths
        filtered = []
        for path in paths:
            finish = extract_finish(path.name, phrase)
            if finish == "Default" and len(color_list) == 1:
                filtered.append(path)
                continue
            if any(color_matches_finish(color, finish) for color in color_list):
                filtered.append(path)
        return filtered

    primary_folders = [category_folder] if category_folder else []
    alternate_phrase = re.sub(r"\blefty\b", "", phrase).strip()
    primary_matches = filter_by_colors(collect_matches(primary_folders))
    if primary_matches:
        return primary_matches

    primary_matches_without_lefty = filter_by_colors(collect_matches(primary_folders, enforce_lefty=False))
    if primary_matches_without_lefty:
        return primary_matches_without_lefty

    if alternate_phrase and alternate_phrase != phrase:
        alternate_primary_matches = filter_by_colors(collect_matches(primary_folders, enforce_lefty=False, match_phrase=alternate_phrase))
        if alternate_primary_matches:
            return alternate_primary_matches

    fallback_matches = filter_by_colors(collect_matches(other_folders))
    if fallback_matches:
        return fallback_matches
    fallback_matches_without_lefty = filter_by_colors(collect_matches(other_folders, enforce_lefty=False))
    if fallback_matches_without_lefty:
        return fallback_matches_without_lefty
    if alternate_phrase and alternate_phrase != phrase:
        return filter_by_colors(collect_matches(other_folders, enforce_lefty=False, match_phrase=alternate_phrase))
    return []


def row_to_product(row):
    sku = row.get("sku", "").strip().upper()
    notes = row.get("notes", "").strip() or row.get("colors", "").strip()
    image_url = row.get("normalized_image_path", "").strip() or row.get("source_image_path", "").strip()
    image_file = row.get("source_image_name", "").strip()
    finishes = []

    colors = color_values(row)

    if sku in SPECIAL_FINISH_IMAGES:
        finishes = []
        for finish_image in SPECIAL_FINISH_IMAGES[sku]:
            finish_name, image_file_name = finish_image[:2]
            image_path = finish_image[2] if len(finish_image) > 2 else str(CATALOG_LINKS_ROOT / image_file_name)
            finishes.append(
                {
                    "finish": finish_name,
                    "imageFile": image_file_name,
                    "imageUrl": image_path,
                }
            )

    if not finishes and row.get("brand", "").strip() == "Danelectro":
        danelectro_matches = danelectro_match_images(row)
        phrase = family_phrase(row.get("product_name", ""))
        finishes = [
            {
                "finish": extract_finish(path.name, phrase),
                "imageFile": path.name,
                "imageUrl": danelectro_image_url(path),
            }
            for path in danelectro_matches
        ]
        if len(finishes) == 1 and len(colors) == 1:
            finishes[0]["finish"] = colors[0]

    if not finishes and image_url:
        finishes = []
        finish_names = colors or ["Default"]
        for finish_name in finish_names:
            finishes.append(
                {
                    "finish": finish_name,
                    "imageFile": image_file,
                    "imageUrl": image_url,
                }
            )

    finishes = use_photo_library_paths(sku, finishes)

    product = {
        "brand": row.get("brand", "").strip(),
        "productName": normalize_product_name(row.get("product_name", "").strip(), sku),
        "sku": sku,
        "section": row.get("top_category", "").strip(),
        "category": row.get("subcategory", "").strip() or "Uncategorized",
        "map": parse_money(row.get("map_price", "")),
        "list": parse_money(row.get("list_price", "")),
        "net": parse_money(row.get("net_price", "")),
        "netBulk4": parse_money(row.get("net_price_if_buy_4_or_more", "")),
        "netBulk5": parse_money(row.get("net_price_if_buy_5_or_more", "")),
        "netBulk6": parse_money(row.get("net_price_if_buy_6_or_more", "")),
        "netBulk10": parse_money(row.get("net_price_if_buy_10_or_more", "")),
        "netBulk12": parse_money(row.get("net_price_if_buy_12_or_more", "")),
        "netBulk20": parse_money(row.get("net_price_if_buy_20_or_more", "")),
        "netBulk24": parse_money(row.get("net_price_if_buy_24_or_more", "")),
        "netBulk36": parse_money(row.get("net_price_if_buy_36_or_more", "")),
        "matchType": "csv-import",
        "description": row.get("description", "").strip(),
        "notes": notes,
        "finishes": finishes,
        "variants": [],
    }
    return product


def row_score(row):
    product_name = row.get("product_name", "").strip()
    image_url = row.get("normalized_image_path", "").strip() or row.get("source_image_path", "").strip()
    return (
        100 if image_url else 0,
        50 if product_name and product_name != row.get("sku", "").strip().upper() else 0,
        len(row.get("description", "").strip()),
        len(product_name),
        len(row.get("notes", "").strip() or row.get("colors", "").strip()),
    )


def clean_section_rows(rows, section_name):
    def duplicate_bucket_key(item):
        sku = item["sku"]
        variant = item.get("variant", "").strip()
        family_id = item.get("product_family_id", "").strip()
        if variant and family_id:
            return f"{sku}::variant::{variant.lower()}"
        return sku

    def merge_duplicate_items(items):
        merged = dict(items[0])
        color_values_seen = []
        for item in items:
            for color in color_values(item):
                if color not in color_values_seen:
                    color_values_seen.append(color)
            if len(item.get("description", "").strip()) > len(merged.get("description", "").strip()):
                merged["description"] = item.get("description", "").strip()
            if len((item.get("notes", "").strip() or item.get("colors", "").strip())) > len((merged.get("notes", "").strip() or merged.get("colors", "").strip())):
                if "notes" in merged:
                    merged["notes"] = item.get("notes", "").strip()
                if "colors" in merged:
                    merged["colors"] = item.get("colors", "").strip()
            if not (merged.get("source_image_path", "").strip()) and item.get("source_image_path", "").strip():
                merged["source_image_path"] = item.get("source_image_path", "").strip()
                merged["source_image_name"] = item.get("source_image_name", "").strip()
        if color_values_seen and "colors" in merged:
            merged["colors"] = ", ".join(color_values_seen)
        return merged

    cleaned = []
    qa_rows = []
    duplicates = {}
    for index, row in enumerate(rows):
        item = dict(row)
        item["_source_index"] = index
        item["top_category"] = item.get("top_category", "").strip() or section_name
        item["sku"] = item.get("sku", "").strip().upper()
        item["brand"] = item.get("brand", "").strip()
        item["subcategory"] = item.get("subcategory", "").strip() or "Uncategorized"
        item["product_name"] = item.get("product_name", "").strip() or item["sku"]
        item["description"] = item.get("description", "").strip()
        if "notes" in item:
            item["notes"] = item.get("notes", "").strip()
        if "colors" in item:
            item["colors"] = item.get("colors", "").strip()

        sku = item["sku"]
        if not sku:
            qa_rows.append(
                {
                    "Section": section_name,
                    "SKU": "",
                    "Issue": "Dropped blank SKU row",
                    "Resolution": "Skipped during merge",
                }
            )
            continue
        duplicates.setdefault(duplicate_bucket_key(item), []).append(item)

    for duplicate_key, items in duplicates.items():
        sku = items[0]["sku"]
        if len(items) == 1:
            cleaned.append(items[0])
            continue
        all_same_product = len({
            (
                item.get("brand", "").strip().lower(),
                item.get("subcategory", "").strip().lower(),
                item.get("product_name", "").strip().lower(),
            )
            for item in items
        }) == 1
        winner = merge_duplicate_items(items) if all_same_product else max(items, key=row_score)
        cleaned.append(winner)
        qa_rows.append(
            {
                "Section": section_name,
                "SKU": sku,
                "Issue": f"Duplicate SKU rows ({len(items)})",
                "Resolution": (
                    f"Merged complementary duplicate rows into row {winner['_source_index'] + 2}"
                    if all_same_product
                    else f"Kept row {winner['_source_index'] + 2} using best available name/image/details"
                ),
            }
        )

    cleaned.sort(key=lambda item: item["_source_index"])
    return cleaned, qa_rows


def load_section_rows(path, section_name):
    with path.open(newline="", encoding="utf-8-sig") as handle:
        rows = list(csv.DictReader(handle))
    return clean_section_rows(rows, section_name)


def merged_products():
    imported_sections = {
        "Fretted Instruments": STRINGED_CSV,
        "Percussion": PERCUSSION_CSV,
        "Keyboards": KEYBOARD_CSV,
        "Band & Orchestra": BAND_ORCHESTRA_CSV,
        "Harmonicas, Books & Novelties": HARM_CSV,
    }
    existing = [
        product
        for product in load_catalog_products()
        if product.get("section") not in imported_sections and product.get("matchType") != "csv-import"
    ]
    all_products = list(existing)
    qa_rows = []

    for section_name in SECTION_ORDER:
        path = imported_sections.get(section_name)
        if not path:
            continue
        cleaned_rows, section_qa = load_section_rows(path, section_name)
        qa_rows.extend(section_qa)
        if section_name == "Percussion":
            all_products.extend(percussion_grouped_products(cleaned_rows))
        elif section_name == "Band & Orchestra":
            all_products.extend(grouped_family_products(cleaned_rows, band_orchestra_row_image_paths))
        else:
            all_products.extend(row_to_product(row) for row in cleaned_rows)

    return all_products, qa_rows


def write_data_js(products):
    DATA_JS.write_text(
        "window.CATALOG_PRODUCTS = " + json.dumps(products, indent=2, ensure_ascii=False) + ";\n",
        encoding="utf-8",
    )


def write_products_csv(products):
    with MERGED_PRODUCTS_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "SKU",
                "Brand",
                "Product Name",
                "Section",
                "Category",
                "MAP",
                "LIST",
                "NET",
                "NET 4+",
                "NET 5+",
                "NET 6+",
                "NET 10+",
                "NET 12+",
                "NET 20+",
                "NET 24+",
                "NET 36+",
                "Image Match Type",
                "Finish Count",
                "Variant Count",
                "Description",
                "Notes",
            ],
        )
        writer.writeheader()
        for product in products:
            writer.writerow(
                {
                    "SKU": product.get("sku", ""),
                    "Brand": product.get("brand", ""),
                    "Product Name": product.get("productName", ""),
                    "Section": product.get("section", ""),
                    "Category": product.get("category", ""),
                    "MAP": product.get("map", ""),
                    "LIST": product.get("list", ""),
                    "NET": product.get("net", ""),
                    "NET 4+": product.get("netBulk4", ""),
                    "NET 5+": product.get("netBulk5", ""),
                    "NET 6+": product.get("netBulk6", ""),
                    "NET 10+": product.get("netBulk10", ""),
                    "NET 12+": product.get("netBulk12", ""),
                    "NET 20+": product.get("netBulk20", ""),
                    "NET 24+": product.get("netBulk24", ""),
                    "NET 36+": product.get("netBulk36", ""),
                    "Image Match Type": product.get("matchType", ""),
                    "Finish Count": len(product.get("finishes", []) or []),
                    "Variant Count": len(product.get("variants", []) or []),
                    "Description": product.get("description", ""),
                    "Notes": product.get("notes", ""),
                }
            )


def write_finishes_csv(products):
    with MERGED_FINISHES_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "SKU",
                "Product Name",
                "Finish",
                "Image File",
                "Image Folder",
                "Image Path",
                "Sort Order",
                "Section",
                "Category",
            ],
        )
        writer.writeheader()
        for product in products:
            finishes = product.get("finishes", []) or []
            if not finishes:
                writer.writerow(
                    {
                        "SKU": product.get("sku", ""),
                        "Product Name": product.get("productName", ""),
                        "Finish": "",
                        "Image File": "",
                        "Image Folder": product.get("category", ""),
                        "Image Path": "",
                        "Sort Order": 1,
                        "Section": product.get("section", ""),
                        "Category": product.get("category", ""),
                    }
                )
                continue
            for index, finish in enumerate(finishes, start=1):
                writer.writerow(
                    {
                        "SKU": product.get("sku", ""),
                        "Product Name": product.get("productName", ""),
                        "Finish": finish.get("finish", ""),
                        "Image File": finish.get("imageFile", ""),
                        "Image Folder": product.get("category", ""),
                        "Image Path": finish.get("imageUrl", ""),
                        "Sort Order": index,
                        "Section": product.get("section", ""),
                        "Category": product.get("category", ""),
                    }
                )


def write_merge_qa_csv(rows):
    with MERGE_QA_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["Section", "SKU", "Issue", "Resolution"])
        writer.writeheader()
        writer.writerows(rows)


def main():
    products, qa_rows = merged_products()
    write_data_js(products)
    write_products_csv(products)
    write_finishes_csv(products)
    write_merge_qa_csv(qa_rows)
    print(f"Merged {len(products)} total products")


if __name__ == "__main__":
    main()
