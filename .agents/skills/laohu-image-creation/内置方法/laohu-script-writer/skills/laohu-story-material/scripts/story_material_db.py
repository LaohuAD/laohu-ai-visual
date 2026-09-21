#!/usr/bin/env python3
"""CLI façade for the layered story-material authority and retrieval sessions."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


PACKAGE = Path(__file__).resolve().parents[3]
DEFAULT_ROOT = next((p / "02_共享资产库/故事素材库" for p in PACKAGE.parents if (p / "02_共享资产库/故事素材库/manifest.json").is_file()), None) if (PACKAGE / "SKILL.md").is_file() else None


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
    if args.root is None:
        parser = _parser()
        parser.error("完整来源库未提供；应用原子请使用包内 scripts/story_atoms.py，采集请显式指定 --root")
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
        if args.command in {"add-source", "add-atoms", "log-usage", "migrate-legacy"} and DEFAULT_ROOT is not None and args.root.resolve() == DEFAULT_ROOT.resolve():
            sys.path.insert(0, str(PACKAGE / "scripts"))
            from story_atoms import sync, DEFAULT_ATOMS
            try:
                summary = sync(args.root, DEFAULT_ATOMS)
            except (OSError, ValueError, KeyError) as exc:
                print(json.dumps({"ok": False, "source_saved": True,
                                  "error": f"来源库已保存，应用原子同步失败：{exc}",
                                  "recovery": "修复原因后执行包内 scripts/story_atoms.py sync；不要重复新增来源或原子。"},
                                 ensure_ascii=False), file=sys.stderr)
                return 1
            print(json.dumps({"application_sync": summary}, ensure_ascii=False), file=sys.stderr)
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
