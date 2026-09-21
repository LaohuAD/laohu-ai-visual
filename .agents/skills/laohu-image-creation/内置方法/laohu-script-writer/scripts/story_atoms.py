#!/usr/bin/env python3
"""Synchronize and read portable application atoms without shipping source transcripts."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import tempfile

PACKAGE = Path(__file__).resolve().parents[1]
DEFAULT_ATOMS = PACKAGE / "references/故事原子"


def local_library():
    for ancestor in PACKAGE.parents:
        candidate = ancestor / "02_共享资产库/故事素材库"
        if candidate.is_dir():
            return candidate
    return None


def atomic_text(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent,
                                     prefix=".atom-", delete=False) as stream:
        temporary = Path(stream.name)
        try:
            stream.write(text)
            stream.flush()
            os.fsync(stream.fileno())
        except BaseException:
            temporary.unlink(missing_ok=True)
            raise
    os.replace(temporary, path)


def sync(library, destination):
    """Preserve complete atoms/constraints; export only source metadata, not original words."""
    library, destination = Path(library), Path(destination)
    if not library.is_dir() or not (library / "manifest.json").is_file():
        raise ValueError("完整来源库不存在；不会覆盖已有应用原子")
    sources = {s["id"]: s for p in sorted((library / "sources").rglob("*.json"))
               for s in [json.loads(p.read_text())]}
    usage = [json.loads(line) for p in sorted((library / "usage").rglob("*.jsonl"))
             for line in p.read_text().splitlines() if line.strip()]
    records, staged = [], {}
    for path in sorted((library / "atoms").rglob("*.json")):
        atom = json.loads(path.read_text())
        if not re.fullmatch(r"ATM-\d{8}-\d{3,}", atom.get("id", "")):
            raise ValueError("原子编号无效")
        source = sources.get(atom.get("source_id"))
        if source is None:
            raise ValueError("原子缺少可追溯source；中止同步")
        availability = atom["status"] if source["status"] == "active" else "source_archived"
        for event in sorted(usage, key=lambda e: (e["created_at"], e["id"])):
            if atom["id"] in event["atom_ids"] and event["scope"] == "library":
                if event["event_type"] == "paused":
                    availability = "paused"
                elif event["event_type"] == "reopened" and source["status"] == "active":
                    availability = atom["status"]
        exported = dict(atom)
        exported["availability"] = availability
        exported["source_context"] = {
            "source_id": source["id"],
            "source_type": source["source_type"],
            "fact_status": source["fact_status"],
            "rights_note": source["rights_note"],
            "original_included": False,
        }
        payload = json.dumps(exported, ensure_ascii=False, indent=2)
        text = (f"# {atom['id']}\n\n{atom['atom']}\n\n"
                "以下记录包含应用机制、可见证据、适用边界和置信度。来源编号可在本地完整库溯源；"
                "当前文件不包含source原话。应用分析不是可替代真实来源的事实证明。\n\n"
                f"```json\n{payload}\n```\n")
        filename = atom["id"] + ".md"
        staged[filename] = text
        records.append({"id": atom["id"], "source_id": atom["source_id"],
                        "summary": atom["atom"], "availability": availability,
                        "file": filename, "sha256": hashlib.sha256(text.encode()).hexdigest()})
    # Validate all source relations before touching existing application data.
    previous = destination / "manifest.json"
    old_records = json.loads(previous.read_text()).get("atoms", []) if previous.is_file() else []
    for name, text in staged.items():
        atomic_text(destination / name, text)
    manifest = {"schema_version": 1, "source_original_included": False, "atoms": records}
    atomic_text(previous, json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    for item in old_records:
        filename = item["file"]
        if filename not in staged and re.fullmatch(r"ATM-\d{8}-\d{3,}\.md", filename):
            (destination / filename).unlink(missing_ok=True)
    catalog = ["# 故事原子应用目录", "", "先浏览本页，按当前创作缺口读取入围原子；不默认加载全部详情。",
               "只有callable可直接作为候选；pending_evidence需补证，paused或source_archived不默认采用。",
               "结论、证据、限制与置信度共同使用，不能把原子直接拼成剧情。", ""]
    catalog += [f"- [{r['id']}]({r['file']})｜{r['availability']}｜{r['summary']}" for r in records]
    atomic_text(destination / "README.md", "\n".join(catalog) + "\n")
    return {"atom_count": len(records), "source_count": len(sources),
            "callable_count": sum(r["availability"] == "callable" for r in records),
            "source_original_included": False}


def read_manifest(root):
    path = Path(root) / "manifest.json"
    if not path.is_file():
        return {"atoms": []}
    return json.loads(path.read_text())


def get_atom(root, atom_id):
    item = next((r for r in read_manifest(root)["atoms"] if r["id"] == atom_id), None)
    if item is None:
        raise ValueError("没有该原子")
    filename = item["file"]
    if not re.fullmatch(r"ATM-\d{8}-\d{3,}\.md", filename):
        raise ValueError("原子文件路径无效")
    text = (Path(root) / filename).read_text()
    if hashlib.sha256(text.encode()).hexdigest() != item["sha256"]:
        raise ValueError("原子内容与清单不一致，需要从权威库重新同步")
    return json.loads(re.search(r"```json\n(.*?)\n```", text, re.S)[1])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--atoms", type=Path, default=DEFAULT_ATOMS)
    sub = parser.add_subparsers(dest="command", required=True)
    s = sub.add_parser("sync")
    s.add_argument("--library", type=Path)
    sub.add_parser("stats")
    s = sub.add_parser("search")
    s.add_argument("query", nargs="?", default="")
    s.add_argument("--offset", type=int, default=0)
    s.add_argument("--limit", type=int, default=10)
    s.add_argument("--include-unavailable", action="store_true")
    sub.add_parser("get").add_argument("id")
    args = parser.parse_args()
    try:
        if args.command == "sync":
            library = args.library or local_library()
            if library is None:
                raise ValueError("云端应用包没有完整来源库；使用现有原子，或显式指定--library")
            result = sync(library, args.atoms)
        elif args.command == "get":
            result = get_atom(args.atoms, args.id)
        else:
            rows = read_manifest(args.atoms)["atoms"]
            if args.command == "stats":
                result = {"atom_count": len(rows), "callable_count": sum(r["availability"] == "callable" for r in rows),
                          "source_original_included": False}
            else:
                if args.offset < 0 or not 1 <= args.limit <= 50:
                    raise ValueError("offset必须非负，limit必须为1—50；可继续翻页，不限制总候选数")
                terms = args.query.casefold().split()
                ranked = []
                for row in rows:
                    if not args.include_unavailable and row["availability"] != "callable":
                        continue
                    atom = get_atom(args.atoms, row["id"])
                    text = json.dumps(atom, ensure_ascii=False).casefold()
                    score = sum(text.count(term) for term in terms)
                    if not terms or score:
                        ranked.append((score, row))
                ranked.sort(key=lambda v: (-v[0], v[1]["id"]))
                page = [row for _, row in ranked[args.offset:args.offset + args.limit]]
                end = args.offset + len(page)
                result = {"items": page, "total": len(ranked),
                          "next_offset": end if end < len(ranked) else None}
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (ValueError, OSError, KeyError, json.JSONDecodeError) as error:
        parser.exit(2, str(error) + "\n")


if __name__ == "__main__":
    raise SystemExit(main())
