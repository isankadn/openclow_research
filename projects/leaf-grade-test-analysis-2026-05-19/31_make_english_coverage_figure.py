#!/usr/bin/env python3
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "outputs"
PAPER_FIGS = ROOT.parents[1] / "paper_draft" / "figures"
PAPER_FIGS.mkdir(parents=True, exist_ok=True)

GRADE = {
    "中1": "JH1",
    "中2": "JH2",
    "中3": "JH3",
    "高1": "SH1",
    "高2": "SH2",
    "高3": "SH3",
    "(missing)": "Missing",
}
SUBJECT = {
    "数学": "Math",
    "英語": "English",
    "国語": "Japanese",
    "(missing)": "Missing",
}
FAMILY = {
    "school_regular_exam": "regular exam",
    "unit_or_chapter_test": "unit/chapter",
    "external_benesse": "external Benesse",
    "break_after_test": "after-break",
}


def read_csv(path):
    with path.open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


def esc(text):
    return str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def label(row):
    grade = GRADE.get(row["grade_level"], row["grade_level"])
    subject = SUBJECT.get(row["course_subject"], row["course_subject"])
    family = FAMILY.get(row["test_family"], row["test_family"].replace("_", " "))
    return f"{grade} {subject}, {family}"


def main():
    rows = [
        r for r in read_csv(OUT / "candidate_analysis_cells_v2.csv")
        if r["paper_candidate_flag"] == "strong_candidate"
        and r["test_family"] in {"school_regular_exam", "unit_or_chapter_test", "external_benesse"}
    ]
    priority = {"school_regular_exam": 0, "unit_or_chapter_test": 1, "external_benesse": 2}
    rows.sort(key=lambda r: (priority.get(r["test_family"], 9), r["grade_level"], r["course_subject"]))

    width = 1120
    left = 315
    right = 1015
    top = 82
    gap = 38
    height = top + len(rows) * gap + 78
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        "<style>text{font-family:Arial,Helvetica,sans-serif}.title{font-size:20px;font-weight:700}.sub{font-size:12px;fill:#555}.label{font-size:12px;fill:#222}.axis{font-size:11px;fill:#444}.val{font-size:11px;fill:#222}</style>",
        '<rect width="100%" height="100%" fill="white"/>',
        '<text x="24" y="34" class="title">Same-Course Trace Coverage in Candidate Cells</text>',
        '<text x="24" y="56" class="sub">3-month pre-test Bookroll/xAPI coverage; labels are translated to avoid font-dependent rendering</text>',
    ]
    for tick in [0, 0.25, 0.5, 0.75, 1.0]:
        x = left + (right - left) * tick
        parts.append(f'<line x1="{x:.1f}" y1="70" x2="{x:.1f}" y2="{height-44}" stroke="#e6e6e6"/>')
        parts.append(f'<text x="{x:.1f}" y="{height-20}" class="axis" text-anchor="middle">{int(tick*100)}%</text>')
    for i, row in enumerate(rows):
        y = top + i * gap
        rate = float(row["m3_rate"])
        bar_w = (right - left) * rate
        color = "#2E7D32" if row["test_family"] in {"school_regular_exam", "unit_or_chapter_test"} else "#607D8B"
        parts.append(f'<text x="{left-12}" y="{y+5}" class="label" text-anchor="end">{esc(label(row))}</text>')
        parts.append(f'<rect x="{left}" y="{y-12}" width="{bar_w:.1f}" height="18" fill="{color}" opacity="0.85"/>')
        parts.append(f'<text x="{left+bar_w+8:.1f}" y="{y+3}" class="val">{rate:.0%}</text>')
    parts.append(f'<text x="{(left+right)/2:.1f}" y="{height-4}" class="axis" text-anchor="middle">Rows with same-course pre-test trace activity</text>')
    parts.append("</svg>")
    (PAPER_FIGS / "Figure1_same_course_coverage_candidate_cells.svg").write_text("\n".join(parts) + "\n", encoding="utf-8")
    print(PAPER_FIGS / "Figure1_same_course_coverage_candidate_cells.svg")


if __name__ == "__main__":
    main()
