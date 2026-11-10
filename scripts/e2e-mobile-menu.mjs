#!/usr/bin/env node
/**
 * Mobile menu smoke test — requires: npx playwright install chromium
 * Server: python3 -m http.server 8765 from repo root
 */
import { chromium } from "playwright";
import assert from "node:assert/strict";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(__dirname, "..");
const ARTIFACTS = "/opt/cursor/artifacts";
const BASE = process.env.E2E_BASE_URL || "http://127.0.0.1:8765";

const locales = [
  { path: "/", slug: "pl", cta: "Napisz do mnie" },
  { path: "/en/", slug: "en", cta: "Get in touch" },
  { path: "/ua/", slug: "ua", cta: "Напишіть мені" },
];

const browser = await chromium.launch();
const mobile = await browser.newContext({
  viewport: { width: 390, height: 844 },
  isMobile: true,
  hasTouch: true,
  deviceScaleFactor: 2,
});
const desktop = await browser.newContext({
  viewport: { width: 1440, height: 900 },
});

async function testMobile({ path: pagePath, slug, cta }) {
  const page = await mobile.newPage();
  await page.goto(`${BASE}${pagePath === "/" ? "/" : pagePath}`, { waitUntil: "networkidle" });

  const toggle = page.locator("[data-menu-toggle]");
  const wrap = page.locator("[data-nav-mobile]");
  await toggle.tap();

  await page.waitForFunction(() => {
    const w = document.querySelector("[data-nav-mobile]");
    return w && !w.hasAttribute("hidden") && w.classList.contains("is-open");
  });
  await page.waitForTimeout(500);

  const panelBox = await page.locator(".nav-mobile-panel").boundingBox();
  assert(panelBox, "panel should have layout box");
  assert(panelBox.height >= 500, `panel too short: ${panelBox.height}px`);
  assert(panelBox.y >= 60 && panelBox.y <= 80, `panel top y=${panelBox.y}`);

  const navLinks = page.locator(".nav-mobile a");
  assert.equal(await navLinks.count(), 5, "five nav links");
  assert.ok(await page.locator(".nav-mobile-cta").isVisible());
  assert.equal(await page.locator(".nav-mobile-footer .lang-switch").count(), 0);
  assert.ok(await page.locator(".site-header .lang-switch").isVisible());

  await page.screenshot({
    path: `${ARTIFACTS}/menu-open-${slug}-390.png`,
    fullPage: false,
  });
  await page.locator("[data-menu-toggle]").screenshot({
    path: `${ARTIFACTS}/menu-toggle-x-${slug}-390.png`,
  });

  await page.locator(".nav-mobile a").first().tap();
  await page.waitForFunction(() => {
    const t = document.querySelector("[data-menu-toggle]");
    return t?.getAttribute("aria-expanded") === "false";
  });
  assert.equal(await wrap.getAttribute("hidden"), "");

  await page.close();
  console.log(`OK mobile ${slug}`);
}

async function testDesktop() {
  const page = await desktop.newPage();
  await page.goto(`${BASE}/`, { waitUntil: "networkidle" });
  assert.equal(await page.locator("[data-menu-toggle]").count(), 1);
  assert.ok(!(await page.locator(".nav-mobile-wrap").isVisible()));
  await page.screenshot({ path: `${ARTIFACTS}/menu-desktop-1440.png` });
  await page.close();
  console.log("OK desktop 1440");
}

for (const loc of locales) {
  await testMobile(loc);
}
await testDesktop();

await browser.close();
console.log("All mobile menu e2e checks passed.");
