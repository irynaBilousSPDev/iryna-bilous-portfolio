#!/usr/bin/env node
import { chromium } from "playwright";
import assert from "node:assert/strict";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { spawn } from "node:child_process";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(__dirname, "..");
const ARTIFACTS = "/opt/cursor/artifacts";
const PORT = Number(process.env.E2E_PORT || 8779);
const BASE = process.env.E2E_BASE_URL || `http://127.0.0.1:${PORT}`;

const locales = [
  { path: "/", slug: "pl", title: "Kompleksowa Ścieżka Integracji" },
  { path: "/en/", slug: "en", title: "Comprehensive Integration Path" },
  { path: "/ua/", slug: "ua", title: "Комплексний шлях інтеграції" },
];

const server = spawn("python3", ["-m", "http.server", String(PORT)], {
  cwd: ROOT,
  stdio: "ignore",
});
await new Promise((r) => setTimeout(r, 400));

try {
  const browser = await chromium.launch();
  for (const width of [360, 390, 1440]) {
    const mobile = width < 900;
    const ctx = await browser.newContext({
      viewport: { width, height: 900 },
      isMobile: mobile,
      hasTouch: mobile,
    });
    for (const { path: pagePath, slug, title } of locales) {
      const page = await ctx.newPage();
      await page.goto(pagePath === "/" ? `${BASE}/` : `${BASE}${pagePath}`, {
        waitUntil: "networkidle",
      });
      await page.locator("#realizacje").scrollIntoViewIfNeeded();
      const card = page
        .locator("article.project-card")
        .filter({ has: page.locator('.host:text("aktywnaukraina.com")') })
        .first();
      await card.waitFor({ state: "visible" });
      assert.match(await card.locator("h3").innerText(), new RegExp(title));
      assert.equal(
        await card.locator(".project-card__badges .team").count(),
        0,
        "no team badge"
      );
      const avistaCards = page.locator(
        'h3.period-heading:has-text("Avista") + .gallery-grid article.project-card'
      );
      const firstHost = await avistaCards.first().locator(".host").innerText();
      assert.equal(
        firstHost,
        "aktywnaukraina.com",
        "newest Avista card first"
      );

      if (slug === "pl" && width === 390) {
        await card.screenshot({
          path: `${ARTIFACTS}/project-card-aktywnaukraina-pl-390.png`,
        });
      }
      if (slug === "pl" && width === 1440) {
        await card.screenshot({
          path: `${ARTIFACTS}/project-card-aktywnaukraina-pl-1440.png`,
        });
      }
      console.log(`OK aktywna ${slug} @ ${width}px`);
      await page.close();
    }
    await ctx.close();
  }
  await browser.close();
} finally {
  server.kill();
}