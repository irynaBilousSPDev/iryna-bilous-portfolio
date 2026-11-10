#!/usr/bin/env node
/**
 * Mobile menu — open at top / after scroll; header stays visible.
 */
import { chromium } from "playwright";
import assert from "node:assert/strict";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { spawn } from "node:child_process";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(__dirname, "..");
const ARTIFACTS = "/opt/cursor/artifacts";
const PORT = Number(process.env.E2E_PORT || 8765);
const BASE = process.env.E2E_BASE_URL || `http://127.0.0.1:${PORT}`;

const locales = [
  { path: "/", slug: "pl", cta: "Napisz do mnie" },
  { path: "/en/", slug: "en", cta: "Get in touch" },
  { path: "/ua/", slug: "ua", cta: "Напишіть мені" },
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
  const mobile = await browser.newContext({
    viewport: { width: 390, height: 844 },
    isMobile: true,
    hasTouch: true,
    deviceScaleFactor: 2,
  });
  const desktop = await browser.newContext({
    viewport: { width: 1440, height: 900 },
  });

  async function assertMenuLayout(page, { screenshotAfterScroll = false } = {}) {
    const toggle = page.locator("[data-menu-toggle]");
    const header = page.locator(".site-header");
    const panel = page.locator(".nav-mobile-panel");
    const backdrop = page.locator(".nav-mobile-backdrop");

    await page.waitForTimeout(500);

    assert(await toggle.isVisible(), "menu toggle must be visible");
    assert(await header.isVisible(), "header must stay visible when menu open");
    assert(await toggle.getAttribute("aria-expanded"), "true");

    const headerBox = await header.boundingBox();
    const panelBox = await panel.boundingBox();
    const backdropBox = await backdrop.boundingBox();
    const toggleBox = await toggle.boundingBox();
    const viewport = page.viewportSize();

    assert(headerBox, "header box");
    assert(panelBox, "panel box");
    assert(backdropBox, "backdrop box");
    assert(toggleBox, "toggle box");

    assert(headerBox.y >= -1 && headerBox.y <= 4, `header y=${headerBox.y}`);
    assert(toggleBox.y >= headerBox.y && toggleBox.y <= headerBox.y + headerBox.height, "toggle inside header");
    assert(
      panelBox.y >= headerBox.height - 2,
      `panel should start under header: panel.y=${panelBox.y} header.h=${headerBox.height}`
    );
    assert(panelBox.x <= 1, `panel side gap left: x=${panelBox.x}`);
    assert(
      panelBox.width >= viewport.width - 2,
      `panel width ${panelBox.width} vs viewport ${viewport.width}`
    );
    assert(backdropBox.width >= viewport.width - 2, "backdrop full width");

    if (screenshotAfterScroll) {
      await page.screenshot({
        path: `${ARTIFACTS}/menu-open-after-scroll-pl-390.png`,
        fullPage: false,
      });
    }
  }

  async function openMenu(page) {
    const toggle = page.locator("[data-menu-toggle]");
    await toggle.tap();
    await page.waitForFunction(() => {
      const w = document.querySelector("[data-nav-mobile]");
      return w && !w.hasAttribute("hidden") && w.classList.contains("is-open");
    });
  }

  async function closeMenuViaX(page) {
    const toggle = page.locator("[data-menu-toggle]");
    await toggle.tap();
    await page.waitForFunction(() => {
      const t = document.querySelector("[data-menu-toggle]");
      return t?.getAttribute("aria-expanded") === "false";
    });
    const wrap = page.locator("[data-nav-mobile]");
    assert.equal(await wrap.getAttribute("hidden"), "");
  }

  async function testMobileAtTop({ path: pagePath, slug }) {
    const page = await mobile.newPage();
    await page.goto(`${BASE}${pagePath === "/" ? "/" : pagePath}`, { waitUntil: "networkidle" });
    await openMenu(page);
    await assertMenuLayout(page);

    const navLinks = page.locator(".nav-mobile a");
    assert.equal(await navLinks.count(), 5, "five nav links");
    assert.equal(await page.locator(".nav-mobile-footer .lang-switch").count(), 0);

    if (slug === "pl") {
      await page.screenshot({
        path: `${ARTIFACTS}/menu-open-${slug}-390.png`,
        fullPage: false,
      });
    }

    await page.locator(".nav-mobile a").first().tap();
    await page.waitForFunction(() => {
      const t = document.querySelector("[data-menu-toggle]");
      return t?.getAttribute("aria-expanded") === "false";
    });

    await page.close();
    console.log(`OK mobile top ${slug}`);
  }

  async function testMobileScrolledPL() {
    const page = await mobile.newPage();
    await page.goto(`${BASE}/`, { waitUntil: "networkidle" });

    await page.locator("#o-mnie").scrollIntoViewIfNeeded();
    await openMenu(page);
    await assertMenuLayout(page, { screenshotAfterScroll: true });
    await closeMenuViaX(page);

    await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
    await page.waitForTimeout(200);
    await openMenu(page);
    await assertMenuLayout(page);
    await closeMenuViaX(page);

    await page.close();
    console.log("OK mobile menu after scroll (PL)");
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
    await testMobileAtTop(loc);
  }
  await testMobileScrolledPL();
  await testDesktop();

  await browser.close();
  console.log("All mobile menu e2e checks passed.");
} finally {
  server.kill();
}
