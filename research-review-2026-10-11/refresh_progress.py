"""Refresh the private research index from saved records and verified reviews."""
import hashlib
import csv
import json
from pathlib import Path

root = Path(__file__).resolve().parent
queue = json.loads((root / "queue.json").read_text())["entries"]
audit = json.loads((root / "primary-review.json").read_text())["reviews"]
records = {}
for path in root.glob("lane-*/records/*.json"):
    record = json.loads(path.read_text())
    records[record["id"]] = (record, path)
valid = {
    int(key): review for key, review in audit.items()
    if int(key) in records
    and review["record_sha256"] == hashlib.sha256(records[int(key)][1].read_bytes()).hexdigest()
}
status = json.loads((root / "status.json").read_text())
status.update(draft_records_saved=len(records), primary_review_complete=len(valid), research_complete=len(valid))
lines = [
    "# SaxoBrain repertoire research index", "",
    "Started October 11, 2026. Scope: 409 currently unassigned works with existing research.", "",
    "Three GPT-6 Luna agents research separate groups. The primary agent reviews their findings. Each work retains a global number for your decisions. Catalog levels and other fields remain unchanged.", "",
    f"Research records saved: {len(records)} / 409. Primary review: {len(valid)} / 409. " + ("The research pass is complete. Work-specific evidence gaps remain documented." if len(valid) == 409 else "Research and evidence checks remain in progress."), "",
    f"[Decision table](<{root / 'decision-table.csv'}>) gives one row per work with findings, collection context, gaps, and packet links. Difficulty remains for Tim to decide.", "",
    "| Packet | Work IDs | Count | Status |", "|---|---|---|---|",
]
for batch in status["batches"]:
    ids = batch["ids"]
    reviewed = [n for n in ids if n in valid]
    saved = [n for n in ids if n in records]
    packet = root / f'lane-{batch["lane"]}/packets/batch-{batch["batch"]:02}.md'
    batch["reviewed_ids"] = reviewed
    batch["status"] = "reviewed_with_gaps" if len(reviewed) == len(ids) else "research_and_review_in_progress"
    label = f'{batch["batch"]:02}'
    if packet.exists():
        label = f'[{label}](<{packet}>)'
    progress = f"{len(reviewed)} reviewed; {len(saved)} drafts saved" if saved else "Research in progress"
    lines.append(f'| {label} | {ids[0]} to {ids[-1]} | {len(ids)} | {progress} |')
lines += ["", "## Work register", "",
          "A research pass can leave specific score or edition gaps. Review completion does not imply a level can be assigned confidently.", "",
          "| ID | Work | Research |", "|---|---|---|"]
for entry in queue:
    n = entry["id"]
    title = entry["filename"].removesuffix(".md").replace("|", "\\|")
    label = f'[{title}](<{entry["path"]}>)'
    packet = root / f'lane-{entry["lane"]}/packets/batch-{entry["batch"]:02}.md'
    research = f'Packet {entry["batch"]:02}'
    if packet.exists():
        research = f'[{research}](<{packet}>)'
    if n in valid:
        research += "; reviewed with gaps"
    elif n in records:
        research += "; draft under review"
    lines.append(f"| {n} | {label} | {research} |")
(root / "status.json").write_text(json.dumps(status, ensure_ascii=False, indent=2) + "\n")
(root / "index.md").write_text("\n".join(lines) + "\n")
def plain(value):
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        return " | ".join(plain(item) for item in value)
    if isinstance(value, dict):
        return str(value.get("claim", value.get("observation", json.dumps(value, ensure_ascii=False))))
    return "" if value is None else str(value)

with (root / "decision-table.csv").open("w", newline="", encoding="utf-8-sig") as stream:
    writer = csv.writer(stream)
    writer.writerow(["ID", "Composer and work", "Review status", "Identity", "Observed notation (scope in text)", "Review focus", "Collection context", "Gaps", "Proposed catalog checks", "Sources", "Packet", "Catalog file"])
    for entry in queue:
        n = entry["id"]
        record = records.get(n, ({}, None))[0]
        writer.writerow([
            n, entry["filename"].removesuffix(".md"),
            "Reviewed with gaps" if n in valid else "Draft under review",
            plain(record.get("identity")), plain(record.get("score_observations")),
            plain(record.get("review_focus")), plain(record.get("collection_flag")),
            plain(record.get("gaps")), plain(record.get("proposed_corrections")),
            " | ".join(dict.fromkeys(e.get("url", "") for e in record.get("evidence", []))),
            str(root / f'lane-{entry["lane"]}/packets/batch-{entry["batch"]:02}.md'),
            entry["path"],
        ])
print(f"Drafts: {len(records)}. Current reviewed records: {len(valid)}.")
