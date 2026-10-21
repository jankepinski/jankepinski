#!/usr/bin/env python3
"""Generate the profile banner (assets/banner.svg).

A code editor window that types itself: first a `const jan = {...}` object, line by line,
then a few commands in the terminal pane. Text is set in Geist Mono (OFL, assets/fonts);
only the glyphs used are embedded as a base64 WOFF subset, so the SVG renders the same
through <img> and GitHub's image proxy. Viewers with reduced motion get the final state.

Usage:  python3 scripts/banner.py
Needs:  pip install fonttools
"""

import base64
import io
from pathlib import Path
from xml.sax.saxutils import escape

from fontTools import subset
from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parent.parent
FONT = ROOT / "assets" / "fonts" / "GeistMono-Regular.ttf"

W = 1200
TITLE = "Jan Kępiński: AI Engineer · Fullstack"

# GitHub dark syntax colours
KEYWORD, PROP, STRING, PUNCT, VAR = "#ff7b72", "#79c0ff", "#a5d6ff", "#c9d1d9", "#d2a8ff"
BG, FG, MUTED, GREEN, BORDER = "#0d1117", "#e6edf3", "#8b949e", "#7ee787", "#30363d"

CODE_CPS, TERM_CPS = 0.011, 0.035  # seconds per typed character
TOP, STEP, SIZE, TERM_SIZE = 106, 30, 20, 17


def arr(items):
    out = []
    for k, item in enumerate(items):
        out += [(f'"{item}"', STRING)] + ([(", ", PUNCT)] if k < len(items) - 1 else [])
    return out


CODE = [
    [("const ", KEYWORD), ("jan", VAR), (" = {", PUNCT)],
    [("  name", PROP), (": ", PUNCT), ('"Jan Kępiński"', STRING), (",", PUNCT)],
    [("  role", PROP), (": ", PUNCT), ('"AI Engineer · Fullstack"', STRING), (",", PUNCT)],
    [("  stack", PROP), (": [", PUNCT), *arr(["TypeScript", "React", "Next.js", "Node.js"]), (",", PUNCT)],
    [(" " * 10, PUNCT), *arr(["Vercel AI SDK", "LLMs", "promptfoo"]), ("],", PUNCT)],
    [("  builds", PROP), (": [", PUNCT), *arr(["LLM agents", "RAG chatbots", "MCP servers"]), (",", PUNCT)],
    [(" " * 11, PUNCT), *arr(["web apps", "APIs", "internal tools"]), ("],", PUNCT)],
    [("};", PUNCT)],
]
TERMINAL = [
    ("whoami", "Jan Kępiński, AI engineer"),
    ("location", "Kraków, Poland"),
    ("experience", "3+ years in production"),
]


class Mono:
    """Geist Mono: collects used characters, measures text, builds the embedded subset."""

    def __init__(self):
        self.font = TTFont(FONT)
        self.used = set()
        cmap, hmtx = self.font.getBestCmap(), self.font["hmtx"]
        self.advance = hmtx[cmap[ord("x")]][0] / self.font["head"].unitsPerEm  # em per character

    def t(self, text):
        self.used.update(text)
        return escape(text)

    def width(self, text, size):
        return len(text) * self.advance * size

    def font_face(self):
        font = TTFont(FONT)
        opts = subset.Options()
        opts.flavor = "woff"
        opts.layout_features = ["kern", "liga", "calt"]
        sub = subset.Subsetter(opts)
        sub.populate(text="".join(sorted(self.used)))
        sub.subset(font)
        buf = io.BytesIO()
        font.save(buf)
        data = base64.b64encode(buf.getvalue()).decode()
        return f"@font-face{{font-family:'k-mono';src:url(data:font/woff;base64,{data}) format('woff')}}"


def banner():
    m = Mono()
    h = TOP + STEP * (len(CODE) - 1) + 52
    cw, tcw = m.width("x", SIZE), m.width("x", TERM_SIZE)
    code_w = max(m.width("".join(s for s, _ in segs), SIZE) for segs in CODE)
    split = round(98 + code_w + 40)
    tx = split + 24

    def typed(x, y, n, t, cps, size):
        """A cover that uncovers n characters from the left, plus a caret that follows them.

        Fill is backwards only: once typing ends, the static style (cover scaled to 0) takes over,
        so a rounding error in the last steps() frame can never leave a character covered.
        """
        d, chw = max(n * cps, 0.05), m.width("x", size)
        cover = (
            f'<rect x="{x - 1:.1f}" y="{y - size - 1}" width="{n * chw + 3:.1f}" height="{size * 1.4:.0f}" fill="{BG}" class="cover" '
            f'style="animation:reveal {d:.3f}s steps({n}) {t:.3f}s backwards"/>'
        )
        caret = (
            f'<rect x="{x:.1f}" y="{y - size * 0.85:.1f}" width="2" height="{size * 1.05:.1f}" fill="{FG}" class="caret" '
            f'style="--w:{n * chw:.1f}px;animation:move {d:.3f}s steps({n}) {t:.3f}s,show {d:.3f}s linear {t:.3f}s"/>'
        )
        return cover + caret, t + d

    out, t = [], 0.3
    for i, segs in enumerate(CODE):
        y = TOP + i * STEP
        text = "".join(s for s, _ in segs)
        indent = len(text) - len(text.lstrip(" "))
        spans = "".join(f'<tspan fill="{c}">{m.t(s)}</tspan>' for s, c in segs)
        out.append(
            f'<text x="76" y="{y}" font-size="15" fill="#484f58" text-anchor="end" '
            f'style="animation:appear .01s {t:.3f}s backwards">{m.t(str(i + 1))}</text>'
        )
        out.append(f'<text x="98" y="{y}" font-size="{SIZE}" xml:space="preserve">{spans}</text>')
        anim, t = typed(98 + indent * cw, y, len(text) - indent, t, CODE_CPS, SIZE)
        out.append(anim)
        t += 0.05

    t += 0.25
    m.t("$ ")
    for k, (cmd, result) in enumerate(TERMINAL):
        y = TOP + 2 * k * STEP
        out.append(
            f'<text x="{tx}" y="{y}" font-size="{TERM_SIZE}" fill="{FG}" xml:space="preserve" '
            f'style="animation:appear .01s {t:.3f}s backwards"><tspan fill="{GREEN}">$</tspan> {m.t(cmd)}</text>'
        )
        anim, t = typed(tx + 2 * tcw, y, len(cmd), t + 0.1, TERM_CPS, TERM_SIZE)
        out.append(anim)
        t += 0.12
        out.append(
            f'<text x="{tx}" y="{y + STEP}" font-size="{TERM_SIZE}" fill="{MUTED}" '
            f'style="animation:appear .01s {t:.3f}s backwards">{m.t(result)}</text>'
        )
        t += 0.2
    y = TOP + 2 * len(TERMINAL) * STEP
    out.append(
        f'<g style="animation:appear .01s {t:.3f}s backwards"><text x="{tx}" y="{y}" font-size="{TERM_SIZE}" fill="{GREEN}">$</text>'
        f'<rect class="blink" x="{tx + 2 * tcw:.1f}" y="{y - TERM_SIZE * 0.85:.1f}" width="{tcw:.1f}" height="{TERM_SIZE * 1.05:.1f}" fill="{FG}"/></g>'
    )

    wy, wh = 20, h - 40
    css = m.font_face() + (
        "text{font-family:'k-mono',ui-monospace,monospace}"
        ".cover{transform-box:fill-box;transform-origin:right;transform:scaleX(0)}"
        "@keyframes reveal{from{transform:scaleX(1)}to{transform:scaleX(0)}}"
        ".caret{opacity:0}@keyframes move{to{transform:translateX(var(--w))}}@keyframes show{0%,100%{opacity:1}}"
        "@keyframes appear{from{opacity:0}to{opacity:1}}"
        ".blink{animation:blink 1.1s steps(1) infinite}@keyframes blink{50%{opacity:0}}"
        "@media (prefers-reduced-motion:reduce){*{animation:none!important}}"
    )
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {h}" width="{W}" height="{h}" role="img" aria-labelledby="t">
  <title id="t">{escape(TITLE)}</title>
  <style>{css}</style>
  <defs>
    <clipPath id="card"><rect width="{W}" height="{h}" rx="16"/></clipPath>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#1c2230"/><stop offset="1" stop-color="#0b0f17"/></linearGradient>
  </defs>
  <g clip-path="url(#card)">
    <rect width="{W}" height="{h}" fill="url(#bg)"/>
    <rect x="28" y="{wy}" width="1144" height="{wh}" rx="12" fill="{BG}" stroke="{BORDER}"/>
    <path d="M28 {wy + 12}a12 12 0 0 1 12-12h1120a12 12 0 0 1 12 12v26H28z" fill="#161b22"/>
    <line x1="28" y1="{wy + 38}" x2="1172" y2="{wy + 38}" stroke="{BORDER}"/>
    <circle cx="52" cy="{wy + 19}" r="6" fill="#ff5f57"/><circle cx="72" cy="{wy + 19}" r="6" fill="#febc2e"/><circle cx="92" cy="{wy + 19}" r="6" fill="#28c840"/>
    <rect x="120" y="{wy + 6}" width="96" height="32" rx="6" fill="{BG}"/>
    <text x="136" y="{wy + 27}" font-size="14" fill="{FG}">{m.t("jan.ts")}</text>
    <text x="{tx}" y="{wy + 24}" font-size="13" fill="{MUTED}" letter-spacing="1">{m.t("TERMINAL")}</text>
    <line x1="{split}" y1="{wy + 38}" x2="{split}" y2="{wy + wh}" stroke="{BORDER}"/>
    {"".join(out)}
  </g>
</svg>
"""
    return svg, h, t


def main():
    svg, h, done = banner()
    path = ROOT / "assets" / "banner.svg"
    path.write_text(svg, encoding="utf-8")
    print(f"{path.relative_to(ROOT)}  {path.stat().st_size / 1024:.1f} KB, {W}x{h}, typing done at {done:.1f}s")


if __name__ == "__main__":
    main()
