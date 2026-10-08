"""Render data/contributions.json as an animated heatmap: contrib-heatmap.svg.

53 weeks x 7 days of rounded cells that slide down diagonally once,
plus a Less -> More legend and a stats footer.
Set STATIC=1 to emit a frozen frame (for local previews).
"""
import datetime as dt
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data", "contributions.json")
OUT = os.path.join(ROOT, "contrib-heatmap.svg")
STATIC = os.environ.get("STATIC") == "1"

PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353", "#69f0a0"]
BG, BORDER, FG, DIM, GREEN = "#0d1117", "#30363d", "#c9d1d9", "#7d8590", "#3fb950"
FONT = "ui-monospace,SFMono-Regular,Menlo,Consolas,'DejaVu Sans Mono',monospace"

W = 860
CELL, GAP = 12, 3
PAD_X = (W - (53 * (CELL + GAP) - GAP)) // 2
GRID_Y = 74


def level(n, peak):
    if n == 0:
        return 0
    q = n / max(peak, 1)
    return 1 if q <= .15 else 2 if q <= .35 else 3 if q <= .6 else 4 if q <= .85 else 5


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def main():
    with open(DATA) as f:
        data = json.load(f)
    days = data["days"]
    end = dt.date.fromisoformat(data["generated"])
    start = end - dt.timedelta(days=364)
    start -= dt.timedelta(days=(start.weekday() + 1) % 7)  # back to Sunday
    peak = max(days.values() or [1])

    cells, months, last_month = [], [], None
    d = start
    while d <= end:
        col, row = (d - start).days // 7, (d.weekday() + 1) % 7
        n = days.get(d.isoformat(), 0)
        x, y = PAD_X + col * (CELL + GAP), GRID_Y + row * (CELL + GAP)
        delay = (col + row) * 0.022
        style = "" if STATIC else f' style="animation-delay:{delay:.3f}s"'
        tip = f"{n} contribution{'s' if n != 1 else ''} on {d:%b %d, %Y}"
        cells.append(f'<rect class="c" x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2.5" '
                     f'fill="{PALETTE[level(n, peak)]}"{style}><title>{tip}</title></rect>')
        if row == 0 and d.month != last_month and col < 52:
            months.append(f'<text x="{x}" y="{GRID_Y - 8}" class="m">{d:%b}</text>')
            last_month = d.month
        d += dt.timedelta(days=1)

    grid_bottom = GRID_Y + 7 * (CELL + GAP) - GAP
    right = PAD_X + 53 * (CELL + GAP) - GAP

    # legend (right aligned)
    sq = 11
    lx = right - (len(PALETTE) * (sq + 3)) - 76
    ly = grid_bottom + 22
    legend = [f'<text x="{lx}" y="{ly + 9}" class="s">Less</text>']
    for i, c in enumerate(PALETTE):
        legend.append(f'<rect x="{lx + 36 + i * (sq + 3)}" y="{ly}" width="{sq}" height="{sq}" rx="2" fill="{c}"/>')
    legend.append(f'<text x="{lx + 40 + len(PALETTE) * (sq + 3)}" y="{ly + 9}" class="s">More</text>')

    best = data["best_day"]
    best_d = dt.date.fromisoformat(best["date"])
    stats = [
        ("total", f'{data["total"]}'),
        ("current streak", f'{data["current_streak"]}d'),
        ("longest streak", f'{data["longest_streak"]}d'),
        ("best day", f'{best["count"]} on {best_d:%b %d}'),
    ]
    sy = ly + 40
    stat_svg, colw = [], (right - PAD_X) / len(stats)
    for i, (k, v) in enumerate(stats):
        x = PAD_X + i * colw
        stat_svg.append(f'<text x="{x:.0f}" y="{sy}" class="k">{esc(k)}</text>'
                        f'<text x="{x:.0f}" y="{sy + 20}" class="v">{esc(v)}</text>')

    H = sy + 40
    anim = "" if STATIC else """
  .c{opacity:0;transform-box:fill-box;animation:drop .45s cubic-bezier(.2,.8,.2,1) forwards}
  @keyframes drop{from{opacity:0;transform:translateY(-10px)}to{opacity:1;transform:none}}
  .f{opacity:0;animation:fade .6s ease 1.8s forwards}
  @keyframes fade{to{opacity:1}}"""

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="{data["total"]} contributions in the last year">
<style>
  text{{font-family:{FONT}}}
  .p{{font-size:13px;fill:{FG}}} .u{{fill:{GREEN}}} .d{{fill:{DIM}}}
  .m{{font-size:10px;fill:{DIM}}} .s{{font-size:10px;fill:{DIM}}}
  .k{{font-size:10px;fill:{DIM};text-transform:uppercase;letter-spacing:.08em}}
  .v{{font-size:15px;fill:{FG};font-weight:600}}{anim}
</style>
<rect width="{W}" height="{H}" rx="12" fill="{BG}" stroke="{BORDER}"/>
<text x="{PAD_X}" y="32" class="p"><tspan class="u">sandeep@github</tspan><tspan class="d"> ~ $ </tspan>./contributions.sh --last 365d</text>
{"".join(months)}
{"".join(cells)}
<g class="f">{"".join(legend)}{"".join(stat_svg)}</g>
</svg>
'''
    with open(OUT, "w") as f:
        f.write(svg)
    print(f"wrote {OUT} ({len(svg) // 1024} KB)")


if __name__ == "__main__":
    main()
