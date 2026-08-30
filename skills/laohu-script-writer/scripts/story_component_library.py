#!/usr/bin/env python3
"""Validate and progressively query the de-identified story component library."""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[3]
DEFAULT_LIBRARY = (
    ROOT / "skills" / "laohu-script-writer" / "references" / "07_故事构件库.jsonl"
)
ID_PATTERN = re.compile(r"^CMP-\d{3,}$")

CATEGORIES = {
    "人性与关系",
    "欲望与目标",
    "错误方法",
    "触发",
    "约束",
    "加压",
    "信息",
    "代价与残留",
    "选择",
    "回收",
    "感官载体",
    "场景条件",
    "传播",
}
STATUSES = {"seed", "observed", "used", "validated", "paused"}
EVIDENCE_STATUSES = {
    "theory_supported",
    "multi_source_observed",
    "project_used",
    "real_result",
}
LIST_FIELDS = {
    "dramatic_functions",
    "preconditions",
    "visible_evidence",
    "compatible_tags",
    "conflict_tags",
    "failure_modes",
    "boundaries",
    "source_refs",
}
AUDIENCE_FIELDS = {"knows", "believes", "waits_for"}
PRIVATE_FIELDS = {
    "original",
    "source_id",
    "source_url",
    "privacy",
    "source_title",
    "non_replaceable",
}
COMPACT_FIELDS = (
    "id",
    "name",
    "category",
    "dramatic_functions",
    "operation",
    "state_change",
    "compatible_tags",
    "conflict_tags",
    "evidence_status",
    "status",
)
SEARCH_WEIGHTS = {
    "dramatic_functions": 5,
    "category": 4,
    "compatible_tags": 3,
    "state_change": 2,
    "name": 1,
    "operation": 1,
    "evidence_status": 1,
    "status": 1,
}


class ValidationError(ValueError):
    """Raised when a component record or query violates the library contract."""


def _require(record: dict, field: str, expected_type: type):
    value = record.get(field)
    if not isinstance(value, expected_type):
        raise ValidationError(
            f"{record.get('id', '<unknown>')} field {field} must be "
            f"{expected_type.__name__}"
        )
    return value


def _require_text(record: dict, field: str) -> str:
    value = _require(record, field, str)
    if not value.strip():
        raise ValidationError(f"{record.get('id', '<unknown>')} field {field} is empty")
    return value


def _require_string_list(record: dict, field: str) -> list[str]:
    values = _require(record, field, list)
    if any(not isinstance(value, str) or not value.strip() for value in values):
        raise ValidationError(
            f"{record.get('id', '<unknown>')} field {field} must contain strings"
        )
    return values


def load_records(path: Path) -> list[dict]:
    if not path.is_file():
        raise ValidationError(f"component library does not exist: {path}")
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
                raise ValidationError(f"line {line_number} must be a JSON object")
            records.append(value)
    return records


def validate_records(records: list[dict]) -> None:
    seen: set[str] = set()
    for record in records:
        if record.get("record_type") != "component":
            raise ValidationError("story component library accepts component records only")
        forbidden = PRIVATE_FIELDS.intersection(record)
        if forbidden:
            raise ValidationError(
                f"{record.get('id', '<unknown>')} contains private source fields: "
                + ", ".join(sorted(forbidden))
            )

        component_id = _require_text(record, "id")
        if not ID_PATTERN.fullmatch(component_id):
            raise ValidationError(f"invalid component id: {component_id}")
        if component_id in seen:
            raise ValidationError(f"duplicate component id: {component_id}")
        seen.add(component_id)

        _require_text(record, "name")
        category = _require_text(record, "category")
        if category not in CATEGORIES:
            raise ValidationError(f"{component_id} has unknown category: {category}")
        _require_text(record, "character_intention")
        _require_text(record, "operation")

        for field in LIST_FIELDS:
            _require_string_list(record, field)

        state_change = _require(record, "state_change", dict)
        for field in ("before", "after"):
            value = state_change.get(field)
            if not isinstance(value, str) or not value.strip():
                raise ValidationError(
                    f"{component_id} state_change.{field} must be non-empty"
                )

        audience_shift = _require(record, "audience_shift", dict)
        if set(audience_shift) != AUDIENCE_FIELDS:
            raise ValidationError(
                f"{component_id} audience_shift must contain "
                + ", ".join(sorted(AUDIENCE_FIELDS))
            )
        for field in AUDIENCE_FIELDS:
            values = audience_shift[field]
            if not isinstance(values, list) or any(
                not isinstance(value, str) or not value.strip() for value in values
            ):
                raise ValidationError(
                    f"{component_id} audience_shift.{field} must contain strings"
                )

        fit = _require(record, "fit", dict)
        for field in ("lengths", "positions"):
            values = fit.get(field)
            if not isinstance(values, list) or any(
                not isinstance(value, str) or not value.strip() for value in values
            ):
                raise ValidationError(f"{component_id} fit.{field} must contain strings")

        evidence_status = _require_text(record, "evidence_status")
        if evidence_status not in EVIDENCE_STATUSES:
            raise ValidationError(
                f"{component_id} has unknown evidence_status: {evidence_status}"
            )
        status = _require_text(record, "status")
        if status not in STATUSES:
            raise ValidationError(f"{component_id} has unknown status: {status}")


def stats(records: list[dict]) -> dict:
    validate_records(records)
    callable_records = [record for record in records if record["status"] != "paused"]
    return {
        "total": len(records),
        "callable": len(callable_records),
        "categories": dict(sorted(Counter(r["category"] for r in records).items())),
        "statuses": dict(sorted(Counter(r["status"] for r in records).items())),
        "evidence_statuses": dict(
            sorted(Counter(r["evidence_status"] for r in records).items())
        ),
        "recent_ids": [record["id"] for record in records[-10:]],
    }


def _as_search_text(value) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        return " ".join(_as_search_text(item) for item in value)
    if isinstance(value, dict):
        return " ".join(_as_search_text(item) for item in value.values())
    return ""


def _matches(record: dict, field: str, expected: Iterable[str]) -> bool:
    haystack = _as_search_text(record.get(field, ""))
    return all(value in haystack for value in expected)


def _validate_query(query: dict) -> None:
    if not isinstance(query, dict):
        raise ValidationError("search query must be an object")
    for section in ("must", "prefer"):
        value = query.get(section, {})
        if not isinstance(value, dict):
            raise ValidationError(f"query {section} must be an object")
        for field, expected in value.items():
            if field not in SEARCH_WEIGHTS:
                raise ValidationError(f"unsupported search field: {field}")
            if not isinstance(expected, list) or any(
                not isinstance(item, str) or not item.strip() for item in expected
            ):
                raise ValidationError(f"query {section}.{field} must contain strings")
    exclude_ids = query.get("exclude_ids", [])
    if not isinstance(exclude_ids, list) or any(
        not isinstance(value, str) for value in exclude_ids
    ):
        raise ValidationError("exclude_ids must be a string list")
    limit = query.get("limit", 12)
    if not isinstance(limit, int) or limit < 1 or limit > 200:
        raise ValidationError("limit must be an integer from 1 to 200")
    if not isinstance(query.get("include_paused", False), bool):
        raise ValidationError("include_paused must be boolean")


def search(records: list[dict], query: dict) -> list[dict]:
    validate_records(records)
    _validate_query(query)
    must = query.get("must", {})
    prefer = query.get("prefer", {})
    exclude_ids = set(query.get("exclude_ids", []))
    include_paused = query.get("include_paused", False)
    ranked: list[tuple[int, str, dict]] = []

    for record in records:
        if record["id"] in exclude_ids:
            continue
        if record["status"] == "paused" and not include_paused:
            continue
        if any(not _matches(record, field, values) for field, values in must.items()):
            continue
        score = 0
        for field, values in prefer.items():
            haystack = _as_search_text(record.get(field, ""))
            score += SEARCH_WEIGHTS[field] * sum(value in haystack for value in values)
        compact = {field: record[field] for field in COMPACT_FIELDS}
        compact["score"] = score
        ranked.append((-score, record["id"], compact))

    ranked.sort(key=lambda item: (item[0], item[1]))
    return [item[2] for item in ranked[: query.get("limit", 12)]]


def get_records(records: list[dict], ids: list[str]) -> list[dict]:
    validate_records(records)
    if not ids:
        raise ValidationError("get requires at least one component id")
    requested = set(ids)
    found = [record for record in records if record["id"] in requested]
    missing = requested.difference(record["id"] for record in found)
    if missing:
        raise ValidationError("unknown component ids: " + ", ".join(sorted(missing)))
    return found


def _read_query(path: str) -> dict:
    if path == "-":
        raw = sys.stdin.read()
    else:
        raw = Path(path).read_text(encoding="utf-8")
    try:
        value = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValidationError(f"invalid query JSON: {exc.msg}") from exc
    if not isinstance(value, dict):
        raise ValidationError("query JSON must be an object")
    return value


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", type=Path, default=DEFAULT_LIBRARY)
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("validate")
    subparsers.add_parser("stats")
    search_parser = subparsers.add_parser("search")
    search_parser.add_argument("--input", required=True)
    get_parser = subparsers.add_parser("get")
    get_parser.add_argument("--id", action="append", required=True)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        records = load_records(args.db)
        validate_records(records)
        if args.command == "validate":
            result = {"valid": True, "records": len(records)}
        elif args.command == "stats":
            result = stats(records)
        elif args.command == "search":
            result = search(records, _read_query(args.input))
        else:
            result = get_records(records, args.id)
    except (OSError, ValidationError) as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
