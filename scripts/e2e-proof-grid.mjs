#!/usr/bin/env node
/**
 * Hero proof grid — WCAG two-line num; mobile font floors.
 */
import { chromium } from "playwright";
import assert from "node:assert/strict";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { spawn } from "node:child_process";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(__dirname, "..");
const ARTIFACTS = "/opt/cursor/artifacts";
const PORT = Number(process.env.E2E_PORT || 8766);
const BASE = process.env.E2E_BASE_URL || `http://127.0.0.1:${PORT}`;

const locales = [
  { path: "/", slug: "pl" },
  { path: "/en/", slug: "en" },
  { path: "/ua/", slug: "ua" },
];

const widths = [360, 390, 430, 1440];

function startServer() {
  return spawn("python3", ["-m", "http.server", String(PORT)], {
    cwd: ROOT,
    stdio: "ignore",
  });
}

const server = startServer();
await new Promise((r) => setTimeout(r, 400));

try {
  const browser = await chromium.launch();

  for (const width of widths) {
    const mobile = width < 900;
    const context = await browser.newContext({
      viewport: { width, height: 900 },
      isMobile: mobile,
      deviceScaleFactor: mobile ? 2 : 1,
    });

    for (const { path: pagePath, slug } of locales) {
      const page = await context.newPage();
      const url = pagePath === "/" ? `${BASE}/` : `${BASE}${pagePath}`;
      await page.goto(url, { waitUntil: "networkidle" });

      const wcagNum = page
        .locator(".proof-grid .proof-card .num--split")
        .first();
      await wcagNum.waitFor({ state: "visible" });

      const sampleNum = page.locator(".proof-grid .proof-card .num").first();

      const wcag = await wcagNum.evaluate((el) => {
        const style = getComputedStyle(el);
        const fontSize = parseFloat(style.fontSize);
        const lines = el.querySelectorAll(".num-line");
        const lineTexts = [...lines].map((l) => l.textContent?.trim() ?? "");
        const lineHeight =
          style.lineHeight === "normal"
            ? fontSize * 1.1
            : parseFloat(style.lineHeight);
        const visualLines = el.scrollHeight / lineHeight;
        return {
          fontSize,
          lineTexts,
          lineCount: lines.length,
          visualLines,
        };
      });

      assert.equal(wcag.lineCount, 2, `${slug}@${width}px: expected 2 num-line spans`);
      assert.deepEqual(
        wcag.lineTexts,
        ["WCAG", "2.1"],
        `${slug}@${width}px: WCAG lines text`
      );
      assert(
        wcag.visualLines >= 1.8 && wcag.visualLines <= 2.35,
        `${slug}@${width}px: expected ~2 visual lines, got ${wcag.visualLines.toFixed(2)}`
      );

      const sampleFontPx = await sampleNum.evaluate((el) =>
        parseFloat(getComputedStyle(el).fontSize)
      );

      if (width === 360) {
        assert(
          sampleFontPx >= 20,
          `${slug}@${width}px: .num font ${sampleFontPx}px < 20px`
        );
      }
      if (width === 390 || width === 430) {
        assert(
          sampleFontPx >= 22,
          `${slug}@${width}px: .num font ${sampleFontPx}px < 22px`
        );
      }
      if (width === 1440) {
        assert(
          sampleFontPx >= 28,
          `${slug}@${width}px: desktop .num font ${sampleFontPx}px < 28px`
        );
      }

      if (width === 390 && slug === "pl") {
        await page.locator(".proof-grid").screenshot({
          path: `${ARTIFACTS}/proof-grid-pl-390.png`,
        });
      }

      console.log(`OK proof-grid ${slug} @ ${width}px`);
      await page.close();
    }

    await context.close();
  }

  await browser.close();
  console.log("All proof-grid e2e checks passed.");
} finally {
  server.kill();
}
