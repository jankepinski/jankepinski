#!/usr/bin/env python3
"""Generate the profile banner (assets/banner.svg).

A sticker-bomb banner: a mesh-gradient card, hand-drawn SVG stickers for the things
I work on, and the name as bouncy toy letters. The lettering (Bungee for the name,
Source Sans 3 for the role pill, both OFL, in assets/fonts) is converted to paths
with fontTools, so no font is needed at render time.

Usage:  python3 scripts/banner.py
Needs:  pip install fonttools
"""

from pathlib import Path

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parent.parent
FONT_DIR = ROOT / "assets" / "fonts"

W, H = 1200, 380
NAME = "Jan Kępiński"
ROLE = "AI Engineer · Fullstack"

INK = "#1f1535"
VIOLET, PINK, YELLOW, CYAN, GREEN, ORANGE = "#7c5cff", "#ff5fa2", "#ffd23f", "#2ed3e6", "#3ddc97", "#ff8a3d"


def st(width: float = 3.5) -> str:
    return f'stroke="{INK}" stroke-width="{width}" stroke-linejoin="round" stroke-linecap="round"'


STROKE = st()


# ---------- lettering ----------

def glyphs(ttf: str, text: str, size: float):
    """Yield (char, svg path in px with baseline at y=0, advance in px) for each character."""
    font = TTFont(FONT_DIR / ttf)
    gs, cmap, hmtx = font.getGlyphSet(), font.getBestCmap(), font["hmtx"]
    scale = size / font["head"].unitsPerEm
    for ch in text:
        name = cmap[ord(ch)]
        pen = SVGPathPen(gs)
        gs[name].draw(pen)
        yield ch, pen.getCommands(), scale, hmtx[name][0] * scale


def wordmark(cx: float, baseline: float) -> str:
    """Name as toy letters: colourful fill, ink outline, hard ink shadow, a gentle wave."""
    size, gap = 100, 4
    letters = list(glyphs("Bungee-Regular.ttf", NAME, size))
    width = sum(adv + gap for _, _, _, adv in letters) - gap
    x = cx - width / 2
    fills = [YELLOW, PINK, CYAN, GREEN, ORANGE, "#b69cff"]
    tilts = [-9, 6, -4, 8, -10, 5, -6, 9, -3, 7, -8]
    lifts = [2, -8, 5, -3, 4, -9, 3, -5, 6, -2, 4]
    out, i = [], 0
    for ch, d, s, adv in letters:
        if ch != " ":
            fill = fills[i % len(fills)]
            path = f'<path d="{d}" transform="scale({s:.5f} {-s:.5f})"'
            cxl = adv / 2
            out.append(
                f'<g transform="translate({x:.1f} {baseline + lifts[i % len(lifts)]}) rotate({tilts[i % len(tilts)]} {cxl:.1f} {-size * 0.33:.1f})">'
                f'<g class="bob" style="animation-delay:{i * 0.11:.2f}s">'
                f'{path} fill="{INK}" stroke="{INK}" stroke-width="{16 / s:.0f}" stroke-linejoin="round" '
                f'style="transform:translate(6px,8px) scale({s:.5f},{-s:.5f})"/>'
                f'{path} fill="{fill}" stroke="{INK}" stroke-width="{11 / s:.0f}" stroke-linejoin="round" paint-order="stroke"/>'
                f"</g></g>"
            )
            i += 1
        x += adv + gap
    return "".join(out)


def pill(cx: float, cy: float) -> str:
    """Role label as a white sticker pill with a hard shadow."""
    size = 30
    letters = list(glyphs("SourceSans3-Semibold.ttf", ROLE, size))
    width = sum(adv for *_, adv in letters)
    pw, ph = width + 64, 54
    x0 = cx - width / 2
    text, x = [], x0
    for ch, d, s, adv in letters:
        if ch != " ":
            fill = VIOLET if ch == "·" else INK
            text.append(f'<path d="{d}" fill="{fill}" transform="translate({x:.1f} {cy + 10:.1f}) scale({s:.5f} {-s:.5f})"/>')
        x += adv
    return (
        f'<g transform="rotate(-2 {cx} {cy})">'
        f'<rect x="{cx - pw / 2 + 5:.1f}" y="{cy - ph / 2 + 6:.1f}" width="{pw:.1f}" height="{ph}" rx="{ph / 2}" fill="{INK}"/>'
        f'<rect x="{cx - pw / 2:.1f}" y="{cy - ph / 2:.1f}" width="{pw:.1f}" height="{ph}" rx="{ph / 2}" fill="#fff" {STROKE}/>'
        f'{"".join(text)}</g>'
    )


# ---------- stickers (each drawn around 0,0, roughly -45..45) ----------

def robot() -> str:
    return f"""
    <line x1="0" y1="-40" x2="0" y2="-28" {STROKE}/><circle cx="0" cy="-43" r="6" fill="{PINK}" {STROKE}/>
    <rect x="-40" y="-12" width="8" height="18" rx="4" fill="{PINK}" {STROKE}/><rect x="32" y="-12" width="8" height="18" rx="4" fill="{PINK}" {STROKE}/>
    <rect x="-33" y="-28" width="66" height="50" rx="16" fill="{VIOLET}" {STROKE}/>
    <rect x="-24" y="-19" width="48" height="31" rx="10" fill="{INK}"/>
    <g class="blink"><circle cx="-11" cy="-6" r="5.5" fill="{CYAN}"/><circle cx="11" cy="-6" r="5.5" fill="{CYAN}"/></g>
    <path d="M-7 4 Q0 9 7 4" fill="none" stroke="{CYAN}" stroke-width="3" stroke-linecap="round"/>
    <rect x="-20" y="22" width="40" height="16" rx="6" fill="{YELLOW}" {STROKE}/>"""


def chat() -> str:
    dots = "".join(
        f'<circle class="typing" style="animation-delay:{k * 0.18:.2f}s" cx="{x}" cy="1" r="5.5" fill="{INK}"/>'
        for k, x in enumerate((-17, 0, 17))
    )
    return f"""
    <path d="M-34 -24h68a10 10 0 0 1 10 10v30a10 10 0 0 1-10 10h-40l-16 14v-14h-12a10 10 0 0 1-10-10v-30a10 10 0 0 1 10-10z" fill="{CYAN}" {STROKE}/>
    {dots}"""


def atom() -> str:
    orbit = 'rx="42" ry="15" fill="none" stroke="#149eca" stroke-width="5"'
    return f"""
    <g class="spin">
      <ellipse {orbit}/><ellipse {orbit} transform="rotate(60)"/><ellipse {orbit} transform="rotate(120)"/>
    </g>
    <circle r="8" fill="#149eca"/>"""


def gamepad() -> str:
    return f"""
    <path d="M-40 -14q0-14 16-14h48q16 0 16 14l6 22q4 16-10 18q-9 1-15-9l-5-7h-32l-5 7q-6 10-15 9q-14-2-10-18z" fill="{PINK}" {STROKE}/>
    <path d="M-23 -18h6v6h6v6h-6v6h-6v-6h-6v-6h6z" fill="{INK}"/>
    <circle cx="17" cy="-13" r="5" fill="{YELLOW}" {STROKE}/><circle cx="27" cy="-3" r="5" fill="{CYAN}" {STROKE}/>"""


def synth() -> str:
    w, x0, n = 76, -38, 7
    whites = "".join(f'<line x1="{x0 + w / n * k:.1f}" y1="-4" x2="{x0 + w / n * k:.1f}" y2="22" {st(2.5)}/>' for k in range(1, n))
    blacks = "".join(
        f'<rect x="{x0 + w / n * k - 3.5:.1f}" y="-4" width="7" height="15" rx="1.5" fill="{INK}"/>' for k in (1, 2, 4, 5, 6)
    )
    return f"""
    <rect x="-46" y="-30" width="92" height="58" rx="9" fill="{YELLOW}" {STROKE}/>
    <circle cx="-30" cy="-17" r="6" fill="#fff" {st(3)}/><circle cx="-14" cy="-17" r="6" fill="#fff" {st(3)}/>
    <rect x="2" y="-24" width="36" height="14" rx="4" fill="{INK}"/>
    <path class="wave" d="M6 -17q4-7 7 0t7 0t7 0t7 0" fill="none" stroke="{CYAN}" stroke-width="2.5" stroke-linecap="round"/>
    <rect x="{x0}" y="-4" width="{w}" height="26" rx="3" fill="#fff" {st(3)}/>{whites}{blacks}"""


def terminal() -> str:
    return f"""
    <rect x="-44" y="-32" width="88" height="64" rx="10" fill="{INK}" {STROKE}/>
    <circle cx="-33" cy="-21" r="3.5" fill="{PINK}"/><circle cx="-23" cy="-21" r="3.5" fill="{YELLOW}"/><circle cx="-13" cy="-21" r="3.5" fill="{GREEN}"/>
    <path d="M-30 -6l11 9l-11 9" fill="none" stroke="{GREEN}" stroke-width="4.5" stroke-linecap="round" stroke-linejoin="round"/>
    <rect class="cursor" x="-12" y="9" width="16" height="4.5" rx="2" fill="#fff"/>
    <rect x="10" y="-8" width="22" height="4" rx="2" fill="{VIOLET}"/><rect x="10" y="1" width="14" height="4" rx="2" fill="{CYAN}"/>"""


def invader() -> str:
    rows = ["..X.....X..", "...X...X...", "..XXXXXXX..", ".XX.XXX.XX.", "XXXXXXXXXXX", "X.XXXXXXX.X", "X.X.....X.X", "...XX.XX..."]
    p = 6.5
    x0, y0 = -len(rows[0]) * p / 2, -len(rows) * p / 2
    rects = "".join(
        f'<rect x="{x0 + c * p:.1f}" y="{y0 + r * p:.1f}" width="{p + 0.3:.1f}" height="{p + 0.3:.1f}"/>'
        for r, row in enumerate(rows) for c, v in enumerate(row) if v == "X"
    )
    return f'<g class="wiggle" fill="{GREEN}">{rects}</g>'


def cube() -> str:
    return f"""
    <path d="M0 -36L31 -18L0 0L-31 -18Z" fill="{YELLOW}" {STROKE}/>
    <path d="M-31 -18L0 0L0 36L-31 18Z" fill="{ORANGE}" {STROKE}/>
    <path d="M31 -18L0 0L0 36L31 18Z" fill="{PINK}" {STROKE}/>"""


def plug() -> str:
    return f"""
    <path d="M0 14v8q0 14-16 14q-16 0-16 14" fill="none" {st(5)}/>
    <rect x="-11" y="-36" width="7" height="16" rx="2" fill="#fff" {st(3)}/><rect x="4" y="-36" width="7" height="16" rx="2" fill="#fff" {st(3)}/>
    <rect x="-18" y="-22" width="36" height="36" rx="8" fill="{VIOLET}" {STROKE}/>
    <path class="zap" d="M26 -38l-8 14h8l-6 13" fill="none" stroke="{ORANGE}" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round"/>
    <text x="0" y="3" font-family="system-ui,sans-serif" font-size="13" font-weight="800" fill="#fff" text-anchor="middle">MCP</text>"""


def notes() -> str:
    return f"""
    <ellipse cx="-17" cy="22" rx="11" ry="8" transform="rotate(-20 -17 22)" fill="{INK}"/>
    <ellipse cx="17" cy="14" rx="11" ry="8" transform="rotate(-20 17 14)" fill="{INK}"/>
    <path d="M-7 20V-20M27 12V-28" {st(4)}/>
    <path d="M-7 -20L27 -28L27 -17L-7 -9Z" fill="{INK}"/>"""


def sparkle(x: float, y: float, r: float, fill: str, delay: float) -> str:
    k = r / 20
    return (
        f'<g transform="translate({x} {y}) scale({k:.2f})"><path class="twinkle" style="animation-delay:{delay}s" '
        f'd="M0 -20C2 -6 6 -2 20 0C6 2 2 6 0 20C-2 6 -6 2 -20 0C-6 -2 -2 -6 0 -20Z" fill="{fill}"/></g>'
    )


def confetti() -> str:
    white = 'fill="none" stroke="#fff" stroke-width="4" stroke-linecap="round" stroke-linejoin="round" opacity="0.8"'
    return "".join([
        f'<path d="M430 58l12-10l12 10l12-10l12 10" {white}/>',
        f'<path d="M700 40q10-14 20 0t20 0" {white}/>',
        f'<path d="M560 352l12-10l12 10l12-10" {white}/>',
        f'<circle cx="820" cy="56" r="9" fill="none" stroke="{YELLOW}" stroke-width="4"/>',
        f'<circle cx="345" cy="205" r="7" fill="none" stroke="#fff" stroke-width="3.5" opacity="0.8"/>',
        f'<circle cx="1010" cy="200" r="5" fill="{PINK}"/>',
        f'<circle cx="180" cy="200" r="5" fill="{YELLOW}"/>',
        f'<circle cx="660" cy="335" r="4" fill="#fff" opacity="0.8"/>',
        f'<path d="M868 214h14M875 207v14" stroke="#fff" stroke-width="4" stroke-linecap="round" opacity="0.8"/>',
        f'<path d="M649 95h12M655 89v12" stroke="{YELLOW}" stroke-width="4" stroke-linecap="round"/>',
    ])


def sticker(art: str, x: float, y: float, rot: float, scale: float = 1.0, base: str = "circle", fill: str = "#fff", delay: float = 0) -> str:
    disc = {
        "circle": f'<circle r="58" fill="{fill}" filter="url(#shadow)"/>',
        "square": f'<rect x="-56" y="-56" width="112" height="112" rx="28" fill="{fill}" filter="url(#shadow)"/>',
    }.get(base, "")
    return (
        f'<g transform="translate({x} {y}) rotate({rot}) scale({scale})">'
        f'<g class="float" style="animation-delay:{delay}s">{disc}{art}</g></g>'
    )


# ---------- the card ----------

def banner() -> str:
    stickers = "".join([
        sticker(robot(), 96, 104, -10, 1.02, delay=0),
        sticker(atom(), 262, 298, 8, 0.8, "square", delay=1.1),
        sticker(terminal(), 86, 292, 6, 0.88, delay=2.0),
        sticker(invader(), 262, 72, 12, 0.72, fill=INK, delay=0.6),
        sticker(chat(), 1104, 96, 8, 0.98, delay=0.4),
        sticker(synth(), 1098, 282, -7, 0.98, "square", delay=1.6),
        sticker(gamepad(), 940, 308, 10, 0.8, delay=0.9),
        sticker(cube(), 942, 72, -10, 0.72, "square", delay=2.3),
        sticker(plug(), 815, 322, -12, 0.7, "square", delay=1.3),
        sticker(notes(), 392, 324, -10, 0.62, fill=YELLOW, delay=0.2),
    ])
    sparkles = "".join([
        sparkle(345, 62, 16, "#fff", 0), sparkle(855, 150, 12, YELLOW, 0.8), sparkle(185, 200, 11, "#fff", 1.5),
        sparkle(1010, 190, 14, "#fff", 0.4), sparkle(640, 330, 10, YELLOW, 1.1), sparkle(560, 50, 9, "#fff", 1.9),
    ])
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-labelledby="t">
  <title id="t">{NAME}: {ROLE}</title>
  <style>
    .float{{animation:float 5s ease-in-out infinite}}
    .bob{{animation:bob 2.6s ease-in-out infinite}}
    .blink{{animation:blink 4s infinite;transform-box:fill-box;transform-origin:center}}
    .typing{{animation:typing 1.2s ease-in-out infinite}}
    .spin{{animation:spin 14s linear infinite;transform-box:view-box;transform-origin:0 0}}
    .cursor{{animation:cursor 1s steps(1) infinite}}
    .wiggle{{animation:wiggle 1.6s steps(2) infinite}}
    .twinkle{{animation:twinkle 2.4s ease-in-out infinite;transform-box:fill-box;transform-origin:center}}
    .zap{{animation:cursor 1.4s steps(1) infinite}}
    .wave{{animation:wave 1.2s linear infinite;stroke-dasharray:4 3}}
    @keyframes float{{0%,100%{{transform:translateY(0)}}50%{{transform:translateY(-7px)}}}}
    @keyframes bob{{0%,100%{{transform:translateY(0)}}50%{{transform:translateY(-9px)}}}}
    @keyframes blink{{0%,92%,100%{{transform:scaleY(1)}}96%{{transform:scaleY(.1)}}}}
    @keyframes typing{{0%,60%,100%{{transform:translateY(0)}}30%{{transform:translateY(-6px)}}}}
    @keyframes spin{{to{{transform:rotate(360deg)}}}}
    @keyframes cursor{{50%{{opacity:0}}}}
    @keyframes wiggle{{50%{{transform:translateY(-3px)}}}}
    @keyframes twinkle{{0%,100%{{transform:scale(.55);opacity:.55}}50%{{transform:scale(1.1);opacity:1}}}}
    @keyframes wave{{to{{stroke-dashoffset:-14}}}}
    @media (prefers-reduced-motion:reduce){{*{{animation:none!important}}}}
  </style>
  <defs>
    <clipPath id="card"><rect width="{W}" height="{H}" rx="24"/></clipPath>
    <radialGradient id="m1" cx="0.1" cy="0" r="0.7"><stop offset="0" stop-color="#6a4cff"/><stop offset="1" stop-color="#6a4cff" stop-opacity="0"/></radialGradient>
    <radialGradient id="m2" cx="0.85" cy="0.05" r="0.6"><stop offset="0" stop-color="#ff6fc0"/><stop offset="1" stop-color="#ff6fc0" stop-opacity="0"/></radialGradient>
    <radialGradient id="m3" cx="1" cy="1" r="0.55"><stop offset="0" stop-color="#ffc86b"/><stop offset="1" stop-color="#ffc86b" stop-opacity="0"/></radialGradient>
    <radialGradient id="m4" cx="0" cy="1" r="0.6"><stop offset="0" stop-color="#45d4e8"/><stop offset="1" stop-color="#45d4e8" stop-opacity="0"/></radialGradient>
    <pattern id="dots" width="22" height="22" patternUnits="userSpaceOnUse"><circle cx="11" cy="11" r="1.6" fill="#fff" opacity="0.22"/></pattern>
    <filter id="shadow" x="-30%" y="-30%" width="160%" height="170%"><feDropShadow dx="0" dy="7" stdDeviation="6" flood-color="#2a0b4a" flood-opacity="0.28"/></filter>
  </defs>
  <g clip-path="url(#card)">
    <rect width="{W}" height="{H}" fill="#9a7bff"/>
    <rect width="{W}" height="{H}" fill="url(#m1)"/><rect width="{W}" height="{H}" fill="url(#m2)"/>
    <rect width="{W}" height="{H}" fill="url(#m3)"/><rect width="{W}" height="{H}" fill="url(#m4)"/>
    <rect width="{W}" height="{H}" fill="url(#dots)"/>
    {confetti()}
    {stickers}
    {sparkles}
    {wordmark(W / 2, 202)}
    {pill(W / 2, 270)}
  </g>
</svg>
"""


def main() -> None:
    path = ROOT / "assets" / "banner.svg"
    path.write_text(banner(), encoding="utf-8")
    print(f"{path.relative_to(ROOT)}  {path.stat().st_size / 1024:.1f} KB")


if __name__ == "__main__":
    main()
