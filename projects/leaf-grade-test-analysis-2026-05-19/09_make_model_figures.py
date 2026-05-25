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
    return (
        str(text)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def feature_label(name):
    labels = {
        "log_events_m3": "Event volume",
        "log_active_days_m3": "Active days",
        "navigation_rate_m3": "Navigation share",
        "memo_rate_m3": "Memo share",
        "marker_rate_m3": "Marker share",
        "content_session_rate_m3": "Open/close share",
    }
    return labels.get(name, name)


def global_forest():
    rows = read_csv(OUT / "model_global_fixed_effects_v1.csv")
    width, height = 920, 430
    left, right, top, row_h = 230, 850, 70, 46
    min_x, max_x = -0.18, 0.22

    def xscale(v):
        return left + (v - min_x) / (max_x - min_x) * (right - left)

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        '<text x="24" y="34" font-family="Arial" font-size="20" font-weight="700">Assessment-Fixed-Effects Model: Global Standardized Effects</text>',
        '<text x="24" y="56" font-family="Arial" font-size="12" fill="#555">Outcome: normalized score residual; predictors: 3-month same-course BookRoll behavior residuals; intervals: student-cluster bootstrap</text>',
    ]
    zero = xscale(0)
    parts.append(f'<line x1="{zero:.1f}" x2="{zero:.1f}" y1="{top-18}" y2="{top + row_h * len(rows) + 8}" stroke="#888" stroke-width="1"/>')
    for tick in [-0.15, -0.10, -0.05, 0, 0.05, 0.10, 0.15, 0.20]:
        x = xscale(tick)
        parts.append(f'<line x1="{x:.1f}" x2="{x:.1f}" y1="{top + row_h * len(rows) + 8}" y2="{top + row_h * len(rows) + 14}" stroke="#777"/>')
        parts.append(f'<text x="{x:.1f}" y="{top + row_h * len(rows) + 30}" font-family="Arial" font-size="11" text-anchor="middle" fill="#444">{tick:+.2f}</text>')
    for i, row in enumerate(rows):
        y = top + i * row_h
        beta = float(row["beta_std"])
        lo = float(row["ci_low"])
        hi = float(row["ci_high"])
        color = "#1f7a4d" if lo > 0 else ("#9b2c2c" if hi < 0 else "#666666")
        parts.append(f'<text x="24" y="{y+5}" font-family="Arial" font-size="13" dominant-baseline="middle">{esc(feature_label(row["feature"]))}</text>')
        parts.append(f'<line x1="{xscale(lo):.1f}" x2="{xscale(hi):.1f}" y1="{y+5}" y2="{y+5}" stroke="{color}" stroke-width="3" stroke-linecap="round"/>')
        parts.append(f'<circle cx="{xscale(beta):.1f}" cy="{y+5}" r="6" fill="{color}"/>')
        parts.append(f'<text x="{right+15}" y="{y+5}" font-family="Arial" font-size="12" dominant-baseline="middle" fill="#333">{beta:+.3f}</text>')
    parts.append(f'<text x="{(left+right)/2:.1f}" y="{height-18}" font-family="Arial" font-size="12" text-anchor="middle" fill="#444">Standardized coefficient</text>')
    parts.append("</svg>")
    (FIG / "fig5_global_model_effects.svg").write_text("\n".join(parts) + "\n", encoding="utf-8")


def cell_top_effects():
    rows = read_csv(OUT / "model_cell_fixed_effects_v1.csv")
    rows = sorted(rows, key=lambda r: abs(float(r["beta_std"])), reverse=True)[:15]
    width, height = 1100, 660
    left, right, top, row_h = 420, 1010, 80, 36
    min_x, max_x = -0.26, 0.36

    def xscale(v):
        return left + (v - min_x) / (max_x - min_x) * (right - left)

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        '<text x="24" y="34" font-family="Arial" font-size="20" font-weight="700">Largest Strong-Cell Behavior Signals</text>',
        '<text x="24" y="56" font-family="Arial" font-size="12" fill="#555">Univariate standardized effects with assessment fixed effects; intervals use student-cluster bootstrap</text>',
    ]
    zero = xscale(0)
    parts.append(f'<line x1="{zero:.1f}" x2="{zero:.1f}" y1="{top-18}" y2="{top + row_h * len(rows) + 8}" stroke="#888" stroke-width="1"/>')
    for tick in [-0.2, -0.1, 0, 0.1, 0.2, 0.3]:
        x = xscale(tick)
        parts.append(f'<line x1="{x:.1f}" x2="{x:.1f}" y1="{top + row_h * len(rows) + 8}" y2="{top + row_h * len(rows) + 14}" stroke="#777"/>')
        parts.append(f'<text x="{x:.1f}" y="{top + row_h * len(rows) + 30}" font-family="Arial" font-size="11" text-anchor="middle" fill="#444">{tick:+.1f}</text>')
    for i, row in enumerate(rows):
        y = top + i * row_h
        beta = float(row["beta_std"])
        lo = float(row["ci_low"])
        hi = float(row["ci_high"])
        color = "#1f7a4d" if lo > 0 else ("#9b2c2c" if hi < 0 else "#666666")
        label = f'{row["grade_level"]} {row["course_subject"]} {row["test_family"]} / {feature_label(row["feature"])}'
        parts.append(f'<text x="24" y="{y+5}" font-family="Arial" font-size="12" dominant-baseline="middle">{esc(label)}</text>')
        parts.append(f'<line x1="{xscale(lo):.1f}" x2="{xscale(hi):.1f}" y1="{y+5}" y2="{y+5}" stroke="{color}" stroke-width="3" stroke-linecap="round"/>')
        parts.append(f'<circle cx="{xscale(beta):.1f}" cy="{y+5}" r="5" fill="{color}"/>')
        parts.append(f'<text x="{right+14}" y="{y+5}" font-family="Arial" font-size="11" dominant-baseline="middle" fill="#333">{beta:+.3f}</text>')
    parts.append(f'<text x="{(left+right)/2:.1f}" y="{height-32}" font-family="Arial" font-size="12" text-anchor="middle" fill="#444">Standardized coefficient</text>')
    parts.append("</svg>")
    (FIG / "fig6_top_cell_effects.svg").write_text("\n".join(parts) + "\n", encoding="utf-8")


def main():
    global_forest()
    cell_top_effects()
    print("Wrote fig5_global_model_effects.svg and fig6_top_cell_effects.svg")


if __name__ == "__main__":
    main()
