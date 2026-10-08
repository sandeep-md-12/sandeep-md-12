"""Neofetch-style info card -> info-card.svg.

Lines fade and slide in with a short stagger, once.
Set STATIC=1 to emit a frozen frame (for local previews).
Edit ROWS to update the card.
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "info-card.svg")
STATIC = os.environ.get("STATIC") == "1"

BG, PANEL, BORDER = "#0d1117", "#161b22", "#30363d"
FG, DIM = "#c9d1d9", "#7d8590"
GREEN, CYAN, YELLOW, PINK = "#3fb950", "#58c4dc", "#e3b341", "#db61a2"
FONT = "ui-monospace,SFMono-Regular,Menlo,Consolas,'DejaVu Sans Mono',monospace"

ROWS = [
    ("Name",   "Sandeepkumar M D", YELLOW),
    ("Role",   "Backend / Full Stack Engineer", CYAN),
    ("Exp",    "1.8 yrs", CYAN),
    ("Prev",   "HLM (Backend, freelance)", CYAN),
    ("",       "Avasoft (Software Engineer)", CYAN),
    ("Stack",  "Python · FastAPI · PostgreSQL", PINK),
    ("",       "React · Node.js", PINK),
    ("Infra",  "Redis · Docker · AWS · GitLab CI", PINK),
    ("AI",     "LangChain · RAG · Vector Search", PINK),
    ("Wins",   "40% faster invoicing", GREEN),
    ("",       "12k-user HR platform", GREEN),
    ("",       "SIH 2022 Grand Finalist", GREEN),
    ("Web",    "sandeepkumarmd.vercel.app", YELLOW),
    ("Status", "Open to work · immediate joiner", YELLOW),
]

W = 490
LINE = 22
TOP = 46
X, KEY_W = 24, 74


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def main():
    lines = []
    head_y = TOP + 22
    lines.append(f'<text x="{X}" y="{head_y}" class="h">sandeep<tspan class="d">@</tspan>backend</text>')
    lines.append(f'<line x1="{X}" y1="{head_y + 10}" x2="{X + 200}" y2="{head_y + 10}" stroke="{BORDER}"/>')
    for i, (k, v, col) in enumerate(ROWS):
        y = head_y + 36 + i * LINE
        style = "" if STATIC else f' style="animation-delay:{0.35 + i * 0.12:.2f}s"'
        key = f'<tspan fill="{col}" font-weight="700">{esc(k)}</tspan><tspan class="d">:</tspan>' if k else ""
        lines.append(f'<g class="r"{style}><text x="{X}" y="{y}" class="t">{key}</text>'
                     f'<text x="{X + KEY_W}" y="{y}" class="t">{esc(v)}</text></g>')

    # colour swatch row, neofetch-style
    sy = head_y + 36 + len(ROWS) * LINE + 2
    sw = [BORDER, "#ff5f56", GREEN, YELLOW, "#388bfd", PINK, CYAN, FG]
    style = "" if STATIC else f' style="animation-delay:{0.35 + len(ROWS) * 0.12:.2f}s"'
    lines.append(f'<g class="r"{style}>' + "".join(
        f'<rect x="{X + KEY_W + i * 22}" y="{sy - 10}" width="18" height="12" rx="2" fill="{c}"/>'
        for i, c in enumerate(sw)) + "</g>")

    H = sy + 26
    dots = "".join(f'<circle cx="{20 + i * 18}" cy="17" r="5.5" fill="{c}"/>'
                   for i, c in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]))
    anim = "" if STATIC else """
  .r{opacity:0;animation:in .45s cubic-bezier(.2,.8,.2,1) forwards}
  @keyframes in{from{opacity:0;transform:translateX(-8px)}to{opacity:1;transform:none}}"""

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Sandeepkumar M D - Backend / Full Stack Engineer">
<style>
  text{{font-family:{FONT};font-size:13px;fill:{FG}}}
  .h{{font-size:15px;font-weight:700;fill:{CYAN}}} .d{{fill:{DIM}}} .tt{{font-size:11px;fill:{DIM}}}{anim}
</style>
<rect width="{W}" height="{H}" rx="12" fill="{PANEL}" stroke="{BORDER}"/>
<path d="M0 34 H{W}" stroke="{BORDER}"/>
{dots}
<text x="{W / 2}" y="21" text-anchor="middle" class="tt">sandeep — neofetch</text>
{"".join(lines)}
</svg>
'''
    with open(OUT, "w") as f:
        f.write(svg)
    print(f"wrote {OUT} ({W}x{H})")


if __name__ == "__main__":
    main()
