(function () {
  const header = document.querySelector(".site-header");
  const toggle = document.querySelector("[data-menu-toggle]");
  const menuWrap = document.querySelector("[data-nav-mobile]");
  const backdrop = document.querySelector("[data-menu-backdrop]");
  const srLabel = toggle?.querySelector(".sr-only");

  if (header) {
    const onScroll = () => {
      header.classList.toggle("is-scrolled", window.scrollY > 8);
    };
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
  }

  function closeMenu({ returnFocus = false } = {}) {
    if (!toggle || !menuWrap) return;
    toggle.setAttribute("aria-expanded", "false");
    menuWrap.classList.remove("is-open");
    menuWrap.setAttribute("hidden", "");
    document.documentElement.classList.remove("is-menu-open");
    document.body.classList.remove("is-menu-open");
    if (srLabel && srLabel.dataset.open) {
      srLabel.textContent = srLabel.dataset.open;
    }
    if (returnFocus) {
      toggle.focus();
    }
  }

  function openMenu() {
    if (!toggle || !menuWrap) return;
    toggle.setAttribute("aria-expanded", "true");
    menuWrap.removeAttribute("hidden");
    menuWrap.classList.add("is-open");
    document.documentElement.classList.add("is-menu-open");
    document.body.classList.add("is-menu-open");
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
