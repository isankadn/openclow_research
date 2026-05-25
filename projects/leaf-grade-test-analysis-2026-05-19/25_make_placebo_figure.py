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
    rows = [r for r in read_csv(OUT / "future_activity_placebo_v1.csv") if r["feature"] == "log_active_days"]
    families = ["school_regular_exam", "unit_or_chapter_test"]
    windows = ["pre_m3", "future_m3_placebo"]
    colors = {"pre_m3": "#1f7a4d", "future_m3_placebo": "#9b2c2c"}
    lookup = {(r["test_family"], r["window_type"]): r for r in rows}
    width, height = 940, 260
    left, right, top, row_h = 270, 830, 86, 70
    min_x, max_x = -0.14, 0.14

    def xscale(v):
        return left + (v - min_x) / (max_x - min_x) * (right - left)

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        '<text x="24" y="34" font-family="Arial" font-size="20" font-weight="700">Placebo Check: Pre-Test vs Future Active Days</text>',
        '<text x="24" y="56" font-family="Arial" font-size="12" fill="#555">Student and assessment fixed effects; adjusted behavior model</text>',
    ]
    zero = xscale(0)
    parts.append(f'<line x1="{zero:.1f}" x2="{zero:.1f}" y1="{top-28}" y2="{top+row_h*len(families)-22}" stroke="#888"/>')
    for i, family in enumerate(families):
        y = top + i * row_h
        parts.append(f'<text x="24" y="{y+8}" font-family="Arial" font-size="13" dominant-baseline="middle">{esc(family)}</text>')
        for j, window in enumerate(windows):
            r = lookup[(family, window)]
            beta = float(r["beta_std"])
            lo = float(r["ci_low"])
            hi = float(r["ci_high"])
            yy = y + j * 18
            color = colors[window]
            label = "pre" if window == "pre_m3" else "future"
            parts.append(f'<line x1="{xscale(lo):.1f}" x2="{xscale(hi):.1f}" y1="{yy}" y2="{yy}" stroke="{color}" stroke-width="3" stroke-linecap="round"/>')
            parts.append(f'<circle cx="{xscale(beta):.1f}" cy="{yy}" r="5" fill="{color}"/>')
            parts.append(f'<text x="{right+12}" y="{yy+1}" font-family="Arial" font-size="11" dominant-baseline="middle" fill="#333">{label} {beta:+.3f}</text>')
    parts.append(f'<text x="{(left+right)/2:.1f}" y="{height-22}" font-family="Arial" font-size="12" text-anchor="middle" fill="#444">Standardized coefficient for log active days</text>')
    parts.append("</svg>")
    (FIG / "fig14_future_placebo_active_days.svg").write_text("\n".join(parts) + "\n", encoding="utf-8")
    print("Wrote figures/fig14_future_placebo_active_days.svg")


if __name__ == "__main__":
    main()
