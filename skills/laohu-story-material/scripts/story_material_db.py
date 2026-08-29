#!/usr/bin/env python3
"""Private JSONL store for story sources, reusable atoms, and usage events."""

from __future__ import annotations

import argparse
import fcntl
import hashlib
import json
import os
import re
import sys
import tempfile
from collections import Counter
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Iterator


ROOT = Path(__file__).resolve().parents[3]
DEFAULT_DB = ROOT / "00_输入原料" / "故事素材原子库.jsonl"
ID_PATTERN = re.compile(r"^(SRC|ATM|USE)-\d{8}-\d{3,}$")

SOURCE_TYPES = {
    "life_observation", "short_video", "conversation", "news",
    "personal_idea", "image", "audio", "other", "unknown",
}
FACT_STATUS = {"personal_observation", "sourced", "unverified", "fiction", "unknown"}
CURATION = {"laohu_selected", "laohu_approved_external"}
SOURCE_STATUS = {"active", "archived"}
ATOM_STATUS = {"callable", "pending_evidence"}
FACT_CONFIDENCE = {"high", "medium", "low", "unknown"}
ANALYSIS_CONFIDENCE = {"high", "medium", "low"}
PROJECT_EVENTS = {"shortlisted", "used", "validated", "rejected"}
LIBRARY_EVENTS = {"paused", "reopened"}
LIST_FIELDS = {
    "human_truth", "mechanisms", "material_types", "dramatic_functions",
    "memory_carriers", "relationships", "emotions", "themes",
    "visible_evidence", "extensions", "boundaries",
}
SEARCH_WEIGHTS = {
    "mechanisms": 5,
    "dramatic_functions": 4,
    "human_truth": 4,
    "relationships": 3,
    "material_types": 2,
    "emotions": 2,
    "themes": 1,
    "memory_carriers": 1,
}
COMPACT_FIELDS = (
    "id", "source_id", "atom", "human_truth", "mechanisms", "material_types",
    "dramatic_functions", "memory_carriers", "relationships", "emotions", "themes",
    "fact_confidence", "analysis_confidence",
)


class ValidationError(ValueError):
    """Raised when a write would violate the material-store contract."""


def _now() -> datetime:
    return datetime.now().astimezone()


def _require(record: dict, field: str, expected_type: type) -> object:
    value = record.get(field)
    if not isinstance(value, expected_type):
        raise ValidationError(
            f"{record.get('id', '<new>')} field {field} must be {expected_type.__name__}"
        )
    return value


def _require_enum(record: dict, field: str, allowed: set[str]) -> str:
    value = _require(record, field, str)
    if value not in allowed:
        raise ValidationError(
            f"{record.get('id', '<new>')} field {field} has invalid value: {value}"
        )
    return value


def load_records(path: Path) -> list[dict]:
    if not path.exists():
        return []
    records: list[dict] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            try:
                value = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValidationError(
                    f"invalid JSON at line {line_number}: {exc.msg}"
                ) from exc
            if not isinstance(value, dict):
                raise ValidationError(f"line {line_number} must contain a JSON object")
            records.append(value)
    return records


def validate_records(records: list[dict]) -> None:
    seen: set[str] = set()
    source_ids: set[str] = set()
    atom_ids: set[str] = set()
    for record in records:
        record_type = _require(record, "record_type", str)
        if record_type not in {"source", "atom", "usage"}:
            raise ValidationError(f"unsupported record_type: {record_type}")
        record_id = _require(record, "id", str)
        if not ID_PATTERN.fullmatch(record_id):
            raise ValidationError(f"invalid record id: {record_id}")
        if record_id in seen:
            raise ValidationError(f"duplicate record id: {record_id}")
        seen.add(record_id)
        _require(record, "created_at", str)
        if record_type == "source":
            if not _require(record, "original", str).strip():
                raise ValidationError(f"{record_id} original cannot be empty")
            _require_enum(record, "source_type", SOURCE_TYPES)
            _require_enum(record, "fact_status", FACT_STATUS)
            _require_enum(record, "curation_priority", CURATION)
            _require_enum(record, "status", SOURCE_STATUS)
            if _require(record, "privacy", str) != "private":
                raise ValidationError(f"{record_id} privacy must be private")
            for field in ("source_url", "source_title", "rights_note"):
                _require(record, field, str)
            source_ids.add(record_id)
        elif record_type == "atom":
            atom_ids.add(record_id)

    for record in records:
        record_type = record["record_type"]
        record_id = record["id"]
        if record_type == "atom":
            if _require(record, "source_id", str) not in source_ids:
                raise ValidationError(f"{record_id} references missing source")
            if not _require(record, "atom", str).strip():
                raise ValidationError(f"{record_id} atom cannot be empty")
            for field in LIST_FIELDS:
                values = _require(record, field, list)
                if any(
                    not isinstance(value, str) or not value.strip()
                    for value in values
                ):
                    raise ValidationError(
                        f"{record_id} field {field} must contain non-empty strings"
                    )
            _require(record, "non_replaceable", str)
            _require(record, "fit", dict)
            _require_enum(record, "fact_confidence", FACT_CONFIDENCE)
            _require_enum(record, "analysis_confidence", ANALYSIS_CONFIDENCE)
            _require_enum(record, "status", ATOM_STATUS)
        elif record_type == "usage":
            ids = _require(record, "atom_ids", list)
            if not ids or any(
                not isinstance(atom_id, str) or atom_id not in atom_ids
                for atom_id in ids
            ):
                raise ValidationError(f"{record_id} has missing or invalid atom_ids")
            scope = _require(record, "scope", str)
            event = _require(record, "event_type", str)
            if scope == "project" and event not in PROJECT_EVENTS:
                raise ValidationError(f"{record_id} project scope cannot use event {event}")
            if scope == "library" and event not in LIBRARY_EVENTS:
                raise ValidationError(f"{record_id} library scope cannot use event {event}")
            if scope not in {"project", "library"}:
                raise ValidationError(f"{record_id} has invalid scope: {scope}")
            for field in (
                "project", "script_position", "usage_role", "transformation",
                "result", "evidence_path",
            ):
                _require(record, field, str)


def _next_id(records: list[dict], prefix: str, date: str) -> str:
    start = f"{prefix}-{date}-"
    numbers = [
        int(record["id"].rsplit("-", 1)[1])
        for record in records
        if record.get("id", "").startswith(start)
    ]
    return f"{start}{max(numbers, default=0) + 1:03d}"


@contextmanager
def _exclusive_lock(path: Path) -> Iterator[None]:
    digest = hashlib.sha256(str(path.resolve()).encode("utf-8")).hexdigest()[:20]
    lock_path = Path(tempfile.gettempdir()) / f"laohu-story-material-{digest}.lock"
    with lock_path.open("a+", encoding="utf-8") as handle:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


def _write_records(path: Path, records: list[dict]) -> None:
    validate_records(records)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            "w", encoding="utf-8", dir=path.parent,
            prefix=f".{path.name}.", delete=False,
        ) as handle:
            temporary = Path(handle.name)
            os.chmod(temporary, 0o600)
            for record in records:
                handle.write(
                    json.dumps(record, ensure_ascii=False, separators=(",", ":")) + "\n"
                )
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if temporary is not None and temporary.exists():
            temporary.unlink()


def add_source(path: Path, payload: dict) -> dict:
    if payload.get("record_type") not in {None, "source"}:
        raise ValidationError("add_source cannot ingest non-source records")
    with _exclusive_lock(path):
        records = load_records(path)
        moment = _now()
        record = dict(payload)
        record.update(
            record_type="source",
            id=_next_id(records, "SRC", moment.strftime("%Y%m%d")),
            created_at=moment.isoformat(timespec="seconds"),
        )
        updated = [*records, record]
        validate_records(updated)
        _write_records(path, updated)
        return record


def add_atoms(path: Path, payloads: list[dict]) -> list[dict]:
    if not payloads:
        raise ValidationError("add_atoms requires at least one atom")
    if any(payload.get("record_type") not in {None, "atom"} for payload in payloads):
        raise ValidationError("add_atoms cannot ingest non-atom records")
    with _exclusive_lock(path):
        records = load_records(path)
        moment = _now()
        created: list[dict] = []
        for payload in payloads:
            record = dict(payload)
            record.update(
                record_type="atom",
                id=_next_id(
                    [*records, *created], "ATM", moment.strftime("%Y%m%d")
                ),
                created_at=moment.isoformat(timespec="seconds"),
            )
            created.append(record)
        updated = [*records, *created]
        validate_records(updated)
        _write_records(path, updated)
        return created


def log_usage(path: Path, payload: dict) -> dict:
    if payload.get("record_type") not in {None, "usage"}:
        raise ValidationError("log_usage cannot ingest non-usage records")
    with _exclusive_lock(path):
        records = load_records(path)
        moment = _now()
        record = dict(payload)
        record.update(
            record_type="usage",
            id=_next_id(records, "USE", moment.strftime("%Y%m%d")),
            created_at=moment.isoformat(timespec="seconds"),
        )
        updated = [*records, record]
        validate_records(updated)
        _write_records(path, updated)
        return record


def _effective_status(atom: dict, usage: list[dict]) -> str:
    status = atom["status"]
    if status != "callable":
        return status
    for event in usage:
        if event["scope"] != "library" or atom["id"] not in event["atom_ids"]:
            continue
        status = "paused" if event["event_type"] == "paused" else "callable"
    return status


def _values(record: dict, field: str, source: dict, effective_status: str) -> set[str]:
    if field == "curation_priority":
        value = source["curation_priority"]
    elif field == "effective_status":
        value = effective_status
    else:
        value = record.get(field, [])
    if isinstance(value, str):
        return {value}
    if isinstance(value, list):
        return {item for item in value if isinstance(item, str)}
    return set()


def search_records(path: Path, query: dict) -> list[dict]:
    records = load_records(path)
    validate_records(records)
    sources = {
        record["id"]: record for record in records
        if record["record_type"] == "source"
    }
    atoms = [record for record in records if record["record_type"] == "atom"]
    usage = [record for record in records if record["record_type"] == "usage"]
    must = query.get("must", {})
    prefer = query.get("prefer", {})
    if not isinstance(must, dict) or not isinstance(prefer, dict):
        raise ValidationError("search must and prefer must be objects")
    for section_name, section in (("must", must), ("prefer", prefer)):
        for field, wanted in section.items():
            if not isinstance(wanted, list) or any(
                not isinstance(value, str) for value in wanted
            ):
                raise ValidationError(
                    f"search {section_name}.{field} must be an array of strings"
                )
    exclude_ids = set(query.get("exclude_ids", []))
    limit = max(1, int(query.get("limit", 20)))
    per_source_limit = max(1, int(query.get("per_source_limit", 2)))
    candidates: list[dict] = []
    for atom in atoms:
        source = sources[atom["source_id"]]
        status = _effective_status(atom, usage)
        if (
            source["status"] != "active"
            or status != "callable"
            or atom["id"] in exclude_ids
        ):
            continue
        if any(
            not (_values(atom, field, source, status) & set(wanted))
            for field, wanted in must.items()
        ):
            continue
        score = sum(
            SEARCH_WEIGHTS.get(field, 1)
            * len(_values(atom, field, source, status) & set(wanted))
            for field, wanted in prefer.items()
        )
        project_events = [
            event for event in usage
            if event["scope"] == "project" and atom["id"] in event["atom_ids"]
        ]
        item = {field: atom[field] for field in COMPACT_FIELDS}
        item.update(
            curation_priority=source["curation_priority"],
            effective_status=status,
            usage_summary={
                "shortlisted": sum(
                    event["event_type"] == "shortlisted"
                    for event in project_events
                ),
                "used": sum(
                    event["event_type"] == "used" for event in project_events
                ),
                "validated": sum(
                    event["event_type"] == "validated"
                    for event in project_events
                ),
                "rejected": sum(
                    event["event_type"] == "rejected"
                    for event in project_events
                ),
                "latest_result": project_events[-1]["result"] if project_events else "",
            },
            score=score,
        )
        candidates.append(item)
    candidates.sort(
        key=lambda item: (
            -item["score"],
            item["curation_priority"] != "laohu_selected",
            item["id"],
        )
    )
    selected: list[dict] = []
    source_counts: Counter[str] = Counter()
    for item in candidates:
        if source_counts[item["source_id"]] >= per_source_limit:
            continue
        selected.append(item)
        source_counts[item["source_id"]] += 1
        if len(selected) >= limit:
            break
    return selected


def get_records(path: Path, atom_ids: list[str]) -> dict:
    records = load_records(path)
    validate_records(records)
    wanted = set(atom_ids)
    atoms = [
        record for record in records
        if record["record_type"] == "atom" and record["id"] in wanted
    ]
    found = {atom["id"] for atom in atoms}
    if found != wanted:
        missing = sorted(wanted - found)
        raise ValidationError("unknown atom ids: " + ", ".join(missing))
    source_ids = {atom["source_id"] for atom in atoms}
    return {
        "atoms": atoms,
        "sources": [
            record for record in records
            if record["record_type"] == "source" and record["id"] in source_ids
        ],
        "usage": [
            record for record in records
            if record["record_type"] == "usage"
            and wanted.intersection(record["atom_ids"])
        ],
    }


def stats(path: Path) -> dict:
    records = load_records(path)
    validate_records(records)
    sources = [record for record in records if record["record_type"] == "source"]
    source_by_id = {source["id"]: source for source in sources}
    atoms = [record for record in records if record["record_type"] == "atom"]
    usage = [record for record in records if record["record_type"] == "usage"]
    project_used = {
        atom_id
        for event in usage
        if event["scope"] == "project"
        for atom_id in event["atom_ids"]
    }
    callable_atoms = [
        atom for atom in atoms
        if source_by_id[atom["source_id"]]["status"] == "active"
        and _effective_status(atom, usage) == "callable"
    ]
    top: dict[str, list[list[object]]] = {}
    for field in (
        "relationships", "mechanisms", "dramatic_functions", "themes", "emotions",
    ):
        counts = Counter(value for atom in atoms for value in atom[field])
        top[field] = [[value, count] for value, count in counts.most_common(10)]
    return {
        "source_count": len(sources),
        "atom_count": len(atoms),
        "callable_count": len(callable_atoms),
        "usage_count": len(usage),
        "recent_atom_ids": [
            atom["id"]
            for atom in sorted(
                atoms, key=lambda item: item["created_at"], reverse=True
            )[:10]
        ],
        "long_unused_atom_ids": [
            atom["id"] for atom in callable_atoms
            if atom["id"] not in project_used
        ][:10],
        "top": top,
    }


def _read_payload(location: str) -> object:
    text = (
        sys.stdin.read()
        if location == "-"
        else Path(location).read_text(encoding="utf-8")
    )
    return json.loads(text)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", type=Path, default=DEFAULT_DB)
    subparsers = parser.add_subparsers(dest="command", required=True)
    for name in ("add-source", "add-atoms", "search", "log-usage"):
        command = subparsers.add_parser(name)
        command.add_argument("--input", required=True)
    get = subparsers.add_parser("get")
    get.add_argument("--id", action="append", required=True)
    subparsers.add_parser("stats")
    subparsers.add_parser("validate")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        if args.command == "add-source":
            payload = _read_payload(args.input)
            if not isinstance(payload, dict):
                raise ValidationError("add-source input must be an object")
            result = add_source(args.db, payload)
        elif args.command == "add-atoms":
            payload = _read_payload(args.input)
            if not isinstance(payload, list) or any(
                not isinstance(item, dict) for item in payload
            ):
                raise ValidationError("add-atoms input must be an array of objects")
            result = add_atoms(args.db, payload)
        elif args.command == "search":
            payload = _read_payload(args.input)
            if not isinstance(payload, dict):
                raise ValidationError("search input must be an object")
            result = search_records(args.db, payload)
        elif args.command == "get":
            result = get_records(args.db, args.id)
        elif args.command == "log-usage":
            payload = _read_payload(args.input)
            if not isinstance(payload, dict):
                raise ValidationError("log-usage input must be an object")
            result = log_usage(args.db, payload)
        elif args.command == "stats":
            result = stats(args.db)
        else:
            records = load_records(args.db)
            validate_records(records)
            result = {"ok": True, "record_count": len(records)}
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (ValidationError, json.JSONDecodeError) as exc:
        print(
            json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False),
            file=sys.stderr,
        )
        return 2
    except OSError as exc:
        print(
            json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False),
            file=sys.stderr,
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
