"""Stop a publish that would break existing links.

Compares the addresses in the new build (public/addresses.txt) with the live
site's addresses.txt. Every live address must still exist, either as a page or
as a redirect (an entry in some file's `aliases:` list). Also fails if two
pages claim the same address.

Usage: python3 scripts/check_addresses.py public/addresses.txt https://example.org/addresses.txt
"""
import collections
import sys
import urllib.error
import urllib.request


def read_lines(text):
    # Hugo writes alias addresses without the trailing slash; compare without it
    return [line.strip().rstrip("/") or "/" for line in text.splitlines() if line.strip()]


def main(new_path, live_url):
    new = read_lines(open(new_path, encoding="utf-8").read())
    problems = []

    dupes = [a for a, n in collections.Counter(new).items() if n > 1]
    for a in dupes:
        problems.append(f"Two pages claim the same address: {a}")

    try:
        with urllib.request.urlopen(live_url, timeout=60) as r:
            live = read_lines(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        if e.code == 404:
            print("No live address list yet (first publish). Skipping the comparison.")
            live = []
        else:
            raise

    missing = sorted(set(live) - set(new))
    for a in missing:
        problems.append(f"This address is live but would disappear: {a}\n"
                        f"    Fix: add it to the `aliases:` list of the page it should point to.")

    if problems:
        print("Publish stopped. Existing links would break:\n")
        print("\n".join(problems))
        sys.exit(1)
    print(f"Address check passed: {len(new)} addresses, none lost.")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
