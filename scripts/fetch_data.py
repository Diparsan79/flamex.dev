import json
import os
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

LASTFM_USER = "flamex67"
LETTERBOXD_USER = "flamexgod"

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data.json"
UA = "flamex.dev-data-fetch/1.0 (+https://github.com/Diparsan79/flamex.dev)"
LB_NS = {"lb": "https://letterboxd.com"}

def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=20) as resp:
        return resp.read()

def fetch_lastfm(api_key):
    qs = urllib.parse.urlencode({
        "method": "user.getrecenttracks",
        "user": LASTFM_USER,
        "api_key": api_key,
        "format": "json",
        "limit": 1,
    })
    data = json.loads(get("https://ws.audioscrobbler.com/2.0/?" + qs))
    tracks = data["recenttracks"]["track"]
    if isinstance(tracks, dict):
        tracks = [tracks]
    t = tracks[0]
    return {
        "track": t["name"],
        "artist": t["artist"]["#text"],
        "url": t.get("url", f"https://www.last.fm/user/{LASTFM_USER}"),
        "nowplaying": t.get("@attr", {}).get("nowplaying") == "true",
    }

def fetch_letterboxd():
    root = ET.fromstring(get(f"https://letterboxd.com/{LETTERBOXD_USER}/rss/"))
    for item in root.iter("item"):
        title = item.findtext("lb:filmTitle", namespaces=LB_NS)
        if not title:  # list entries etc. have no film fields
            continue
        return {
            "title": title,
            "year": item.findtext("lb:filmYear", namespaces=LB_NS),
            "rating": item.findtext("lb:memberRating", namespaces=LB_NS),
            "url": item.findtext("link") or f"https://letterboxd.com/{LETTERBOXD_USER}/",
        }
    raise ValueError("no film entries in feed")

def main():
    try:
        out = json.loads(OUT.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        out = {}
    before = json.loads(json.dumps(out))

    key = os.environ.get("LASTFM_API_KEY")
    if key:
        try:
            out["lastfm"] = fetch_lastfm(key)
        except Exception as e:  # never print the URL: it contains the key
            print(f"Last.fm failed: {type(e).__name__}")
    else:
        print("LASTFM_API_KEY not set, skipping Last.fm")

    try:
        out["letterboxd"] = fetch_letterboxd()
    except Exception as e:
        print(f"Letterboxd failed: {type(e).__name__}: {e}")

    # only bump the timestamp when content changed, so the Action doesn't commit for nothing
    if {k: v for k, v in out.items() if k != "updated"} != {k: v for k, v in before.items() if k != "updated"} or "updated" not in out:
        out["updated"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    OUT.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("Wrote", OUT.name)

if __name__ == "__main__":
    main()