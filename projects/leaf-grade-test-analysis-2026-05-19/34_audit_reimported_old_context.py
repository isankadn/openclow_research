#!/usr/bin/env python3
import base64
import csv
import io
import os
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "outputs"
REPORTS = ROOT / "reports"
OUT.mkdir(exist_ok=True)
REPORTS.mkdir(exist_ok=True)

CLICKHOUSE_HOST = os.environ.get("CLICKHOUSE_HOST", "http://10.236.173.4:8123/")
CLICKHOUSE_USER = os.environ.get("CLICKHOUSE_USER", "reader")
CLICKHOUSE_PASSWORD = os.environ.get("CLICKHOUSE_PASSWORD", "a9847KHJLv2vK")


def ch(query):
    req = urllib.request.Request(CLICKHOUSE_HOST + "?query=" + urllib.parse.quote(query + " FORMAT TSVWithNames"))
    auth = base64.b64encode(f"{CLICKHOUSE_USER}:{CLICKHOUSE_PASSWORD}".encode()).decode()
    req.add_header("Authorization", "Basic " + auth)
    with urllib.request.urlopen(req, timeout=600) as response:
        return response.read().decode("utf-8", "replace")


def ch_tsv(query):
    return list(csv.DictReader(io.StringIO(ch(query)), delimiter="\t"))


def write_csv(path, rows):
    if not rows:
        return
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def nfmt(value):
    return f"{int(value):,}"


def main():
    coverage = ch_tsv(
        """
        SELECT
          'old_bookroll_content_events_2019_to_2025_04_01' AS scope,
          count() AS rows,
          countIf(notEmpty(context_id)) AS with_context_id,
          countIf(empty(context_id)) AS missing_context_id,
          countIf(notEmpty(context_title)) AS with_context_title,
          countIf(empty(context_title)) AS missing_context_title,
          countIf(notEmpty(context_label)) AS with_context_label,
          countIf(empty(context_label)) AS missing_context_label,
          uniqExact(context_id) AS distinct_context_ids,
          uniqExact(context_title) AS distinct_context_titles,
          uniqExact(context_label) AS distinct_context_labels,
          uniqExact(splitByChar('@', actor_account_name)[1]) AS students,
          uniqExact(contents_id) AS contents
        FROM saikyo_old.statements_mv
        WHERE timestamp >= toDateTime('2019-01-01 00:00:00')
          AND timestamp < toDateTime('2025-04-01 00:00:00')
          AND position(actor_account_homePage, 'bookroll') > 0
          AND notEmpty(operation_name)
          AND notEmpty(contents_id)
        """
    )
    by_year = ch_tsv(
        """
        SELECT
          toString(toYear(timestamp)) AS year,
          count() AS rows,
          countIf(notEmpty(context_id)) AS with_context_id,
          countIf(empty(context_id)) AS missing_context_id,
          uniqExact(context_id) AS distinct_context_ids,
          uniqExact(splitByChar('@', actor_account_name)[1]) AS students,
          uniqExact(contents_id) AS contents
        FROM saikyo_old.statements_mv
        WHERE timestamp >= toDateTime('2019-01-01 00:00:00')
          AND timestamp < toDateTime('2025-04-01 00:00:00')
          AND position(actor_account_homePage, 'bookroll') > 0
          AND notEmpty(operation_name)
          AND notEmpty(contents_id)
        GROUP BY year
        ORDER BY year
        """
    )
    top_contexts = ch_tsv(
        """
        SELECT
          context_id,
          any(context_title) AS context_title,
          any(context_label) AS context_label,
          count() AS rows,
          uniqExact(splitByChar('@', actor_account_name)[1]) AS students,
          uniqExact(contents_id) AS contents
        FROM saikyo_old.statements_mv
        WHERE timestamp >= toDateTime('2019-01-01 00:00:00')
          AND timestamp < toDateTime('2025-04-01 00:00:00')
          AND position(actor_account_homePage, 'bookroll') > 0
          AND notEmpty(operation_name)
          AND notEmpty(contents_id)
          AND notEmpty(context_id)
        GROUP BY context_id
        ORDER BY rows DESC
        LIMIT 50
        """
    )

    write_csv(OUT / "old_reimport_context_coverage.csv", coverage)
    write_csv(OUT / "old_reimport_context_coverage_by_year.csv", by_year)
    write_csv(OUT / "old_reimport_top_contexts.csv", top_contexts)

    report = ["# Reimported Old XAPI Course Context Audit", ""]
    if coverage:
        c = coverage[0]
        rows = int(c["rows"])
        with_context = int(c["with_context_id"])
        missing = int(c["missing_context_id"])
        report.extend(
            [
                "## Overall Coverage",
                f"- Scope: old Bookroll content events from 2019-01-01 through before 2025-04-01, requiring non-empty operation_name and contents_id.",
                f"- Rows audited: {nfmt(rows)}",
                f"- Rows with context_id: {nfmt(with_context)} ({with_context / rows:.2%})",
                f"- Rows missing context_id: {nfmt(missing)} ({missing / rows:.2%})",
                f"- Rows with context_title: {nfmt(c['with_context_title'])}",
                f"- Rows with context_label: {nfmt(c['with_context_label'])}",
                f"- Distinct context_id values: {nfmt(c['distinct_context_ids'])}",
                f"- Distinct students: {nfmt(c['students'])}",
                f"- Distinct contents: {nfmt(c['contents'])}",
                "",
            ]
        )
    report.append("## Coverage By Calendar Year")
    for r in by_year:
        rows = int(r["rows"])
        with_context = int(r["with_context_id"])
        missing = int(r["missing_context_id"])
        report.append(
            f"- {r['year']}: rows={nfmt(rows)}, with_context_id={nfmt(with_context)} ({with_context / rows:.2%}), missing_context_id={nfmt(missing)}, contexts={nfmt(r['distinct_context_ids'])}, students={nfmt(r['students'])}, contents={nfmt(r['contents'])}"
        )
    report.extend(["", "## Top Contexts By Event Count"])
    for r in top_contexts[:20]:
        report.append(
            f"- context_id={r['context_id']}, title={r['context_title'] or r['context_label']}, rows={nfmt(r['rows'])}, students={nfmt(r['students'])}, contents={nfmt(r['contents'])}"
        )

    path = REPORTS / "old_reimport_context_audit.md"
    path.write_text("\n".join(report) + "\n", encoding="utf-8")
    print("\n".join(report))


if __name__ == "__main__":
    main()
