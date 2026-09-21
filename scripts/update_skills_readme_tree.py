#!/usr/bin/env python3
"""Refresh the five-package file tree in .agents/skills/README.md from the real filesystem.

Keeps every existing description, adds newly created methods, drops deleted ones, and
never invents a file that does not exist. Run after changing package files, then run
validate_skill_packages.py.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / ".agents/skills"
README = SKILLS / "README.md"
PACKAGES = ["laohu-ai-visual", "laohu-script-writer", "laohu-image-creation",
            "laohu-video-prompt", "laohu-language-mode"]
DIR_NOTES = {
    "agents": "宿主识别元数据",
    "references": "按需读取的专业方法、案例与合同",
    "scripts": "执行、检索或校验工具",
    "skills": "内部专业，每项有自己的入口与验收",
    "内置方法": "本包实际保存的跨专业方法，维护时同步",
    "语言模式": "随包携带的语言正文，来源由语言包维护",
}
SKIP = {"__pycache__", ".DS_Store", ".git", ".ipynb_checkpoints"}
ENTRY = re.compile(r"^(?P<prefix>(?:[│ ]   )*)(?P<mark>[├└])── (?P<name>.+?)(?:  (?P<desc>.*))?$")


def heading(path: Path) -> str:
    if path.suffix != ".md":
        return ""
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        if line.startswith("# "):
            return line[2:].strip()
        if line.strip() and not line.startswith(("---", ">", "<!--")):
            break
    return ""


def describe(rel: Path, node: Path, existing: str) -> str:
    if existing:
        return existing
    if node.is_dir():
        return DIR_NOTES.get(node.name, "")
    if node.name == "SKILL.md":
        return "触发、主责、流程与方法路由"
    text = heading(node)
    return "" if text == node.stem else text


def parse_tree(lines: list[str]) -> dict:
    root: dict = {"name": "", "desc": "", "dirs": {}, "files": {}}
    stack: list[tuple[int, dict]] = [(-1, root)]
    for line in lines:
        match = ENTRY.match(line)
        if not match:
            continue
        depth = len(match.group("prefix")) // 4
        name = match.group("name").strip()
        desc = (match.group("desc") or "").strip()
        is_dir = name.endswith("/")
        while stack and stack[-1][0] >= depth:
            stack.pop()
        parent = stack[-1][1]
        node = {"name": name, "desc": desc, "dirs": {}, "files": {},
                "order": len(parent["dirs"]) + len(parent["files"])}
        bucket = parent["dirs"] if is_dir else parent["files"]
        bucket[name] = node
        if is_dir:
            stack.append((depth, node))
    return root


def walk(path: Path, old: dict) -> dict:
    node = {"name": old.get("name", path.name + "/" if path.is_dir() else path.name),
            "desc": old.get("desc", ""), "dirs": {}, "files": {},
            "order": old.get("order", 10 ** 6)}
    old_dirs, old_files = old.get("dirs", {}), old.get("files", {})
    for child in sorted(path.iterdir(), key=lambda p: p.name):
        if child.name in SKIP or child.name.startswith("."):
            continue
        key = child.name + "/" if child.is_dir() else child.name
        previous = (old_dirs if child.is_dir() else old_files).get(key, {})
        if child.is_dir():
            # A directory listed without children in the README stays a leaf note.
            if key in old_dirs and not previous.get("dirs") and not previous.get("files"):
                node["dirs"][key] = {"name": key, "desc": previous.get("desc", ""),
                                     "dirs": {}, "files": {},
                                     "order": previous.get("order", 10 ** 6)}
                continue
            node["dirs"][key] = walk(child, previous)
        else:
            node["files"][key] = {"name": key, "desc": previous.get("desc", ""), "path": child,
                                  "dirs": {}, "files": {}, "order": previous.get("order", 10 ** 6)}
    return node


def render(node: dict, base: Path, prefix: str = "") -> list[str]:
    out: list[str] = []
    dirs = list(node["dirs"].values())
    files = list(node["files"].values())
    rank = {name: i for i, name in enumerate(["agents/", "references/", "scripts/", "skills/"])}
    dirs.sort(key=lambda n: (n["order"], rank.get(n["name"], len(rank)), n["name"]))
    files.sort(key=lambda n: (n["order"], n["name"] == "SKILL.md", n["name"]))
    entries = dirs + files
    for index, entry in enumerate(entries):
        last = index == len(entries) - 1
        if "path" in entry:
            child_base = entry["path"]
        else:
            child_base = base / entry["name"].rstrip("/")
        desc = describe(child_base.relative_to(ROOT), child_base, entry["desc"])
        if not desc and child_base.is_dir():
            skill = child_base / "SKILL.md"
            if skill.is_file():
                desc = heading(skill)
        label = entry["name"] + ("  " + desc if desc else "")
        out.append(f"{prefix}{'└' if last else '├'}── {label}")
        if entry["dirs"] or entry["files"]:
            out.extend(render(entry, child_base, prefix + ("    " if last else "│   ")))
    return out


def main() -> int:
    readme = README.read_text(encoding="utf-8")
    blocks = list(re.finditer(r"<summary>([^<]*?)：(" + "|".join(PACKAGES) + r")（含(\d+)个Skill入口）</summary>\n\n(.*?)\n\n```text\n(.*?)\n```",
                              readme, re.S))
    if len(blocks) != len(PACKAGES):
        print(f"expected {len(PACKAGES)} package blocks, found {len(blocks)}")
        return 1
    updated = readme
    for match in reversed(blocks):
        package = match.group(2)
        intro = match.group(4)
        old_tree = parse_tree(match.group(5).splitlines())
        real = walk(SKILLS / package, old_tree)
        count = sum(1 for _ in (SKILLS / package).rglob("SKILL.md"))
        tree = "\n".join([package + "/"] + render(real, SKILLS / package))
        summary = (f"<summary>{match.group(1)}：{package}（含{count}个Skill入口）</summary>\n\n"
                   f"{intro}\n\n```text\n{tree}\n```")
        updated = updated[:match.start()] + summary + updated[match.end():]
    README.write_text(updated, encoding="utf-8")
    print("updated", README.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    sys.exit(main())
