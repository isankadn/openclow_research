#!/usr/bin/env python3
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent
WORKSPACE = ROOT.parents[1]
PAPER = WORKSPACE / "paper_draft"
TABLES = PAPER / "tables"
TABLES.mkdir(parents=True, exist_ok=True)


def read_csv(path):
    with path.open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


def md_table(headers, rows):
    out = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
    out.extend("| " + " | ".join(str(cell) for cell in row) + " |" for row in rows)
    return "\n".join(out) + "\n"


def fnum(x, digits=3):
    return f"{float(x):+.{digits}f}"


def nfmt(x):
    return f"{int(float(x)):,}"


def ci(row):
    return f"[{fnum(row['ci_low'])}, {fnum(row['ci_high'])}]"


def main():
    family = read_csv(ROOT / "outputs" / "family_specific_active_days_twfe_v1.csv")
    fam_rows = []
    for fam in ["school_regular_exam", "unit_or_chapter_test", "external_benesse"]:
        for win in ["m3", "m6", "m12"]:
            rows = [
                r for r in family
                if r["test_family"] == fam
                and r["window"] == win
                and r["model"] == "adjusted_behavior_twfe"
                and r["feature"] == "log_active_days"
            ]
            if not rows:
                continue
            r = rows[0]
            fam_rows.append([
                fam,
                win,
                fnum(r["beta_std"]),
                ci(r),
                f"{float(r['p_cluster']):.3f}",
                nfmt(r["identified_rows"]),
                nfmt(r["students"]),
                nfmt(r["assessments"]),
            ])
    (TABLES / "table1_family_active_days.md").write_text(
        md_table(["Assessment family", "Window", "Active-days beta", "95% CI", "p", "Rows", "Students", "Assessments"], fam_rows),
        encoding="utf-8",
    )

    strategy = read_csv(ROOT / "outputs" / "strategy_feature_adjusted_twfe_v1.csv")
    strategy_rows = []
    for label in [
        "distributed_navigation",
        "distributed_sustained",
        "late_intensive",
        "intermittent_activity",
        "early_declining",
        "single_month_activity",
    ]:
        total = [r for r in strategy if r["model"] == "strategy_total_twfe" and r["feature"] == "strategy_" + label][0]
        adjusted = [r for r in strategy if r["model"] == "strategy_adjusted_for_behavior_twfe" and r["feature"] == "strategy_" + label][0]
        strategy_rows.append([
            label,
            fnum(total["beta_std"]),
            ci(total),
            fnum(adjusted["beta_std"]),
            ci(adjusted),
        ])
    (TABLES / "table2_strategy_adjustment.md").write_text(
        md_table(["Temporal strategy", "Total beta", "Total 95% CI", "Adjusted beta", "Adjusted 95% CI"], strategy_rows),
        encoding="utf-8",
    )

    placebo = read_csv(ROOT / "outputs" / "future_activity_placebo_v1.csv")
    placebo_rows = []
    for fam in ["school_regular_exam", "unit_or_chapter_test"]:
        for wt in ["pre_m3", "future_m3_placebo"]:
            r = [x for x in placebo if x["test_family"] == fam and x["window_type"] == wt and x["feature"] == "log_active_days"][0]
            placebo_rows.append([
                fam,
                wt,
                fnum(r["beta_std"]),
                ci(r),
                f"{float(r['p_cluster']):.3f}",
                nfmt(r["identified_rows"]),
                nfmt(r["students"]),
                nfmt(r["assessments"]),
            ])
    (TABLES / "table3_future_placebo.md").write_text(
        md_table(["Assessment family", "Window", "Active-days beta", "95% CI", "p", "Rows", "Students", "Assessments"], placebo_rows),
        encoding="utf-8",
    )

    grade = read_csv(ROOT / "outputs" / "grade_subject_active_days_consistency_v1.csv")
    grade_rows = []
    for r in grade:
        if r["status"] != "estimated":
            continue
        if r["window"] != "m12":
            continue
        grade_rows.append([
            f"{r['grade_level']} {r['course_subject']}",
            r["test_family"],
            fnum(r["beta_std"]),
            ci(r),
            f"{float(r['p_cluster']):.3f}",
        ])
    (TABLES / "supp_table_grade_consistency_m12.md").write_text(
        md_table(["Cell", "Assessment family", "m12 beta", "95% CI", "p"], grade_rows),
        encoding="utf-8",
    )

    print("Wrote paper tables to", TABLES)


if __name__ == "__main__":
    main()
