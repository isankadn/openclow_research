import base64, csv, io, json, math, statistics, urllib.parse, urllib.request
from pathlib import Path

ROOT = Path('/home/ubuntu/.openclaw/workspace/projects/leaf-db-exploration-2026-03-30')
OUT = ROOT / 'pilot-content-friction-results-saikyo_new'
FIG = OUT / 'figures'
OUT.mkdir(exist_ok=True)
FIG.mkdir(exist_ok=True)

HOST = 'http://10.236.173.4:8123/'
AUTH = base64.b64encode(b'reader:a9847KHJLv2vK').decode()
DATE_WHERE = "timestamp >= toDateTime('2019-01-01 00:00:00') AND timestamp < now() + INTERVAL 1 DAY"


def ch(query: str) -> str:
    req = urllib.request.Request(HOST + '?query=' + urllib.parse.quote(query))
    req.add_header('Authorization', 'Basic ' + AUTH)
    with urllib.request.urlopen(req, timeout=180) as r:
        return r.read().decode('utf-8', 'replace')


def ch_tsv(query: str):
    txt = ch(query + ' FORMAT TSVWithNames')
    return list(csv.DictReader(io.StringIO(txt), delimiter='\t'))


def write_text(path: Path, text: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)


def save_tsv(path: Path, rows):
    if not rows:
        return
    cols = list(rows[0].keys())
    with path.open('w') as f:
        f.write('\t'.join(cols) + '\n')
        for row in rows:
            f.write('\t'.join(str(row.get(c, '')).replace('\t', ' ').replace('\n', ' ') for c in cols) + '\n')


def num(v):
    if v is None or v == '':
        return 0.0
    try:
        if isinstance(v, (int, float)):
            return v
        if any(c in str(v) for c in '.eE'):
            return float(v)
        return int(v)
    except Exception:
        try:
            return float(v)
        except Exception:
            return v


def svg_wrap(width, height, body):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
<style>
text {{ font-family: Arial, sans-serif; fill: #222; }}
.small {{ font-size: 12px; }}
.label {{ font-size: 13px; }}
.title {{ font-size: 18px; font-weight: bold; }}
.axis {{ stroke: #333; stroke-width: 1; }}
.grid {{ stroke: #ddd; stroke-width: 1; }}
</style>
{body}
</svg>'''


def save_svg(name, content):
    write_text(FIG / name, content)


def bar_chart(rows, label_key, value_key, title, filename, width=1200, height=700, topn=15):
    rows = rows[:topn]
    margin = dict(left=260, right=40, top=60, bottom=40)
    plot_w = width - margin['left'] - margin['right']
    plot_h = height - margin['top'] - margin['bottom']
    maxv = max(float(r[value_key]) for r in rows) if rows else 1
    bar_h = plot_h / max(len(rows),1) * 0.7
    gap = plot_h / max(len(rows),1) * 0.3
    body = [f'<text x="{margin["left"]}" y="30" class="title">{title}</text>']
    body.append(f'<line x1="{margin["left"]}" y1="{margin["top"]}" x2="{margin["left"]}" y2="{height-margin["bottom"]}" class="axis"/>')
    for i in range(6):
        x = margin['left'] + plot_w * i / 5
        body.append(f'<line x1="{x}" y1="{margin["top"]}" x2="{x}" y2="{height-margin["bottom"]}" class="grid"/>')
        body.append(f'<text x="{x}" y="{height-10}" class="small" text-anchor="middle">{int(maxv*i/5):,}</text>')
    y = margin['top']
    for r in rows:
        label = str(r[label_key]) or '(blank)'
        val = float(r[value_key])
        w = plot_w * val / maxv if maxv else 0
        body.append(f'<rect x="{margin["left"]}" y="{y}" width="{w}" height="{bar_h}" fill="#4e79a7"/>')
        body.append(f'<text x="{margin["left"]-10}" y="{y+bar_h*0.7}" class="label" text-anchor="end">{label[:42]}</text>')
        body.append(f'<text x="{margin["left"]+w+8}" y="{y+bar_h*0.7}" class="small">{int(val):,}</text>')
        y += bar_h + gap
    save_svg(filename, svg_wrap(width, height, '\n'.join(body)))


def scatterplot(rows, xkey, ykey, title, filename, width=1000, height=800):
    margin = dict(left=80, right=30, top=60, bottom=70)
    plot_w = width - margin['left'] - margin['right']
    plot_h = height - margin['top'] - margin['bottom']
    xs = [max(float(r[xkey]), 1) for r in rows]
    ys = [max(float(r[ykey]), 1) for r in rows]
    lx = [math.log10(x) for x in xs]
    ly = [math.log10(y) for y in ys]
    minx, maxx = min(lx), max(lx)
    miny, maxy = min(ly), max(ly)
    def sx(v): return margin['left'] + (math.log10(max(float(v),1)) - minx) / (maxx-minx or 1) * plot_w
    def sy(v): return height - margin['bottom'] - (math.log10(max(float(v),1)) - miny) / (maxy-miny or 1) * plot_h
    body = [f'<text x="{margin["left"]}" y="30" class="title">{title}</text>']
    body.append(f'<line x1="{margin["left"]}" y1="{margin["top"]}" x2="{margin["left"]}" y2="{height-margin["bottom"]}" class="axis"/>')
    body.append(f'<line x1="{margin["left"]}" y1="{height-margin["bottom"]}" x2="{width-margin["right"]}" y2="{height-margin["bottom"]}" class="axis"/>')
    for i in range(5):
        x = margin['left'] + plot_w*i/4
        y = margin['top'] + plot_h*i/4
        body.append(f'<line x1="{x}" y1="{margin["top"]}" x2="{x}" y2="{height-margin["bottom"]}" class="grid"/>')
        body.append(f'<line x1="{margin["left"]}" y1="{y}" x2="{width-margin["right"]}" y2="{y}" class="grid"/>')
    for r in rows:
        included = float(r[xkey]) >= 30 and float(r[ykey]) >= 300
        color = '#e15759' if included else '#9c9c9c'
        body.append(f'<circle cx="{sx(r[xkey])}" cy="{sy(r[ykey])}" r="4" fill="{color}" fill-opacity="0.65"/>')
    body.append(f'<text x="{width/2}" y="{height-20}" class="label" text-anchor="middle">unique users per content (log scale)</text>')
    body.append(f'<text x="20" y="{height/2}" class="label" transform="rotate(-90 20,{height/2})" text-anchor="middle">unique events per content (log scale)</text>')
    body.append(f'<text x="{width-220}" y="{margin["top"]+20}" class="small" fill="#e15759">red = meets pilot threshold</text>')
    save_svg(filename, svg_wrap(width, height, '\n'.join(body)))


def heatmap(rows, cols, title, filename, width=1500, height=850):
    margin = dict(left=320, right=20, top=120, bottom=20)
    cell_w = (width - margin['left'] - margin['right']) / len(cols)
    cell_h = (height - margin['top'] - margin['bottom']) / len(rows)
    vals = {c:[float(r[c]) for r in rows] for c in cols}
    stats = {c:(min(v), max(v)) for c,v in vals.items()}
    body = [f'<text x="{margin["left"]}" y="30" class="title">{title}</text>']
    for j,c in enumerate(cols):
        x = margin['left'] + j*cell_w + cell_w/2
        body.append(f'<text x="{x}" y="{margin["top"]-20}" class="small" text-anchor="middle" transform="rotate(-35 {x},{margin["top"]-20})">{c}</text>')
    for i,r in enumerate(rows):
        y = margin['top'] + i*cell_h
        body.append(f'<text x="{margin["left"]-10}" y="{y+cell_h*0.65}" class="small" text-anchor="end">{str(r["contents_name"])[:44]}</text>')
        for j,c in enumerate(cols):
            v = float(r[c])
            mn,mx = stats[c]
            t = (v-mn)/((mx-mn) or 1)
            red = int(255*t)
            blue = int(255*(1-t))
            green = 220-int(80*abs(t-0.5)*2)
            x = margin['left'] + j*cell_w
            body.append(f'<rect x="{x}" y="{y}" width="{cell_w-2}" height="{cell_h-2}" fill="rgb({red},{green},{blue})"/>')
            body.append(f'<text x="{x+cell_w/2}" y="{y+cell_h*0.62}" class="small" text-anchor="middle">{v:.2f}</text>')
    save_svg(filename, svg_wrap(width, height, '\n'.join(body)))


def top_contents_bar(rows, title, filename, width=1200, height=700, topn=12):
    rows = rows[:topn]
    margin = dict(left=80, right=20, top=60, bottom=220)
    plot_w = width - margin['left'] - margin['right']
    plot_h = height - margin['top'] - margin['bottom']
    maxv = max(float(r['pilot_friction_score']) for r in rows) if rows else 1
    body = [f'<text x="{margin["left"]}" y="30" class="title">{title}</text>']
    body.append(f'<line x1="{margin["left"]}" y1="{margin["top"]}" x2="{margin["left"]}" y2="{height-margin["bottom"]}" class="axis"/>')
    body.append(f'<line x1="{margin["left"]}" y1="{height-margin["bottom"]}" x2="{width-margin["right"]}" y2="{height-margin["bottom"]}" class="axis"/>')
    bar_w = plot_w / max(len(rows),1) * 0.7
    gap = plot_w / max(len(rows),1) * 0.3
    x = margin['left'] + gap/2
    for r in rows:
        val = float(r['pilot_friction_score'])
        h = plot_h * val / maxv if maxv else 0
        y = height - margin['bottom'] - h
        body.append(f'<rect x="{x}" y="{y}" width="{bar_w}" height="{h}" fill="#f28e2b"/>')
        body.append(f'<text x="{x+bar_w/2}" y="{height-margin["bottom"]+15}" class="small" text-anchor="end" transform="rotate(-55 {x+bar_w/2},{height-margin["bottom"]+15})">{str(r["contents_name"])[:28]}</text>')
        body.append(f'<text x="{x+bar_w/2}" y="{y-5}" class="small" text-anchor="middle">{val:.2f}</text>')
        x += bar_w + gap
    save_svg(filename, svg_wrap(width, height, '\n'.join(body)))


def concentration_plot(content_rows, title, filename, width=1200, height=700):
    # content_rows: list of dicts for one contents_id with user_events desc
    vals = [float(r['user_events']) for r in content_rows if float(r['user_events']) > 0]
    total = sum(vals) or 1
    cum = 0.0
    points = [(0,0)]
    for i,v in enumerate(vals, start=1):
        cum += v
        points.append((i/len(vals), cum/total))
    margin = dict(left=80, right=20, top=60, bottom=70)
    plot_w = width - margin['left'] - margin['right']
    plot_h = height - margin['top'] - margin['bottom']
    def sx(x): return margin['left'] + x*plot_w
    def sy(y): return height - margin['bottom'] - y*plot_h
    poly = ' '.join(f'{sx(x)},{sy(y)}' for x,y in points)
    body = [f'<text x="{margin["left"]}" y="30" class="title">{title}</text>']
    body.append(f'<line x1="{margin["left"]}" y1="{margin["top"]}" x2="{margin["left"]}" y2="{height-margin["bottom"]}" class="axis"/>')
    body.append(f'<line x1="{margin["left"]}" y1="{height-margin["bottom"]}" x2="{width-margin["right"]}" y2="{height-margin["bottom"]}" class="axis"/>')
    body.append(f'<line x1="{margin["left"]}" y1="{height-margin["bottom"]}" x2="{width-margin["right"]}" y2="{margin["top"]}" stroke="#999" stroke-dasharray="5,5"/>')
    body.append(f'<polyline points="{poly}" fill="none" stroke="#59a14f" stroke-width="3"/>')
    body.append(f'<text x="{width/2}" y="{height-20}" class="label" text-anchor="middle">cumulative share of users</text>')
    body.append(f'<text x="20" y="{height/2}" class="label" transform="rotate(-90 20,{height/2})" text-anchor="middle">cumulative share of events</text>')
    save_svg(filename, svg_wrap(width, height, '\n'.join(body)))


def zscores(vals):
    m = statistics.mean(vals)
    s = statistics.pstdev(vals) or 1.0
    return [(v-m)/s for v in vals]


# Q1
q1 = ch_tsv(f"""
SELECT
    count() AS raw_rows,
    uniqExact(_id) AS uniq_record_ids,
    count() - uniqExact(_id) AS duplicate_row_gap,
    min(timestamp) AS min_ts,
    max(timestamp) AS max_ts,
    uniqExact(actor_account_name) AS uniq_users,
    uniqExact(contents_id) AS uniq_contents,
    uniqExact(operation_name) AS uniq_ops,
    countIf(operation_name = '' OR operation_name IS NULL) AS blank_op_rows
FROM saikyo_new.statements_mv
WHERE {DATE_WHERE}
""")
q1 = [{k:num(v) for k,v in q1[0].items()}]
save_tsv(OUT/'q1_dataset_sanity.tsv', [{k:str(v) for k,v in q1[0].items()}])

# Q2
q2 = ch_tsv(f"""
SELECT
    operation_name,
    count() AS rows,
    uniqExact(_id) AS uniq_record_ids,
    uniqExact(actor_account_name) AS uniq_users,
    uniqExact(contents_id) AS uniq_contents
FROM saikyo_new.statements_mv
WHERE {DATE_WHERE}
GROUP BY operation_name
ORDER BY rows DESC
LIMIT 25
""")
for r in q2:
    for k in ['rows','uniq_record_ids','uniq_users','uniq_contents']:
        r[k]=num(r[k])
save_tsv(OUT/'q2_operation_profile.tsv', [{k:str(v) for k,v in r.items()} for r in q2])

# Q3a sample top contents
q3_top = ch_tsv(f"""
SELECT
    contents_id,
    any(contents_name) AS contents_name,
    count() AS raw_events,
    uniqExact(_id) AS uniq_events,
    uniqExact(actor_account_name) AS uniq_users,
    min(timestamp) AS first_ts,
    max(timestamp) AS last_ts
FROM saikyo_new.statements_mv
WHERE {DATE_WHERE}
  AND contents_id != ''
GROUP BY contents_id
ORDER BY uniq_events DESC
LIMIT 200
""")
for r in q3_top:
    for k in ['raw_events','uniq_events','uniq_users']:
        r[k]=num(r[k])
save_tsv(OUT/'q3_top_contents.tsv', [{k:str(v) for k,v in r.items()} for r in q3_top])

# Q3b all contents for scatterplot/threshold summary
q3_all = ch_tsv(f"""
SELECT
    contents_id,
    any(contents_name) AS contents_name,
    uniqExact(_id) AS uniq_events,
    uniqExact(actor_account_name) AS uniq_users
FROM saikyo_new.statements_mv
WHERE {DATE_WHERE}
  AND contents_id != ''
GROUP BY contents_id
""")
for r in q3_all:
    for k in ['uniq_events','uniq_users']:
        r[k]=num(r[k])
save_tsv(OUT/'q3_all_contents.tsv', [{k:str(v) for k,v in r.items()} for r in q3_all[:5000]])

# Q4/Q5 combined features with thresholds
features = ch_tsv(f"""
WITH content_features AS (
    SELECT
        contents_id,
        any(contents_name) AS contents_name,
        uniqExact(_id) AS uniq_events,
        uniqExact(actor_account_name) AS uniq_users,
        countIf(operation_name = 'NEXT') AS n_next,
        countIf(operation_name = 'PREV') AS n_prev,
        countIf(operation_name = 'PAGE_JUMP') AS n_page_jump,
        countIf(operation_name = 'BOOKMARK_JUMP') AS n_bookmark_jump,
        countIf(operation_name IN ('ADD_MEMO','CHANGE_MEMO','ADD_HW_MEMO')) AS n_memo,
        countIf(operation_name IN ('ADD_MARKER','DELETE_MARKER')) AS n_marker,
        countIf(operation_name = 'OPEN_RECOMMENDATION') AS n_open_rec,
        countIf(operation_name = 'CLICK_RECOMMENDATION') AS n_click_rec,
        countIf(operation_name = 'ANSWER_QUIZ') AS n_quiz,
        medianIf(time_from_last_activity, time_from_last_activity IS NOT NULL) AS median_gap
    FROM saikyo_new.statements_mv
    WHERE {DATE_WHERE}
      AND contents_id != ''
    GROUP BY contents_id
    HAVING uniq_users >= 30
       AND uniq_events >= 300
)
SELECT
    contents_id,
    contents_name,
    uniq_events,
    uniq_users,
    round((n_prev + n_page_jump + n_bookmark_jump) / uniq_events, 6) AS nav_instability_rate,
    round(n_memo / uniq_events, 6) AS memo_rate,
    round(n_marker / uniq_events, 6) AS marker_rate,
    round(n_open_rec / uniq_events, 6) AS rec_open_rate,
    round(if(n_open_rec = 0, 0, n_click_rec / n_open_rec), 6) AS rec_click_through_rate,
    round(n_quiz / uniq_events, 6) AS quiz_rate,
    round(median_gap, 3) AS median_gap
FROM content_features
ORDER BY uniq_events DESC
""")
for r in features:
    for k in ['uniq_events','uniq_users','nav_instability_rate','memo_rate','marker_rate','rec_open_rate','rec_click_through_rate','quiz_rate','median_gap']:
        r[k]=num(r[k])

# add z-score-based pilot friction
for metric in ['nav_instability_rate','memo_rate','rec_open_rate','median_gap','rec_click_through_rate']:
    vals = [float(r[metric]) for r in features]
    zs = zscores(vals)
    for r,z in zip(features,zs):
        r[f'z_{metric}']=z
for r in features:
    r['pilot_friction_score'] = (
        r['z_nav_instability_rate'] +
        r['z_memo_rate'] +
        r['z_rec_open_rate'] +
        r['z_median_gap'] -
        r['z_rec_click_through_rate']
    )
features_sorted = sorted(features, key=lambda r: r['pilot_friction_score'], reverse=True)
save_tsv(OUT/'q5_content_features.tsv', [{k:str(v) for k,v in r.items()} for r in features_sorted[:500]])

# Q6 for top 5 contents by pilot score
shortlist = features_sorted[:5]
short_ids = ','.join("'{}'".format(r['contents_id'].replace("'","''")) for r in shortlist)
q6 = ch_tsv(f"""
SELECT
    contents_id,
    actor_account_name,
    uniqExact(_id) AS user_events,
    countIf(operation_name = 'PREV') AS n_prev,
    countIf(operation_name = 'PAGE_JUMP') AS n_page_jump,
    countIf(operation_name IN ('ADD_MEMO','CHANGE_MEMO','ADD_HW_MEMO')) AS n_memo,
    countIf(operation_name = 'OPEN_RECOMMENDATION') AS n_open_rec
FROM saikyo_new.statements_mv
WHERE {DATE_WHERE}
  AND contents_id IN ({short_ids})
GROUP BY contents_id, actor_account_name
ORDER BY contents_id, user_events DESC
""")
for r in q6:
    for k in ['user_events','n_prev','n_page_jump','n_memo','n_open_rec']:
        r[k]=num(r[k])
save_tsv(OUT/'q6_user_concentration.tsv', [{k:str(v) for k,v in r.items()} for r in q6])

# Q7 event summaries for shortlist
q7 = ch_tsv(f"""
SELECT
    contents_id,
    any(contents_name) AS contents_name,
    operation_name,
    count() AS rows,
    uniqExact(actor_account_name) AS uniq_users
FROM saikyo_new.statements_mv
WHERE {DATE_WHERE}
  AND contents_id IN ({short_ids})
GROUP BY contents_id, operation_name
ORDER BY contents_id, rows DESC
""")
for r in q7:
    for k in ['rows','uniq_users']:
        r[k]=num(r[k])
save_tsv(OUT/'q7_shortlist_event_mix.tsv', [{k:str(v) for k,v in r.items()} for r in q7])

# figures
bar_chart(q2, 'operation_name', 'rows', 'Top operation counts after timestamp filtering', 'fig1_operation_mix.svg', topn=15)
scatterplot(q3_all, 'uniq_users', 'uniq_events', 'Content coverage by unique users and unique events', 'fig2_content_coverage.svg')
heat_cols = ['nav_instability_rate','memo_rate','marker_rate','rec_open_rate','rec_click_through_rate','quiz_rate','median_gap','pilot_friction_score']
heatmap(features_sorted[:12], heat_cols, 'Top candidate friction contents: signature heatmap', 'fig3_friction_heatmap.svg')
top_contents_bar(features_sorted[:12], 'Top candidate contents by provisional pilot friction score', 'fig4_top_friction_contents.svg')
for i,content in enumerate(shortlist[:3], start=1):
    rows = [r for r in q6 if r['contents_id'] == content['contents_id']]
    concentration_plot(rows, f'User-event concentration: {content["contents_name"][:50]}', f'fig5_concentration_{i}.svg')

# summary stats
included = [r for r in q3_all if r['uniq_users'] >= 30 and r['uniq_events'] >= 300]
summary = {
    'dataset_sanity': q1[0],
    'n_contents_total': len(q3_all),
    'n_contents_meeting_threshold': len(included),
    'median_users_per_content': statistics.median([r['uniq_users'] for r in q3_all]) if q3_all else 0,
    'median_events_per_content': statistics.median([r['uniq_events'] for r in q3_all]) if q3_all else 0,
    'top_shortlist': [
        {
            'rank': i+1,
            'contents_id': r['contents_id'],
            'contents_name': r['contents_name'],
            'uniq_users': r['uniq_users'],
            'uniq_events': r['uniq_events'],
            'nav_instability_rate': round(r['nav_instability_rate'],4),
            'memo_rate': round(r['memo_rate'],4),
            'marker_rate': round(r['marker_rate'],4),
            'rec_open_rate': round(r['rec_open_rate'],4),
            'rec_click_through_rate': round(r['rec_click_through_rate'],4),
            'quiz_rate': round(r['quiz_rate'],4),
            'median_gap': round(r['median_gap'],2),
            'pilot_friction_score': round(r['pilot_friction_score'],3),
        }
        for i,r in enumerate(shortlist)
    ]
}
write_text(OUT/'summary.json', json.dumps(summary, indent=2, ensure_ascii=False))

# markdown report
report = []
report.append('# Pilot analysis results\n')
report.append('## Scope\n')
report.append('- Database: `saikyo_new.statements_mv`\n- This pass is xAPI-only\n- Timestamp filter: `2019-01-01` onward, excluding obvious older anomalies\n- Content inclusion threshold for the pilot: `uniq_users >= 30` and `uniq_events >= 300`\n')
report.append('## Dataset sanity\n')
report.append(f"- Raw filtered rows: **{q1[0]['raw_rows']:,}**\n")
report.append(f"- Unique `_id`: **{q1[0]['uniq_record_ids']:,}**\n")
report.append(f"- Duplicate row gap (`count - uniqExact(_id)`): **{q1[0]['duplicate_row_gap']:,}**\n")
report.append(f"- Unique users: **{q1[0]['uniq_users']:,}**\n")
report.append(f"- Unique contents: **{q1[0]['uniq_contents']:,}**\n")
report.append(f"- Unique operations: **{q1[0]['uniq_ops']:,}**\n")
report.append(f"- Blank operation rows: **{q1[0]['blank_op_rows']:,}**\n")
report.append(f"- Time range after filter: **{q1[0]['min_ts']}** to **{q1[0]['max_ts']}**\n")
report.append('\n### Figure 1. Operation mix after filtering\n\n![](figures/fig1_operation_mix.svg)\n\nThis chart shows the most frequent operation names after timestamp filtering.\n')
report.append('\n## Content coverage\n')
report.append(f"- Total contents observed: **{len(q3_all):,}**\n")
report.append(f"- Contents meeting pilot threshold: **{len(included):,}**\n")
report.append(f"- Median unique users per content: **{summary['median_users_per_content']:.1f}**\n")
report.append(f"- Median unique events per content: **{summary['median_events_per_content']:.1f}**\n")
report.append('\n### Figure 2. Content coverage by users and events\n\n![](figures/fig2_content_coverage.svg)\n\nRed points meet the pilot inclusion threshold (`uniq_users >= 30` and `uniq_events >= 300`).\n')
report.append('\n## Top candidate friction contents (provisional)\n')
report.append('| Rank | contents_id | contents_name | uniq_users | uniq_events | nav_instability_rate | memo_rate | rec_open_rate | rec_click_through_rate | median_gap | pilot_friction_score |\n')
report.append('|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|\n')
for item in summary['top_shortlist']:
    report.append(f"| {item['rank']} | {item['contents_id']} | {str(item['contents_name']).replace('|','/')} | {item['uniq_users']} | {item['uniq_events']} | {item['nav_instability_rate']:.4f} | {item['memo_rate']:.4f} | {item['rec_open_rate']:.4f} | {item['rec_click_through_rate']:.4f} | {item['median_gap']:.2f} | {item['pilot_friction_score']:.3f} |\n")
report.append('\n### Figure 3. Friction-signature heatmap for top candidate contents\n\n![](figures/fig3_friction_heatmap.svg)\n\nThis heatmap compares the top-ranked contents across the main heuristic features used in the pilot score.\n')
report.append('\n### Figure 4. Top contents by provisional pilot friction score\n\n![](figures/fig4_top_friction_contents.svg)\n\nHigher scores indicate stronger provisional friction signatures under this pilot heuristic.\n')
for i,content in enumerate(shortlist[:3], start=1):
    report.append(f"\n### Figure 5.{i} User concentration check: {content['contents_name']}\n\n![](figures/fig5_concentration_{i}.svg)\n\nThis plot checks whether the signal is broadly distributed across users or dominated by a small number of heavy users.\n")
report.append('\n## Initial interpretation\n')
report.append('- This pilot score is a **heuristic ranking**, not a final scientific friction index.\n')
report.append('- High-ranking contents tend to combine **navigation instability**, **memo activity**, **recommendation exposure**, and **longer median time gaps**.\n')
report.append('- Contents should not be labeled as problematic from a single variable alone. Heavy memo activity may also reflect productive deep engagement.\n')
report.append('- The duplicate gap in `_id` means deduplication must stay part of the workflow.\n')
report.append('- The next interpretation step requires confirmed content→course→subject/grade mapping from relational metadata.\n')
write_text(OUT/'results.md', ''.join(report))

print('Pilot analysis complete for saikyo_new.')
print('Results written to:', OUT/'results.md')
