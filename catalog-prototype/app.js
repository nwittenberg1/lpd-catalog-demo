const PROJECT_PHOTOS_PREFIX = "/Users/lpdmusic/Documents/New project/Photos/";

function encodePathPreservingSlashes(path) {
  return String(path || "")
    .split("/")
    .map((segment) => encodeURIComponent(segment))
    .join("/");
}

function portableImageUrl(url) {
  const value = String(url || "");
  if (!value) return "";
  if (/^(https?:|data:|blob:|\.{1,2}\/|\/assets\/|\.\/assets\/)/i.test(value)) return value;
  if (value.startsWith(PROJECT_PHOTOS_PREFIX)) {
    const relativePhotoPath = value.slice(PROJECT_PHOTOS_PREFIX.length);
    return `../Photos/${encodePathPreservingSlashes(relativePhotoPath)}`;
  }
  return value;
}

function absoluteFileUrl(path) {
  const value = String(path || "");
  if (!value.startsWith("/")) return "";
  return `file://${encodePathPreservingSlashes(value)}`;
}

function normalizeVariant(variant) {
  return {
    ...variant,
    sourceImageUrl: variant?.imageUrl || "",
    imageUrl: portableImageUrl(variant?.imageUrl || ""),
  };
}

function normalizeFinish(finish) {
  return {
    ...finish,
    sourceImageUrl: finish?.imageUrl || "",
    imageUrl: portableImageUrl(finish?.imageUrl || ""),
  };
}

function normalizeRecord(record) {
  return {
    ...record,
    variants: Array.isArray(record?.variants) ? record.variants.map(normalizeVariant) : [],
    finishes: Array.isArray(record?.finishes) ? record.finishes.map(normalizeFinish) : [],
  };
}

const records = Array.isArray(window.CATALOG_PRODUCTS) ? window.CATALOG_PRODUCTS.map(normalizeRecord) : [];
const topCategories = [
  {
    name: "Fretted Instruments",
    image: "./assets/categories/fretted.png",
    status: "active",
  },
  {
    name: "Amplifiers & Effects",
    image: "./assets/categories/amps.png",
    status: "coming-soon",
  },
  {
    name: "Accessories",
    image: "./assets/categories/accessories.png",
    status: "coming-soon",
  },
  {
    name: "Percussion",
    image: "./assets/categories/percussion.png",
    status: "coming-soon",
  },
  {
    name: "Keyboards",
    image: "./assets/categories/keyboards.png",
    status: "coming-soon",
  },
  {
    name: "Band & Orchestra",
    image: "./assets/categories/band-orchestra.png",
    status: "coming-soon",
  },
  {
    name: "Pro Audio",
    image: "./assets/categories/pro-audio.png",
    status: "coming-soon",
  },
  {
    name: "Harmonicas, Books & Novelties",
    image: "./assets/categories/harmbooks.png",
    status: "coming-soon",
  },
];

const categoryOrder = topCategories.map((category) => category.name);
const liveSections = categoryOrder.filter((section) => records.some((record) => record.section === section));
let activeSection = "";
let searchQuery = "";
let activeViewMode = "grid-default";
let filtersOpen = false;
let expandedFilterGroup = "";
let sortOpen = false;
let activeSort = "best-match";
let globalDismissalsWired = false;
let dealerSelectionMode = false;
const selectedRecordKeys = new Set();
const activeFilters = {
  productType: new Set(),
  brand: new Set(),
  netPrice: new Set(),
  bulkDeals: new Set(),
  colors: new Set(),
};

const checkboxIcons = {
  active: "./assets/icons/checkbox-active.svg",
  inactive: "./assets/icons/checkbox-inactive.svg",
};

const sortOptions = [
  { key: "best-match", label: "Best Match" },
  { key: "price-low", label: "Price: Low to High" },
  { key: "price-high", label: "Price: High to Low" },
  { key: "name-az", label: "Name: A - Z" },
  { key: "name-za", label: "Name: Z - A" },
];

const bulkDealOptions = [
  { key: "netBulk4", label: "Buy 4 or more" },
  { key: "netBulk5", label: "Buy 5 or more" },
  { key: "netBulk6", label: "Buy 6 or more" },
  { key: "netBulk10", label: "Buy 10 or more" },
  { key: "netBulk12", label: "Buy 12 or more" },
  { key: "netBulk20", label: "Buy 20 or more" },
  { key: "netBulk24", label: "Buy 24 or more" },
  { key: "netBulk36", label: "Buy 36 or more" },
];

const netPriceBuckets = [
  { key: "under-10", label: "Under $10", min: 0, max: 10 },
  { key: "10-24", label: "$10 - $24.99", min: 10, max: 25 },
  { key: "25-49", label: "$25 - $49.99", min: 25, max: 50 },
  { key: "50-99", label: "$50 - $99.99", min: 50, max: 100 },
  { key: "100-249", label: "$100 - $249.99", min: 100, max: 250 },
  { key: "250-plus", label: "$250+", min: 250, max: Infinity },
];

const categoryClassMap = {
  "Electric Guitars": "category-electric",
  "Specialty Guitars": "category-specialty",
  "Bass Guitars": "category-bass",
};

function money(value) {
  const amount = Number(String(value || "").replace(/[$,]/g, ""));
  if (!Number.isFinite(amount) || amount <= 0) return "N/A";
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(amount);
}

function moneyNumber(value) {
  const amount = Number(String(value || "").replace(/[$,]/g, ""));
  return Number.isFinite(amount) && amount > 0 ? amount : null;
}

function sortValue(record) {
  const primary = recordVariantPool(record)[0] || record;
  return moneyNumber(primary.net) ?? moneyNumber(primary.map) ?? moneyNumber(primary.list) ?? Number.POSITIVE_INFINITY;
}

function searchableText(record) {
  const finishes = Array.isArray(record.finishes) ? record.finishes.map((finish) => finish.finish).join(" ") : "";
  const variants = Array.isArray(record.variants)
    ? record.variants.map((variant) => [variant.label, variant.sku].filter(Boolean).join(" ")).join(" ")
    : "";
  return [
    record.productName,
    record.sku,
    record.brand,
    record.category,
    record.section,
    record.description,
    record.notes,
    finishes,
    variants,
  ]
    .filter(Boolean)
    .join(" ")
    .toLowerCase();
}

function slug(text) {
  return String(text || "")
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "");
}

function titleCase(text) {
  const transformSimple = (word) => {
    const cleaned = word.replace(/^[^a-z0-9]+|[^a-z0-9+]+$/gi, "");
    if (!cleaned) return word;
    if (/[a-z]/i.test(cleaned) && cleaned.toUpperCase() === cleaned) {
      return word.toUpperCase();
    }
    const hasPlus = cleaned.includes("+");
    const hasDigit = /\d/.test(cleaned);
    const noVowels = !/[aeiou]/i.test(cleaned);
    const hasTrailingCode = /\d+[a-z]+$/i.test(cleaned);
    const isShortCode = cleaned.length <= 3 && noVowels;
    const shortCode = cleaned.length <= 3;
    const isCodeWord = hasPlus || (hasDigit && noVowels) || hasTrailingCode || isShortCode;
    if (isCodeWord) {
      return word.toUpperCase();
    }
    const shouldKeepUpper = hasPlus || (hasDigit && shortCode) || (shortCode && noVowels);
    if (shouldKeepUpper) {
      return word.toUpperCase();
    }
    return word.charAt(0).toUpperCase() + word.slice(1).toLowerCase();
  };

  const transformWord = (word) => {
    const cleaned = word.replace(/^[^a-z0-9]+|[^a-z0-9+]+$/gi, "");
    if (!cleaned) return word;
    if (word.includes("-")) {
      const parts = word.split("-");
      if (parts.length >= 2 && parts.every((part) => /^[a-z0-9+]*$/i.test(part))) {
        return parts.map(transformSimple).join("-");
      }
    }
    return transformSimple(word);
  };

  return String(text || "").replace(/\S+/g, (word) => transformWord(word));
}

function uniqueValues(values) {
  return Array.from(new Set(values.filter(Boolean)));
}

function recordVariantPool(record) {
  return Array.isArray(record.variants) && record.variants.length ? record.variants : [record];
}

function recordNetValues(record) {
  return uniqueValues(recordVariantPool(record).map((item) => moneyNumber(item.net)).filter((value) => value !== null));
}

function recordBulkDealKeys(record) {
  const matched = new Set();
  recordVariantPool(record).forEach((item) => {
    bulkDealOptions.forEach((option) => {
      if (moneyNumber(item[option.key]) !== null) {
        matched.add(option.key);
      }
    });
  });
  return Array.from(matched);
}

function recordColors(record) {
  const finishes = Array.isArray(record.finishes) ? record.finishes : [];
  return uniqueValues(
    finishes
      .map((finish) => titleCase(finish.finish || ""))
      .filter((finish) => finish && finish !== "Default")
  );
}

function recordColorGroups(record) {
  const grouped = new Map();
  recordColors(record).forEach((colorName) => {
    const swatch = finishDotColor(colorName);
    if (!grouped.has(swatch)) grouped.set(swatch, []);
    grouped.get(swatch).push(colorName);
  });
  return grouped;
}

function optionCountLabel(count) {
  return `(${count})`;
}

function recordSelectionKey(record) {
  const variantSignature = recordVariantPool(record)
    .map((item) => item.sku || "")
    .filter(Boolean)
    .join("|");
  return [record.section, record.brand, record.category, record.productName, variantSignature || record.sku || ""].join("::");
}

function isRecordSelected(record) {
  return selectedRecordKeys.has(recordSelectionKey(record));
}

function recordSelectionToken(record) {
  return encodeURIComponent(recordSelectionKey(record));
}

function toggleRecordSelection(record) {
  const key = recordSelectionKey(record);
  if (selectedRecordKeys.has(key)) {
    selectedRecordKeys.delete(key);
  } else {
    selectedRecordKeys.add(key);
  }
}

function selectedRecords() {
  return records.filter((record) => selectedRecordKeys.has(recordSelectionKey(record)));
}

function exportSkuCount() {
  return selectedRecords().flatMap((record) => exportRowsForRecord(record)).length;
}

function csvEscape(value) {
  const text = String(value ?? "");
  if (/[",\n]/.test(text)) {
    return `"${text.replace(/"/g, '""')}"`;
  }
  return text;
}

function exportRowsForRecord(record) {
  const base = {
    section: record.section || "",
    category: record.category || "",
    brand: record.brand || "",
    productName: record.productName || "",
    finishOptions: recordColors(record).join(", "),
    description: record.description || "",
    notes: record.notes || "",
  };

  if (Array.isArray(record.variants) && record.variants.length) {
    return record.variants.map((variant) => ({
      ...base,
      sku: variant.sku || record.sku || "",
      variant: variant.label === "Default" ? "" : variant.label || "",
      list: variant.list || "",
      map: variant.map || "",
      net: variant.net || "",
      netBulk4: variant.netBulk4 || "",
      netBulk5: variant.netBulk5 || "",
      netBulk6: variant.netBulk6 || "",
      netBulk10: variant.netBulk10 || "",
      netBulk12: variant.netBulk12 || "",
      netBulk20: variant.netBulk20 || "",
      netBulk24: variant.netBulk24 || "",
      netBulk36: variant.netBulk36 || "",
      imageUrl: variant.imageUrl || "",
    }));
  }

  return [{
    ...base,
    sku: record.sku || "",
    variant: "",
    list: record.list || "",
    map: record.map || "",
    net: record.net || "",
    netBulk4: record.netBulk4 || "",
    netBulk5: record.netBulk5 || "",
    netBulk6: record.netBulk6 || "",
    netBulk10: record.netBulk10 || "",
    netBulk12: record.netBulk12 || "",
    netBulk20: record.netBulk20 || "",
    netBulk24: record.netBulk24 || "",
    netBulk36: record.netBulk36 || "",
    imageUrl: record.finishes?.[0]?.imageUrl || "",
  }];
}

function imageAssetsForRecord(record) {
  const assets = [];

  if (Array.isArray(record.variants) && record.variants.length) {
    record.variants.forEach((variant) => {
      if (!variant.imageUrl) return;
      assets.push({
        fileName: variant.imageFile || variant.imageUrl.split("/").pop() || `${variant.sku || record.sku}.png`,
        imageUrl: variant.imageUrl,
        sourceImageUrl: variant.sourceImageUrl || "",
      });
    });
  }

  if (Array.isArray(record.finishes) && record.finishes.length) {
    record.finishes.forEach((finish) => {
      if (!finish.imageUrl) return;
      assets.push({
        fileName: finish.imageFile || finish.imageUrl.split("/").pop() || `${record.sku}.png`,
        imageUrl: finish.imageUrl,
        sourceImageUrl: finish.sourceImageUrl || "",
      });
    });
  }

  return assets;
}

async function writeFileToDirectory(directoryHandle, fileName, contents, type = "text/plain") {
  const fileHandle = await directoryHandle.getFileHandle(fileName, { create: true });
  const writable = await fileHandle.createWritable();
  if (contents instanceof Blob) {
    await writable.write(contents);
  } else {
    await writable.write(new Blob([contents], { type }));
  }
  await writable.close();
}

async function fetchImageBlob(asset) {
  const fetchFromLocalApi = async () => {
    if (!/^https?:$/i.test(window.location.protocol)) {
      throw new Error("Local export API unavailable outside http(s)");
    }
    const sourcePath = asset?.sourceImageUrl || "";
    if (!sourcePath) {
      throw new Error("No source image path available for local export API");
    }
    const response = await fetch(`/api/source-image?path=${encodeURIComponent(sourcePath)}`);
    if (!response.ok) {
      throw new Error(`Local export API failed for ${sourcePath}`);
    }
    return response.blob();
  };

  const tryFetch = async (url) => {
    const response = await fetch(url);
    if (!response.ok) {
      throw new Error(`Unable to fetch ${url}`);
    }
    return response.blob();
  };

  const loadImageBlob = (src) => new Promise((resolve, reject) => {
    const img = new Image();
    img.onload = () => {
      const canvas = document.createElement("canvas");
      canvas.width = img.naturalWidth || img.width;
      canvas.height = img.naturalHeight || img.height;
      const ctx = canvas.getContext("2d");
      if (!ctx) {
        reject(new Error(`Unable to create drawing context for ${src}`));
        return;
      }
      ctx.drawImage(img, 0, 0);

      const extension = (src.split(".").pop() || "").toLowerCase();
      const mimeType = extension === "jpg" || extension === "jpeg"
        ? "image/jpeg"
        : extension === "webp"
          ? "image/webp"
          : "image/png";

      canvas.toBlob((blob) => {
        if (!blob) {
          reject(new Error(`Unable to create blob for ${src}`));
          return;
        }
        resolve(blob);
      }, mimeType);
    };
    img.onerror = () => reject(new Error(`Unable to load ${src}`));
    img.src = src;
  });

  const candidates = Array.from(new Set([
    asset?.imageUrl || "",
    asset?.sourceImageUrl || "",
    absoluteFileUrl(asset?.sourceImageUrl || ""),
  ].filter(Boolean)));

  let lastError = null;
  try {
    return await fetchFromLocalApi();
  } catch (apiError) {
    lastError = apiError;
  }
  for (const candidate of candidates) {
    try {
      return await tryFetch(candidate);
    } catch (fetchError) {
      lastError = fetchError;
    }
    try {
      return await loadImageBlob(candidate);
    } catch (imageError) {
      lastError = imageError;
    }
  }

  throw lastError || new Error("Unable to export image asset");
}

async function exportSelectedProductsCsv() {
  const exportRows = selectedRecords().flatMap((record) => exportRowsForRecord(record));
  if (!exportRows.length) return;

  const columns = [
    ["section", "Section"],
    ["category", "Category"],
    ["brand", "Brand"],
    ["productName", "Product Name"],
    ["sku", "SKU"],
    ["variant", "Variant"],
    ["finishOptions", "Finish Options"],
    ["list", "List"],
    ["map", "Map"],
    ["net", "Net"],
    ["netBulk4", "Net 4+"],
    ["netBulk5", "Net 5+"],
    ["netBulk6", "Net 6+"],
    ["netBulk10", "Net 10+"],
    ["netBulk12", "Net 12+"],
    ["netBulk20", "Net 20+"],
    ["netBulk24", "Net 24+"],
    ["netBulk36", "Net 36+"],
    ["description", "Description"],
    ["notes", "Notes"],
    ["imageUrl", "Image URL"],
  ];

  const lines = [
    columns.map(([, label]) => csvEscape(label)).join(","),
    ...exportRows.map((row) => columns.map(([key]) => csvEscape(row[key])).join(",")),
  ];

  const stamp = new Date().toISOString().slice(0, 10);
  const csvText = lines.join("\n");
  const assets = selectedRecords()
    .flatMap((record) => imageAssetsForRecord(record))
    .filter((asset) => asset.imageUrl || asset.sourceImageUrl);
  const dedupedAssets = Array.from(new Map(assets.map((asset) => [`${asset.fileName}::${asset.sourceImageUrl || asset.imageUrl}`, asset])).values());

  if (/^https?:$/i.test(window.location.protocol)) {
    try {
      const response = await fetch("/api/export-dealer-list", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          stamp,
          csvText,
          fileName: `dealer-list-${stamp}.csv`,
          assets: dedupedAssets.map((asset) => ({
            fileName: asset.fileName,
            imageUrl: asset.imageUrl || "",
            sourceImageUrl: asset.sourceImageUrl || "",
          })),
        }),
      });
      if (!response.ok) {
        throw new Error("Zip export failed");
      }
      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = `LPD-Dealer-List-${stamp}.zip`;
      document.body.appendChild(link);
      link.click();
      link.remove();
      URL.revokeObjectURL(url);
      return;
    } catch (error) {
      console.warn("Zip export unavailable, falling back to direct download", error);
    }
  }

  const blob = new Blob([csvText], { type: "text/csv;charset=utf-8;" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = `lpd-dealer-selection-${stamp}.csv`;
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
}

function toggleFilterValue(group, value) {
  const bucket = activeFilters[group];
  if (!bucket) return;
  if (bucket.has(value)) {
    bucket.delete(value);
  } else {
    bucket.add(value);
  }
}

function colorOptionMarkup(option, count, isSelected) {
  const dotColor = option.value;
  const isLight = ["#f1ede1", "#d6d7dc"].includes(dotColor);
  const label = `${option.label} ${optionCountLabel(count)}`;
  return `
    <button
      class="catalog-filter-color-option ${isSelected ? "is-selected" : ""} ${isLight ? "is-light" : ""}"
      type="button"
      data-filter-option
      data-group="colors"
      data-value="${dotColor}"
      aria-pressed="${isSelected ? "true" : "false"}"
      aria-label="${label}"
      title="${label}"
      style="--filter-color: ${dotColor};"
    >
      <span class="catalog-filter-color-swatch"></span>
    </button>
  `;
}

function fallbackMarkup(record) {
  const initials = String(record.sku || record.productName || "SKU")
    .replace(/[^a-z0-9]+/gi, " ")
    .trim()
    .split(/\s+/)
    .slice(0, 2)
    .map((part) => part[0])
    .join("")
    .toUpperCase();

  return `<div class="image-fallback" aria-hidden="true">${initials || "SKU"}</div>`;
}

function orderedCategoryGroups(items) {
  const groups = new Map();
  items.forEach((item) => {
    const key = item.category || "Uncategorized";
    if (!groups.has(key)) groups.set(key, []);
    groups.get(key).push(item);
  });
  return Array.from(groups.entries());
}

function sortRecords(items) {
  const sorted = [...items];
  if (activeSort === "price-low") {
    sorted.sort((a, b) => sortValue(a) - sortValue(b) || a.productName.localeCompare(b.productName));
    return sorted;
  }
  if (activeSort === "price-high") {
    sorted.sort((a, b) => sortValue(b) - sortValue(a) || a.productName.localeCompare(b.productName));
    return sorted;
  }
  if (activeSort === "name-az") {
    sorted.sort((a, b) => a.productName.localeCompare(b.productName));
    return sorted;
  }
  if (activeSort === "name-za") {
    sorted.sort((a, b) => b.productName.localeCompare(a.productName));
    return sorted;
  }
  return sorted;
}

function finishDotColor(finishName) {
  const finish = String(finishName || "").toLowerCase();
  if (!finish || finish === "default") return "#d6d7dc";
  if (finish.includes("black")) return "#2a2a2d";
  if (finish.includes("white") || finish.includes("cream")) return "#f1ede1";
  if (finish.includes("red")) return "#b3312d";
  if (finish.includes("burgundy") || finish.includes("maroon")) return "#6f2a38";
  if (finish.includes("orange")) return "#e68933";
  if (finish.includes("yellow") || finish.includes("gold")) return "#d9a93f";
  if (finish.includes("green") || finish.includes("jade")) return "#5b8561";
  if (finish.includes("seafoam") || finish.includes("aqua")) return "#8fcfca";
  if (finish.includes("blue")) return "#4a6ea8";
  if (finish.includes("purple")) return "#64518f";
  if (finish.includes("grey") || finish.includes("gray") || finish.includes("silver")) return "#a6abb4";
  if (finish.includes("copper") || finish.includes("burst") || finish.includes("sunburst")) return "#9a5d36";
  if (finish.includes("walnut")) return "#5d4333";
  if (finish.includes("flake") || finish.includes("crackle")) return "#76707f";
  return "#b9a18d";
}

function supportPriceRows(selection) {
  return [
    selection.netBulk4 ? `<div class="price-row"><span>Net 4+</span><span class="price-value">${money(selection.netBulk4)}</span></div>` : "",
    selection.netBulk5 ? `<div class="price-row"><span>Net 5+</span><span class="price-value">${money(selection.netBulk5)}</span></div>` : "",
    selection.netBulk6 ? `<div class="price-row"><span>Net 6+</span><span class="price-value">${money(selection.netBulk6)}</span></div>` : "",
    selection.netBulk10 ? `<div class="price-row"><span>Net 10+</span><span class="price-value">${money(selection.netBulk10)}</span></div>` : "",
    selection.netBulk12 ? `<div class="price-row"><span>Net 12+</span><span class="price-value">${money(selection.netBulk12)}</span></div>` : "",
    selection.netBulk20 ? `<div class="price-row"><span>Net 20+</span><span class="price-value">${money(selection.netBulk20)}</span></div>` : "",
    selection.netBulk24 ? `<div class="price-row"><span>Net 24+</span><span class="price-value">${money(selection.netBulk24)}</span></div>` : "",
    selection.netBulk36 ? `<div class="price-row"><span>Net 36+</span><span class="price-value">${money(selection.netBulk36)}</span></div>` : "",
  ].join("");
}

function priceTableMarkup(selection) {
  const netPrice = money(selection.net);
  const mapPrice = money(selection.map);
  const listPrice = money(selection.list);
  return [
    `<div class="price-row price-row-primary"><span>Net</span><span class="price-value">${netPrice}</span></div>`,
    mapPrice !== "N/A" ? `<div class="price-row"><span>Map</span><span class="price-value">${mapPrice}</span></div>` : "",
    listPrice !== "N/A" ? `<div class="price-row"><span>List</span><span class="price-value">${listPrice}</span></div>` : "",
    supportPriceRows(selection),
  ].join("");
}

function productCard(record) {
  const finishes = Array.isArray(record.finishes) ? record.finishes : [];
  const variants = Array.isArray(record.variants) ? record.variants : [];
  const selectedVariant = variants[0];
  const selectedFinish = finishes[0];
  const selectedImage = selectedVariant?.imageUrl || selectedFinish?.imageUrl;
  const selectedAlt = selectedVariant
    ? `${record.productName} ${selectedVariant.label || selectedVariant.sku || ""}`.trim()
    : `${record.productName} ${selectedFinish?.finish || ""}`.trim();
  const gallery = selectedImage
    ? `
        <div class="product-image">
          <img
            class="product-main-image"
            src="${selectedImage}"
            alt="${selectedAlt}"
            loading="lazy"
            decoding="async"
          />
        </div>
      `
    : `<div class="product-image is-missing">${fallbackMarkup(record)}</div>`;

  const selectorBar = finishes.length > 0
    ? `
        <div class="selector-bar" aria-label="Finish selector">
          <div class="selector-dots-row">
            ${finishes.map((finish, index) => {
              const dotColor = finishDotColor(finish.finish);
              const isLight = ["#f1ede1", "#d6d7dc"].includes(dotColor);
              return `
                <button
                  class="selector-dot ${index === 0 ? "is-active" : ""} ${isLight ? "is-light" : ""}"
                  type="button"
                  aria-label="${titleCase(finish.finish)}"
                  title="${titleCase(finish.finish)}"
                  data-image="${finish.imageUrl}"
                  data-alt="${titleCase(record.productName)} ${titleCase(finish.finish)}"
                data-finish="${titleCase(finish.finish)}"
                style="--dot-color: ${dotColor};"
                ${finishes.length === 1 ? "disabled" : ""}
              ></button>
            `;
          }).join("")}
          </div>
        </div>
      `
    : "";

  const priceRows = priceTableMarkup(selectedVariant || record);
  const currentSku = selectedVariant?.sku || record.sku;
  const selected = isRecordSelected(record);
  const selectionIndicator = dealerSelectionMode
    ? `
        <div class="product-selection-indicator ${selected ? "is-selected" : ""}" aria-hidden="true">
          <img
            class="product-selection-indicator-icon"
            src="${selected ? checkboxIcons.active : checkboxIcons.inactive}"
            alt=""
          />
        </div>
      `
    : "";

  return `
    <article
      class="product-card ${dealerSelectionMode ? "is-selection-mode" : ""} ${selected ? "is-selected" : ""}"
      data-record-key="${recordSelectionToken(record)}"
      data-detail-url="./product.html?sku=${encodeURIComponent(currentSku)}"
      tabindex="0"
      role="${dealerSelectionMode ? "button" : "link"}"
      aria-label="${dealerSelectionMode ? `${selected ? "Deselect" : "Select"} ${record.productName}` : `View ${record.productName}`}"
    >
      ${selectionIndicator}
      <div class="product-gallery">${gallery}</div>
      <div class="product-body">
        ${selectorBar}
        <h3 class="product-name">${record.productName}</h3>
        <div class="product-meta">${titleCase(record.brand)} · ${titleCase(record.category)}</div>
        <div class="product-meta product-sku" data-sku-label>SKU ${currentSku}</div>
        <div class="price-table" data-price-table>${priceRows}</div>
      </div>
    </article>
  `;
}

function recordImageCount(record) {
  const finishes = Array.isArray(record.finishes) ? record.finishes : [];
  if (finishes.length) return finishes.length;
  const variants = Array.isArray(record.variants) ? record.variants : [];
  return new Set(variants.map((variant) => variant.imageUrl).filter(Boolean)).size;
}

function categoryBlock(category, items) {
  const categoryClass = categoryClassMap[category] || "";
  const totalImages = items.reduce((sum, item) => sum + recordImageCount(item), 0);
  return `
    <section class="category-block ${categoryClass}" id="${slug(category)}">
      <div class="category-header">
        <h3 class="category-name">${titleCase(category)}</h3>
        <div class="category-count">${items.length} products · ${totalImages} catalog images</div>
      </div>
      <div class="product-grid">
        ${items.map(productCard).join("")}
      </div>
    </section>
  `;
}

function renderTopCategories() {
  const root = document.getElementById("category-app-grid");
  if (!root) return;
  const availableSections = new Set(records.map((record) => record.section));

  root.innerHTML = topCategories
    .map((category) => `
      <button
        class="category-app ${activeSection === category.name ? "is-active" : ""}"
        type="button"
        data-section="${category.name}"
        ${availableSections.has(category.name) ? "" : "disabled"}
      >
        <div class="category-app-image-wrap">
          <img class="category-app-image" src="${category.image}" alt="${category.name}" />
        </div>
        <div class="category-app-copy">
          <h3>${titleCase(category.name)}</h3>
          <p>${availableSections.has(category.name) ? "Live now" : "Coming soon"}</p>
        </div>
      </button>
    `)
    .join("");
}

function baseRecordsForSection() {
  return records.filter((record) => {
    const matchesSection = !activeSection || record.section === activeSection;
    const matchesQuery = !searchQuery || searchableText(record).includes(searchQuery);
    return matchesSection && matchesQuery;
  });
}

function recordMatchesFilterGroup(record, groupKey, selectedValues) {
  if (!selectedValues || selectedValues.size === 0) return true;

  if (groupKey === "productType") {
    return selectedValues.has(record.category || "Uncategorized");
  }

  if (groupKey === "brand") {
    return selectedValues.has(record.brand || "");
  }

  if (groupKey === "netPrice") {
    const values = recordNetValues(record);
    return Array.from(selectedValues).some((bucketKey) => {
      const bucket = netPriceBuckets.find((item) => item.key === bucketKey);
      return bucket && values.some((value) => value >= bucket.min && value < bucket.max);
    });
  }

  if (groupKey === "bulkDeals") {
    const available = new Set(recordBulkDealKeys(record));
    return Array.from(selectedValues).some((value) => available.has(value));
  }

  if (groupKey === "colors") {
    const colorGroups = recordColorGroups(record);
    return Array.from(selectedValues).some((value) => colorGroups.has(value));
  }

  return true;
}

function recordMatchesActiveFilters(record, ignoredGroup = null) {
  return Object.entries(activeFilters).every(([groupKey, selectedValues]) => {
    if (groupKey === ignoredGroup) return true;
    return recordMatchesFilterGroup(record, groupKey, selectedValues);
  });
}

function buildFilterGroups(baseRecords) {
  const groups = [];

  const productTypeOptions = uniqueValues(baseRecords.map((record) => record.category || "Uncategorized"))
    .sort((a, b) => a.localeCompare(b))
    .map((value) => ({ value, label: titleCase(value) }));
  if (productTypeOptions.length) {
    groups.push({ key: "productType", label: "Product Type", options: productTypeOptions });
  }

  const brandOptions = uniqueValues(baseRecords.map((record) => record.brand || ""))
    .sort((a, b) => a.localeCompare(b))
    .map((value) => ({ value, label: titleCase(value) }));
  if (brandOptions.length) {
    groups.push({ key: "brand", label: "Brand", options: brandOptions });
  }

  const priceOptions = netPriceBuckets
    .filter((bucket) => baseRecords.some((record) => recordNetValues(record).some((value) => value >= bucket.min && value < bucket.max)))
    .map((bucket) => ({ value: bucket.key, label: bucket.label }));
  if (priceOptions.length) {
    groups.push({ key: "netPrice", label: "Net Price", options: priceOptions });
  }

  const bulkOptions = bulkDealOptions
    .filter((option) => baseRecords.some((record) => recordBulkDealKeys(record).includes(option.key)))
    .map((option) => ({ value: option.key, label: option.label }));
  if (bulkOptions.length) {
    groups.push({ key: "bulkDeals", label: "Bulk Deals", options: bulkOptions });
  }

  const colorOptions = Array.from(
    baseRecords.reduce((map, record) => {
      recordColors(record).forEach((colorName) => {
        const swatch = finishDotColor(colorName);
        if (!map.has(swatch)) map.set(swatch, new Set());
        map.get(swatch).add(colorName);
      });
      return map;
    }, new Map()).entries()
  )
    .map(([value, names]) => ({
      value,
      label: Array.from(names).sort((a, b) => a.localeCompare(b)).join(", "),
    }))
    .sort((a, b) => a.label.localeCompare(b.label));
  if (colorOptions.length) {
    groups.push({ key: "colors", label: "Colors", options: colorOptions });
  }

  return groups;
}

function sanitizeActiveFilters(groups) {
  const availableByGroup = new Map(groups.map((group) => [group.key, new Set(group.options.map((option) => option.value))]));
  Object.entries(activeFilters).forEach(([groupKey, selectedValues]) => {
    const available = availableByGroup.get(groupKey);
    if (!available) {
      selectedValues.clear();
      return;
    }
    Array.from(selectedValues).forEach((value) => {
      if (!available.has(value)) {
        selectedValues.delete(value);
      }
    });
  });
}

function filterPanelMarkup(baseRecords, groups) {
  if (!groups.length) {
    return `<div class="catalog-filters-empty">No filters available for this section.</div>`;
  }

  return groups
    .map((group, groupIndex) => {
      const defaultExpandedKey = filterGroupsDefaultKey(groups);
      const isExpanded = expandedFilterGroup
        ? expandedFilterGroup === group.key
        : filtersOpen && defaultExpandedKey === group.key;
      const scopedRecords = baseRecords.filter((record) => recordMatchesActiveFilters(record, group.key));
      const optionMarkup = group.options
        .map((option) => {
          const count = scopedRecords.filter((record) => recordMatchesFilterGroup(record, group.key, new Set([option.value]))).length;
          if (count === 0 && !activeFilters[group.key].has(option.value)) return null;
          const isSelected = activeFilters[group.key].has(option.value);
          if (group.key === "colors") {
            return colorOptionMarkup(option, count, isSelected);
          }
          return `
            <button
              class="catalog-filter-option ${isSelected ? "is-selected" : ""}"
              type="button"
              data-filter-option
              data-group="${group.key}"
              data-value="${option.value}"
              aria-pressed="${isSelected ? "true" : "false"}"
            >
              <img
                class="catalog-filter-option-icon"
                src="${isSelected ? checkboxIcons.active : checkboxIcons.inactive}"
                alt=""
                aria-hidden="true"
              />
              <span class="catalog-filter-option-label">${option.label}</span>
              <span class="catalog-filter-option-count">${optionCountLabel(count)}</span>
            </button>
          `;
        })
        .filter(Boolean)
        .join("");

      if (!optionMarkup) return "";

      const optionsClass = group.key === "colors" ? "catalog-filter-options catalog-filter-options-colors" : "catalog-filter-options";

      return `
        <section class="catalog-filter-group ${isExpanded ? "is-expanded" : ""}">
          <button class="catalog-filter-group-toggle" type="button" data-filter-group-toggle data-group="${group.key}">
            <span class="catalog-filter-group-label">${group.label}</span>
            <span class="catalog-filter-group-chevron">${isExpanded ? "⌃" : "⌄"}</span>
          </button>
          ${isExpanded ? `<div class="${optionsClass}">${optionMarkup}</div>` : ""}
        </section>
      `;
    })
    .filter(Boolean)
    .join("");
}

function filterGroupsDefaultKey(groups) {
  return groups[0]?.key || "";
}

function renderUtilityBar(records, groups) {
  const count = document.getElementById("catalog-results-count");
  if (count) {
    count.textContent = String(records.length);
  }

  const filterButtonLabel = document.getElementById("catalog-filter-button-label");
  if (filterButtonLabel) {
    filterButtonLabel.textContent = filtersOpen ? "Hide Filters" : "Filter";
  }

  const panel = document.getElementById("catalog-filters-panel");
  if (panel) {
    panel.classList.toggle("is-hidden", !filtersOpen);
    panel.innerHTML = filtersOpen ? filterPanelMarkup(baseRecordsForSection(), groups) : "";
  }

  const sortButton = document.querySelector("[data-toolbar-sort]");
  const sortPanel = document.getElementById("catalog-sort-panel");
  if (sortButton) {
    sortButton.setAttribute("aria-expanded", sortOpen ? "true" : "false");
    sortButton.classList.toggle("is-open", sortOpen);
  }
  if (sortPanel) {
    sortPanel.classList.toggle("is-hidden", !sortOpen);
    sortPanel.innerHTML = sortOpen
      ? sortOptions.map((option) => `
          <button
            class="catalog-sort-option ${activeSort === option.key ? "is-active" : ""}"
            type="button"
            data-sort-option="${option.key}"
          >${option.label}</button>
        `).join("")
      : "";
  }

  document.querySelectorAll("[data-view-mode]").forEach((button) => {
    button.classList.toggle("is-active", button.dataset.viewMode === activeViewMode);
  });

  const selectionModeLabel = document.getElementById("catalog-selection-mode-label");
  if (selectionModeLabel) {
    selectionModeLabel.textContent = dealerSelectionMode ? "Done Building List" : "Build Dealer List";
  }

  const dealerListBar = document.getElementById("dealer-list-bar");
  if (dealerListBar) {
    dealerListBar.classList.toggle("is-hidden", !dealerSelectionMode);
  }

  const exportLabel = document.getElementById("dealer-list-export-label");
  if (exportLabel) {
    exportLabel.textContent = `Export ${exportSkuCount()} SKUs`;
  }

  document.querySelectorAll("[data-selection-export]").forEach((button) => {
    button.disabled = selectedRecordKeys.size === 0;
  });

  document.querySelectorAll("[data-selection-clear]").forEach((button) => {
    button.disabled = selectedRecordKeys.size === 0;
  });
}

function renderCatalog(records) {
  const root = document.getElementById("catalog-root");
  root.className = `catalog-root view-${activeViewMode}`;
  root.innerHTML = orderedCategoryGroups(records)
    .map(([category, items]) => categoryBlock(category, items))
    .join("");
}

function wireProductSelectors() {
  document.querySelectorAll(".product-card").forEach((card) => {
    const image = card.querySelector(".product-main-image");
    const buttons = card.querySelectorAll(".selector-dot");

    if (image && buttons.length) {
      buttons.forEach((button) => {
        button.addEventListener("click", () => {
          buttons.forEach((item) => item.classList.remove("is-active"));
          button.classList.add("is-active");
          image.src = button.dataset.image || image.src;
          image.alt = button.dataset.alt || image.alt;
        });
      });
    }
  });
}

function wireProductLinks() {
  document.querySelectorAll(".product-card[data-detail-url]").forEach((card) => {
    if (!card.dataset.detailUrl) return;

    card.addEventListener("click", (event) => {
      if (event.target.closest(".selector-dot, .variant-button")) return;
      if (dealerSelectionMode) {
        const key = decodeURIComponent(card.dataset.recordKey || "");
        const record = records.find((item) => recordSelectionKey(item) === key);
        if (!record) return;
        toggleRecordSelection(record);
        renderAll();
        return;
      }
      if (card.dataset.detailUrl) {
        window.location.href = card.dataset.detailUrl;
      }
    });

    card.addEventListener("keydown", (event) => {
      if (event.key !== "Enter" && event.key !== " ") return;
      if (event.target.closest(".selector-dot, .variant-button")) return;
      event.preventDefault();
      if (dealerSelectionMode) {
        const key = decodeURIComponent(card.dataset.recordKey || "");
        const record = records.find((item) => recordSelectionKey(item) === key);
        if (!record) return;
        toggleRecordSelection(record);
        renderAll();
        return;
      }
      if (card.dataset.detailUrl) {
        window.location.href = card.dataset.detailUrl;
      }
    });
  });
}

function filterRecords() {
  return baseRecordsForSection().filter((record) => recordMatchesActiveFilters(record));
}

function renderAll() {
  const baseRecords = baseRecordsForSection();
  const filterGroups = buildFilterGroups(baseRecords);
  sanitizeActiveFilters(filterGroups);
  if (expandedFilterGroup && !filterGroups.some((group) => group.key === expandedFilterGroup)) {
    expandedFilterGroup = "";
  }
  const filteredRecords = baseRecords.filter((record) => recordMatchesActiveFilters(record));
  const sortedRecords = sortRecords(filteredRecords);
  renderTopCategories();
  renderUtilityBar(sortedRecords, filterGroups);
  renderCatalog(sortedRecords);
  wireProductSelectors();
  wireProductLinks();
  wireTopCategories();
  wireUtilityBar(filterGroups);
}

function wireTopCategories() {
  document.querySelectorAll(".category-app[data-section]").forEach((button) => {
    button.addEventListener("click", () => {
      const nextSection = button.dataset.section || "";
      if (!nextSection) return;
      activeSection = nextSection === activeSection ? "" : nextSection;
      if (filtersOpen) {
        expandedFilterGroup = "";
      }
      renderAll();
      const root = document.getElementById("catalog-root");
      if (root) {
        root.scrollIntoView({ behavior: "smooth", block: "start" });
      }
    });
  });
}

function wireUtilityBar(filterGroups) {
  const filterButton = document.querySelector("[data-toolbar-filter]");
  if (filterButton) {
    filterButton.onclick = () => {
      filtersOpen = !filtersOpen;
      sortOpen = false;
      if (filtersOpen && !expandedFilterGroup && filterGroups[0]) {
        expandedFilterGroup = filterGroups[0].key;
      }
      renderAll();
    };
  }

  const sortButton = document.querySelector("[data-toolbar-sort]");
  if (sortButton) {
    sortButton.onclick = () => {
      sortOpen = !sortOpen;
      if (sortOpen) filtersOpen = false;
      renderAll();
    };
  }

  document.querySelectorAll("[data-view-mode]").forEach((button) => {
    button.onclick = () => {
      const nextMode = button.dataset.viewMode || "grid-default";
      if (nextMode === activeViewMode) return;
      activeViewMode = nextMode;
      renderAll();
    };
  });

  document.querySelectorAll("[data-filter-group-toggle]").forEach((button) => {
    button.onclick = () => {
      const group = button.dataset.group || "";
      if (!group) return;
      expandedFilterGroup = expandedFilterGroup === group ? "" : group;
      renderAll();
    };
  });

  document.querySelectorAll("[data-filter-option]").forEach((button) => {
    button.onclick = () => {
      const group = button.dataset.group || "";
      const value = button.dataset.value || "";
      if (!group || !value) return;
      toggleFilterValue(group, value);
      renderAll();
    };
  });

  document.querySelectorAll("[data-sort-option]").forEach((button) => {
    button.onclick = () => {
      const nextSort = button.dataset.sortOption || "best-match";
      activeSort = nextSort;
      sortOpen = false;
      renderAll();
    };
  });

  const selectionModeButton = document.querySelector("[data-selection-mode]");
  if (selectionModeButton) {
    selectionModeButton.onclick = () => {
      dealerSelectionMode = !dealerSelectionMode;
      renderAll();
    };
  }

  const clearButton = document.querySelector("[data-selection-clear]");
  if (clearButton) {
    clearButton.onclick = () => {
      selectedRecordKeys.clear();
      renderAll();
    };
  }

  const exportButton = document.querySelector("[data-selection-export]");
  if (exportButton) {
    exportButton.onclick = () => {
      exportSelectedProductsCsv();
    };
  }

}

function wireGlobalDismissals() {
  if (globalDismissalsWired) return;
  globalDismissalsWired = true;

  document.addEventListener("click", (event) => {
    const target = event.target;
    if (!(target instanceof Element)) return;
    if (sortOpen && !target.closest(".catalog-sort-shell")) {
      sortOpen = false;
      renderAll();
    }
  });
}

function wireSearch() {
  const input = document.getElementById("catalog-search");
  if (!input) return;

  input.addEventListener("input", () => {
    searchQuery = input.value.trim().toLowerCase();
    renderAll();
  });
}

renderAll();
wireSearch();
wireGlobalDismissals();
