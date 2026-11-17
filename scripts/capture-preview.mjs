#!/usr/bin/env node
/** Capture homepage preview 640×357 WebP for a project host. */
import { chromium } from "playwright";
import { spawnSync } from "node:child_process";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(__dirname, "..");

const url = process.argv[2] || "https://aktywnaukraina.com/";
const host = process.argv[3] || "aktywnaukraina.com";
const out = path.join(ROOT, `assets/img/previews/${host}.webp`);
const tmp = `/tmp/${host}-preview.png`;

const W = 640;
const H = 357;

const browser = await chromium.launch();
const page = await browser.newPage({
  viewport: { width: 1280, height: 900 },
});
await page.goto(url, { waitUntil: "networkidle", timeout: 120_000 });
await page.waitForTimeout(1500);
await page.screenshot({
  path: tmp,
  clip: { x: 0, y: 0, width: 1280, height: Math.round((1280 * H) / W) },
});
await browser.close();

fs.mkdirSync(path.dirname(out), { recursive: true });

let converted = false;
const cwebp = spawnSync("cwebp", ["-q", "82", tmp, "-o", out], { encoding: "utf8" });
if (cwebp.status === 0) {
  converted = true;
} else {
  const { default: sharp } = await import("sharp");
  await sharp(tmp).resize(W, H, { fit: "cover", position: "top" }).webp({ quality: 82 }).toFile(out);
  converted = true;
}
fs.unlinkSync(tmp);
if (!converted) process.exit(1);
console.log("Wrote", out);