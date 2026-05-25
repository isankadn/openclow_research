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


def forest(rows, title, subtitle, output, label_field, max_rows=12):
    rows = sorted(rows, key=lambda r: float(r["score_resid_std_mean"]), reverse=True)[:max_rows]
    width, height = 1120, 110 + 44 * len(rows)
    left, right, top, row_h = 430, 1000, 82, 42
    vals = []
    for r in rows:
        vals.extend([float(r["score_resid_ci_low"]), float(r["score_resid_ci_high"]), float(r["score_resid_std_mean"])])
    min_x = min(-0.22, min(vals) - 0.02)
    max_x = max(0.32, max(vals) + 0.02)

    def xscale(v):
        return left + (v - min_x) / (max_x - min_x) * (right - left)

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        f'<text x="24" y="34" font-family="Arial" font-size="20" font-weight="700">{esc(title)}</text>',
        f'<text x="24" y="56" font-family="Arial" font-size="12" fill="#555">{esc(subtitle)}</text>',
    ]
    zero = xscale(0)
    parts.append(f'<line x1="{zero:.1f}" x2="{zero:.1f}" y1="{top-22}" y2="{top+row_h*len(rows)-18}" stroke="#888"/>')
    for i, r in enumerate(rows):
        y = top + i * row_h
        beta = float(r["score_resid_std_mean"])
        lo = float(r["score_resid_ci_low"])
        hi = float(r["score_resid_ci_high"])
        color = "#1f7a4d" if lo > 0 else ("#9b2c2c" if hi < 0 else "#666666")
        label = r[label_field]
        parts.append(f'<text x="24" y="{y}" font-family="Arial" font-size="12" dominant-baseline="middle">{esc(label)}</text>')
        parts.append(f'<text x="24" y="{y+16}" font-family="Arial" font-size="10" fill="#666">rows {int(r["rows"]):,}, students {int(r["students"]):,}</text>')
        parts.append(f'<line x1="{xscale(lo):.1f}" x2="{xscale(hi):.1f}" y1="{y+7}" y2="{y+7}" stroke="{color}" stroke-width="3" stroke-linecap="round"/>')
        parts.append(f'<circle cx="{xscale(beta):.1f}" cy="{y+7}" r="5" fill="{color}"/>')
        parts.append(f'<text x="{right+12}" y="{y+8}" font-family="Arial" font-size="11" fill="#333" dominant-baseline="middle">{beta:+.3f}</text>')
    parts.append(f'<text x="{(left+right)/2:.1f}" y="{height-22}" font-family="Arial" font-size="12" text-anchor="middle" fill="#444">Assessment-residual score, SD units</text>')
    parts.append("</svg>")
    (FIG / output).write_text("\n".join(parts) + "\n", encoding="utf-8")


def main():
    forest(
        read_csv(OUT / "temporal_phase_strategy_summary_v1.csv"),
        "Temporal Strategy Patterns Before Tests",
        "Three-month phase strategies; outcome is assessment fixed-effect residual score",
        "fig9_temporal_phase_strategies.svg",
        "phase_strategy",
    )
    forest(
        read_csv(OUT / "combined_strategy_profile_summary_v1.csv"),
        "Combined Temporal and Behavior Strategy Profiles",
        "Only combinations with at least 100 rows; local row assignments are not exported here",
        "fig10_combined_strategy_profiles.svg",
        "combined_strategy",
        max_rows=16,
    )
    print("Wrote fig9_temporal_phase_strategies.svg and fig10_combined_strategy_profiles.svg")


if __name__ == "__main__":
    main()
