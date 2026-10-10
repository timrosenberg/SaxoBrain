#!/usr/bin/env python3
"""Apply staged research (one JSON per batch) to content/works.

Usage: apply_research.py <staging dir> [--write]

Also appends a clickable "Research notes (private)" list to the body (never published; layouts/_partials/body.html strips it).
Fills only empty fields: composer `website`, composed, streaming, purchase, download. Adds a private
`research:` list (never rendered) for facts that help judge difficulty, each
line ending with its source URL. Never touches year-of-study, existing values
or the body. Without --write it prints what it would change.
"""
import glob
import json
import os
import re
import sys

WORKS = os.path.join(os.path.dirname(__file__), "..", "content", "works")
COMPOSERS = os.path.join(os.path.dirname(__file__), "..", "content", "composers")
YT = re.compile(r"^https://(www\.)?(youtube\.com/watch\?v=|youtu\.be/)[\w-]{11}")
URL = re.compile(r"^https?://\S+$")
UNSURE = re.compile(r"not confirmed|unconfirmed|search summary|unverified|could not|probabl|likely", re.I)


def q(s):
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def is_empty(fm, key):
    # a bare "key:" line with a block list under it is not empty
    return bool(re.search(rf"^{key}:[ \t]*(\[\])?[ \t]*$(?!\n[ \t]*- )", fm, re.M))


def set_scalar(fm, key, value):
    return re.sub(rf"^{key}:[ \t]*$", f"{key}: {value}", fm, count=1, flags=re.M)


def set_list(fm, key, items):
    block = f"{key}:\n" + "\n".join(f"  - {q(i)}" for i in items)
    return re.sub(rf"^{key}:[ \t]*(\[\])?[ \t]*$(?!\n[ \t]*- )", block, fm, count=1, flags=re.M)


HEADING = "## Research notes (private)"


def body_block(fm):
    m = re.search(r"^research:\n((?:[ \t]+- .*\n?)+)", fm + "\n", re.M)
    if not m:
        return ""
    out = []
    for l in m.group(1).splitlines():
        item = l.strip()[2:].strip().strip('"').replace('\\"', '"')
        text, _, url = item.rpartition(" · ")
        if URL.match(url):
            host = re.sub(r"^https?://(www\.)?([^/]+).*$", r"\2", url)
            out.append(f"- {text} · [{host}]({url})")
        else:
            out.append(f"- {item}")
    return HEADING + "\n\n" + "\n".join(out) + "\n"


def with_body_block(fm, body):
    """Append the clickable research list to the body unless one exists. Never edits an existing block."""
    if HEADING in body:
        return body, False
    block = body_block(fm)
    if not block:
        return body, False
    if not body.strip():
        return block, True
    return body.rstrip("\n") + "\n\n" + block, True


def apply(fm, r):
    notes = []
    y = (r.get("composed") or "").strip()
    if re.fullmatch(r"1[0-9]{3}|20[0-2][0-9]", y) and r.get("composed_source") and is_empty(fm, "composed"):
        fm = set_scalar(fm, "composed", y)
        notes.append(f"composed {y}")
    s = (r.get("streaming") or "").strip()
    if YT.match(s) and is_empty(fm, "streaming"):
        fm = set_scalar(fm, "streaming", q(s))
        notes.append("streaming")
    if is_empty(fm, "purchase"):
        items = []
        for p in r.get("purchase") or []:
            if URL.match(p.get("url", "")):
                items.append(p["url"])  # bare URL: a label would break the clickable link in Obsidian
        if items:
            fm = set_list(fm, "purchase", items)
            notes.append(f"purchase x{len(items)}")
    if re.search(r"^download:", fm, re.M):
        dl_empty = is_empty(fm, "download")
    else:
        dl_empty = True
    dls = [d["url"] for d in r.get("download") or [] if URL.match(d.get("url", ""))]
    if dls and dl_empty:
        if re.search(r"^download:", fm, re.M):
            fm = set_list(fm, "download", dls)
        else:
            fm = re.sub(r"^(purchase:.*?)(?=^\w)", lambda m: m.group(1) + "download:\n" + "\n".join(f"  - {q(d)}" for d in dls) + "\n", fm, count=1, flags=re.M | re.S)
        notes.append(f"download x{len(dls)}")
    lines = [l.strip() for l in r.get("research") or [] if l and URL.search(l.split(" · ")[-1].strip()) and not UNSURE.search(l)]
    if lines and not re.search(r"^research:", fm, re.M):
        block = "research:\n" + "\n".join(f"  - {q(l)}" for l in lines) + "\n"
        fm = re.sub(r"^aliases:", lambda m: block + "aliases:", fm, count=1, flags=re.M)
        notes.append(f"research x{len(lines)}")
    return fm, notes


def main():
    staging = sys.argv[1]
    write = "--write" in sys.argv
    total = changed = 0
    for jf in sorted(glob.glob(os.path.join(staging, "*.json"))):
        try:
            data = json.load(open(jf))
        except ValueError:
            print("SKIP unreadable", jf)
            continue
        for name, c in data.get("composers", {}).items():
            site = (c.get("website") or "").strip()
            cpath = os.path.join(COMPOSERS, name + ".md")
            if not (URL.match(site) and site.startswith("http") and os.path.exists(cpath)):
                continue
            ctext = open(cpath, encoding="utf-8").read()
            cm = re.match(r"---\n(.*?)\n---\n(.*)", ctext, re.S)
            cfm = cm.group(1)
            if re.search(r"^website:[ \t]*\S", cfm, re.M):
                continue
            if re.search(r"^website:", cfm, re.M):
                cfm = re.sub(r"^website:.*$", f"website: {site}", cfm, count=1, flags=re.M)
            else:
                cfm = re.sub(r"^(photo-source:.*)$", lambda m: m.group(1) + f"\nwebsite: {site}", cfm, count=1, flags=re.M)
            print("composer", name, "| website")
            if write:
                open(cpath, "w", encoding="utf-8").write(f"---\n{cfm}\n---\n{cm.group(2)}")
        for fn, r in data.get("works", {}).items():
            path = os.path.join(WORKS, fn)
            if not os.path.exists(path):
                print("MISSING", fn)
                continue
            total += 1
            text = open(path, encoding="utf-8").read()
            m = re.match(r"---\n(.*?)\n---\n(.*)", text, re.S)
            fm, notes = apply(m.group(1), r)
            body, added = with_body_block(fm, m.group(2))
            if added:
                notes.append("body links")
            if not notes:
                continue
            changed += 1
            print(fn, "|", ", ".join(notes))
            if write:
                open(path, "w", encoding="utf-8").write(f"---\n{fm}\n---\n{body}")
    synced = 0
    for path in sorted(glob.glob(os.path.join(WORKS, "*.md"))):
        text = open(path, encoding="utf-8").read()
        m = re.match(r"---\n(.*?)\n---\n(.*)", text, re.S)
        if not m:
            continue
        body, added = with_body_block(m.group(1), m.group(2))
        if added:
            synced += 1
            if write:
                open(path, "w", encoding="utf-8").write(f"---\n{m.group(1)}\n---\n{body}")
    print(f"{changed} of {total} works changed" + ("" if write else " (dry run)"))
    print(f"{synced} works got a clickable research list in the body" + ("" if write else " (dry run)"))


main()
