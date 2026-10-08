"""ASCII portrait -> ascii-portrait.svg.

Uses source-prepped.png (from prep_photo.py) if present; otherwise draws an
"SMD" monogram so the README works before a photo is added.

Each row is revealed by a left-to-right wipe with a block cursor, staggered
top to bottom (SMIL), plays once and freezes. STATIC=1 -> frozen frame.
"""
import os

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "source-prepped.png")
OUT = os.path.join(ROOT, "ascii-portrait.svg")
STATIC = os.environ.get("STATIC") == "1"

RAMP = " .`:-=+*cs#%@"          # light -> dark
COLS = 96
W = 370
FS = 6.4                       # font size
CW = (W - 20) / COLS           # char advance we space to
LH = 7.6                       # line height
FLOOR = 0.10                   # min density inside the subject (keeps dark hair visible)
GAMMA = 1.35
MIN_H = 440                    # match info-card height so the table lines up
INK = "#c9d1d9"
BG, BORDER = "#0d1117", "#30363d"
FONT = "ui-monospace,SFMono-Regular,Menlo,Consolas,'DejaVu Sans Mono',monospace"


def monogram():
    im = Image.new("L", (900, 900), 255)
    d = ImageDraw.Draw(im)
    d.ellipse([40, 40, 860, 860], outline=0, width=40)
    d.ellipse([100, 100, 800, 800], outline=150, width=6)
    f = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 300)
    tw = d.textlength("SMD", font=f)
    d.text(((900 - tw) / 2, 260), "SMD", font=f, fill=0)
    f2 = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf", 70)
    t2 = "</>"
    d.text(((900 - d.textlength(t2, font=f2)) / 2, 610), t2, font=f2, fill=60)
    return im


def to_rows(im):
    w, h = im.size
    rows = max(1, round(COLS * (h / w) * (CW / LH)))
    if im.mode in ("LA", "RGBA"):
        # cut-out photo: light ink on dark bg, so brighter = denser; background blank
        lum = np.asarray(im.convert("L").filter(ImageFilter.UnsharpMask(4, 160, 2))
                         .resize((COLS, rows), Image.LANCZOS), dtype=float) / 255
        alpha = np.asarray(im.getchannel("A").resize((COLS, rows), Image.LANCZOS), dtype=float) / 255
        inside = lum[alpha > .5]
        lo, hi = np.percentile(inside, 3), np.percentile(inside, 97)
        lum = np.clip((lum - lo) / max(hi - lo, 1e-3), 0, 1)
        dens = (FLOOR + (1 - FLOOR) * lum ** GAMMA) * alpha
    else:
        dens = 1 - np.asarray(im.convert("L").resize((COLS, rows), Image.LANCZOS), dtype=float) / 255
    idx = (dens * (len(RAMP) - 1)).round().astype(int)
    return ["".join(RAMP[i] for i in r).rstrip() for r in idx]


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def main():
    src = Image.open(SRC) if os.path.exists(SRC) else monogram()
    rows = to_rows(src)
    H = max(round(14 + len(rows) * LH + 12), MIN_H)
    top = (H - len(rows) * LH) / 2 - 2
    body, defs = [], []
    row_t, gap = 0.35, 0.045
    for i, line in enumerate(rows):
        if not line.strip():
            continue
        y = top + (i + 1) * LH
        text = (f'<text x="10" y="{y:.1f}" textLength="{len(line) * CW:.1f}" '
                f'lengthAdjust="spacingAndGlyphs" xml:space="preserve">{esc(line)}</text>')
        if STATIC:
            body.append(text)
            continue
        begin = f"{i * gap:.2f}s"
        lw = len(line) * CW
        defs.append(
            f'<clipPath id="c{i}"><rect x="10" y="{y - LH + 1.5:.1f}" width="0" height="{LH:.1f}">'
            f'<animate attributeName="width" from="0" to="{lw:.1f}" begin="{begin}" dur="{row_t}s" fill="freeze"/>'
            f'</rect></clipPath>')
        body.append(f'<g clip-path="url(#c{i})">{text}</g>')
        # block cursor riding the wipe edge, then vanishing
        body.append(
            f'<rect x="10" y="{y - LH + 1.5:.1f}" width="{CW:.1f}" height="{LH - 1:.1f}" fill="#3fb950" opacity="0">'
            f'<set attributeName="opacity" to="1" begin="{begin}"/>'
            f'<animate attributeName="x" from="10" to="{10 + lw:.1f}" begin="{begin}" dur="{row_t}s" fill="freeze"/>'
            f'<set attributeName="opacity" to="0" begin="{i * gap + row_t:.2f}s"/></rect>')

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="ASCII portrait">
<style>text{{font-family:{FONT};font-size:{FS}px;fill:{INK}}}</style>
<defs>{"".join(defs)}</defs>
<rect width="{W}" height="{H}" rx="12" fill="{BG}" stroke="{BORDER}"/>
{"".join(body)}
</svg>
'''
    with open(OUT, "w") as f:
        f.write(svg)
    print(f"wrote {OUT} ({len(rows)} rows, {W}x{H}, {len(svg) // 1024} KB)"
          + ("" if os.path.exists(SRC) else "  [monogram - add a photo with prep_photo.py]"))


if __name__ == "__main__":
    main()
