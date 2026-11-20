#!/usr/bin/env python3
"""Rebuild the list in watchlist.html from watchlist.csv (Letterboxd export).

Usage: put the fresh watchlist.csv next to this file, then run
    python3 update_watchlist.py
"""
import csv
import html
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CSV_PATH = HERE / "watchlist.csv"
HTML_PATH = HERE / "watchlist.html"

START = "<!-- WATCHLIST:START -->"
END = "<!-- WATCHLIST:END -->"


def load_rows():
    with open(CSV_PATH, encoding="utf-8-sig", newline="") as f:
        rows = [r for r in csv.DictReader(f) if (r.get("Name") or "").strip()]
    # newest added first; sort is stable, so same-day rows keep CSV order
    rows.sort(key=lambda r: r.get("Date", ""), reverse=True)
    return rows


def render(rows):
    items = []
    for r in rows:
        name = html.escape(r["Name"].strip())
        year = html.escape((r.get("Year") or "").strip())
        uri = (r.get("Letterboxd URI") or "").strip()
        year_html = f' <span class="year">({year})</span>' if year else ""
        if uri.startswith("https://"):
            link = html.escape(uri, quote=True)
            inner = f'<a href="{link}" target="_blank" rel="noopener noreferrer">{name}{year_html}</a>'
        else:
            inner = f"{name}{year_html}"
        items.append(f"                    <li>{inner}</li>")

    count = len(rows)
    noun = "film" if count == 1 else "films"
    return (
        f'{START}\n'
        f'                <h1>Watchlist</h1>\n'
        f'                <p class="watch-count">{count} {noun} · newest added first</p>\n'
        f'                <ul class="watch-list">\n'
        + "\n".join(items)
        + f'\n                </ul>\n                {END}'
    )


def main():
    if not CSV_PATH.exists():
        sys.exit(f"Missing {CSV_PATH.name}. Export it from Letterboxd and put it next to this script.")
    page = HTML_PATH.read_text(encoding="utf-8")
    if START not in page or END not in page:
        sys.exit("Markers not found in watchlist.html.")

    rows = load_rows()
    block = render(rows)
    pattern = re.compile(re.escape(START) + r".*?" + re.escape(END), re.DOTALL)
    HTML_PATH.write_text(pattern.sub(lambda _m: block, page, count=1), encoding="utf-8")
    print(f"Wrote {len(rows)} films to {HTML_PATH.name}")


if __name__ == "__main__":
    main()
