#!/usr/bin/env python3
import base64
import csv
import io
import urllib.parse
import urllib.request
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "outputs"
DETAIL = OUT / "tests_2025_2026_detail.csv"

HOST = "http://10.236.173.4:8123/"
AUTH = base64.b64encode(b"reader:a9847KHJLv2vK").decode()


def ch(query):
    req = urllib.request.Request(HOST + "?query=" + urllib.parse.quote(query))
    req.add_header("Authorization", "Basic " + AUTH)
    with urllib.request.urlopen(req, timeout=180) as response:
        return response.read().decode("utf-8", "replace")


def ch_tsv(query):
    return list(csv.DictReader(io.StringIO(ch(query + " FORMAT TSVWithNames")), delimiter="\t"))


def quote_list(values):
    return ",".join("'" + str(v).replace("'", "\\'") + "'" for v in values)


def write_csv(path, fieldnames, rows):
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main():
    score_rows = list(csv.DictReader(DETAIL.open(encoding="utf-8")))
    course_ids = sorted({row["course_id"] for row in score_rows}, key=lambda v: int(v))
    course_meta = {}
    score_students_by_course = defaultdict(set)
    tests_by_course = defaultdict(set)
    score_rows_by_course = defaultdict(int)
    for row in score_rows:
        cid = row["course_id"]
        course_meta[cid] = {
            "course_id": cid,
            "course_name": row["course_name"],
            "grade_level": row["grade_level"],
            "subject": row["subject"],
        }
        score_students_by_course[cid].add(row["student_id"])
        tests_by_course[cid].add(row["test_name"])
        score_rows_by_course[cid] += int(row["score_rows"])

    ids = quote_list(course_ids)
    base_where = f"""
      context_id IN ({ids})
      AND timestamp >= toDateTime('2024-04-01 00:00:00')
      AND timestamp < toDateTime('2025-03-06 00:00:00')
      AND actor_name_role = 'student'
    """
    xapi_by_course = ch_tsv(
        f"""
        SELECT
          context_id AS course_id,
          any(context_title) AS context_title,
          count() AS xapi_events,
          uniqExact(actor_account_name) AS xapi_actor_accounts,
          uniqExact(splitByChar('@', actor_account_name)[1]) AS xapi_actor_prefixes,
          uniqExact(contents_id) AS contents,
          uniqExact(operation_name) AS operations,
          min(timestamp) AS first_xapi,
          max(timestamp) AS last_xapi
        FROM saikyo_new.statements_mv
        WHERE {base_where}
        GROUP BY context_id
        ORDER BY xapi_events DESC
        """
    )
    xapi_lookup = {row["course_id"]: row for row in xapi_by_course}

    actors_by_course = ch_tsv(
        f"""
        SELECT
          context_id AS course_id,
          splitByChar('@', actor_account_name)[1] AS actor_prefix,
          count() AS xapi_events
        FROM saikyo_new.statements_mv
        WHERE {base_where}
        GROUP BY context_id, actor_prefix
        """
    )
    xapi_students_by_course = defaultdict(set)
    for row in actors_by_course:
        if row["actor_prefix"]:
            xapi_students_by_course[row["course_id"]].add(row["actor_prefix"])

    op_by_course = ch_tsv(
        f"""
        SELECT
          context_id AS course_id,
          operation_name,
          count() AS xapi_events
        FROM saikyo_new.statements_mv
        WHERE {base_where}
        GROUP BY context_id, operation_name
        ORDER BY course_id, xapi_events DESC
        """
    )
    write_csv(OUT / "xapi_2025_relevant_operations_by_course.csv", ["course_id", "operation_name", "xapi_events"], op_by_course)

    course_rows = []
    for cid in course_ids:
        meta = course_meta[cid]
        xapi = xapi_lookup.get(cid, {})
        score_students = score_students_by_course[cid]
        xapi_students = xapi_students_by_course[cid]
        overlap = score_students & xapi_students
        course_rows.append(
            {
                **meta,
                "score_rows": score_rows_by_course[cid],
                "score_students": len(score_students),
                "score_tests": len(tests_by_course[cid]),
                "xapi_events": int(xapi.get("xapi_events") or 0),
                "xapi_students": len(xapi_students),
                "student_id_overlap": len(overlap),
                "student_overlap_rate_of_score_students": round(len(overlap) / len(score_students), 4) if score_students else 0,
                "contents": int(xapi.get("contents") or 0),
                "operations": int(xapi.get("operations") or 0),
                "first_xapi": xapi.get("first_xapi", ""),
                "last_xapi": xapi.get("last_xapi", ""),
            }
        )
    write_csv(
        OUT / "xapi_2025_relevant_by_course.csv",
        [
            "course_id",
            "course_name",
            "grade_level",
            "subject",
            "score_rows",
            "score_students",
            "score_tests",
            "xapi_events",
            "xapi_students",
            "student_id_overlap",
            "student_overlap_rate_of_score_students",
            "contents",
            "operations",
            "first_xapi",
            "last_xapi",
        ],
        course_rows,
    )

    def agg_by(keys):
        buckets = defaultdict(lambda: defaultdict(int))
        for row in course_rows:
            key = tuple(row[k] or "(unclassified)" for k in keys)
            b = buckets[key]
            b["courses"] += 1
            b["score_rows"] += row["score_rows"]
            b["score_students_course_sum"] += row["score_students"]
            b["score_tests_course_sum"] += row["score_tests"]
            b["xapi_events"] += row["xapi_events"]
            b["xapi_students_course_sum"] += row["xapi_students"]
            b["student_overlap_course_sum"] += row["student_id_overlap"]
            b["contents_course_sum"] += row["contents"]
            b["operations_course_sum"] += row["operations"]
        out = []
        for key, b in buckets.items():
            out.append({**{keys[i]: key[i] for i in range(len(keys))}, **b})
        return sorted(out, key=lambda r: (-r["xapi_events"], -r["score_rows"], tuple(r[k] for k in keys)))

    grade_subject = agg_by(["grade_level", "subject"])
    write_csv(
        OUT / "xapi_2025_relevant_by_grade_subject.csv",
        [
            "grade_level",
            "subject",
            "courses",
            "score_rows",
            "score_students_course_sum",
            "score_tests_course_sum",
            "xapi_events",
            "xapi_students_course_sum",
            "student_overlap_course_sum",
            "contents_course_sum",
            "operations_course_sum",
        ],
        grade_subject,
    )

    covered_courses = [row for row in course_rows if row["xapi_events"] > 0]
    overlap_courses = [row for row in course_rows if row["student_id_overlap"] > 0]
    enough_sequence_courses = [row for row in course_rows if row["xapi_events"] >= 1000 and row["xapi_students"] >= 30]
    enough_outcome_courses = [row for row in course_rows if row["student_id_overlap"] >= 30 and row["score_tests"] >= 1]

    report = []
    report.append("# 2025 Score-To-XAPI Sufficiency Check")
    report.append("")
    report.append("## Scope")
    report.append("- Score/test window: test conduct dates in 2025 and 2026, currently 2025 only.")
    report.append("- XAPI window checked: 2024-04-01 through 2025-03-05, matching the school-year lead-up to the 2025 tests.")
    report.append("- XAPI source: saikyo_new.statements_mv.")
    report.append("- Course link: score course_id equals xAPI context_id.")
    report.append("- Student link tested: score student_id equals xAPI actor_account_name prefix before @.")
    report.append("")
    report.append("## Overall")
    report.append(f"- Score courses in recent-test set: {len(course_rows)}")
    report.append(f"- Courses with any matching xAPI: {len(covered_courses)}")
    report.append(f"- Courses with any score-student/xAPI-actor overlap: {len(overlap_courses)}")
    report.append(f"- Courses meeting basic sequence-analysis threshold (>=1000 xAPI events and >=30 xAPI students): {len(enough_sequence_courses)}")
    report.append(f"- Courses meeting basic outcome-link threshold (>=30 overlapping students): {len(enough_outcome_courses)}")
    report.append(f"- Total xAPI events on matching courses: {sum(row['xapi_events'] for row in course_rows):,}")
    report.append(f"- Total overlapping course-student links: {sum(row['student_id_overlap'] for row in course_rows):,}")
    report.append("")
    report.append("## By Grade And Subject")
    for row in grade_subject:
        report.append(
            f"- {row['grade_level']} {row['subject']}: {row['courses']} courses, "
            f"{row['score_rows']:,} score rows, {row['xapi_events']:,} xAPI events, "
            f"{row['xapi_students_course_sum']:,} xAPI course-student counts, "
            f"{row['student_overlap_course_sum']:,} overlapping course-student links"
        )
    report.append("")
    report.append("## Top XAPI-Covered Courses")
    for row in sorted(course_rows, key=lambda r: -r["xapi_events"])[:15]:
        report.append(
            f"- {row['course_id']} {row['course_name']}: {row['xapi_events']:,} xAPI events, "
            f"{row['xapi_students']} xAPI students, {row['student_id_overlap']} overlapping score students, "
            f"{row['score_rows']} score rows, {row['score_tests']} tests"
        )
    report.append("")
    report.append("## Sufficiency Interpretation")
    if enough_outcome_courses:
        report.append("- Outcome-linked modeling is possible for the covered subset, but should be restricted to courses/cells with confirmed student overlap.")
    else:
        report.append("- Outcome-linked modeling is not yet safe because confirmed student overlap is too small.")
    report.append("- Descriptive behavior mapping and sequence/pattern discovery are possible for xAPI-covered courses with enough events/students.")
    report.append("- Mixed-effects modeling across all K-12 courses is not justified unless many grade/subject cells show confirmed score-xAPI student overlap.")
    report.append("- The paper should report this as a deliberately scoped recent-course subset, not as full K-12 coverage.")
    (OUT / "xapi_2025_sufficiency_report.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    print("\n".join(report))


if __name__ == "__main__":
    main()
