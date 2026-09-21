#!/usr/bin/env python3
"""Record an authorized edit of a migrated file so historical audits stay reversible.

The migration manifest keeps, for every file that moved during the five-package
refactor, the hash of its post-move content plus inverse edits that reconstruct the
pre-package original. Any later legitimate edit makes the hash stale and the historical
reconstruction fail loudly ("package target changed without recorded evolution").

This tool turns that failure into a precise record: it appends the region-level inverse
edits for the current change, refreshes after_sha256, and verifies that the whole chain
still reconstructs the recorded pre-package original. It never rewrites an existing
record and never invents content.

Run it only for changes that are intended and reviewed. Use --check to report stale
records without writing.
"""
from __future__ import annotations

import argparse
import difflib
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "04_诊断与系统日志/五包迁移清单.json"


def digest(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def baseline_text(record: dict, current: str) -> str:
    """Return the recorded post-move content this manifest expects for the file.

    A record we have already advanced carries its own snapshot, so a second authorized
    edit can still be recorded region by region without rewriting the earlier ones.
    """
    path = record["new_path"]
    snapshot = record.get("after_snapshot")
    if snapshot is not None and digest(snapshot) == record["after_sha256"]:
        return snapshot
    try:
        committed = subprocess.run(["git", "show", f"HEAD:{path}"], cwd=ROOT,
                                   capture_output=True, text=True, check=True).stdout
    except (subprocess.CalledProcessError, FileNotFoundError):
        committed = None
    for candidate in (committed, current):
        if candidate is not None and digest(candidate) == record["after_sha256"]:
            return candidate
    raise ValueError(
        f"cannot recover the recorded state of {path}; "
        "restore the file to its recorded content or update the record by hand")


def region_edits(before: str, after: str) -> list[dict]:
    a_lines, b_lines = before.splitlines(keepends=True), after.splitlines(keepends=True)
    edits: list[dict] = []
    b_offset = 0
    for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(None, a_lines, b_lines, autojunk=False).get_opcodes():
        a_text, b_text = "".join(a_lines[i1:i2]), "".join(b_lines[j1:j2])
        if tag != "equal":
            edits.append({"after_start": b_offset, "after_end": b_offset + len(b_text),
                          "before_text": a_text})
        b_offset += len(b_text)
    return edits


def reconstruct(text: str, edits: list[dict]) -> str:
    for edit in reversed(edits):
        text = text[:edit["after_start"]] + edit["before_text"] + text[edit["after_end"]:]
    return text


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="report stale records only")
    parser.add_argument("--manifest", type=Path, default=MANIFEST)
    args = parser.parse_args()

    data = json.loads(args.manifest.read_text())
    stale, recorded, unresolved = [], [], []
    for record in data["files"]:
        path = ROOT / record["new_path"]
        if not path.is_file():
            continue
        current = path.read_text()
        if digest(current) == record["after_sha256"]:
            continue
        stale.append(record["new_path"])
        if args.check:
            continue
        try:
            before = baseline_text(record, current)
        except ValueError as error:
            unresolved.append(str(error))
            continue
        edits = region_edits(before, current)
        if reconstruct(current, edits) != before:
            unresolved.append(f"region edits do not round-trip: {record['new_path']}")
            continue
        record.setdefault("inverse_edits", []).extend(edits)
        if reconstruct(current, record["inverse_edits"]) != reconstruct(before, record["inverse_edits"][:-len(edits)]):
            unresolved.append(f"pre-package chain broken: {record['new_path']}")
            continue
        if digest(reconstruct(current, record["inverse_edits"])) != record["before_sha256"]:
            unresolved.append(f"pre-package content mismatch: {record['new_path']}")
            continue
        record["after_sha256"] = digest(current)
        record["after_snapshot"] = current
        recorded.append((record["new_path"], len(edits)))

    if not args.check and recorded:
        args.manifest.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"stale": stale, "recorded": [p for p, _ in recorded],
                      "unresolved": unresolved}, ensure_ascii=False, indent=2))
    if unresolved:
        return 1
    return 1 if (stale and args.check) else 0


if __name__ == "__main__":
    sys.exit(main())
