#!/usr/bin/env node
/**
 * Hero proof grid — WCAG 2.1 single-line on narrow 2-column layouts.
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

const widths = [360, 390, 430];

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
    const context = await browser.newContext({
      viewport: { width, height: 844 },
      isMobile: true,
      deviceScaleFactor: 2,
    });

    for (const { path: pagePath, slug } of locales) {
      const page = await context.newPage();
      const url = pagePath === "/" ? `${BASE}/` : `${BASE}${pagePath}`;
      await page.goto(url, { waitUntil: "networkidle" });

      const wcagNum = page
        .locator(".proof-grid .proof-card")
        .filter({ hasText: "WCAG 2.1" })
        .locator(".num")
        .first();
      await wcagNum.waitFor({ state: "visible" });

      const metrics = await wcagNum.evaluate((el) => {
        const style = getComputedStyle(el);
        const fontSize = parseFloat(style.fontSize);
        const lineHeight =
          style.lineHeight === "normal"
            ? fontSize * 1.1
            : parseFloat(style.lineHeight);
        const lines = el.scrollHeight / lineHeight;
        return {
          lines,
          whiteSpace: style.whiteSpace,
          scrollWidth: el.scrollWidth,
          clientWidth: el.clientWidth,
        };
      });

      assert(
        metrics.lines < 1.35,
        `${slug}@${width}px: WCAG .num wraps (${metrics.lines.toFixed(2)} lines)`
      );
      assert.equal(
        metrics.whiteSpace,
        "nowrap",
        `${slug}@${width}px: expected nowrap`
      );

      if (width === 390 && slug === "pl") {
        const grid = page.locator(".proof-grid");
        await grid.screenshot({
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
