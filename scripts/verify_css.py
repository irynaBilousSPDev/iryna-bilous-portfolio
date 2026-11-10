#!/usr/bin/env python3
"""Fail if any HTML class is missing from compiled main.css."""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CSS = ROOT / "assets/css/main.css"
HTML_FILES = (ROOT / "index.html", ROOT / "en/index.html", ROOT / "ua/index.html")


def css_defines(name: str, css: str) -> bool:
    pat = re.compile(r"\." + re.escape(name) + r"(?:[,\s\.#\[{>+~:_-]|$)")
    return bool(pat.search(css))


def main() -> int:
    if not CSS.is_file():
        print("missing", CSS, file=sys.stderr)
        return 1
    css = CSS.read_text(encoding="utf-8")
    classes: set[str] = set()
    for path in HTML_FILES:
        text = path.read_text(encoding="utf-8")
        for m in re.finditer(r'\bclass="([^"]*)"', text):
            classes.update(m.group(1).split())
    missing = sorted(c for c in classes if not css_defines(c, css))
    if missing:
        print("Classes in HTML but not in main.css:", ", ".join(missing), file=sys.stderr)
        return 1
    print(f"OK — {len(classes)} classes checked in {CSS.name} ({CSS.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
