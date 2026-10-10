#!/usr/bin/env python3
"""Check every outside link in content/ and report the broken and redirected ones.

Never edits content. Writes scripts/migration/link-check.csv (one row per problem link and the files
that use it) and prints a summary.

  python3 scripts/check_links.py              # all links
  python3 scripts/check_links.py --only youtube

YouTube links are checked through YouTube's oEmbed endpoint, which answers 404 or 401 for removed
and private videos (a plain page request always answers 200). Some shops (Amazon, Sheet Music Plus)
refuse automated requests; those come back as "blocked" and need a look in a browser.
Alexander Street links need a library login and are skipped.
"""
import argparse, csv, re, sys, time, urllib.parse, urllib.request, urllib.error
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "scripts/migration/link-check.csv"
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
URL_RE = re.compile(r"https?://[^\s\"<>|\]]+")
SKIP = ("alexanderstreet.com",)


def collect():
    uses = {}
    for p in sorted((ROOT / "content").rglob("*.md")):
        for u in URL_RE.findall(p.read_text(encoding="utf-8")):
            u = u.rstrip(".,;:'*_")
            while u.endswith(")") and u.count(")") > u.count("("):  # Markdown link end, not part of the address
                u = u[:-1].rstrip(".,;:'*_")
            if any(s in u for s in SKIP):
                continue
            uses.setdefault(u, set()).add(str(p.relative_to(ROOT)))
    return uses


def youtube_watch(u):
    """The watch or playlist form of a YouTube video link (oEmbed accepts only those), or None."""
    m = re.search(r"(?:youtu\.be/|youtube(?:-nocookie)?\.com/(?:watch\?(?:[^#]*&)?v=|shorts/|embed/|live/))([A-Za-z0-9_-]{11})", u)
    if m:
        return "https://www.youtube.com/watch?v=" + m.group(1)
    m = re.search(r"youtube\.com/(?:playlist|watch)\?(?:[^#]*&)?list=([A-Za-z0-9_-]+)", u)
    if m:
        return "https://www.youtube.com/playlist?list=" + m.group(1)
    return None


def fetch(u, method="GET", tries=4):
    for i in range(tries):
        try:
            return _fetch(u, method)
        except urllib.error.HTTPError as e:
            if e.code != 429 or i == tries - 1:
                raise
            time.sleep(5 * (i + 1))


def _fetch(u, method):
    req = urllib.request.Request(u, method=method, headers={"User-Agent": UA, "Accept-Language": "en-US,en;q=0.9",
                                                            "Accept": "text/html,application/xhtml+xml,*/*;q=0.8"})
    with urllib.request.urlopen(req, timeout=25) as r:
        return r.status, r.geturl()


def same_place(a, b):
    """A redirect counts only when it changes the host (ignoring www) or the path (ignoring a trailing slash and case)."""
    pa, pb = urllib.parse.urlsplit(a), urllib.parse.urlsplit(b)
    host = lambda p: p.netloc.lower().removeprefix("www.")
    path = lambda p: urllib.parse.unquote(p.path).rstrip("/").lower()
    return host(pa) == host(pb) and path(pa) == path(pb)


def check(u):
    try:
        if youtube_watch(u):
            o = "https://www.youtube.com/oembed?format=json&url=" + urllib.parse.quote(youtube_watch(u), safe="")
            try:
                fetch(o)
                return u, "ok", ""
            except urllib.error.HTTPError as e:
                if e.code in (401, 403):
                    return u, "private or embedding off", str(e.code)
                if e.code == 404:
                    return u, "removed", "404"
                if e.code == 400:
                    return u, "not a video or playlist link", "400"
                return u, "error", str(e.code)
        try:
            status, final = fetch(u)
        except urllib.error.HTTPError as e:
            if e.code in (401, 403, 405, 429, 503, 999):
                return u, "blocked", str(e.code)
            if e.code in (404, 410):
                return u, "dead", str(e.code)
            return u, "error", str(e.code)
        if not same_place(u, final):
            # A shop that sends a removed product to its home page or a search page is a dead link.
            p = urllib.parse.urlsplit(final)
            if p.path in ("", "/") or "search" in p.path.lower() or "notfound" in final.lower().replace("-", ""):
                return u, "dead (redirects to home or search)", final
            return u, "redirected", final
        return u, "ok", ""
    except Exception as e:  # timeouts, DNS failures, TLS errors
        msg = str(getattr(e, "reason", e))
        return u, "unreachable", msg[:120]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", help="check only links whose address contains this text")
    a = ap.parse_args()
    uses = collect()
    urls = [u for u in uses if not a.only or a.only in u]
    print(f"Checking {len(urls)} links...", file=sys.stderr)
    # Wikimedia rate-limits parallel requests, so its links go one at a time alongside the rest.
    slow = [u for u in urls if "wikimedia.org" in u]
    fast = [u for u in urls if u not in slow]
    with ThreadPoolExecutor(12) as ex:
        fut_slow = ex.submit(lambda: [check(u) for u in slow])
        results = list(ex.map(check, fast)) + fut_slow.result()
    problems = [r for r in results if r[1] != "ok"]
    order = ["dead", "dead (redirects to home or search)", "removed", "private or embedding off", "not a video or playlist link",
             "unreachable", "error", "redirected", "blocked"]
    problems.sort(key=lambda r: (order.index(r[1]) if r[1] in order else 99, r[0]))
    with OUT.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["status", "detail", "url", "files"])
        for u, s, d in problems:
            w.writerow([s, d, u, "; ".join(sorted(uses[u]))])
    counts = {}
    for _, s, _ in results:
        counts[s] = counts.get(s, 0) + 1
    for s, n in sorted(counts.items(), key=lambda x: -x[1]):
        print(f"{n:5}  {s}")
    print(f"Report: {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
