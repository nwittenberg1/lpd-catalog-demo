# LPD Catalog Portable Demo

This demo is portable as long as these two folders stay together in the same parent folder:

- `catalog-prototype`
- `Photos`

The launcher and local server expect this structure:

```text
Demo Folder/
catalog-prototype/
Photos/
```

## How To Run On Another Mac

1. Copy the full demo parent folder to the other computer.
2. Keep `catalog-prototype` and `Photos` side by side.
3. Open `catalog-prototype`.
4. Double-click:

```text
start_catalog_demo.command
```

5. If macOS warns you, allow it to run.
6. The browser should open:

```text
http://127.0.0.1:8000/catalog-prototype/index.html
```

## Important

- Use the demo from the localhost URL opened by the launcher.
- Do **not** open `index.html` directly in the browser from Finder.
- The dealer list zip export with images depends on the local demo server.

## What Works In The Demo

- catalog browsing
- category switching
- search, filter, sort, and view controls
- product detail pages
- Build Dealer List mode
- one-click zip export:
  - CSV
  - `Images/` folder inside the zip

## If The Browser Opens But Looks Old

Hard refresh the page once:

- `Command + Shift + R`

## If The Launcher Does Not Open

Open Terminal, then run:

```bash
cd "/path/to/your/demo/catalog-prototype"
./start_catalog_demo.command
```

## If macOS Blocks The Launcher

You may need to:

1. Right-click `start_catalog_demo.command`
2. Choose `Open`
3. Confirm the security prompt

After that, future launches should be easier.
