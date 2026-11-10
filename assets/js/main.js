(function () {
  const header = document.querySelector(".site-header");
  const toggle = document.querySelector("[data-menu-toggle]");
  const menuWrap = document.querySelector("[data-nav-mobile]");
  const backdrop = document.querySelector("[data-menu-backdrop]");
  const srLabel = toggle?.querySelector(".sr-only");
  let menuScrollY = 0;

  function syncHeaderHeightVar() {
    if (!header) return;
    document.documentElement.style.setProperty("--header-height", `${header.offsetHeight}px`);
  }

  if (header) {
    const onScroll = () => {
      header.classList.toggle("is-scrolled", window.scrollY > 8);
    };
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
    syncHeaderHeightVar();
    window.addEventListener("resize", syncHeaderHeightVar, { passive: true });
  }

  function unlockPageScroll() {
    const { body } = document;
    const y = menuScrollY;
    body.style.position = "";
    body.style.top = "";
    body.style.left = "";
    body.style.right = "";
    body.style.width = "";
    body.style.paddingRight = "";
    if (header) header.style.paddingRight = "";
    window.scrollTo(0, y);
    menuScrollY = 0;
  }

  function closeMenu({ returnFocus = false } = {}) {
    if (!toggle || !menuWrap) return;
    toggle.setAttribute("aria-expanded", "false");
    menuWrap.classList.remove("is-open");
    menuWrap.setAttribute("hidden", "");
    document.documentElement.classList.remove("is-menu-open");
    document.body.classList.remove("is-menu-open");
    unlockPageScroll();
    if (srLabel && srLabel.dataset.open) {
      srLabel.textContent = srLabel.dataset.open;
    }
    if (returnFocus) {
      toggle.focus();
    }
  }

  function openMenu() {
    if (!toggle || !menuWrap) return;
    menuScrollY = window.scrollY;
    syncHeaderHeightVar();
    const { body, documentElement } = document;
    const scrollbarGap = window.innerWidth - documentElement.clientWidth;
    if (scrollbarGap > 0) {
      body.style.paddingRight = `${scrollbarGap}px`;
      header.style.paddingRight = `${scrollbarGap}px`;
    }
    body.style.position = "fixed";
    body.style.top = `-${menuScrollY}px`;
    body.style.left = "0";
    body.style.right = "0";
    body.style.width = "100%";
    toggle.setAttribute("aria-expanded", "true");
    menuWrap.removeAttribute("hidden");
    menuWrap.classList.add("is-open");
    documentElement.classList.add("is-menu-open");
    body.classList.add("is-menu-open");
    if (srLabel && srLabel.dataset.close) {
      srLabel.textContent = srLabel.dataset.close;
    }
  }

  if (toggle && menuWrap) {
    toggle.addEventListener("click", () => {
      const open = toggle.getAttribute("aria-expanded") === "true";
      if (open) {
        closeMenu();
      } else {
        openMenu();
      }
    });

    backdrop?.addEventListener("click", () => closeMenu());

    menuWrap.querySelectorAll(".nav-mobile a[href^='#'], .nav-mobile-cta").forEach((link) => {
      link.addEventListener("click", () => closeMenu());
    });

    document.addEventListener("keydown", (ev) => {
      if (ev.key === "Escape" && toggle.getAttribute("aria-expanded") === "true") {
        ev.preventDefault();
        closeMenu({ returnFocus: true });
      }
    });
  }
})();
