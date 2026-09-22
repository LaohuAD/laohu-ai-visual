#!/usr/bin/env python3
"""Migration audit and dependency check for the top-level skill packages.

This file used to generate package-local run copies of cross-package methods. That
behaviour is retired: every shared method now has exactly one canonical source in the
repository, and consumers read it by relative address. The tool is kept under its old
name so existing maintenance habits still find it, but it no longer writes methods.

What it does now
----------------
``--check`` (the only supported mode) audits the recorded migration ledger:

* every historical ``copies[]`` entry is resolved through the source chain to the file
  that really holds the method now (``shared_moves``, ``method_redirects``, ``layout``,
  and the package extractions recorded in ``skill_package_layout``);
* a copy that still exists on disk is reported as ``stale_methods`` - the runtime tree
  must not grow run copies again;
* a copy whose canonical source cannot be resolved is reported as ``missing_sources``;
* a formal consumer that still points at a retired copy path is reported as
  ``orphan_consumers``;
* the project-scope file, anchor and parent-chain check is delegated to
  ``validate_skill_packages`` so there is one dependency authority, not two.

Running the tool without ``--check`` refuses to write: copy generation is disabled and
the command exits non-zero with the correct maintenance entry point.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.skill_package_layout import PACKAGES, current_location

DEFAULT_MANIFEST = ROOT / "04_诊断与系统日志/五包迁移清单.json"
RETIRED_MARKERS = ("内置方法/", "references/语言模式/")
MARKER_OWNERS = {"validate_skill_packages.py", "sync_skill_packages.py"}
PACKAGE_NAMES = set(PACKAGES)
SKIP_DIRS = {"__pycache__", ".git", "node_modules", ".ipynb_checkpoints"}
REFERENCE_MARKER = re.compile(r"^reference(-[a-z]+)?\.md$")


def load_manifest(path: Path) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def canonical_source(source: str, manifest: dict) -> str | None:
    """Resolve one recorded source path to the file that holds the method today."""
    if (ROOT / source).is_file():
        return source
    shared = manifest.get("shared_moves", {})
    if source in shared and (ROOT / shared[source]).is_file():
        return shared[source]
    redirects = manifest.get("method_redirects", {})
    if source in redirects:
        successor = redirects[source]
        if (ROOT / successor).is_file():
            return successor
        # A redirected method can itself be renamed later in the same consolidation;
        # follow that rename to the file that really holds the text.
        renamed = current_location(successor, ROOT)
        if renamed != successor and (ROOT / renamed).is_file():
            return renamed
    for old, new in sorted(manifest.get("layout", {}).items(), key=lambda item: -len(item[0])):
        if source == old or source.startswith(old + "/"):
            candidate = new + source[len(old):]
            if (ROOT / candidate).is_file():
                return candidate
    path = Path(source)
    if REFERENCE_MARKER.match(path.name):
        candidate = path.parent / "references" / path.name
        if (ROOT / candidate).is_file():
            return str(candidate)
    # A capability extracted into another top-level package keeps its ledger address and
    # lives at the current package location.
    moved = current_location(source, ROOT)
    if moved != source and (ROOT / moved).is_file():
        return moved
    return None


def resolve_chain(record: dict, by_target: dict) -> tuple[str | None, list[str]]:
    """Follow target->source links until the real source, detecting cycles."""
    target, chain, seen = record["target"], [], set()
    while target in by_target and target not in seen:
        seen.add(target)
        chain.append(target)
        target = by_target[target]
    if target in seen:
        return None, chain + ["<cycle>"]
    return target, chain


def formal_consumers() -> list[str]:
    """Formal consumers of a retired copy path: package files and repository tooling.

    Navigation documents and the implementation record describe the retirement itself and
    are not consumers; the tools that name the markers in order to detect them are not
    consumers either.
    """
    hits = []
    scope = list((ROOT / ".agents/skills").rglob("*")) + list((ROOT / "scripts").glob("*.py"))
    for path in scope:
        if not path.is_file() or path.suffix not in {".md", ".py", ".json", ".yaml", ".yml"}:
            continue
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        relative = str(path.relative_to(ROOT))
        if relative.startswith(".agents/skills/README.md"):
            continue
        if path.name in MARKER_OWNERS:
            continue
        body = path.read_text(encoding="utf-8", errors="ignore")
        for marker in RETIRED_MARKERS:
            if marker in body:
                hits.append(f"{relative} -> {marker}")
                break
    return hits


def audit(manifest_path: Path) -> dict:
    manifest = load_manifest(manifest_path)
    copies = manifest.get("copies", [])
    by_target = {record["target"]: record["source"] for record in copies}
    stale, missing, cycles = [], [], []
    for record in copies:
        source, chain = resolve_chain(record, by_target)
        if source is None:
            cycles.append(record["target"])
            continue
        if (ROOT / record["target"]).is_file():
            stale.append(record["target"])
        if canonical_source(source, manifest) is None:
            missing.append({"target": record["target"], "source": source})
    orphans = formal_consumers()
    try:
        from scripts.validate_skill_packages import check_repository
        dependency_errors, _, _ = check_repository()
    except Exception as error:  # pragma: no cover - the audit must still report
        dependency_errors = [f"project dependency check failed to run: {error}"]
    return {"ok": not (stale or missing or orphans or cycles or dependency_errors),
            "copies": len(copies), "stale_methods": stale, "missing_sources": missing,
            "source_cycles": cycles, "orphan_consumers": orphans,
            "dependency_errors": dependency_errors}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--check", action="store_true",
                        help="audit the migration ledger and the project dependencies")
    args = parser.parse_args()
    if not args.check:
        print(json.dumps({"ok": False, "status": "WRITE_DISABLED",
                          "message": "副本生成模式已停用：共用方法只保留一份正文，"
                                     "改用 python3 scripts/sync_skill_packages.py --check "
                                     "与 python3 scripts/validate_skill_packages.py 做依赖检查。",
                          "stale_methods": []}, ensure_ascii=False))
        return 2
    report = audit(args.manifest)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
