#!/usr/bin/env node
import { chromium } from "playwright";
import assert from "node:assert/strict";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { spawn } from "node:child_process";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(__dirname, "..");
const ARTIFACTS = "/opt/cursor/artifacts";
const PORT = Number(process.env.E2E_PORT || 8778);
const BASE = process.env.E2E_BASE_URL || `http://127.0.0.1:${PORT}`;

const locales = [
  { path: "/", slug: "pl", more: "Więcej" },
  { path: "/en/", slug: "en", more: "More" },
  { path: "/ua/", slug: "ua", more: "Більше" },
];

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

  for (const width of [390, 1440]) {
    const mobile = width < 500;
    const context = await browser.newContext({
      viewport: { width, height: 900 },
      isMobile: mobile,
      hasTouch: mobile,
    });

    for (const { path: pagePath, slug, more } of locales) {
      const page = await context.newPage();
      const url = pagePath === "/" ? `${BASE}/` : `${BASE}${pagePath}`;
      await page.goto(url, { waitUntil: "networkidle" });
      await page.locator("#realizacje").scrollIntoViewIfNeeded();

      const card = page
        .locator("article.project-card--has-more")
        .filter({ has: page.locator('.host:text("akademiata.pl")') })
        .first();
      await card.scrollIntoViewIfNeeded();

      const details = card.locator("details.card-details");
      assert.equal(await details.count(), 1, `${slug}@${width}: one details`);
      assert.equal(
        await details.evaluate((el) => el.open),
        false,
        "collapsed by default"
      );
      assert.match(
        await card.locator("summary").innerText(),
        new RegExp(more),
        "localized toggle"
      );
      assert.equal(
        await card.locator(".card-note").isVisible(),
        false,
        "note hidden when collapsed"
      );

      if (slug === "pl" && width === 390) {
        await card.screenshot({
          path: `${ARTIFACTS}/project-card-akademiata-collapsed-pl-390.png`,
        });
      }

      const beforeUrl = page.url();
      const popupPromise = page.waitForEvent("popup", { timeout: 2000 }).catch(() => null);
      if (mobile) {
        await card.locator("summary").tap();
      } else {
        await card.locator("summary").click();
      }
      await popupPromise;
      assert.equal(page.url(), beforeUrl, "summary tap must not navigate");
      assert.equal(await details.evaluate((el) => el.open), true, "expanded");

      if (slug === "pl" && width === 390) {
        await card.screenshot({
          path: `${ARTIFACTS}/project-card-akademiata-expanded-pl-390.png`,
        });
      }

      assert.ok(await card.locator(".card-note").isVisible(), "note visible when open");

      const popup = page.waitForEvent("popup");
      await card.locator("h3").click({ position: { x: 10, y: 10 } });
      const newPage = await popup;
      assert.ok(newPage.url().includes("akademiata.pl"), "card link opens site");
      await newPage.close();

      console.log(`OK project-card-details ${slug} @ ${width}px`);
      await page.close();
    }
    await context.close();
  }

  await browser.close();
  console.log("All project-card details checks passed.");
} finally {
  server.kill();
}
