"""24×24 stroke icons from approved variant A (build_A_final / handoff)."""
from __future__ import annotations

# Paths match portfolio-A-final/build_A_final.py IC dict (verified design).
IC = {
    "network": '<rect x="9" y="3" width="6" height="5" rx="1.2"/><rect x="3" y="16" width="6" height="5" rx="1.2"/><rect x="15" y="16" width="6" height="5" rx="1.2"/><path d="M12 8v4M6 16v-2.5h12V16"/>',
    "link": '<rect x="3" y="3" width="8" height="8" rx="2"/><rect x="13" y="13" width="8" height="8" rx="2"/><path d="M11 7h3a3 3 0 0 1 3 3v3"/>',
    "spark": '<path d="M12 3l2.1 5.6 5.9.9-4.5 3.9 1.4 5.8L12 16.1l-4.9 3.1 1.4-5.8L4 9.5l5.9-.9z"/>',
    "bulb": '<path d="M9 18h6M10 21h4M12 3a6 6 0 0 0-3.6 10.8V16h7.2v-2.2A6 6 0 0 0 12 3z"/>',
    "code": '<path d="M8 7l-5 5 5 5M16 7l5 5-5 5M14 4l-4 16"/>',
    "megaphone": '<path d="M3 10v4h4l8 5V5l-8 5z"/><path d="M18.5 9a4 4 0 0 1 0 6"/>',
    "people": '<circle cx="9" cy="8" r="3.5"/><path d="M3 20a6 6 0 0 1 11-3.3"/><circle cx="17" cy="15" r="2.6"/><path d="M19 17l2.2 2.2"/>',
    "shield": '<path d="M12 3l8 3v6c0 4.5-3.4 8-8 9-4.6-1-8-4.5-8-9V6z"/><path d="M8.5 12l2.5 2.5 4.5-5"/>',
    "pin": '<path d="M12 21s-7-6.4-7-11.8a7 7 0 0 1 14 0C19 14.6 12 21 12 21z"/><circle cx="12" cy="9.2" r="2.5"/>',
    "globe": '<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c2.6 2.6 3.8 5.6 3.8 9s-1.2 6.4-3.8 9c-2.6-2.6-3.8-5.6-3.8-9S9.4 5.6 12 3z"/>',
    "cap": '<path d="M2 9l10-5 10 5-10 5z"/><path d="M6 11v5c3.3 2.6 8.7 2.6 12 0v-5"/>',
    "mountain": '<path d="M3 20l6.5-11 4 6.5 2-3L21 20z"/>',
    "cart": '<path d="M3 4h2.2l2.4 11h10.6l2-7.8H6.4"/><circle cx="9" cy="19.5" r="1.4"/><circle cx="17" cy="19.5" r="1.4"/>',
    "box": '<path d="M12 3l8 4.5v9L12 21l-8-4.5v-9z"/><path d="M4 7.5l8 4.5 8-4.5M12 12v9"/>',
}

CURRENT_WORK_ICON_KEYS = ["network", "box", "cart", "link"]

COMP_ICON_KEYS = [
    "network",
    "link",
    "spark",
    "bulb",
    "code",
    "megaphone",
    "people",
    "shield",
]

FACT_ICON_KEYS = ["pin", "globe", "cap", "mountain"]

BLUE = "#1E40AF"
PINK = "#B0174F"


def stroke_icon(name: str, *, color: str, size: int = 22, stroke_width: float = 1.8) -> str:
    if name not in IC:
        raise KeyError(name)
    inner = IC[name]
    return (
        f'<svg class="ui-icon" width="{size}" height="{size}" viewBox="0 0 24 24" '
        f'fill="none" stroke="{color}" stroke-width="{stroke_width}" '
        f'stroke-linecap="round" stroke-linejoin="round" focusable="false" aria-hidden="true">'
        f"{inner}</svg>"
    )


def comp_icon_color(index: int) -> str:
    row, col = divmod(index, 2)
    return BLUE if (row + col) % 2 == 0 else PINK
