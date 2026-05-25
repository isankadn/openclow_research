#!/usr/bin/env python3
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "outputs"
FIG = ROOT / "figures"
FIG.mkdir(exist_ok=True)


def read_csv(path):
    with path.open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


def esc(text):
    return str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def main():
    rows = read_csv(OUT / "strategy_feature_adjusted_twfe_v1.csv")
    strategies = [
        r for r in rows
        if r["model"] in {"strategy_total_twfe", "strategy_adjusted_for_behavior_twfe"}
        and r["feature"].startswith("strategy_")
    ]
    labels = sorted({r["feature"].replace("strategy_", "") for r in strategies})
    lookup = {(r["model"], r["feature"].replace("strategy_", "")): r for r in strategies}
    width, height = 1080, 460
    left, right, top, row_h = 280, 980, 82, 52
    min_x, max_x = -0.14, 0.26

    def xscale(v):
        return left + (v - min_x) / (max_x - min_x) * (right - left)

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        '<text x="24" y="34" font-family="Arial" font-size="20" font-weight="700">Strategy Effects Before and After Behavior Adjustment</text>',
        '<text x="24" y="56" font-family="Arial" font-size="12" fill="#555">Two-way fixed effects: student and assessment occasion; baseline is no same-course activity</text>',
    ]
    zero = xscale(0)
    parts.append(f'<line x1="{zero:.1f}" x2="{zero:.1f}" y1="{top-24}" y2="{top+row_h*len(labels)-18}" stroke="#888"/>')
    colors = {"strategy_total_twfe": "#2868a8", "strategy_adjusted_for_behavior_twfe": "#b05a28"}
    names = {"strategy_total_twfe": "Strategy total", "strategy_adjusted_for_behavior_twfe": "Adjusted for behavior features"}
    for i, label in enumerate(labels):
        y = top + i * row_h
        parts.append(f'<text x="24" y="{y+6}" font-family="Arial" font-size="12" dominant-baseline="middle">{esc(label)}</text>')
        for j, model in enumerate(["strategy_total_twfe", "strategy_adjusted_for_behavior_twfe"]):
            r = lookup[(model, label)]
            beta = float(r["beta_std"])
            lo = float(r["ci_low"])
            hi = float(r["ci_high"])
            yy = y + j * 17
            color = colors[model]
            parts.append(f'<line x1="{xscale(lo):.1f}" x2="{xscale(hi):.1f}" y1="{yy}" y2="{yy}" stroke="{color}" stroke-width="3" stroke-linecap="round"/>')
            parts.append(f'<circle cx="{xscale(beta):.1f}" cy="{yy}" r="5" fill="{color}"/>')
            parts.append(f'<text x="{right+12}" y="{yy+1}" font-family="Arial" font-size="11" fill="#333" dominant-baseline="middle">{beta:+.3f}</text>')
    legend_x = 690
    for j, model in enumerate(["strategy_total_twfe", "strategy_adjusted_for_behavior_twfe"]):
        y = 33 + j * 18
        parts.append(f'<circle cx="{legend_x}" cy="{y}" r="5" fill="{colors[model]}"/>')
        parts.append(f'<text x="{legend_x+12}" y="{y+1}" font-family="Arial" font-size="12" dominant-baseline="middle">{names[model]}</text>')
    parts.append(f'<text x="{(left+right)/2:.1f}" y="{height-22}" font-family="Arial" font-size="12" text-anchor="middle" fill="#444">Standardized coefficient</text>')
    parts.append("</svg>")
    (FIG / "fig11_strategy_adjusted_twfe.svg").write_text("\n".join(parts) + "\n", encoding="utf-8")
    print("Wrote figures/fig11_strategy_adjusted_twfe.svg")


if __name__ == "__main__":
    main()
