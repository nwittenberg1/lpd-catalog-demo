const fs = require("fs");
const path = require("path");
const JSZip = require("jszip");

const projectRoot = path.resolve(__dirname, "..");
const allowedRoots = [
  projectRoot,
  path.join(projectRoot, "Photos"),
  path.join(projectRoot, "catalog-prototype"),
];

function isWithinAllowedRoots(candidate) {
  const resolved = path.resolve(candidate);
  return allowedRoots.some((root) => resolved === root || resolved.startsWith(`${root}${path.sep}`));
}

function resolveAssetPath(sourceImageUrl, imageUrl) {
  const sourceCandidate = String(sourceImageUrl || "").trim();
  if (sourceCandidate) {
    const absolute = path.resolve(sourceCandidate);
    if (isWithinAllowedRoots(absolute)) {
      return absolute;
    }
  }

  let cleaned = String(imageUrl || "").trim();
  if (!cleaned) return null;
  cleaned = cleaned.replace(/^https?:\/\/[^/]+/i, "");
  cleaned = cleaned.replace(/^\.\.\//, "");
  cleaned = cleaned.replace(/^\.\//, "");
  cleaned = cleaned.replace(/^\/+/, "");

  const absolute = path.resolve(projectRoot, cleaned);
  if (isWithinAllowedRoots(absolute)) {
    return absolute;
  }
  return null;
}

module.exports = async (req, res) => {
  if (req.method !== "POST") {
    res.status(405).json({ error: "Method not allowed" });
    return;
  }

  try {
    const payload = typeof req.body === "string" ? JSON.parse(req.body) : (req.body || {});
    const stamp = String(payload.stamp || "").trim() || "dealer-list";
    const csvText = String(payload.csvText || "");
    const csvName = String(payload.fileName || `dealer-list-${stamp}.csv`);
    const assets = Array.isArray(payload.assets) ? payload.assets : [];

    const zip = new JSZip();
    zip.file(csvName, csvText);

    for (const asset of assets) {
      const fileName = path.basename(String(asset.fileName || ""));
      const assetPath = resolveAssetPath(asset.sourceImageUrl, asset.imageUrl);
      if (!fileName || !assetPath) continue;
      if (!fs.existsSync(assetPath) || !fs.statSync(assetPath).isFile()) continue;
      const fileBuffer = fs.readFileSync(assetPath);
      zip.file(`Images/${fileName}`, fileBuffer);
    }

    const zipBuffer = await zip.generateAsync({ type: "nodebuffer", compression: "DEFLATE" });
    res.setHeader("Content-Type", "application/zip");
    res.setHeader("Content-Disposition", `attachment; filename="LPD-Dealer-List-${stamp}.zip"`);
    res.setHeader("Cache-Control", "no-store");
    res.status(200).send(zipBuffer);
  } catch (error) {
    res.status(500).json({ error: "Export failed", detail: error.message });
  }
};
