"""Look up Wayback Machine snapshots for each original-url in content and save the verified ones.

Usage: python3 -I scripts/migration/wayback_lookup.py
Writes scripts/migration/wayback.json (original URL -> snapshot URL, or null when none exists).
Waits between requests; archive.org rate-limits quickly. Rerun to retry the ones that failed.
"""
import glob
import json
import os
import re
import time
import urllib.parse
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, "scripts", "migration", "wayback.json")
urls = set()
for f in glob.glob(os.path.join(ROOT, "content", "**", "*.md"), recursive=True):
    m = re.search(r'^original-url: "([^"]+)"', open(f, encoding="utf-8").read(), re.M)
    if m:
        urls.add(m.group(1))
done = json.load(open(OUT, encoding="utf-8")) if os.path.exists(OUT) else {}
for u in sorted(urls):
    if u in done and done[u] is not False:
        continue
    api = "https://archive.org/wayback/available?url=" + urllib.parse.quote(u, safe="")
    for attempt in range(4):
        try:
            req = urllib.request.Request(api, headers={"User-Agent": "SaxoBrain-migration (Timothy Rosenberg)"})
            data = json.load(urllib.request.urlopen(req, timeout=40))
            snap = data.get("archived_snapshots", {}).get("closest")
            done[u] = snap["url"].replace("http://", "https://") if snap and snap.get("available") else None
            print("ok  ", u, "->", done[u])
            break
        except Exception as e:  # rate limit or network; wait and retry
            print("wait", u, type(e).__name__, str(e)[:60])
            time.sleep(30 * (attempt + 1))
    else:
        done[u] = False  # unknown, retry on next run
    json.dump(done, open(OUT, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    time.sleep(8)
