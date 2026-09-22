#!/usr/bin/env python3
"""Validate package files, repository-wide method dependencies and skill-chain integrity.

This is a mechanical reachability check, not a visual-quality or writing-quality score.
It implements the T02 scope of the consolidation round:

  * resolve the repository root from ``__file__``, never from the caller's cwd;
  * allow a runtime method to live in another package as long as it resolves to a real
    file inside the same repository (one canonical source, no re-copied run mirrors);
  * refuse a method dependency that escapes the repository;
  * resolve every Markdown relative link from the directory of the file that contains it;
  * classify URLs, mail addresses, template placeholders and explicit anchors instead of
    treating them as missing methods;
  * require anchors to land on a real heading or an explicit anchor;
  * check inline method paths, script resource relations and local Python imports;
  * parse YAML frontmatter for real, including folded ``description: >-`` blocks;
  * require the runtime layer ``references/`` to hold direct files only, with root-level
    ``reference.md`` / ``reference-*.md`` already migrated into it;
  * report retired copy trees that still have formal consumers;
  * report duplicate same-source content as a candidate list - never delete by similarity;
  * check that a present parent link stays on the skill's own ancestor chain and that the
    ancestor chain reaches a business root.

A package copied out of the repository cannot carry another package's canonical text by
design, so a link leaving such a copy is reported as a declared repository dependency
(``dependency_notes``) instead of a broken method. Inside the repository the same link
must resolve, otherwise it is a failure.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import unicodedata
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.skill_package_layout import ENTRY_PACKAGES

PACKAGE_ROOT = ROOT / ".agents/skills"
NAMES = set(ENTRY_PACKAGES)
REGISTRY = PACKAGE_ROOT / "laohu-ai-visual/references/能力注册表.json"

# Copy trees retired by this round: a formal consumer inside a package is a failure.
RETIRED_MARKERS = ("内置方法/", "references/语言模式/")
SCHEME = re.compile(r"^[a-z][a-z0-9+.-]*:", re.I)
PLACEHOLDER = re.compile(r"[{}<>*]|^\.\.\.$|^…$")
INLINE_PATH = re.compile(r"^(?:references|scripts|assets|skills|agents|\.\.)/[^ <>|*]+"
                         r"\.(?:md|py|sh|json|jsonl|yaml|yml|txt|csv)$")
INLINE_REPO_PATH = re.compile(r"^\.agents/[^ <>|*]+\.(?:md|py|sh|json|jsonl|yaml|yml|txt|csv)$")
# Tools that have to name the retired markers in order to detect them.
MARKER_OWNERS = {"validate_skill_packages.py", "sync_skill_packages.py"}
SKIP_DIRS = {"__pycache__", ".git", ".ipynb_checkpoints", "node_modules"}
FRONTMATTER = re.compile(r"\A---\r?\n(.*?)\r?\n---\r?\n", re.S)


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def digest(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


# --------------------------------------------------------------------------------------
# Frontmatter (no external YAML dependency: parse the subset the host actually uses)
# --------------------------------------------------------------------------------------

def frontmatter(body: str) -> dict:
    match = FRONTMATTER.match(body)
    if not match:
        return {}
    fields: dict[str, str] = {}
    lines = match.group(1).splitlines()
    index = 0
    while index < len(lines):
        line = lines[index]
        index += 1
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if line[:1] in " \t" or ":" not in line:
            continue
        key, _, value = line.partition(":")
        key, value = key.strip(), value.strip()
        if value in (">-", ">", "|", "|-", "|+"):
            block: list[str] = []
            while index < len(lines) and (not lines[index].strip() or lines[index][:1] in " \t"):
                block.append(lines[index].strip())
                index += 1
            if value.startswith(">"):
                value = " ".join(part for part in block if part)
            else:
                value = "\n".join(block).strip()
        else:
            value = value.strip('"').strip("'")
        fields[key] = value
    return fields


# --------------------------------------------------------------------------------------
# Anchors
# --------------------------------------------------------------------------------------

def slug(title: str) -> str:
    """GitHub-style heading anchor used by the project's Markdown links."""
    text = re.sub(r"`([^`]*)`", r"\1", title.strip())
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)
    text = re.sub(r"[*_~]", "", text)
    text = unicodedata.normalize("NFKC", text).lower()
    text = re.sub(r"[^\w\u4e00-\u9fff\s-]", "", text)
    return re.sub(r"\s+", "-", text).strip("-")


def anchors_of(path: Path) -> set[str]:
    body = read(path)
    found: set[str] = set()
    for match in re.finditer(r"<a\s+(?:name|id)=[\"']([^\"']+)[\"']", body, re.I):
        found.add(match.group(1))
    for match in re.finditer(r"^#{1,6}\s+(.+?)\s*#*\s*$", body, re.M):
        title = match.group(1)
        found.add(slug(title))
        explicit = re.search(r"\{#([^}]+)\}\s*$", title)
        if explicit:
            found.add(explicit.group(1))
            found.add(slug(re.sub(r"\{#[^}]+\}\s*$", "", title)))
    return found


def anchor_ok(path: Path, anchor: str) -> bool:
    anchor = anchor.strip()
    if not anchor:
        return True
    candidates = {anchor, anchor.lower()}
    if anchor.startswith("%") or re.search(r"%(?:[0-9A-Fa-f]{2})", anchor):
        from urllib.parse import unquote
        candidates.add(unquote(anchor))
        candidates.add(unquote(anchor).lower())
    return bool(candidates & anchors_of(path))


# --------------------------------------------------------------------------------------
# Package checking
# --------------------------------------------------------------------------------------

def _repo_for(package: Path, root: Path | None) -> Path | None:
    if root is not None:
        return Path(root).resolve() if package.resolve().is_relative_to(Path(root).resolve()) else None
    return ROOT if package.resolve().is_relative_to(ROOT) else None


def check_package(package, root=None, notes=None):
    """Return the failure list for one package directory.

    ``root`` is the containing repository. When it is omitted, the project root is used
    for a package that lives inside it, and a package outside the project is validated as
    a copy that legitimately depends on the repository it was taken from.
    """
    package = Path(package).resolve()
    repo = _repo_for(package, root)
    notes = notes if notes is not None else []
    errors: list[str] = []
    if not (package / "SKILL.md").is_file():
        return [f"missing package SKILL.md: {package}"]

    def classify_link(owner: Path, raw_target: str):
        """Resolve one Markdown link or inline path into (state, detail)."""
        value = raw_target.strip().strip("<>")
        path_part, sep, anchor = value.partition("#")
        if not path_part:
            return "anchor-only", anchor
        if SCHEME.match(path_part) or path_part.startswith("mailto:"):
            return "external", ""
        if PLACEHOLDER.search(path_part):
            return "placeholder", ""
        resolved = (owner.parent / path_part).resolve()
        if resolved.is_dir():
            return "directory", ""
        if resolved.is_file():
            if resolved.is_relative_to(package):
                return "ok", str(resolved)
            if repo is not None:
                return ("ok" if resolved.is_relative_to(repo) else "escape"), str(resolved)
            # Outside the package and outside any known repository: a declared dependency
            # of the copy, never a method the copy may claim to carry.
            return "dependency", str(resolved)
        if resolved.is_relative_to(package):
            return "missing", str(resolved)
        if repo is not None:
            return "escape", str(resolved)
        return "dependency", str(resolved)

    for path in sorted(package.rglob("*")):
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if path.is_symlink():
            errors.append(f"symlink: {path}")
            continue
        if not path.is_file():
            continue
        relative = path.relative_to(package)
        if path.suffix in {".py", ".sh"}:
            errors.extend(_check_script(path, package, repo))
            continue
        if path.suffix not in {".md", ".yaml", ".yml", ".json"}:
            continue
        body = read(path)
        if path.name == "SKILL.md":
            fields = frontmatter(body)
            name = fields.get("name", "")
            if not re.fullmatch(r"[a-z0-9-]+", name or ""):
                errors.append(f"invalid skill name: {path}")
            elif path.parent != package and name != path.parent.name:
                errors.append(f"skill name does not match directory: {path} -> {name}")
            if not fields.get("description"):
                errors.append(f"missing trigger: {path}")
        if path.suffix != ".md":
            continue
        for raw in re.findall(r"\]\(([^)\n]+)\)", body):
            state, detail = classify_link(path, raw)
            if state == "ok":
                anchor = raw.strip().strip("<>").partition("#")[2]
                if anchor and Path(detail).suffix == ".md" and not anchor_ok(Path(detail), anchor):
                    errors.append(f"missing anchor: {path} -> {raw}")
            elif state == "escape":
                errors.append(f"method path outside repository: {path} -> {raw}")
            elif state == "missing":
                errors.append(f"missing method: {path} -> {raw}")
            elif state == "dependency":
                notes.append({"from": str(path.relative_to(package)), "target": raw,
                              "repository_path": detail})
        for target in re.findall(r"(?<!`)`([^`\n]+)`(?!`)", body):
            target = target.strip()
            if INLINE_REPO_PATH.match(target):
                resolved = ((repo or ROOT) / target).resolve()
                state = "ok" if resolved.is_file() else ("escape" if repo is not None else "dependency")
                detail = str(resolved)
            elif INLINE_PATH.match(target):
                state, detail = classify_inline(path, package, repo, target)
            else:
                continue
            if state == "ok":
                continue
            if state == "escape":
                errors.append(f"method path outside repository: {path} -> {target}")
            elif state == "missing":
                errors.append(f"missing method or outside package in inline path: {path} -> {target}")
            elif state == "dependency":
                notes.append({"from": str(path.relative_to(package)), "target": target,
                              "repository_path": detail})
        errors.extend(_retired_consumers(path, package, body))
        if relative.name.startswith("reference") and relative.parent == Path("."):
            errors.append(f"root-level reference must live in references/: {path}")
    errors.extend(check_runtime_layer(package))
    return errors


def _retired_consumers(path: Path, package: Path, body: str) -> list[str]:
    """A retired copy tree may keep a historical mention only as an honest gap report."""
    failures: list[str] = []
    for line_no, line in enumerate(body.splitlines(), 1):
        for marker in RETIRED_MARKERS:
            if marker in line and "](http" not in line:
                failures.append(
                    f"retired copy path still consumed: {path.relative_to(package)}:{line_no} -> {marker}")
    return failures


def _check_script(path: Path, package: Path, repo: Path | None) -> list[str]:
    """Local Python imports and sibling resource expectations of a package script."""
    failures: list[str] = []
    body = read(path)
    for match in re.finditer(r"^\s*from\s+([.\w]+)\s+import\s|^\s*import\s+([.\w]+)", body, re.M):
        module = match.group(1) or match.group(2)
        if "." not in module:
            continue  # stdlib or third-party
        candidate = path.parent / (module.split(".")[-1] + ".py")
        if not candidate.is_file() and not (package / (module.replace(".", "/") + ".py")).is_file():
            failures.append(f"missing local import: {path} -> {module}")
    for match in re.finditer(r'"([^"\n]+\.py)"', body):
        candidate = (path.parent / match.group(1)).resolve()
        if candidate.is_file():
            continue
        if repo is not None and not candidate.is_relative_to(repo):
            failures.append(f"script resource outside repository: {path} -> {match.group(1)}")
    return failures


def classify_inline(owner: Path, package: Path, repo: Path | None, target: str):
    """Inline code paths are resolved from the file, the package and the repository root.

    ``references/x.md`` is normally written relative to the containing file or package;
    ``scripts/x.py`` and ``.agents/...`` are repository-relative. A repository-relative
    path in a package copied out of the repository is a declared dependency, not a
    broken method.
    """
    repo_relative = target.startswith((".agents/", "scripts/"))
    candidates = []
    if repo is not None:
        candidates.append((repo / target).resolve())
    candidates += [(owner.parent / target).resolve(), (package / target).resolve()]
    for resolved in candidates:
        if resolved.is_file():
            if repo is not None and not resolved.is_relative_to(repo):
                return "escape", str(resolved)
            return "ok", str(resolved)
    if repo is None and repo_relative:
        return "dependency", str((ROOT / target).resolve())
    for resolved in candidates:
        if resolved.is_relative_to(package):
            return "missing", str(resolved)
    if repo is not None:
        return "escape", str(candidates[0])
    return "dependency", str(candidates[0])


def check_runtime_layer(package: Path) -> list[str]:
    """references/ must hold direct files; nested skill or copy trees are failures."""
    failures: list[str] = []
    for skill in sorted(Path(package).rglob("SKILL.md")):
        references = skill.parent / "references"
        if not references.is_dir():
            continue
        for child in sorted(references.iterdir()):
            if child.is_dir():
                failures.append(f"references/ run layer holds a directory, not a direct file: {child}")
    return failures


# --------------------------------------------------------------------------------------
# Parent chain
# --------------------------------------------------------------------------------------

def parent_chain_report():
    """Return (errors, gaps) for parent-link integrity across the top-level packages.

    Registration is checked deterministically: a registered parent must be a real skill
    whose directory is an ancestor of this skill, the chain must be acyclic, and it must
    terminate at a business root. A skill that carries no link to any ancestor is
    reported as an advisory gap (entry rewriting is H01's scope), not as a failure.
    """
    errors: list[str] = []
    gaps: list[str] = []
    if not REGISTRY.is_file():
        return errors, gaps
    registry = json.loads(read(REGISTRY))
    by_name = {node["name"]: node for node in registry["skills"]}
    for node in registry["skills"]:
        skill = ROOT / node["path"]
        if not skill.is_file():
            errors.append(f"registry entry has no SKILL.md: {node['path']}")
            continue
        ancestors, seen, walk = [], {node["name"]}, node
        while walk.get("parent"):
            name = walk["parent"]
            if name in seen:
                errors.append(f"parent chain has a cycle at {node['path']} -> {name}")
                break
            seen.add(name)
            parent = by_name.get(name)
            if parent is None:
                errors.append(f"registry parent is not registered: {node['path']} -> {name}")
                break
            parent_path = (ROOT / parent["path"]).resolve()
            if not parent_path.is_file():
                errors.append(f"registry parent has no SKILL.md: {node['path']} -> {parent['path']}")
                break
            if not skill.resolve().is_relative_to(parent_path.parent):
                errors.append(f"registry parent is not an ancestor directory: {node['path']} -> {parent['path']}")
                break
            ancestors.append((parent_path, name))
            walk = parent
        if not ancestors:
            continue  # business root: no parent expected
        if Path(node["path"]).parts[2] not in NAMES:
            errors.append(f"skill lives outside the registered packages: {node['path']}")
        body = read(skill)
        chain = []
        for target in re.findall(r"\]\(([^)\n]+)\)", body):
            value = target.strip().strip("<>").partition("#")[0]
            if not value.endswith("SKILL.md") or SCHEME.match(value):
                continue
            resolved = (skill.parent / value).resolve()
            if resolved.is_file():
                chain.append(resolved)
        if not any(resolved in [path for path, _ in ancestors] for resolved in chain):
            import os
            expected = sorted({os.path.relpath(path, skill.parent) for path, _ in ancestors})[0]
            gaps.append(f"{node['path']} has no parent link; expected e.g. {expected}")
    return errors, gaps


def duplicate_candidates():
    """Report byte-identical method files as merge candidates; never delete by similarity."""
    seen: dict[str, list[str]] = {}
    for name in sorted(NAMES):
        package = PACKAGE_ROOT / name
        if not package.is_dir():
            continue
        for path in package.rglob("*.md"):
            if any(part in SKIP_DIRS for part in path.parts):
                continue
            seen.setdefault(digest(read(path)), []).append(str(path.relative_to(ROOT)))
    return [paths for paths in seen.values() if len(paths) > 1]


def check_repository():
    """Validate every top-level package plus the repository-wide dependency rules."""
    errors: list[str] = []
    notes: list[str] = []
    packages = [p for p in PACKAGE_ROOT.iterdir() if p.is_dir()]
    if {p.name for p in packages} != NAMES:
        return [f"top-level package entry set mismatch: {sorted(p.name for p in packages)}"], [], []
    for package in sorted(packages):
        errors.extend(check_package(package, root=ROOT, notes=notes))
    chain_errors, gaps = parent_chain_report()
    errors.extend(chain_errors)
    for script in sorted((ROOT / "scripts").glob("*.py")):
        if script.name in MARKER_OWNERS:
            continue  # these tools name the retired markers on purpose
        body = read(script)
        for marker in RETIRED_MARKERS:
            if marker in body:
                errors.append(f"retired copy path still consumed by tooling: {script.relative_to(ROOT)} -> {marker}")
    return errors, notes, gaps


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--package", type=Path, help="validate one directory only")
    parser.add_argument("--json", action="store_true", help="machine-readable output")
    args = parser.parse_args()
    if args.package:
        notes: list[str] = []
        errors = check_package(args.package, notes=notes)
        report = {"ok": not errors, "package_count": 1, "errors": errors,
                  "dependency_notes": notes, "parent_chain_gaps": []}
    else:
        errors, notes, gaps = check_repository()
        report = {"ok": not errors, "package_count": len(NAMES), "errors": errors,
                  "dependency_notes": notes, "parent_chain_gaps": gaps,
                  "duplicate_content_candidates": duplicate_candidates()}
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(json.dumps({key: report[key] for key in
                          ("ok", "package_count", "errors")}, ensure_ascii=False, indent=2))
        if report["parent_chain_gaps"]:
            print(f"parent-link gaps (advisory, owned by H01): {len(report['parent_chain_gaps'])}")
        if report["dependency_notes"]:
            print(f"declared repository dependencies: {len(report['dependency_notes'])}")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
