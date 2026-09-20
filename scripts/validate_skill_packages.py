#!/usr/bin/env python3
"""Validate real package files and local method reachability; not a visual-quality score."""
from pathlib import Path
import argparse
import json
import re

ROOT = Path(__file__).resolve().parents[1]
NAMES = {"laohu-ai-visual", "laohu-script-writer", "laohu-image-creation",
         "laohu-video-prompt", "laohu-language-mode"}


def check_package(package):
    package = Path(package).resolve()
    errors = []
    if not (package / "SKILL.md").is_file():
        return [f"missing package SKILL.md: {package}"]
    for path in package.rglob("*"):
        if path.is_symlink():
            errors.append(f"symlink: {path}")
        if not path.is_file() or path.suffix != ".md":
            continue
        body = path.read_text()
        if path.name == "SKILL.md":
            if not re.search(r"^name: [a-z0-9-]+\s*$", body, re.M):
                errors.append(f"invalid skill name: {path}")
            if not re.search(r"^description: .+", body, re.M):
                errors.append(f"missing trigger: {path}")
        for raw in re.findall(r"\]\(([^)\n]+)\)", body):
            target = raw.strip("<>").split("#", 1)[0]
            if not target or re.match(r"^[a-z]+:", target) or any(c in target for c in "{}"):
                continue
            resolved = (path.parent / target).resolve()
            if not resolved.is_relative_to(package):
                errors.append(f"outside package: {path} -> {target}")
            elif not resolved.exists():
                errors.append(f"missing method: {path} -> {target}")
        for target in re.findall(r"(?<!`)`([^`\n]+)`(?!`)", body):
            if not re.fullmatch(r"(?:references|scripts|\.\.)/[^ <>|*]+\.(?:md|py|sh|json|jsonl|yaml)", target):
                continue
            candidates = [(path.parent / target).resolve(), (package / target).resolve()]
            if not any(p.is_relative_to(package) and p.is_file() for p in candidates):
                errors.append(f"missing method or outside package in inline path: {path} -> {target}")
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package", type=Path)
    args = parser.parse_args()
    if args.package:
        packages = [args.package]
    elif (ROOT / "SKILL.md").is_file():
        packages = [ROOT]
    else:
        base = ROOT / ".agents/skills"
        packages = [p for p in base.iterdir() if p.is_dir()]
        if {p.name for p in packages} != NAMES:
            parser.exit(1, "五包入口集合不一致\n")
    errors = [error for package in packages for error in check_package(package)]
    print(json.dumps({"ok": not errors, "package_count": len(packages), "errors": errors}, ensure_ascii=False, indent=2))
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
