#!/usr/bin/env python3
"""CLI façade for the layered story-material authority and retrieval sessions."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
DEFAULT_ROOT = ROOT / "00_输入原料" / "故事素材库"


def _read_payload(location: str) -> object:
    text = sys.stdin.read() if location == "-" else Path(location).read_text(encoding="utf-8")
    return json.loads(text)


def _load_store():
    scripts_dir = str(Path(__file__).resolve().parent)
    if scripts_dir not in sys.path:
        sys.path.insert(0, scripts_dir)
    from story_material_store import StoryMaterialStore, ValidationError

    return StoryMaterialStore, ValidationError


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Layered private story-material store and dynamic retrieval controller."
    )
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    subparsers = parser.add_subparsers(dest="command", required=True)

    for name in (
        "add-source", "add-atoms", "log-usage", "search-index", "continue-search",
        "facet-values",
    ):
        command = subparsers.add_parser(name)
        command.add_argument("--input", required=True)

    for name in ("get-atom", "get-source"):
        command = subparsers.add_parser(name)
        command.add_argument("--id", action="append", required=True)

    usage = subparsers.add_parser("get-usage")
    usage.add_argument("--atom-id", action="append", required=True)

    for name in ("get-session", "close-session"):
        command = subparsers.add_parser(name)
        command.add_argument("--id", required=True)

    migration = subparsers.add_parser("migrate-legacy")
    migration.add_argument("--legacy-db", type=Path, required=True)
    subparsers.add_parser("stats")
    subparsers.add_parser("validate")
    subparsers.add_parser("rebuild-index")
    return parser


def _object_payload(location: str, command: str) -> dict:
    payload = _read_payload(location)
    if not isinstance(payload, dict):
        raise ValueError(f"{command} input must be an object")
    return payload


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    StoryMaterialStore, ValidationError = _load_store()
    store = StoryMaterialStore(args.root)
    try:
        if args.command == "add-source":
            result = store.add_source(_object_payload(args.input, args.command))
        elif args.command == "add-atoms":
            payload = _read_payload(args.input)
            if not isinstance(payload, list) or any(not isinstance(item, dict) for item in payload):
                raise ValueError("add-atoms input must be an array of objects")
            result = store.add_atoms(payload)
        elif args.command == "log-usage":
            result = store.log_usage(_object_payload(args.input, args.command))
        elif args.command == "search-index":
            result = store.start_search(_object_payload(args.input, args.command))
        elif args.command == "continue-search":
            result = store.continue_search(_object_payload(args.input, args.command))
        elif args.command == "facet-values":
            payload = _object_payload(args.input, args.command)
            result = store.list_facet(
                payload.get("field"),
                cursor=payload.get("cursor", 0),
                page_budget_chars=payload.get("page_budget_chars", 1200),
            )
        elif args.command == "get-atom":
            result = store.get_atoms(args.id)
        elif args.command == "get-source":
            result = store.get_sources(args.id)
        elif args.command == "get-usage":
            result = store.get_usage(args.atom_id)
        elif args.command == "get-session":
            result = store.get_session(args.id)
        elif args.command == "close-session":
            result = store.close_session(args.id)
        elif args.command == "migrate-legacy":
            result = store.migrate_legacy(args.legacy_db)
        elif args.command == "stats":
            result = store.stats()
        elif args.command == "rebuild-index":
            result = store.rebuild_index()
        else:
            result = store.validate()
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (ValidationError, ValueError, json.JSONDecodeError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2
    except OSError as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
