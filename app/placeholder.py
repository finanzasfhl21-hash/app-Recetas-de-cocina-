import hashlib
from xml.sax.saxutils import escape

_BLUE_PALETTE = [
    ("#1e3a8a", "#3b82f6"),
    ("#1d4ed8", "#60a5fa"),
    ("#0c4a6e", "#38bdf8"),
    ("#1e40af", "#93c5fd"),
    ("#0e7490", "#22d3ee"),
    ("#312e81", "#818cf8"),
]


def _pick_palette(name: str) -> tuple[str, str]:
    digest = hashlib.md5(name.encode("utf-8")).hexdigest()
    index = int(digest, 16) % len(_BLUE_PALETTE)
    return _BLUE_PALETTE[index]


def placeholder_svg(name: str) -> str:
    start, end = _pick_palette(name)
    initial = escape((name.strip()[:1] or "?").upper())
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="400" height="240" viewBox="0 0 400 240">
    <defs>
        <linearGradient id="g" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stop-color="{start}"/>
            <stop offset="100%" stop-color="{end}"/>
        </linearGradient>
    </defs>
    <rect width="400" height="240" fill="url(#g)"/>
    <text x="50%" y="55%" font-family="Segoe UI, sans-serif" font-size="96" fill="#ffffff"
          fill-opacity="0.85" text-anchor="middle" dominant-baseline="middle">{initial}</text>
</svg>"""
