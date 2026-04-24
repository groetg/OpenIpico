#!/usr/bin/env python3
"""
OpenIpico — HTML Results Page Generator

Reads a QuickExport.csv (iPicoWiz format) and generates a styled HTML
results page in the MyLaps style.

Usage:
    python3 results_page.py QuickExport.csv [--output results.html]

The CSV should use semicolon delimiter and contain the standard iPicoWiz
QuickExport columns.
"""

import csv
import argparse
from datetime import datetime


def parse_time(time_str):
    """Parse HH:MM:SS time string to total seconds."""
    if not time_str or time_str.strip() == '' or time_str == '-:--':
        return None
    try:
        parts = time_str.strip().split(':')
        if len(parts) == 3:
            return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
        return None
    except (ValueError, TypeError):
        return None


def format_time(seconds):
    """Format seconds to HH:MM:SS."""
    if seconds is None:
        return '-:--'
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    if h > 0:
        return f"{h:02d}:{m:02d}:{s:02d}"
    return f"{m:02d}:{s:02d}"


def load_csv(filepath):
    """Load QuickExport.csv."""
    athletes = []
    with open(filepath, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f, delimiter=';')
        for row in reader:
            athletes.append(row)
    return athletes


def compute_rankings(athletes):
    """Compute per-segment rankings for each athlete."""
    # Build lists for each segment
    segments = {
        'swim': [],
        't1': [],
        'bike': [],
        't2': [],
        'run': [],
        'total': []
    }

    for a in athletes:
        # Skip DNS/DNF
        if a.get('Pl', '') in ('DNS', 'DNF', 'DSQ', ''):
            continue

        # Compute swim time = Start time (time to first mat from gun)
        swim = parse_time(a.get('Start', ''))
        t1 = parse_time(a.get('T1', ''))
        bike = parse_time(a.get('Bike', ''))
        t2 = parse_time(a.get('T2', ''))
        run = parse_time(a.get('Finish', ''))
        total = parse_time(a.get('Result', ''))

        if swim is not None:
            segments['swim'].append((a['Bib'], swim))
        if t1 is not None:
            segments['t1'].append((a['Bib'], t1))
        if bike is not None:
            segments['bike'].append((a['Bib'], bike))
        if t2 is not None:
            segments['t2'].append((a['Bib'], t2))
        if run is not None:
            segments['run'].append((a['Bib'], run))
        if total is not None:
            segments['total'].append((a['Bib'], total))

    # Sort and assign ranks
    ranks = {}
    for seg, items in segments.items():
        items_sorted = sorted(items, key=lambda x: x[1])
        for rank, (bib, _) in enumerate(items_sorted, 1):
            if bib not in ranks:
                ranks[bib] = {}
            ranks[bib][seg] = rank

    return ranks


def get_event_name(athletes):
    """Try to derive event name from data."""
    # Look for distance info to infer event type
    distances = set()
    for a in athletes:
        d = a.get('Distance', '')
        if d:
            distances.add(d)
    return ', '.join(sorted(distances)) if distances else 'Triatlon'


def generate_html(athletes, event_name='', output_file='results.html'):
    """Generate the HTML results page."""
    bib_rank = compute_rankings(athletes)

    # Categorize athletes
    overall = []
    dns = []
    dnf = []
    categories = {}

    for a in athletes:
        bib = a.get('Bib', '')
        pos = a.get('Pl', '')

        if pos in ('DNS', ''):
            name = a.get('Name', '')
            if name and pos == 'DNS':
                dns.append(a)
            continue

        if pos in ('DNF', 'DSQ'):
            dnf.append(a)
            continue

        cat = a.get('Category', 'Overig')
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(a)
        overall.append(a)

    # Sort overall by position
    overall.sort(key=lambda x: int(x.get('Pl', 999)) if x.get('Pl', '').isdigit() else 999)

    html = f"""<!DOCTYPE html>
<html lang="nl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{event_name} | Uitslag</title>
<style>
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{
    font-family: Verdana, Arial, Helvetica, sans-serif;
    font-size: 9pt;
    background: #f5f5f5;
    padding: 20px;
}}
.container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }}
h1 {{ text-align: center; font-size: 18pt; margin-bottom: 5px; }}
h2 {{ text-align: center; font-size: 12pt; color: #666; margin-bottom: 20px; }}
h3 {{ font-size: 11pt; margin: 20px 0 10px 0; border-bottom: 1px solid #ccc; padding-bottom: 5px; }}
select {{ padding: 5px; margin: 10px 0; }}
input[type="text"] {{ padding: 5px; width: 200px; }}
.filter-bar {{ text-align: center; margin-bottom: 20px; }}
.filter-bar select, .filter-bar input {{ margin: 0 5px; }}
table {{ width: 100%; border-collapse: collapse; margin-bottom: 30px; }}
th {{
    background: #555;
    color: white;
    padding: 6px 8px;
    text-align: left;
    font-size: 8pt;
    white-space: nowrap;
}}
td {{
    padding: 5px 8px;
    font-size: 8pt;
    border-bottom: 1px solid #eee;
}}
tr:nth-child(odd) td {{ background: #fff; }}
tr:nth-child(even) td {{ background: #f8f8f8; }}
tr:hover td {{ background: #e8f4ff; }}
.pos {{ font-weight: bold; width: 30px; }}
.bib {{ width: 35px; }}
.name {{ font-weight: bold; min-width: 120px; }}
.club {{ min-width: 100px; color: #555; }}
.time {{ text-align: right; font-family: monospace; white-space: nowrap; }}
.rank {{ color: #888; font-size: 7pt; text-align: center; width: 20px; }}
.cat-header {{ background: #ddd; font-weight: bold; }}
.cat-section {{ margin-bottom: 10px; }}
.dns-table td {{ color: #aaa; font-style: italic; }}
.footer {{ text-align: center; font-size: 7pt; color: #999; margin-top: 30px; }}
.hidden {{ display: none; }}
</style>
<script>
// Simple filter by category
function filterCategory() {{
    var cat = document.getElementById('catFilter').value;
    var search = document.getElementById('searchInput').value.toLowerCase();
    var rows = document.querySelectorAll('tbody tr.data-row');
    rows.forEach(function(row) {{
        var rowCat = row.getAttribute('data-category') || '';
        var rowText = row.textContent.toLowerCase();
        var show = true;
        if (cat && cat !== 'all' && rowCat !== cat) show = false;
        if (search && !rowText.includes(search)) show = false;
        row.style.display = show ? '' : 'none';
    }});
}}
</script>
</head>
<body>
<div class="container">
<h1>{event_name}</h1>
<h2>Gegenereerd: {datetime.now().strftime('%d-%m-%Y %H:%M')}</h2>

<div class="filter-bar">
<select id="catFilter" onchange="filterCategory()">
<option value="all">Alle categorieën</option>
"""

    # Add category options
    for cat in sorted(categories.keys()):
        html += f'<option value="{cat}">{cat}</option>\n'

    html += """</select>
<input type="text" id="searchInput" placeholder="Zoeken op naam, bib of club..." onkeyup="filterCategory()">
</div>
"""

    # Overall table
    html += '<h3>Overall — Totaal</h3>\n'
    html += '<table>\n<thead><tr>'
    headers = ['Pos', 'Bib', 'Naam', 'Club/Cat', 'Zwem', '#Z', 'Fiets', '#F', 'NaFiets', '#NF', 'Loop', '#L', 'Totaal']
    for h in headers:
        html += f'<th>{h}</th>\n'
    html += '</tr></thead><tbody>\n'

    for i, a in enumerate(overall):
        bib = a.get('Bib', '')
        r = bib_rank.get(bib, {})
        row_class = 'even' if i % 2 == 0 else 'odd'
        cat = a.get('Category', '')

        html += f'<tr class="data-row" data-category="{cat}">\n'
        html += f'<td class="pos">{a.get("Pl","")}</td>\n'
        html += f'<td class="bib">{bib}</td>\n'
        html += f'<td class="name">{a.get("Name","")}</td>\n'
        html += f'<td class="club">{a.get("Affiliation","")}</td>\n'
        html += f'<td class="time">{a.get("Start","")}</td>\n'
        html += f'<td class="rank">{r.get("swim","")}</td>\n'
        html += f'<td class="time">{a.get("Bike","")}</td>\n'
        html += f'<td class="rank">{r.get("bike","")}</td>\n'
        # NaFiets = T2
        html += f'<td class="time">{a.get("T2","")}</td>\n'
        html += f'<td class="rank">{r.get("t2","")}</td>\n'
        html += f'<td class="time">{a.get("Finish","")}</td>\n'
        html += f'<td class="rank">{r.get("run","")}</td>\n'
        html += f'<td class="time"><b>{a.get("Result","")}</b></td>\n'
        html += '</tr>\n'

    html += '</tbody></table>\n'

    # Category sections
    for cat in sorted(categories.keys()):
        cat_athletes = sorted(categories[cat], key=lambda x: int(x.get('Pl', 999)) if x.get('Pl', '').isdigit() else 999)
        html += f'<h3>Categorie: {cat}</h3>\n'
        html += '<table>\n<thead><tr>'
        for h in headers:
            html += f'<th>{h}</th>\n'
        html += '</tr></thead><tbody>\n'
        for i, a in enumerate(cat_athletes):
            bib = a.get('Bib', '')
            r = bib_rank.get(bib, {})
            row_class = 'even' if i % 2 == 0 else 'odd'
            html += f'<tr class="data-row" data-category="{cat}">\n'
            html += f'<td class="pos">{a.get("Pl","")}</td>\n'
            html += f'<td class="bib">{bib}</td>\n'
            html += f'<td class="name">{a.get("Name","")}</td>\n'
            html += f'<td class="club">{a.get("Affiliation","")}</td>\n'
            html += f'<td class="time">{a.get("Start","")}</td>\n'
            html += f'<td class="rank">{r.get("swim","")}</td>\n'
            html += f'<td class="time">{a.get("Bike","")}</td>\n'
            html += f'<td class="rank">{r.get("bike","")}</td>\n'
            html += f'<td class="time">{a.get("T2","")}</td>\n'
            html += f'<td class="rank">{r.get("t2","")}</td>\n'
            html += f'<td class="time">{a.get("Finish","")}</td>\n'
            html += f'<td class="rank">{r.get("run","")}</td>\n'
            html += f'<td class="time"><b>{a.get("Result","")}</b></td>\n'
            html += '</tr>\n'
        html += '</tbody></table>\n'

    # DNS section
    if dns:
        html += '<h3>Niet Gestart (DNS)</h3>\n'
        html += '<table class="dns-table"><thead><tr>'
        for h in ['Bib', 'Naam', 'Club', 'Categorie']:
            html += f'<th>{h}</th>\n'
        html += '</tr></thead><tbody>\n'
        for a in dns:
            html += '<tr>'
            html += f'<td>{a.get("Bib","")}</td>'
            html += f'<td>{a.get("Name","")}</td>'
            html += f'<td>{a.get("Affiliation","")}</td>'
            html += f'<td>{a.get("Category","")}</td>'
            html += '</tr>\n'
        html += '</tbody></table>\n'

    html += f'''
<div class="footer">
<p>Powered by OpenIpico — Open source timing software voor IPICO Sports timing readers</p>
<p>Bekijk ook: groetg.github.io/OpenIpico</p>
</div>
</div>
</body>
</html>'''

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"✓ Results written to {output_file}")


def main():
    parser = argparse.ArgumentParser(description='Generate HTML results from QuickExport.csv')
    parser.add_argument('csv', help='Path to QuickExport.csv')
    parser.add_argument('--output', '-o', default='results.html', help='Output HTML file')
    args = parser.parse_args()

    print(f"Loading {args.csv}...")
    athletes = load_csv(args.csv)
    print(f"Loaded {len(athletes)} athletes")

    event_name = get_event_name(athletes)
    print(f"Event: {event_name}")

    generate_html(athletes, event_name, args.output)
    print("Done!")


if __name__ == '__main__':
    main()
