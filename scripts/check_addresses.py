"""Stop a publish that would break existing links.

Compares the addresses in the new build (public/addresses.txt) with the live
site's addresses.txt. Every live address must still exist, either as a page or
as a redirect (an entry in some file's `aliases:` list). Also fails if two
pages claim the same address.

Usage: python3 scripts/check_addresses.py public/addresses.txt <new site base URL> <live addresses.txt URL> [more live URLs]
With more than one live URL, an address that exists at any of them must survive (used while moving to a new domain).
"""
import collections
import sys
import urllib.error
import urllib.parse
import urllib.request


def read_lines(text):
    # Hugo writes alias addresses without the trailing slash; compare without it
    return [line.strip().rstrip("/") or "/" for line in text.splitlines() if line.strip()]


def base_prefix(url):
    """Path part of a site's base URL ("/SaxoBrain" on github.io, "" on a custom domain)."""
    path = urllib.parse.urlparse(url).path
    return path.rsplit("/addresses.txt", 1)[0].rstrip("/") if url.startswith("http") else ""


def strip_prefix(lines, prefix):
    """Make addresses independent of where the site is hosted, so moving to a custom domain
    does not make every address look lost."""
    out = []
    for a in lines:
        if prefix and (a == prefix or a.startswith(prefix + "/")):
            a = a[len(prefix):] or "/"
        out.append(a)
    return out


def main(new_path, new_base, live_urls):
    new = strip_prefix(read_lines(open(new_path, encoding="utf-8").read()), base_prefix(new_base.rstrip("/") + "/addresses.txt"))
    problems = []

    dupes = [a for a, n in collections.Counter(new).items() if n > 1]
    for a in dupes:
        problems.append(f"Two pages claim the same address: {a}")

    live = set()
    for live_url in live_urls:
        try:
            with urllib.request.urlopen(live_url, timeout=60) as r:
                live |= set(strip_prefix(read_lines(r.read().decode("utf-8")), base_prefix(live_url)))
        except urllib.error.HTTPError as e:
            if e.code != 404:
                raise
            print(f"No address list at {live_url} (first publish there). Skipping it.")
        except urllib.error.URLError as e:
            # a new custom domain does not resolve until its DNS is set up
            print(f"Could not reach {live_url} ({e.reason}). Skipping it.")

    missing = sorted(live - set(new))
    for a in missing:
        problems.append(f"This address is live but would disappear: {a}\n"
                        f"    Fix: add it to the `aliases:` list of the page it should point to.")

    if problems:
        print("Publish stopped. Existing links would break:\n")
        print("\n".join(problems))
        sys.exit(1)
    print(f"Address check passed: {len(new)} addresses, none lost.")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3:])
