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


def label(feature):
    return {
        "log_events": "Event volume",
        "log_active_days": "Active days",
        "navigation_rate": "Navigation share",
        "memo_rate": "Memo share",
        "marker_rate": "Marker share",
        "content_session_rate": "Open/close share",
    }.get(feature, feature)


def main():
    rows = read_csv(OUT / "model_window_robustness_v1.csv")
    rows = [r for r in rows if r["scope"] == "all_strong_cells"]
    windows = ["m3", "m6", "m12"]
    features = ["log_events", "log_active_days", "navigation_rate", "memo_rate", "marker_rate", "content_session_rate"]
    lookup = {(r["window"], r["feature"]): r for r in rows}

    width, height = 980, 560
    left, right, top, row_h = 230, 900, 76, 68
    min_x, max_x = -0.14, 0.26
    colors = {"m3": "#3366aa", "m6": "#22845b", "m12": "#b05a28"}

    def xscale(v):
        return left + (v - min_x) / (max_x - min_x) * (right - left)

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        '<text x="24" y="34" font-family="Arial" font-size="20" font-weight="700">Window Robustness: Strong-Cell Fixed-Effects Model</text>',
        '<text x="24" y="56" font-family="Arial" font-size="12" fill="#555">Standardized effects across 3-, 6-, and 12-month pre-test windows; intervals use student-cluster bootstrap</text>',
    ]
    zero = xscale(0)
    parts.append(f'<line x1="{zero:.1f}" x2="{zero:.1f}" y1="{top-22}" y2="{top + row_h * len(features) - 10}" stroke="#888"/>')
    for tick in [-0.10, -0.05, 0, 0.05, 0.10, 0.15, 0.20, 0.25]:
        x = xscale(tick)
        parts.append(f'<line x1="{x:.1f}" x2="{x:.1f}" y1="{top + row_h * len(features) - 10}" y2="{top + row_h * len(features) - 4}" stroke="#777"/>')
        parts.append(f'<text x="{x:.1f}" y="{top + row_h * len(features) + 12}" font-family="Arial" font-size="11" text-anchor="middle" fill="#444">{tick:+.2f}</text>')
    for i, feature in enumerate(features):
        base_y = top + i * row_h
        parts.append(f'<text x="24" y="{base_y+16}" font-family="Arial" font-size="13" dominant-baseline="middle">{esc(label(feature))}</text>')
        for j, window in enumerate(windows):
            r = lookup[(window, feature)]
            beta = float(r["beta_std"])
            lo = float(r["ci_low"])
            hi = float(r["ci_high"])
            y = base_y + 4 + j * 17
            color = colors[window]
            parts.append(f'<line x1="{xscale(lo):.1f}" x2="{xscale(hi):.1f}" y1="{y}" y2="{y}" stroke="{color}" stroke-width="3" stroke-linecap="round"/>')
            parts.append(f'<circle cx="{xscale(beta):.1f}" cy="{y}" r="5" fill="{color}"/>')
            parts.append(f'<text x="{right+12}" y="{y}" font-family="Arial" font-size="11" dominant-baseline="middle" fill="#333">{window} {beta:+.3f}</text>')
    legend_x = 730
    for idx, window in enumerate(windows):
        y = 34 + idx * 18
        parts.append(f'<circle cx="{legend_x}" cy="{y}" r="5" fill="{colors[window]}"/>')
        parts.append(f'<text x="{legend_x+12}" y="{y+1}" font-family="Arial" font-size="12" dominant-baseline="middle">{window}</text>')
    parts.append(f'<text x="{(left+right)/2:.1f}" y="{height-26}" font-family="Arial" font-size="12" text-anchor="middle" fill="#444">Standardized coefficient</text>')
    parts.append("</svg>")
    (FIG / "fig7_window_robustness.svg").write_text("\n".join(parts) + "\n", encoding="utf-8")
    print("Wrote figures/fig7_window_robustness.svg")


if __name__ == "__main__":
    main()
