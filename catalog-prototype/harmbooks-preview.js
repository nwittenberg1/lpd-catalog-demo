const previewItems = Array.isArray(window.HARMBOOKS_PREVIEW) ? window.HARMBOOKS_PREVIEW : [];

function renderPreview() {
  const root = document.getElementById("harmbooks-preview-grid");
  if (!root) return;

  root.innerHTML = previewItems
    .map(
      (item) => `
        <article class="harmbooks-preview-card">
          <div class="harmbooks-preview-image">
            <img src="${item.imageUrl}" alt="${item.title}" loading="lazy" decoding="async" />
          </div>
          <div class="harmbooks-preview-body">
            <h3>${item.title}</h3>
            <p>${item.sourceName}</p>
          </div>
        </article>
      `
    )
    .join("");
}

renderPreview();
