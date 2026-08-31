#!/usr/bin/env python3
"""Layered private store for story sources, atom references, usage, and search index."""

from __future__ import annotations

import fcntl
import hashlib
import json
import os
import re
import sqlite3
import tempfile
from collections import Counter
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Iterator


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
TERM_FIELDS = {
    "human_truth", "mechanisms", "material_types", "dramatic_functions",
    "memory_carriers", "relationships", "emotions", "themes",
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
SCOPE_LEVELS = {"story", "sequence", "scene", "beat", "texture"}
SESSION_PATTERN = re.compile(r"^RET-\d{8}-\d{3,}$")


class ValidationError(ValueError):
    """Raised when the layered material store contract would be violated."""


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


def _validate_source(record: dict) -> None:
    if record.get("record_type") != "source":
        raise ValidationError("source record_type must be source")
    _validate_common(record, "SRC")
    if not _require(record, "original", str).strip():
        raise ValidationError(f"{record['id']} original cannot be empty")
    _require_enum(record, "source_type", SOURCE_TYPES)
    _require_enum(record, "fact_status", FACT_STATUS)
    _require_enum(record, "curation_priority", CURATION)
    _require_enum(record, "status", SOURCE_STATUS)
    if _require(record, "privacy", str) != "private":
        raise ValidationError(f"{record['id']} privacy must be private")
    for field in ("source_url", "source_title", "rights_note"):
        _require(record, field, str)


def _validate_atom(record: dict, source_ids: set[str]) -> None:
    if record.get("record_type") != "atom":
        raise ValidationError("atom record_type must be atom")
    _validate_common(record, "ATM")
    if _require(record, "source_id", str) not in source_ids:
        raise ValidationError(f"{record['id']} references missing source")
    if not _require(record, "atom", str).strip():
        raise ValidationError(f"{record['id']} atom cannot be empty")
    for field in LIST_FIELDS:
        values = _require(record, field, list)
        if any(not isinstance(value, str) or not value.strip() for value in values):
            raise ValidationError(f"{record['id']} field {field} must contain non-empty strings")
    _require(record, "non_replaceable", str)
    _require(record, "fit", dict)
    _require_enum(record, "fact_confidence", FACT_CONFIDENCE)
    _require_enum(record, "analysis_confidence", ANALYSIS_CONFIDENCE)
    _require_enum(record, "status", ATOM_STATUS)


def _validate_usage(record: dict, atom_ids: set[str]) -> None:
    if record.get("record_type") != "usage":
        raise ValidationError("usage record_type must be usage")
    _validate_common(record, "USE")
    ids = _require(record, "atom_ids", list)
    if not ids or any(not isinstance(atom_id, str) or atom_id not in atom_ids for atom_id in ids):
        raise ValidationError(f"{record['id']} has missing or invalid atom_ids")
    scope = _require(record, "scope", str)
    event = _require(record, "event_type", str)
    if scope == "project" and event not in PROJECT_EVENTS:
        raise ValidationError(f"{record['id']} project scope cannot use event {event}")
    if scope == "library" and event not in LIBRARY_EVENTS:
        raise ValidationError(f"{record['id']} library scope cannot use event {event}")
    if scope not in {"project", "library"}:
        raise ValidationError(f"{record['id']} has invalid scope: {scope}")
    for field in (
        "project", "script_position", "usage_role", "transformation",
        "result", "evidence_path",
    ):
        _require(record, field, str)


def _validate_common(record: dict, prefix: str) -> None:
    record_id = _require(record, "id", str)
    if not ID_PATTERN.fullmatch(record_id) or not record_id.startswith(prefix + "-"):
        raise ValidationError(f"invalid {prefix} record id: {record_id}")
    _require(record, "created_at", str)


def _atomic_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            "w", encoding="utf-8", dir=path.parent, prefix=f".{path.name}.", delete=False,
        ) as handle:
            temporary = Path(handle.name)
            os.chmod(temporary, 0o600)
            json.dump(value, handle, ensure_ascii=False, separators=(",", ":"))
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if temporary is not None and temporary.exists():
            temporary.unlink()


def _read_json(path: Path) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValidationError(f"invalid JSON in {path}: {exc.msg}") from exc
    if not isinstance(value, dict):
        raise ValidationError(f"{path} must contain a JSON object")
    return value


def _append_private_jsonl(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor = os.open(path, os.O_WRONLY | os.O_APPEND | os.O_CREAT, 0o600)
    try:
        os.chmod(path, 0o600)
        with os.fdopen(descriptor, "a", encoding="utf-8") as handle:
            descriptor = -1
            handle.write(json.dumps(value, ensure_ascii=False, separators=(",", ":")) + "\n")
            handle.flush()
            os.fsync(handle.fileno())
    finally:
        if descriptor >= 0:
            os.close(descriptor)


class StoryMaterialStore:
    """File authority with a rebuildable SQLite search projection."""

    def __init__(self, root: Path):
        self.root = Path(root)
        self.index_path = self.root / "index" / "story_material.sqlite3"
        self.manifest_path = self.root / "manifest.json"

    def source_path(self, source_id: str) -> Path:
        date = self._id_date(source_id, "SRC")
        return self.root / "sources" / date[:4] / date[4:6] / f"{source_id}.json"

    def atom_path(self, atom_id: str) -> Path:
        date = self._id_date(atom_id, "ATM")
        return self.root / "atoms" / date[:4] / date[4:6] / f"{atom_id}.json"

    def usage_path(self, created_at: str) -> Path:
        try:
            date = datetime.fromisoformat(created_at).date()
        except ValueError as exc:
            raise ValidationError(f"invalid usage created_at: {created_at}") from exc
        return self.root / "usage" / f"{date.year:04d}" / f"{date.month:02d}.jsonl"

    def add_source(self, payload: dict) -> dict:
        with self._lock():
            moment = _now()
            record = dict(payload)
            record.update(
                record_type="source",
                id=self._next_id("SRC", moment.strftime("%Y%m%d")),
                created_at=moment.isoformat(timespec="seconds"),
            )
            _validate_source(record)
            path = self.source_path(record["id"])
            if path.exists():
                raise ValidationError(f"duplicate record id: {record['id']}")
            _atomic_json(path, record)
            self.rebuild_index()
            return record

    def add_atoms(self, payloads: list[dict]) -> list[dict]:
        if not payloads:
            raise ValidationError("add_atoms requires at least one atom")
        with self._lock():
            sources = {record["id"] for record in self.load_sources()}
            moment = _now()
            created: list[dict] = []
            for payload in payloads:
                record = dict(payload)
                record.update(
                    record_type="atom",
                    id=self._next_id("ATM", moment.strftime("%Y%m%d"), created),
                    created_at=moment.isoformat(timespec="seconds"),
                )
                _validate_atom(record, sources)
                if self.atom_path(record["id"]).exists():
                    raise ValidationError(f"duplicate record id: {record['id']}")
                created.append(record)
            for record in created:
                _atomic_json(self.atom_path(record["id"]), record)
            self.rebuild_index()
            return created

    def log_usage(self, payload: dict) -> dict:
        with self._lock():
            atoms = {record["id"] for record in self.load_atoms()}
            moment = _now()
            record = dict(payload)
            record.update(
                record_type="usage",
                id=self._next_id("USE", moment.strftime("%Y%m%d")),
                created_at=moment.isoformat(timespec="seconds"),
            )
            _validate_usage(record, atoms)
            path = self.usage_path(record["created_at"])
            _append_private_jsonl(path, record)
            self.rebuild_index()
            return record

    def get_atoms(self, atom_ids: list[str]) -> list[dict]:
        records: list[dict] = []
        for atom_id in atom_ids:
            path = self.atom_path(atom_id)
            if not path.is_file():
                raise ValidationError(f"unknown atom id: {atom_id}")
            records.append(_read_json(path))
        return records

    def get_sources(self, source_ids: list[str]) -> list[dict]:
        records: list[dict] = []
        for source_id in source_ids:
            path = self.source_path(source_id)
            if not path.is_file():
                raise ValidationError(f"unknown source id: {source_id}")
            records.append(_read_json(path))
        return records

    def get_usage(self, atom_ids: list[str]) -> list[dict]:
        wanted = set(atom_ids)
        known = {record["id"] for record in self.load_atoms()}
        missing = wanted - known
        if missing:
            raise ValidationError("unknown atom ids: " + ", ".join(sorted(missing)))
        return [record for record in self.load_usage() if wanted.intersection(record["atom_ids"])]

    def load_sources(self) -> list[dict]:
        return [_read_json(path) for path in sorted((self.root / "sources").glob("*/*/*.json"))]

    def load_atoms(self) -> list[dict]:
        return [_read_json(path) for path in sorted((self.root / "atoms").glob("*/*/*.json"))]

    def load_usage(self) -> list[dict]:
        records: list[dict] = []
        for path in sorted((self.root / "usage").glob("*/*.jsonl")):
            for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
                if not line.strip():
                    continue
                try:
                    value = json.loads(line)
                except json.JSONDecodeError as exc:
                    raise ValidationError(f"invalid JSON in {path}:{line_number}: {exc.msg}") from exc
                if not isinstance(value, dict):
                    raise ValidationError(f"{path}:{line_number} must contain an object")
                records.append(value)
        return records

    def validate(self) -> dict:
        sources = self.load_sources()
        atoms = self.load_atoms()
        usage = self.load_usage()
        seen: set[str] = set()
        for record in sources:
            _validate_source(record)
            if record["id"] in seen:
                raise ValidationError(f"duplicate record id: {record['id']}")
            seen.add(record["id"])
        source_ids = {record["id"] for record in sources}
        for record in atoms:
            _validate_atom(record, source_ids)
            if record["id"] in seen:
                raise ValidationError(f"duplicate record id: {record['id']}")
            seen.add(record["id"])
        atom_ids = {record["id"] for record in atoms}
        for record in usage:
            _validate_usage(record, atom_ids)
            if record["id"] in seen:
                raise ValidationError(f"duplicate record id: {record['id']}")
            seen.add(record["id"])
        return {
            "ok": True,
            "source_count": len(sources),
            "atom_count": len(atoms),
            "usage_count": len(usage),
        }

    def rebuild_index(self) -> dict:
        result = self.validate()
        sources = self.load_sources()
        atoms = self.load_atoms()
        usage = self.load_usage()
        source_by_id = {record["id"]: record for record in sources}
        usage_by_atom: dict[str, list[dict]] = {record["id"]: [] for record in atoms}
        for event in usage:
            for atom_id in event["atom_ids"]:
                usage_by_atom.setdefault(atom_id, []).append(event)

        self.index_path.parent.mkdir(parents=True, exist_ok=True)
        temporary = self.index_path.with_name(f".{self.index_path.name}.tmp")
        if temporary.exists():
            temporary.unlink()
        connection = sqlite3.connect(temporary)
        try:
            connection.executescript(
                """
                PRAGMA journal_mode=DELETE;
                CREATE TABLE sources(
                    id TEXT PRIMARY KEY,
                    source_type TEXT NOT NULL,
                    fact_status TEXT NOT NULL,
                    curation_priority TEXT NOT NULL,
                    status TEXT NOT NULL,
                    detail_path TEXT NOT NULL
                );
                CREATE TABLE atoms(
                    id TEXT PRIMARY KEY,
                    source_id TEXT NOT NULL,
                    atom TEXT NOT NULL,
                    mechanism_hint TEXT NOT NULL,
                    fact_confidence TEXT NOT NULL,
                    analysis_confidence TEXT NOT NULL,
                    status TEXT NOT NULL,
                    detail_path TEXT NOT NULL
                );
                CREATE TABLE atom_terms(
                    atom_id TEXT NOT NULL,
                    field TEXT NOT NULL,
                    value TEXT NOT NULL,
                    PRIMARY KEY(atom_id, field, value)
                );
                CREATE INDEX atom_terms_lookup ON atom_terms(field, value, atom_id);
                CREATE TABLE usage_summary(
                    atom_id TEXT PRIMARY KEY,
                    shortlisted INTEGER NOT NULL,
                    used INTEGER NOT NULL,
                    validated INTEGER NOT NULL,
                    rejected INTEGER NOT NULL,
                    latest_result TEXT NOT NULL
                );
                """
            )
            for source in sources:
                connection.execute(
                    "INSERT INTO sources VALUES(?,?,?,?,?,?)",
                    (
                        source["id"], source["source_type"], source["fact_status"],
                        source["curation_priority"], source["status"],
                        str(self.source_path(source["id"]).relative_to(self.root)),
                    ),
                )
            for atom in atoms:
                events = [event for event in usage_by_atom.get(atom["id"], []) if event["scope"] == "project"]
                effective = self._effective_status(atom, usage_by_atom.get(atom["id"], []))
                connection.execute(
                    "INSERT INTO atoms VALUES(?,?,?,?,?,?,?,?)",
                    (
                        atom["id"], atom["source_id"], atom["atom"],
                        atom["mechanisms"][0] if atom["mechanisms"] else "",
                        atom["fact_confidence"], atom["analysis_confidence"],
                        effective, str(self.atom_path(atom["id"]).relative_to(self.root)),
                    ),
                )
                for field in TERM_FIELDS:
                    for value in atom[field]:
                        connection.execute(
                            "INSERT INTO atom_terms VALUES(?,?,?)",
                            (atom["id"], field, value),
                        )
                connection.execute(
                    "INSERT INTO usage_summary VALUES(?,?,?,?,?,?)",
                    (
                        atom["id"],
                        sum(event["event_type"] == "shortlisted" for event in events),
                        sum(event["event_type"] == "used" for event in events),
                        sum(event["event_type"] == "validated" for event in events),
                        sum(event["event_type"] == "rejected" for event in events),
                        events[-1]["result"] if events else "",
                    ),
                )
            connection.commit()
        finally:
            connection.close()
        os.chmod(temporary, 0o600)
        os.replace(temporary, self.index_path)
        self._write_manifest(result, sources, atoms, usage)
        return result

    def stats(self) -> dict:
        if not self.index_path.is_file():
            self.rebuild_index()
        sources = self.load_sources()
        atoms = self.load_atoms()
        usage = self.load_usage()
        source_by_id = {source["id"]: source for source in sources}
        callable_atoms = [
            atom for atom in atoms
            if source_by_id[atom["source_id"]]["status"] == "active"
            and self._effective_status(atom, [u for u in usage if atom["id"] in u["atom_ids"]]) == "callable"
        ]
        top: dict[str, list[list[object]]] = {}
        for field in ("relationships", "dramatic_functions", "themes", "emotions"):
            counts = Counter(value for atom in atoms for value in atom[field])
            top[field] = [[value, count] for value, count in counts.most_common(10)]
        return {
            "source_count": len(sources),
            "atom_count": len(atoms),
            "callable_count": len(callable_atoms),
            "usage_count": len(usage),
            "top": top,
            "facets_expandable": True,
        }

    def list_facet(
        self,
        field: str,
        *,
        cursor: int = 0,
        page_budget_chars: int = 1200,
    ) -> dict:
        if field not in TERM_FIELDS:
            raise ValidationError(f"unsupported facet field: {field}")
        if not isinstance(cursor, int) or cursor < 0:
            raise ValidationError("facet cursor must be a non-negative integer")
        if not isinstance(page_budget_chars, int) or page_budget_chars < 64:
            raise ValidationError("facet page_budget_chars must be an integer of at least 64")
        if not self.index_path.is_file():
            self.rebuild_index()

        connection = sqlite3.connect(self.index_path)
        try:
            rows = list(connection.execute(
                """
                SELECT value, COUNT(DISTINCT atom_id) AS atom_count
                FROM atom_terms
                WHERE field=?
                GROUP BY value
                ORDER BY atom_count DESC, value
                LIMIT -1 OFFSET ?
                """,
                (field, cursor),
            ))
        finally:
            connection.close()

        items: list[dict] = []
        used = 0
        consumed = 0
        for value, count in rows:
            item = {"value": value, "count": count}
            size = len(json.dumps(item, ensure_ascii=False, separators=(",", ":")))
            if items and used + size > page_budget_chars:
                break
            items.append(item)
            used += size
            consumed += 1
            if used >= page_budget_chars:
                break
        next_cursor = cursor + consumed
        return {
            "field": field,
            "items": items,
            "next_cursor": next_cursor,
            "has_more": next_cursor < cursor + len(rows),
            "page_char_count": used,
        }

    def migrate_legacy(self, legacy_path: Path) -> dict:
        legacy_path = Path(legacy_path)
        records: list[dict] = []
        for line_number, line in enumerate(legacy_path.read_text(encoding="utf-8").splitlines(), start=1):
            if not line.strip():
                continue
            try:
                value = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValidationError(f"invalid JSON at legacy line {line_number}: {exc.msg}") from exc
            if not isinstance(value, dict):
                raise ValidationError(f"legacy line {line_number} must contain an object")
            records.append(value)
        if any(self.root.glob("sources/*/*/*.json")) or any(self.root.glob("atoms/*/*/*.json")):
            raise ValidationError("layered store is not empty")
        sources = [record for record in records if record.get("record_type") == "source"]
        atoms = [record for record in records if record.get("record_type") == "atom"]
        usage = [record for record in records if record.get("record_type") == "usage"]
        source_ids = {record.get("id") for record in sources}
        atom_ids = {record.get("id") for record in atoms}
        for source in sources:
            _validate_source(source)
        for atom in atoms:
            _validate_atom(atom, source_ids)
        for event in usage:
            _validate_usage(event, atom_ids)
        with self._lock():
            for source in sources:
                _atomic_json(self.source_path(source["id"]), source)
            for atom in atoms:
                _atomic_json(self.atom_path(atom["id"]), atom)
            for event in usage:
                path = self.usage_path(event["created_at"])
                _append_private_jsonl(path, event)
            self.rebuild_index()
        migrated = [*self.load_sources(), *self.load_atoms(), *self.load_usage()]
        original_hashes = {record["id"]: self._record_hash(record) for record in records}
        migrated_hashes = {record["id"]: self._record_hash(record) for record in migrated}
        return {
            "source_count": len(sources),
            "atom_count": len(atoms),
            "usage_count": len(usage),
            "equivalent": original_hashes == migrated_hashes,
            "record_hashes": migrated_hashes,
        }

    def start_search(self, query: dict) -> dict:
        normalized = self._validate_search_query(query)
        with self._lock():
            moment = _now()
            session_id = self._next_session_id(moment.strftime("%Y%m%d"))
            session = {
                "session_id": session_id,
                "created_at": moment.isoformat(timespec="seconds"),
                "updated_at": moment.isoformat(timespec="seconds"),
                "status": "active",
                "scope": normalized["scope"],
                "gap": normalized["gap"],
                "responsibilities": normalized["responsibilities"],
                "query": {
                    key: normalized[key]
                    for key in (
                        "must", "prefer", "text_terms", "exclude_ids",
                        "page_budget_chars", "diversity", "expand_source_ids",
                    )
                },
                "cursor": 0,
                "query_round": 1,
                "seen_ids": [],
                "prior_round_ids": [],
                "round_seen_ids": [],
                "shortlist_ids": [],
                "rejected_summaries": [],
                "covered_directions": [],
                "remaining_gaps": [],
            }
            response = self._advance_session(session)
            _atomic_json(self.session_path(session_id), session)
            return response

    def continue_search(self, update: dict) -> dict:
        session_id = _require(update, "session_id", str)
        with self._lock():
            session = self.get_session(session_id)
            if session.get("status") != "active":
                raise ValidationError(f"retrieval session is not active: {session_id}")
            for field in (
                "shortlist_ids", "rejected_summaries", "covered_directions", "remaining_gaps",
            ):
                if field not in update:
                    continue
                values = update[field]
                if not isinstance(values, list):
                    raise ValidationError(f"continue_search {field} must be a list")
                if field == "remaining_gaps":
                    session[field] = values
                else:
                    session[field] = self._merge_unique(session[field], values)
            override = update.get("query_override")
            if override is not None:
                if not isinstance(override, dict):
                    raise ValidationError("query_override must be an object")
                merged = {
                    **session["query"],
                    **override,
                    "scope": session["scope"],
                    "gap": session["gap"],
                    "responsibilities": session["responsibilities"],
                }
                normalized = self._validate_search_query(merged)
                session["query"] = {
                    key: normalized[key]
                    for key in (
                        "must", "prefer", "text_terms", "exclude_ids",
                        "page_budget_chars", "diversity", "expand_source_ids",
                    )
                }
                session["prior_round_ids"] = self._merge_unique(
                    session["prior_round_ids"],
                    session["round_seen_ids"],
                )
                session["round_seen_ids"] = []
                session["cursor"] = 0
                session["query_round"] += 1
            session["updated_at"] = _now().isoformat(timespec="seconds")
            response = self._advance_session(session)
            _atomic_json(self.session_path(session_id), session)
            return response

    def get_session(self, session_id: str) -> dict:
        path = self.session_path(session_id)
        if not path.is_file():
            raise ValidationError(f"unknown retrieval session: {session_id}")
        return _read_json(path)

    def close_session(self, session_id: str) -> dict:
        with self._lock():
            session = self.get_session(session_id)
            session["status"] = "closed"
            session["updated_at"] = _now().isoformat(timespec="seconds")
            _atomic_json(self.session_path(session_id), session)
            return self._session_summary(session)

    def session_path(self, session_id: str) -> Path:
        if not SESSION_PATTERN.fullmatch(session_id):
            raise ValidationError(f"invalid retrieval session id: {session_id}")
        date = session_id.split("-")[1]
        return self.root / "sessions" / date[:4] / date[4:6] / f"{session_id}.json"

    def _advance_session(self, session: dict) -> dict:
        query = dict(session["query"])
        query["exclude_ids"] = self._merge_unique(
            query["exclude_ids"],
            session["prior_round_ids"],
        )
        cards, next_cursor, has_more, char_count = self._search_page(
            query,
            int(session["cursor"]),
        )
        session["cursor"] = next_cursor
        session["seen_ids"] = self._merge_unique(
            session["seen_ids"],
            [card["id"] for card in cards],
        )
        session["round_seen_ids"] = self._merge_unique(
            session["round_seen_ids"],
            [card["id"] for card in cards],
        )
        return {
            "session_id": session["session_id"],
            "cards": cards,
            "next_cursor": next_cursor,
            "has_more": has_more,
            "page_char_count": char_count,
            "session_summary": self._session_summary(session),
        }

    def _search_page(self, query: dict, offset: int) -> tuple[list[dict], int, bool, int]:
        if not self.index_path.is_file():
            self.rebuild_index()
        budget = int(query["page_budget_chars"])
        selected: list[dict] = []
        used = 0
        cursor = offset
        while True:
            rows = self._query_index(query, cursor, 64)
            if not rows:
                return selected, cursor, False, used
            for row in rows:
                card = self._row_to_card(row)
                size = len(json.dumps(card, ensure_ascii=False, separators=(",", ":")))
                if selected and used + size > budget:
                    return selected, cursor, True, used
                selected.append(card)
                used += size
                cursor += 1
                if used >= budget:
                    return selected, cursor, bool(self._query_index(query, cursor, 1)), used
            if len(rows) < 64:
                return selected, cursor, False, used

    def _query_index(self, query: dict, offset: int, amount: int) -> list[sqlite3.Row]:
        must = query["must"]
        prefer = query["prefer"]
        parameters: list[object] = []
        filters = ["s.status = 'active'", "a.status = 'callable'"]
        for field, wanted in must.items():
            if not wanted:
                continue
            placeholders = ",".join("?" for _ in wanted)
            if field in TERM_FIELDS:
                filters.append(
                    "EXISTS (SELECT 1 FROM atom_terms mt "
                    f"WHERE mt.atom_id=a.id AND mt.field=? AND mt.value IN ({placeholders}))"
                )
                parameters.extend([field, *wanted])
            elif field == "curation_priority":
                filters.append(f"s.curation_priority IN ({placeholders})")
                parameters.extend(wanted)
            elif field in {"source_type", "fact_status"}:
                filters.append(f"s.{field} IN ({placeholders})")
                parameters.extend(wanted)
            elif field in {"fact_confidence", "analysis_confidence", "status"}:
                filters.append(f"a.{field} IN ({placeholders})")
                parameters.extend(wanted)
            else:
                raise ValidationError(f"unsupported must field: {field}")
        text_terms = query.get("text_terms", [])
        for term in text_terms:
            filters.append("(a.atom LIKE ? OR a.mechanism_hint LIKE ?)")
            parameters.extend([f"%{term}%", f"%{term}%"])
        excluded = query.get("exclude_ids", [])
        if excluded:
            placeholders = ",".join("?" for _ in excluded)
            filters.append(f"a.id NOT IN ({placeholders})")
            parameters.extend(excluded)
        score_parts: list[str] = []
        score_parameters: list[object] = []
        for field, wanted in prefer.items():
            if not wanted:
                continue
            if field not in TERM_FIELDS:
                raise ValidationError(f"unsupported prefer field: {field}")
            placeholders = ",".join("?" for _ in wanted)
            score_parts.append(
                "(SELECT COUNT(*) FROM atom_terms pt "
                f"WHERE pt.atom_id=a.id AND pt.field=? AND pt.value IN ({placeholders})) * {SEARCH_WEIGHTS.get(field, 1)}"
            )
            score_parameters.extend([field, *wanted])
        score_sql = " + ".join(score_parts) if score_parts else "0"
        expand = query.get("expand_source_ids", [])
        expand_sql = "0"
        expand_parameters: list[object] = []
        if expand:
            placeholders = ",".join("?" for _ in expand)
            expand_sql = f"CASE WHEN a.source_id IN ({placeholders}) THEN 0 ELSE 1 END"
            expand_parameters.extend(expand)
        base = f"""
            SELECT a.id, a.source_id, a.atom, a.mechanism_hint,
                   a.fact_confidence, a.analysis_confidence,
                   s.curation_priority,
                   u.shortlisted, u.used, u.validated, u.rejected, u.latest_result,
                   ({score_sql}) AS score,
                   ({expand_sql}) AS expand_rank
            FROM atoms a
            JOIN sources s ON s.id=a.source_id
            JOIN usage_summary u ON u.atom_id=a.id
            WHERE {' AND '.join(filters)}
        """
        order = "expand_rank, score DESC, CASE s.curation_priority WHEN 'laohu_selected' THEN 0 ELSE 1 END, a.id"
        if query["diversity"] == "balanced" and not expand:
            sql = f"""
                WITH candidates AS ({base}), ranked AS (
                    SELECT candidates.*,
                           ROW_NUMBER() OVER(PARTITION BY source_id ORDER BY score DESC, id) AS source_rank
                    FROM candidates
                )
                SELECT * FROM ranked
                ORDER BY source_rank, score DESC, id
                LIMIT ? OFFSET ?
            """
        else:
            sql = base + f" ORDER BY {order} LIMIT ? OFFSET ?"
        all_parameters = [*score_parameters, *expand_parameters, *parameters, amount, offset]
        connection = sqlite3.connect(self.index_path)
        connection.row_factory = sqlite3.Row
        try:
            return list(connection.execute(sql, all_parameters))
        finally:
            connection.close()

    def _row_to_card(self, row: sqlite3.Row) -> dict:
        wanted_fields = {"relationships", "dramatic_functions", "emotions", "themes"}
        terms: dict[str, list[str]] = {field: [] for field in wanted_fields}
        connection = sqlite3.connect(self.index_path)
        try:
            for field, value in connection.execute(
                "SELECT field,value FROM atom_terms WHERE atom_id=? ORDER BY field,value",
                (row["id"],),
            ):
                if field in terms:
                    terms[field].append(value)
        finally:
            connection.close()
        return {
            "id": row["id"],
            "source_id": row["source_id"],
            "atom": row["atom"],
            "mechanism_hint": row["mechanism_hint"],
            **terms,
            "fact_confidence": row["fact_confidence"],
            "analysis_confidence": row["analysis_confidence"],
            "curation_priority": row["curation_priority"],
            "usage_summary": {
                "shortlisted": row["shortlisted"],
                "used": row["used"],
                "validated": row["validated"],
                "rejected": row["rejected"],
                "latest_result": row["latest_result"],
            },
            "score": row["score"],
        }

    def _validate_search_query(self, query: dict) -> dict:
        if not isinstance(query, dict):
            raise ValidationError("search query must be an object")
        scope = query.get("scope")
        if not isinstance(scope, dict):
            raise ValidationError("search scope must be an object")
        for field in ("work", "level", "id"):
            if not isinstance(scope.get(field), str) or not scope[field].strip():
                raise ValidationError(f"search scope.{field} must be a non-empty string")
        if scope["level"] not in SCOPE_LEVELS:
            raise ValidationError(f"unsupported search scope level: {scope['level']}")
        gap = query.get("gap")
        if not isinstance(gap, str) or not gap.strip():
            raise ValidationError("search gap must be a non-empty string")
        responsibilities = query.get("responsibilities")
        if not isinstance(responsibilities, list) or any(
            not isinstance(value, str) or not value.strip() for value in responsibilities
        ):
            raise ValidationError("search responsibilities must be a string list")
        normalized = dict(query)
        for section_name in ("must", "prefer"):
            section = normalized.get(section_name, {})
            if not isinstance(section, dict):
                raise ValidationError(f"search {section_name} must be an object")
            for field, values in section.items():
                if not isinstance(values, list) or any(not isinstance(value, str) for value in values):
                    raise ValidationError(f"search {section_name}.{field} must be a string list")
            normalized[section_name] = section
        text_terms = normalized.get("text_terms", [])
        if isinstance(text_terms, str):
            text_terms = [text_terms]
        if not isinstance(text_terms, list) or any(not isinstance(value, str) for value in text_terms):
            raise ValidationError("search text_terms must be a string or string list")
        normalized["text_terms"] = text_terms
        for field in ("exclude_ids", "expand_source_ids"):
            values = normalized.get(field, [])
            if not isinstance(values, list) or any(not isinstance(value, str) for value in values):
                raise ValidationError(f"search {field} must be a string list")
            normalized[field] = values
        try:
            budget = int(normalized.get("page_budget_chars", 4000))
        except (TypeError, ValueError) as exc:
            raise ValidationError("page_budget_chars must be an integer") from exc
        if budget < 1:
            raise ValidationError("page_budget_chars must be positive")
        normalized["page_budget_chars"] = budget
        diversity = normalized.get("diversity", "balanced")
        if diversity not in {"balanced", "open"}:
            raise ValidationError("search diversity must be balanced or open")
        normalized["diversity"] = diversity
        return normalized

    @staticmethod
    def _merge_unique(existing: list, incoming: list) -> list:
        result = list(existing)
        for value in incoming:
            if value not in result:
                result.append(value)
        return result

    @staticmethod
    def _session_summary(session: dict) -> dict:
        return {
            "scope": session["scope"],
            "gap": session["gap"],
            "responsibilities": session["responsibilities"],
            "query_round": session["query_round"],
            "seen_count": len(session["seen_ids"]),
            "shortlist_ids": session["shortlist_ids"],
            "rejected_summaries": session["rejected_summaries"],
            "covered_directions": session["covered_directions"],
            "remaining_gaps": session["remaining_gaps"],
        }

    def _next_session_id(self, date: str) -> str:
        start = f"RET-{date}-"
        ids = [path.stem for path in (self.root / "sessions").glob("*/*/RET-*.json")]
        numbers = [int(value.rsplit("-", 1)[1]) for value in ids if value.startswith(start)]
        return f"{start}{max(numbers, default=0) + 1:03d}"

    def _write_manifest(self, result: dict, sources: list[dict], atoms: list[dict], usage: list[dict]) -> None:
        value = {
            "schema_version": 2,
            "authority": {
                "sources": "sources/YYYY/MM/SRC-*.json",
                "atoms": "atoms/YYYY/MM/ATM-*.json",
                "usage": "usage/YYYY/MM.jsonl",
            },
            "rebuildable_index": "index/story_material.sqlite3",
            "source_original_in_index": False,
            "counts": result,
            "updated_at": _now().isoformat(timespec="seconds"),
        }
        _atomic_json(self.manifest_path, value)

    @staticmethod
    def _record_hash(record: dict) -> str:
        encoded = json.dumps(record, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(encoded.encode("utf-8")).hexdigest()

    @staticmethod
    def _effective_status(atom: dict, events: list[dict]) -> str:
        status = atom["status"]
        if status != "callable":
            return status
        for event in events:
            if event["scope"] != "library" or atom["id"] not in event["atom_ids"]:
                continue
            status = "paused" if event["event_type"] == "paused" else "callable"
        return status

    def _next_id(self, prefix: str, date: str, pending: list[dict] | None = None) -> str:
        if prefix == "SRC":
            ids = [record["id"] for record in self.load_sources()]
        elif prefix == "ATM":
            ids = [record["id"] for record in self.load_atoms()]
        else:
            ids = [record["id"] for record in self.load_usage()]
        ids.extend(record["id"] for record in (pending or []))
        start = f"{prefix}-{date}-"
        numbers = [int(record_id.rsplit("-", 1)[1]) for record_id in ids if record_id.startswith(start)]
        return f"{start}{max(numbers, default=0) + 1:03d}"

    @staticmethod
    def _id_date(record_id: str, prefix: str) -> str:
        if not ID_PATTERN.fullmatch(record_id) or not record_id.startswith(prefix + "-"):
            raise ValidationError(f"invalid {prefix} id: {record_id}")
        return record_id.split("-")[1]

    @contextmanager
    def _lock(self) -> Iterator[None]:
        digest = hashlib.sha256(str(self.root.resolve()).encode("utf-8")).hexdigest()[:20]
        lock_path = Path(tempfile.gettempdir()) / f"laohu-story-material-layered-{digest}.lock"
        with lock_path.open("a+", encoding="utf-8") as handle:
            fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
            try:
                yield
            finally:
                fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
