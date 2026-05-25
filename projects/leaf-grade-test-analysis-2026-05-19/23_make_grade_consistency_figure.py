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
    rows = [r for r in read_csv(OUT / "grade_subject_active_days_consistency_v1.csv") if r["status"] == "estimated"]
    groups = []
    for grade in ["中1", "中2", "中3"]:
        for family in ["school_regular_exam", "unit_or_chapter_test"]:
            groups.append((grade, "数学", family))
    windows = ["m3", "m6", "m12"]
    colors = {"m3": "#2868a8", "m6": "#22845b", "m12": "#b05a28"}
    lookup = {(r["grade_level"], r["course_subject"], r["test_family"], r["window"]): r for r in rows}
    width, height = 1120, 500
    left, right, top, row_h = 350, 1010, 82, 58
    min_x, max_x = -0.10, 0.20

    def xscale(v):
        return left + (v - min_x) / (max_x - min_x) * (right - left)

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        '<text x="24" y="34" font-family="Arial" font-size="20" font-weight="700">Active-Days Mechanism Across Junior-High Mathematics</text>',
        '<text x="24" y="56" font-family="Arial" font-size="12" fill="#555">Student and assessment fixed effects; adjusted for event volume and behavior composition</text>',
    ]
    zero = xscale(0)
    parts.append(f'<line x1="{zero:.1f}" x2="{zero:.1f}" y1="{top-26}" y2="{top+row_h*len(groups)-18}" stroke="#888"/>')
    for i, group in enumerate(groups):
        y = top + i * row_h
        label = f"{group[0]} {group[1]} {group[2]}"
        parts.append(f'<text x="24" y="{y+8}" font-family="Arial" font-size="12" dominant-baseline="middle">{esc(label)}</text>')
        for j, window in enumerate(windows):
            r = lookup.get((*group, window))
            if not r:
                continue
            beta = float(r["beta_std"])
            lo = float(r["ci_low"])
            hi = float(r["ci_high"])
            yy = y + j * 16
            color = colors[window]
            parts.append(f'<line x1="{xscale(lo):.1f}" x2="{xscale(hi):.1f}" y1="{yy}" y2="{yy}" stroke="{color}" stroke-width="3" stroke-linecap="round"/>')
            parts.append(f'<circle cx="{xscale(beta):.1f}" cy="{yy}" r="5" fill="{color}"/>')
            parts.append(f'<text x="{right+12}" y="{yy+1}" font-family="Arial" font-size="10" dominant-baseline="middle" fill="#333">{window} {beta:+.3f}</text>')
    legend_x = 760
    for j, window in enumerate(windows):
        y = 34 + j * 18
        parts.append(f'<circle cx="{legend_x}" cy="{y}" r="5" fill="{colors[window]}"/>')
        parts.append(f'<text x="{legend_x+12}" y="{y+1}" font-family="Arial" font-size="12" dominant-baseline="middle">{window}</text>')
    parts.append(f'<text x="{(left+right)/2:.1f}" y="{height-22}" font-family="Arial" font-size="12" text-anchor="middle" fill="#444">Standardized coefficient for log active days</text>')
    parts.append("</svg>")
    (FIG / "fig13_grade_subject_active_days.svg").write_text("\n".join(parts) + "\n", encoding="utf-8")
    print("Wrote figures/fig13_grade_subject_active_days.svg")


if __name__ == "__main__":
    main()
