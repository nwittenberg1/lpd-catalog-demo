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

function normalizeVariant(variant) {
  return {
    ...variant,
    imageUrl: portableImageUrl(variant?.imageUrl || ""),
  };
}

function normalizeFinish(finish) {
  return {
    ...finish,
    imageUrl: portableImageUrl(finish?.imageUrl || ""),
  };
}

function normalizeProduct(product) {
  return {
    ...product,
    variants: Array.isArray(product?.variants) ? product.variants.map(normalizeVariant) : [],
    finishes: Array.isArray(product?.finishes) ? product.finishes.map(normalizeFinish) : [],
  };
}

const allProducts = Array.isArray(window.CATALOG_PRODUCTS) ? window.CATALOG_PRODUCTS.map(normalizeProduct) : [];

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

function fallbackMarkup(product) {
  const initials = String(product.sku || product.productName || "SKU")
    .replace(/[^a-z0-9]+/gi, " ")
    .trim()
    .split(/\s+/)
    .slice(0, 2)
    .map((part) => part[0])
    .join("")
    .toUpperCase();

  return `<div class="image-fallback" aria-hidden="true">${initials || "SKU"}</div>`;
}

function detailSupportText(selection) {
  return [
    money(selection.map) !== "N/A" ? `Map ${money(selection.map)}` : "",
    money(selection.list) !== "N/A" ? `List ${money(selection.list)}` : "",
    selection.netBulk4 ? `Net 4+ ${money(selection.netBulk4)}` : "",
    selection.netBulk5 ? `Net 5+ ${money(selection.netBulk5)}` : "",
    selection.netBulk6 ? `Net 6+ ${money(selection.netBulk6)}` : "",
    selection.netBulk10 ? `Net 10+ ${money(selection.netBulk10)}` : "",
    selection.netBulk12 ? `Net 12+ ${money(selection.netBulk12)}` : "",
    selection.netBulk20 ? `Net 20+ ${money(selection.netBulk20)}` : "",
    selection.netBulk24 ? `Net 24+ ${money(selection.netBulk24)}` : "",
    selection.netBulk36 ? `Net 36+ ${money(selection.netBulk36)}` : "",
  ].filter(Boolean).join(" · ");
}

function getSkuFromQuery() {
  const params = new URLSearchParams(window.location.search);
  return (params.get("sku") || "").toUpperCase();
}

function specRows(product, selectedVariant = null) {
  const active = selectedVariant || product;
  return [
    ["Brand", titleCase(product.brand) || "N/A"],
    ["SKU", active.sku || product.sku || "N/A"],
    ["Section", titleCase(product.section) || "N/A"],
    ["Category", titleCase(product.category) || "N/A"],
    ["MAP", money(active.map)],
    ["List", money(active.list)],
    ["Net", money(active.net)],
    active.netBulk4 ? ["Net 4+", money(active.netBulk4)] : null,
    active.netBulk5 ? ["Net 5+", money(active.netBulk5)] : null,
    active.netBulk6 ? ["Net 6+", money(active.netBulk6)] : null,
    active.netBulk10 ? ["Net 10+", money(active.netBulk10)] : null,
    active.netBulk12 ? ["Net 12+", money(active.netBulk12)] : null,
    active.netBulk20 ? ["Net 20+", money(active.netBulk20)] : null,
    active.netBulk24 ? ["Net 24+", money(active.netBulk24)] : null,
    active.netBulk36 ? ["Net 36+", money(active.netBulk36)] : null,
    ["Finish Count", String((product.finishes || []).length)],
    product.variants?.length ? ["Variant Count", String((product.variants || []).length)] : null,
    selectedVariant?.label ? ["Variant", titleCase(selectedVariant.label)] : null,
    ["Image Match", product.matchType || "N/A"],
    product.description ? ["Description", product.description] : null,
    product.notes ? ["Notes", product.notes] : null,
  ].filter(Boolean);
}

function specGridMarkup(product, selectedVariant = null) {
  return specRows(product, selectedVariant).map(([label, value]) => `
    <article class="spec-card">
      <span class="spec-label">${label}</span>
      <strong class="spec-value">${value}</strong>
    </article>
  `).join("");
}

function renderNotFound(root) {
  root.innerHTML = `
    <section class="detail-empty">
      <p class="kicker">Product Not Found</p>
      <h1>We couldn’t find that guitar.</h1>
      <p class="lede">Go back to the catalog and pick a product card from the grid.</p>
      <a class="primary-action" href="./index.html">Back To Catalog</a>
    </section>
  `;
}

function renderProduct(root, product) {
  const finishes = product.finishes || [];
  const variants = product.variants || [];
  const selected = finishes[0];
  const selectedVariant = variants[0];
  const activeSelection = selectedVariant || product;
  const mainImage = selectedVariant?.imageUrl || selected?.imageUrl;
  const mainAlt = selectedVariant
    ? `${product.productName} ${selectedVariant.label || selectedVariant.sku || ""}`.trim()
    : `${product.productName} ${selected?.finish || ""}`.trim();
  const related = allProducts
    .filter((item) => item.category === product.category && item.sku !== product.sku)
    .slice(0, 4);
  const supportPrices = detailSupportText(activeSelection);

  root.innerHTML = `
    <a class="back-link" href="./index.html">Back to catalog</a>

    <section class="detail-hero">
      <div class="detail-gallery-card">
        <div class="detail-gallery-stage">
          ${mainImage
            ? `
              <img
                id="detail-main-image"
                class="detail-main-image"
                src="${mainImage}"
                alt="${mainAlt}"
              />
            `
            : fallbackMarkup(product)}
        </div>
        ${finishes.length ? `
        <div class="detail-thumbs">
          ${finishes.map((finish, index) => `
            <button
              class="detail-thumb ${index === 0 ? "is-active" : ""}"
              type="button"
              data-image="${finish.imageUrl}"
              data-alt="${product.productName} ${finish.finish}"
              data-finish="${finish.finish}"
            >
              <img src="${finish.imageUrl}" alt="" loading="lazy" decoding="async" />
            </button>
          `).join("")}
        </div>
        ` : ""}
      </div>

      <aside class="detail-info-card">
        <p class="kicker">${titleCase(product.category)}</p>
        <h1 class="detail-title">${product.productName}</h1>
        <p class="detail-subtitle">${titleCase(product.brand)} · ${titleCase(product.section)} · <span id="detail-sku-label">SKU ${activeSelection.sku || product.sku}</span></p>
        <div class="detail-price" id="detail-price-value">Net ${money(activeSelection.net)}</div>
        <div class="detail-price-support" id="detail-price-support">${supportPrices}</div>
        <p class="detail-copy">
          ${product.description || "This product page is driven from the current dealer catalog sheet and its matched product image set."}
        </p>
        ${variants.length ? `
        <div class="detail-selector">
          <div class="variant-button-row detail-variant-row">
            ${variants.map((variant, index) => `
              <button
                class="variant-button ${index === 0 ? "is-active" : ""}"
                type="button"
                data-detail-variant
                data-label="${titleCase(variant.label || "Default")}"
                data-sku="${variant.sku || ""}"
                data-image="${variant.imageUrl || ""}"
                data-alt="${`${product.productName} ${titleCase(variant.label || variant.sku || "Default")}`.trim()}"
                data-list="${variant.list || ""}"
                data-map="${variant.map || ""}"
                data-net="${variant.net || ""}"
                data-net-bulk4="${variant.netBulk4 || ""}"
                data-net-bulk5="${variant.netBulk5 || ""}"
                data-net-bulk6="${variant.netBulk6 || ""}"
                data-net-bulk10="${variant.netBulk10 || ""}"
                data-net-bulk12="${variant.netBulk12 || ""}"
                data-net-bulk20="${variant.netBulk20 || ""}"
                data-net-bulk24="${variant.netBulk24 || ""}"
                data-net-bulk36="${variant.netBulk36 || ""}"
              >${titleCase(variant.label || "Default")}</button>
            `).join("")}
          </div>
        </div>
        ` : `
        <div class="detail-selector">
          <div class="detail-dot-row">
            ${finishes.map((finish, index) => {
              const color = finishDotColor(finish.finish);
              const isLight = ["#f1ede1", "#d6d7dc"].includes(color);
              return `
                <button
                  class="selector-dot ${index === 0 ? "is-active" : ""} ${isLight ? "is-light" : ""}"
                  type="button"
                  aria-label="${titleCase(finish.finish)}"
                  title="${titleCase(finish.finish)}"
                  data-image="${finish.imageUrl}"
                  data-alt="${titleCase(product.productName)} ${titleCase(finish.finish)}"
                  data-finish="${titleCase(finish.finish)}"
                  style="--dot-color: ${color};"
                ></button>
              `;
            }).join("")}
          </div>
        </div>
        `}
        <div class="detail-buy-row">
          <a class="primary-action" href="./exports/products.csv">View Source Data</a>
          <a class="secondary-action" href="./exports/finishes.csv">View Finishes</a>
        </div>
      </aside>
    </section>

    <section class="detail-section">
      <div class="section-heading">
        <p class="kicker">Specs</p>
        <h2>Current catalog fields</h2>
      </div>
      <div class="spec-grid" id="detail-spec-grid">${specGridMarkup(product, selectedVariant)}</div>
    </section>

    ${variants.length ? `
    <section class="detail-section">
      <div class="section-heading">
        <p class="kicker">Variants</p>
        <h2>Available options in this family</h2>
      </div>
      <div class="variant-preview-grid">
        ${variants.map((variant, index) => `
          <article class="variant-preview ${index === 0 ? "is-active" : ""}" data-variant-card="${variant.sku}">
            <div class="variant-preview-copy">
              <span class="spec-label">Variant</span>
              <strong class="spec-value">${titleCase(variant.label || "Default")}</strong>
              <span class="variant-preview-sku">SKU ${variant.sku}</span>
              <span class="variant-preview-price">Net ${money(variant.net)}</span>
            </div>
          </article>
        `).join("")}
      </div>
    </section>
    ` : ""}

    ${finishes.length ? `
    <section class="detail-section">
      <div class="section-heading">
        <p class="kicker">Finishes</p>
        <h2>Available images for this product</h2>
      </div>
      <div class="finish-preview-grid">
        ${finishes.map((finish, index) => `
          <article class="finish-preview ${index === 0 ? "is-active" : ""}" data-finish-card="${titleCase(finish.finish)}">
            <div class="finish-preview-image">
              <img src="${finish.imageUrl}" alt="${product.productName} ${titleCase(finish.finish)}" loading="lazy" decoding="async" />
            </div>
            <div class="finish-preview-name">${titleCase(finish.finish)}</div>
          </article>
        `).join("")}
      </div>
    </section>
    ` : ""}

    <section class="detail-section">
      <div class="section-heading">
        <p class="kicker">More In Category</p>
        <h2>${titleCase(product.category)}</h2>
      </div>
      <div class="related-grid">
        ${related.map((item) => `
          <a class="related-card" href="./product.html?sku=${encodeURIComponent(item.sku)}">
            <div class="related-image">
              ${item.finishes?.[0]?.imageUrl
                ? `<img src="${item.finishes[0].imageUrl}" alt="${item.productName}" loading="lazy" decoding="async" />`
                : fallbackMarkup(item)}
            </div>
            <div class="related-body">
              <h3>${item.productName}</h3>
              <p>${money(item.map)}</p>
            </div>
          </a>
        `).join("")}
      </div>
    </section>
  `;
}

function wireDetailSelectors(product) {
  const image = document.getElementById("detail-main-image");
  const skuLabel = document.getElementById("detail-sku-label");
  const priceValue = document.getElementById("detail-price-value");
  const priceSupport = document.getElementById("detail-price-support");
  const specGrid = document.getElementById("detail-spec-grid");
  const buttons = document.querySelectorAll(".detail-dot-row .selector-dot, .detail-thumbs .detail-thumb");
  const dotButtons = document.querySelectorAll(".detail-dot-row .selector-dot");
  const thumbButtons = document.querySelectorAll(".detail-thumbs .detail-thumb");
  const previewCards = document.querySelectorAll("[data-finish-card]");
  const variantButtons = document.querySelectorAll("[data-detail-variant]");
  const variantCards = document.querySelectorAll("[data-variant-card]");

  buttons.forEach((button) => {
    button.addEventListener("click", () => {
      const nextImage = button.dataset.image;
      const nextAlt = button.dataset.alt;
      const nextFinish = button.dataset.finish;
      if (image && nextImage) image.src = nextImage;
      if (image && nextAlt) image.alt = nextAlt;

      dotButtons.forEach((item) => item.classList.toggle("is-active", item.dataset.finish === nextFinish));
      thumbButtons.forEach((item) => item.classList.toggle("is-active", item.dataset.finish === nextFinish));
      previewCards.forEach((item) => item.classList.toggle("is-active", item.dataset.finishCard === nextFinish));
    });
  });

  variantButtons.forEach((button) => {
    button.addEventListener("click", () => {
      const selectedVariant = {
        label: button.dataset.label || "",
        sku: button.dataset.sku || "",
        imageUrl: button.dataset.image || "",
        list: button.dataset.list || "",
        map: button.dataset.map || "",
        net: button.dataset.net || "",
        netBulk4: button.dataset.netBulk4 || "",
        netBulk5: button.dataset.netBulk5 || "",
        netBulk6: button.dataset.netBulk6 || "",
        netBulk10: button.dataset.netBulk10 || "",
        netBulk12: button.dataset.netBulk12 || "",
        netBulk20: button.dataset.netBulk20 || "",
        netBulk24: button.dataset.netBulk24 || "",
        netBulk36: button.dataset.netBulk36 || "",
      };
      if (image && selectedVariant.imageUrl) image.src = selectedVariant.imageUrl;
      if (image && button.dataset.alt) image.alt = button.dataset.alt;
      if (skuLabel) skuLabel.textContent = `SKU ${selectedVariant.sku || product.sku}`;
      if (priceValue) priceValue.textContent = `Net ${money(selectedVariant.net)}`;
      if (priceSupport) priceSupport.textContent = detailSupportText(selectedVariant);
      if (specGrid) specGrid.innerHTML = specGridMarkup(product, selectedVariant);

      variantButtons.forEach((item) => item.classList.toggle("is-active", item.dataset.sku === selectedVariant.sku));
      variantCards.forEach((item) => item.classList.toggle("is-active", item.dataset.variantCard === selectedVariant.sku));
    });
  });
}

const root = document.getElementById("product-root");
const sku = getSkuFromQuery();
const product = allProducts.find((item) => String(item.sku || "").toUpperCase() === sku) || allProducts.find((item) => slug(item.productName) === slug(sku));

if (!product) {
  renderNotFound(root);
} else {
  document.title = `${product.productName} | 2026 LPD Music Catalog`;
  renderProduct(root, product);
  wireDetailSelectors(product);
}
