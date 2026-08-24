#!/usr/bin/env python3
"""检查成熟项目删改前的语义迁移台账，不评价视觉审美。"""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path


ACTIONS = {"KEEP", "MOVE", "MERGE", "REWRITE", "RETIRE"}
ROUTED = ACTIONS - {"RETIRE"}


def present(value: object) -> bool:
    return bool(value.strip()) if isinstance(value, str) else bool(value)


def main() -> int:
    if len(sys.argv) not in {2, 3}:
        print("usage: validate_semantic_migration.py <ledger.json> [project-root]")
        return 2
    ledger_path = Path(sys.argv[1]).resolve()
    root = Path(sys.argv[2]).resolve() if len(sys.argv) == 3 else ledger_path.parent
    try:
        ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        print(f"FAIL cannot read ledger: {error}")
        return 1

    errors: list[str] = []
    if ledger.get("schema_version") != 1:
        errors.append("schema_version must be 1")
    if not present(ledger.get("baseline_ref")):
        errors.append("baseline_ref is required")
    if ledger.get("status") != "COMPLETE":
        errors.append("status must be COMPLETE before destructive migration")
    sources = ledger.get("sources", [])
    items = ledger.get("items", [])
    if not isinstance(sources, list) or not sources:
        errors.append("sources must be a non-empty list")
        sources = []
    if not isinstance(items, list) or not items:
        errors.append("items must be a non-empty list")
        items = []

    declared: set[tuple[str, str]] = set()
    for source in sources:
        path = source.get("path") if isinstance(source, dict) else None
        sections = source.get("sections") if isinstance(source, dict) else None
        if not present(path) or not isinstance(sections, list) or not sections:
            errors.append("each source needs path and reviewed sections")
            continue
        for section in sections:
            key = (str(path), str(section))
            if key in declared:
                errors.append(f"duplicate source section: {path} :: {section}")
            declared.add(key)

    covered: list[tuple[str, str]] = []
    seen: set[str] = set()
    for item in items:
        if not isinstance(item, dict):
            errors.append("each item must be an object")
            continue
        item_id = str(item.get("id", ""))
        if not item_id or item_id in seen:
            errors.append(f"missing or duplicate item id: {item_id or '<empty>'}")
        seen.add(item_id)
        for field in ("source_path", "source_sections", "original_function", "unique_information"):
            if not present(item.get(field)):
                errors.append(f"{item_id}: {field} is required")
        source_path = str(item.get("source_path", ""))
        for section in item.get("source_sections", []):
            covered.append((source_path, str(section)))

        action = item.get("action")
        if action not in ACTIONS:
            errors.append(f"{item_id}: invalid action")
        validation = item.get("validation")
        if not isinstance(validation, dict) or not present(validation.get("task")):
            errors.append(f"{item_id}: behavior validation task is required")
        elif validation.get("status") != "PASS":
            errors.append(f"{item_id}: validation must PASS before deletion")

        targets = item.get("target_paths", [])
        routes = item.get("activation_routes", [])
        if action in ROUTED:
            if not isinstance(targets, list) or not targets:
                errors.append(f"{item_id}: target paths are required")
                targets = []
            if not isinstance(routes, list) or not routes:
                errors.append(f"{item_id}: activation route is required")
                routes = []
            for target in targets:
                if not (root / str(target)).exists():
                    errors.append(f"{item_id}: target does not exist: {target}")
            for route in routes:
                if not isinstance(route, dict) or not all(present(route.get(key)) for key in ("from", "trigger", "to")):
                    errors.append(f"{item_id}: activation route needs from, trigger, and to")
                    continue
                if str(route["to"]) not in {str(target) for target in targets}:
                    errors.append(f"{item_id}: activation route points outside targets")
                entry = root / str(route["from"])
                if not entry.exists():
                    errors.append(f"{item_id}: activation entry does not exist: {route['from']}")
                elif str(route["from"]) != str(route["to"]) and entry.is_file():
                    text = entry.read_text(encoding="utf-8", errors="ignore")
                    target_name = Path(str(route["to"])).name
                    if str(route["to"]) not in text and target_name not in text:
                        errors.append(f"{item_id}: entry does not reference route target")
        elif action == "RETIRE" and not present(item.get("retirement_evidence")):
            errors.append(f"{item_id}: retirement evidence is required")

    for key, count in Counter(covered).items():
        if count > 1:
            errors.append(f"source section covered more than once: {key[0]} :: {key[1]}")
    for path, section in sorted(declared - set(covered)):
        errors.append(f"uncovered source section: {path} :: {section}")
    for path, section in sorted(set(covered) - declared):
        errors.append(f"undeclared source section: {path} :: {section}")

    if errors:
        print("semantic migration: FAIL")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"semantic migration: PASS ({len(declared)} sections, {len(items)} items)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
