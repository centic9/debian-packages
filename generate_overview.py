#!/usr/bin/env python3
"""
Generate an HTML overview table of packages across all Debian/Ubuntu distributions
in the aptrepo directory.
"""

import argparse
import gzip
import os
from collections import defaultdict
from html import escape
from datetime import datetime, timezone

BASE_URL = "https://cs37700.dogadoserver.de/apt/debian"

# Distribution order and display labels
DISTRIBUTIONS = [
    ("noble",    "Ubuntu Noble (24.04)"),
    ("resolute", "Ubuntu Resolute (24.10)"),
    ("bookworm", "Debian Bookworm (12)"),
    ("trixie",   "Debian Trixie (13)"),
    ("forky",    "Debian Forky (14)"),
    ("sid",      "Debian Sid"),
]
DIST_CODES = [d[0] for d in DISTRIBUTIONS]


def parse_packages_gz(path):
    """Parse a Packages.gz file and return a list of package dicts."""
    packages = []
    with gzip.open(path, "rt", encoding="utf-8", errors="replace") as f:
        current = {}
        for line in f:
            line = line.rstrip("\n")
            if line == "":
                if current.get("Package"):
                    packages.append(current)
                current = {}
            elif line.startswith(" "):
                # continuation line — ignore for our purposes
                pass
            elif ": " in line:
                key, _, value = line.partition(": ")
                current[key] = value
        if current.get("Package"):
            packages.append(current)
    return packages


def collect_data(aptrepo_dir):
    """
    Returns a dict:
      data[package_name][dist_code] = list of {version, filename, architecture}
    """
    data = defaultdict(lambda: defaultdict(list))

    for dist_code in DIST_CODES:
        packages_gz = os.path.join(
            aptrepo_dir, dist_code, "dists", dist_code, "main", "binary-amd64", "Packages.gz"
        )
        if not os.path.exists(packages_gz):
            print(f"  WARNING: {packages_gz} not found, skipping")
            continue

        packages = parse_packages_gz(packages_gz)
        for pkg in packages:
            name = pkg.get("Package", "")
            version = pkg.get("Version", "")
            filename = pkg.get("Filename", "")
            arch = pkg.get("Architecture", "")
            if name:
                data[name][dist_code].append({
                    "version": version,
                    "filename": filename,
                    "arch": arch,
                })

    return data


def make_cell(entries, dist_code):
    """Build the HTML content for a table cell."""
    if not entries:
        return '<td class="missing">—</td>'

    parts = []
    for entry in entries:
        version = escape(entry["version"])
        filename = entry["filename"]
        arch = escape(entry["arch"])
        url = f"{BASE_URL}/{dist_code}/{filename}"
        parts.append(
            f'<a href="{escape(url)}" title="{escape(filename)}">'
            f'{version}'
            f'</a>'
        )
    return f'<td class="present">{"<br>".join(parts)}</td>'


def generate_html(data):
    dist_labels = {code: label for code, label in DISTRIBUTIONS}
    all_packages = sorted(data.keys(), key=str.lower)

    # Build header row
    header_cells = "\n        ".join(
        f'<th class="dist-header"><span class="dist-name">{escape(dist_labels[code])}</span></th>'
        for code in DIST_CODES
    )

    # Build data rows
    rows_html = []
    for pkg_name in all_packages:
        pkg_data = data[pkg_name]
        cells = "\n        ".join(make_cell(pkg_data.get(code, []), code) for code in DIST_CODES)
        row = (
            f'    <tr>\n'
            f'      <td class="pkg-name">{escape(pkg_name)}</td>\n'
            f'      {cells}\n'
            f'    </tr>'
        )
        rows_html.append(row)

    rows = "\n".join(rows_html)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    pkg_count = len(all_packages)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Debian/Ubuntu Package Repository Overview</title>
  <style>
    *, *::before, *::after {{ box-sizing: border-box; }}

    body {{
      font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
      background: #0f1117;
      color: #e2e8f0;
      margin: 0;
      padding: 2rem 0.5rem;
      min-height: 100vh;
    }}

    header {{
      margin: 0 0 2rem;
    }}

    h1 {{
      font-size: 1.8rem;
      font-weight: 700;
      background: linear-gradient(135deg, #6366f1, #a78bfa, #38bdf8);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      background-clip: text;
      margin: 0 0 0.4rem;
    }}

    .meta {{
      font-size: 0.85rem;
      color: #64748b;
    }}

    .meta strong {{
      color: #94a3b8;
    }}

    .search-wrap {{
      margin-top: 1rem;
    }}

    #search {{
      background: #1e2130;
      border: 1px solid #334155;
      border-radius: 8px;
      color: #e2e8f0;
      font-size: 0.9rem;
      padding: 0.5rem 0.85rem;
      width: 280px;
      outline: none;
      transition: border-color 0.2s;
    }}

    #search:focus {{
      border-color: #6366f1;
      box-shadow: 0 0 0 3px rgba(99,102,241,0.2);
    }}

    .table-wrap {{
      margin: 0;
      overflow-x: auto;
      border-radius: 12px;
      border: 1px solid #1e2a3a;
      box-shadow: 0 4px 32px rgba(0,0,0,0.5);
    }}

    table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 0.82rem;
    }}

    thead tr {{
      background: linear-gradient(135deg, #1a1f35, #1e2a3a);
      position: sticky;
      top: 0;
      z-index: 10;
    }}

    th {{
      padding: 0.9rem 0.75rem;
      text-align: left;
      font-weight: 600;
      border-bottom: 2px solid #334155;
      white-space: nowrap;
    }}

    th.pkg-col {{
      color: #94a3b8;
      min-width: 190px;
      width: 190px;
    }}

    th.dist-header {{
      color: #a5b4fc;
      min-width: 155px;
    }}

    .dist-name {{
      display: block;
    }}

    tbody tr {{
      border-bottom: 1px solid #1e2a3a;
      transition: background 0.15s;
    }}

    tbody tr:hover {{
      background: #1a2035;
    }}

    tbody tr:last-child {{
      border-bottom: none;
    }}

    tbody tr:nth-child(even) {{
      background: #131825;
    }}

    tbody tr:nth-child(even):hover {{
      background: #1a2035;
    }}

    td {{
      padding: 0.55rem 0.75rem;
      vertical-align: top;
    }}

    td.pkg-name {{
      font-family: 'JetBrains Mono', 'Fira Code', monospace;
      font-size: 0.8rem;
      color: #e2e8f0;
      font-weight: 500;
      white-space: nowrap;
    }}

    td.missing {{
      color: #374151;
      text-align: center;
      font-size: 1rem;
    }}

    td.present a {{
      display: inline-block;
      color: #38bdf8;
      text-decoration: none;
      font-family: 'JetBrains Mono', 'Fira Code', monospace;
      font-size: 0.65rem;
      transition: color 0.15s;
    }}

    td.present a:hover {{
      color: #7dd3fc;
      text-decoration: underline;
    }}

    .arch {{
      margin-left: 0.35em;
      color: #64748b;
      font-size: 0.72rem;
    }}

    .hidden {{
      display: none !important;
    }}

    footer {{
      margin: 1.5rem 0 0;
      font-size: 0.8rem;
      color: #374151;
      text-align: center;
    }}
  </style>
</head>
<body>
  <header>
    <h1>Package Repository Overview</h1>
    <p class="meta">
      <strong>{pkg_count}</strong> packages across
      <strong>{len(DISTRIBUTIONS)}</strong> distributions &mdash;
      generated {now}
    </p>
    <div class="search-wrap">
      <input id="search" type="search" placeholder="Filter packages…" autocomplete="off">
    </div>
  </header>

  <div class="table-wrap">
    <table id="pkg-table">
      <thead>
        <tr>
          <th class="pkg-col">Package</th>
          {header_cells}
        </tr>
      </thead>
      <tbody>
{rows}
      </tbody>
    </table>
  </div>

  <footer>
    Repository hosted at <a href="{BASE_URL}" style="color:#6366f1">{BASE_URL}</a>
  </footer>

  <script>
    const input = document.getElementById('search');
    const rows  = document.querySelectorAll('#pkg-table tbody tr');
    input.addEventListener('input', () => {{
      const q = input.value.trim().toLowerCase();
      rows.forEach(row => {{
        const name = row.querySelector('.pkg-name').textContent.toLowerCase();
        row.classList.toggle('hidden', q !== '' && !name.includes(q));
      }});
    }});
  </script>
</body>
</html>
"""
    return html


def main():
    script_dir = os.path.dirname(__file__)
    parser = argparse.ArgumentParser(
        description="Generate an HTML package overview from apt repository Packages.gz files."
    )
    parser.add_argument(
        "aptrepo_dir",
        nargs="?",
        default=os.path.join(script_dir, "aptrepo", "debian"),
        help="Path to the aptrepo/debian directory (default: %(default)s)",
    )
    parser.add_argument(
        "output_file",
        nargs="?",
        default=os.path.join(script_dir, "overview.html"),
        help="Output HTML file path (default: %(default)s)",
    )
    args = parser.parse_args()

    print("Collecting package data…")
    data = collect_data(args.aptrepo_dir)
    print(f"Found {len(data)} unique packages.")

    print("Generating HTML…")
    html = generate_html(data)

    with open(args.output_file, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"Written to {args.output_file}")


if __name__ == "__main__":
    main()
