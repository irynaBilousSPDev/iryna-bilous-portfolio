# Iryna Bilous — portfolio (variant A)

Static multilingual portfolio for GitHub Pages: **Polish** (root), **English** (`/en/`), **Ukrainian** (`/ua/`).

Live URL (project site): `https://irynabilousspdev.github.io/iryna-bilous-portfolio/`

## Structure

| Path | Purpose |
|------|---------|
| `index.html` | Polish homepage |
| `en/index.html`, `ua/index.html` | Translated pages (same sections, static HTML) |
| `assets/css/main.css` | Compiled CSS (committed for Pages without a build step) |
| `assets/scss/` | Source styles — edit here, then recompile |
| `assets/js/main.js` | Mobile navigation only |
| `assets/img/` | Optimised portrait and project preview WebPs |
| `scripts/generate_site.py` | Regenerates HTML from `site-data/projects.json` + copy |
| `site-data/projects.json` | Gallery projects grouped by period (chronological) |

## Update content

1. **Gallery / project order** — edit `site-data/projects.json` (or rerun the logic in the repo’s design handoff tooling), then:
   ```bash
   python3 scripts/generate_site.py
   ```
2. **Copy or translations** — edit strings in `scripts/generate_site.py` (`t()`), regenerate HTML, and ask Iryna to review EN/UA.
3. **Styles** — edit `assets/scss/main.scss`, then:
   ```bash
   npm install
   npx sass assets/scss/main.scss assets/css/main.css --style=compressed
   ```
4. **New project screenshots** — add `assets/img/previews/<host>.webp` (640×357 aspect), matching `host` in `projects.json`.

## GitHub Pages

**Recommended:** Settings → Pages → **Deploy from a branch** → branch `main`, folder **`/` (root)**.

`.nojekyll` is included so Jekyll does not strip paths. All asset links are relative and work under the `/iryna-bilous-portfolio/` project subpath.

Optional: the included GitHub Actions workflow also deploys the root folder on push to `main`.

## Local preview

```bash
python3 -m http.server 8080
```

Open `http://localhost:8080/` (or the subpath if you serve from a parent directory).
