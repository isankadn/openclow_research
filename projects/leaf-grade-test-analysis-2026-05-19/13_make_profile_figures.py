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
    rows = read_csv(OUT / "behavior_profile_summary_v1.csv")
    rows = sorted(rows, key=lambda r: float(r["score_resid_std_mean"]), reverse=True)
    width, height = 1060, 560
    left, mid, right = 260, 610, 1010
    top, row_h = 84, 70
    min_x, max_x = -0.20, 0.24

    def xscale(v):
        return left + (v - min_x) / (max_x - min_x) * (mid - left)

    def color(value, max_value):
        t = 0 if max_value <= 0 else min(1, value / max_value)
        r = int(247 - 140 * t)
        g = int(247 - 60 * t)
        b = int(247 - 165 * t)
        return f"#{r:02x}{g:02x}{b:02x}"

    max_active = max(float(r["active_days_m3_mean"]) for r in rows)
    max_events = max(float(r["events_m3_mean"]) for r in rows)
    metrics = [
        ("active_days_m3_mean", "Days", max_active),
        ("events_m3_mean", "Events", max_events),
        ("navigation_rate_m3_mean", "Nav", 1.0),
        ("memo_rate_m3_mean", "Memo", 1.0),
        ("marker_rate_m3_mean", "Marker", 1.0),
    ]
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        '<text x="24" y="34" font-family="Arial" font-size="20" font-weight="700">Behavior Profiles in Strong Candidate Cells</text>',
        '<text x="24" y="56" font-family="Arial" font-size="12" fill="#555">Score values are assessment fixed-effect residuals; profile assignments stay local</text>',
    ]
    zero = xscale(0)
    parts.append(f'<line x1="{zero:.1f}" x2="{zero:.1f}" y1="{top-24}" y2="{top+row_h*len(rows)-26}" stroke="#888"/>')
    for tick in [-0.15, -0.10, -0.05, 0, 0.05, 0.10, 0.15, 0.20]:
        x = xscale(tick)
        parts.append(f'<line x1="{x:.1f}" x2="{x:.1f}" y1="{top+row_h*len(rows)-24}" y2="{top+row_h*len(rows)-18}" stroke="#777"/>')
        parts.append(f'<text x="{x:.1f}" y="{top+row_h*len(rows)-3}" font-family="Arial" font-size="10" text-anchor="middle" fill="#444">{tick:+.2f}</text>')
    for j, (_, label, _) in enumerate(metrics):
        x = right - 330 + j * 62
        parts.append(f'<text x="{x+22}" y="{top-28}" font-family="Arial" font-size="11" text-anchor="middle" fill="#333">{label}</text>')
    for i, row in enumerate(rows):
        y = top + i * row_h
        profile = row["profile"]
        score = float(row["score_resid_std_mean"])
        lo = float(row["score_resid_ci_low"])
        hi = float(row["score_resid_ci_high"])
        col = "#1f7a4d" if lo > 0 else ("#9b2c2c" if hi < 0 else "#666666")
        parts.append(f'<text x="24" y="{y}" font-family="Arial" font-size="13" font-weight="700">{esc(profile)}</text>')
        parts.append(f'<text x="24" y="{y+18}" font-family="Arial" font-size="11" fill="#555">rows {int(row["rows"]):,}, students {int(row["students"]):,}</text>')
        parts.append(f'<line x1="{xscale(lo):.1f}" x2="{xscale(hi):.1f}" y1="{y+11}" y2="{y+11}" stroke="{col}" stroke-width="3" stroke-linecap="round"/>')
        parts.append(f'<circle cx="{xscale(score):.1f}" cy="{y+11}" r="5" fill="{col}"/>')
        parts.append(f'<text x="{mid+16}" y="{y+12}" font-family="Arial" font-size="11" fill="#333">{score:+.3f}</text>')
        for j, (field, _, max_value) in enumerate(metrics):
            x = right - 330 + j * 62
            val = float(row[field])
            parts.append(f'<rect x="{x}" y="{y+28}" width="44" height="20" rx="3" fill="{color(val, max_value)}" stroke="#ddd"/>')
            label_val = f"{val:.2f}" if val < 100 else f"{val:.0f}"
            parts.append(f'<text x="{x+22}" y="{y+42}" font-family="Arial" font-size="10" text-anchor="middle" fill="#222">{label_val}</text>')
    parts.append(f'<text x="{(left+mid)/2:.1f}" y="{height-18}" font-family="Arial" font-size="12" text-anchor="middle" fill="#444">Assessment-residual score, SD units</text>')
    parts.append("</svg>")
    (FIG / "fig8_behavior_profiles.svg").write_text("\n".join(parts) + "\n", encoding="utf-8")
    print("Wrote figures/fig8_behavior_profiles.svg")


if __name__ == "__main__":
    main()
