# Catalog Image Intake Rulebook

This rulebook defines the standard for every future catalog image so the source CSVs, generated catalog data, and live UI all stay aligned.

## Goal

Every catalog-ready image should:

- live in the organized `Photos` library
- use a predictable filename
- be exactly `2048x2048`
- preserve the same visual framing used in the UI
- be referenced from the source CSVs using the final `Photos` path

## Main Image Library

Use this folder as the single source of truth for catalog-ready images:

```text
/Users/lpdmusic/Documents/New project/Photos
```

## Category Folder Structure

Put each image inside the matching top-level category folder:

```text
Photos/
Fretted Instruments/
Amplifiers & Effects/
Accessories/
Percussion/
Keyboards/
Band & Orchestra/
Pro Audio/
Harmonicas, Books & Novelties/
```

If a product belongs to `Fretted Instruments`, its catalog-ready image goes in:

```text
/Users/lpdmusic/Documents/New project/Photos/Fretted Instruments
```

## Filename Standard

Use this naming format:

```text
brand_sku_finish.ext
```

Rules:

- use lowercase
- use hyphens instead of spaces inside values
- use underscores only between `brand`, `sku`, and `finish`
- keep filenames ASCII only
- keep the file extension that best preserves the image
- prefer `.png` when transparency matters
- use `.jpg` only when the image is fully opaque and does not need transparency

Examples:

```text
danelectro_d56u2-blk_black.png
aria-pro-ii_stg-003_black.png
twisted-wood_pi-100s_default.png
lee-oskar_1910_default.png
```

## Finish Naming in Filenames

The `finish` portion of the filename should be:

- the actual color or finish name when the product has multiple finishes
- `default` when there is only one image for the SKU or one image is used as the representative image

Examples:

```text
aria-pro-ii_714-mk2_ruby-red.jpg
twisted-wood_ko-1000c_default.png
applecreek_acd100k_default.jpg
```

## Image Size Standard

Every catalog-ready image in `Photos` must be:

```text
2048 x 2048 pixels
```

Rules:

- do not crop differently unless intentionally approved
- preserve the current visual look used in the catalog UI
- fit the full product into the square
- center the product on the canvas
- use transparent padding for images that need transparency
- use white padding for fully opaque images

The UI uses `object-fit: contain`, so the goal is to preserve whole-product framing inside a square canvas.

## Image Orientation Standard

Rules:

- instruments should be upright unless a specific product family intentionally uses a different angle
- do not leave a product sideways if the catalog style expects upright presentation
- if an image has already been approved visually in the UI, preserve that orientation exactly

## Source CSV Rules

The source CSVs must point to the final catalog-ready file paths in `Photos`.

Current source files:

```text
/Users/lpdmusic/Documents/New project/stringed-catalog-data.csv
/Users/lpdmusic/Documents/New project/harmbooks-catalog-data.csv
```

Use these columns:

- `stringed-catalog-data.csv`
  - `source_image_name`
  - `source_image_path`
- `harmbooks-catalog-data.csv`
  - `source_image_name`
  - `normalized_image_path`

Rules:

- `source_image_name` should match the final filename in `Photos`
- image path columns should use the absolute path to the file in `Photos`
- do not point source rows at old Dropbox `Links` assets once the catalog-ready `Photos` version exists
- do not point source rows at temporary processing folders

## Representative Images for Multi-Finish Products

Some source rows only support one image path even when the SKU has multiple finishes.

For those rows:

- use a valid representative image from the same SKU in `Photos`
- prefer the first listed finish or the most standard finish unless a different finish is clearly intended
- keep the multi-finish logic in the generated catalog data intact

The source row image is the row-level representative image.
The generated catalog data may still contain multiple finish images for the live UI.

## Intake Workflow For New Images

When adding a new product image:

1. Place or generate the image in the correct `Photos/<Category>/` folder.
2. Rename it to the `brand_sku_finish.ext` format.
3. Normalize it to `2048x2048`.
4. Confirm the product is oriented correctly.
5. Update the source CSV image fields to the new filename and absolute `Photos` path.
6. Rebuild the catalog.
7. Validate that all generated image paths exist.
8. Confirm the UI still loads the image correctly.

## Rebuild Step

After changing image paths or adding images, rebuild with:

```bash
python3 "/Users/lpdmusic/Documents/New project/catalog-prototype/scripts/merge_catalog_sections.py"
```

## Validation Checklist

After rebuild, confirm:

- all generated image paths point into `Photos`
- no generated image paths are missing
- no blank image references exist
- no rows appear in `catalog-skus-needing-images.csv`

Important generated files:

```text
/Users/lpdmusic/Documents/New project/catalog-prototype/data/catalog-products.js
/Users/lpdmusic/Documents/New project/catalog-prototype/exports/products.csv
/Users/lpdmusic/Documents/New project/catalog-prototype/exports/finishes.csv
/Users/lpdmusic/Documents/New project/catalog-skus-needing-images.csv
```

## What Not To Do

- do not use random filenames from vendor downloads
- do not leave images in category folders with spaces, mixed casing, or unclear names
- do not point source CSVs at old placeholder files if a proper `Photos` asset exists
- do not overwrite framing in a way that changes the approved catalog look
- do not use temporary processing folders as final source paths

## Current System Standard

The current catalog system assumes:

- `Photos` is the final image library
- source CSVs point to `Photos`
- generated catalog data points to `Photos`
- catalog-ready images are `2048x2048`

Any future category work should follow this exact format.
