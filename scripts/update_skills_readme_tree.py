#!/usr/bin/env python3
"""Refresh the real trees from the filesystem: the Skills README and the full project tree.

Two outputs, two scopes:

* ``.agents/skills/README.md`` shows the Skills subtree only - six package blocks whose
  trees come straight from the package directories.
* ``04_诊断与系统日志/完整目录树.md`` shows the whole visible project. Hidden caches,
  ``.git``, virtual environments, build output and private work areas are never listed
  file by file: private areas appear as a protected range with their responsibility only.

Every existing description is kept, new methods are added, deleted ones are dropped, and
the tool never invents a file that does not exist. Annotations recorded in an earlier
round are carried over for paths that still exist and listed separately when a path has
been retired, so the plan's trace survives the switch to the actual tree.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / ".agents/skills"
README = SKILLS / "README.md"
FULL_TREE = ROOT / "04_诊断与系统日志/完整目录树.md"
PACKAGES = ["laohu-ai-visual", "laohu-script-writer", "laohu-image-creation",
            "laohu-video-prompt", "laohu-language-mode", "laohu-inspection"]
DIR_NOTES = {
    "agents": "宿主识别元数据",
    "references": "按需读取的专业方法、案例与合同",
    "scripts": "执行、检索或校验工具",
    "skills": "内部专业，每项有自己的入口与验收",
}
SKIP = {"__pycache__", ".DS_Store", ".git", ".ipynb_checkpoints", "node_modules"}
ENTRY = re.compile(r"^(?P<prefix>(?:[│ ]   )*)(?P<mark>[├└])── (?P<name>.+?)(?:  (?P<desc>.*))?$")
ANNOTATION = re.compile(r"^(?P<name>.+?)(?:\s{2,}(?P<desc>.*))?$")

# Directories whose contents stay private: the tree names the protected range only.
PROTECTED = {
    "00_输入原料": "未归属作品的需求、研究与外部资料（本地输入，不逐条公开）",
    "01_作品项目/进行中": "进行中的作品（本地私有：剧本、资产、提示词、生成素材）",
    "01_作品项目/已完成": "已完成的作品（本地私有）",
    "01_作品项目/已发布": "已发布的作品与发布数据（本地私有）",
    "02_共享资产库/故事素材库": "完整来源原话、原子与 usage（私人内容，不入公开树）",
    ".agents/skills/laohu-script-writer/assets/故事原子": "私有故事应用原子（受 .gitignore 保护，不逐条列出）",
}
PROJECT_SKIP = {"tmp", "output", ".git", "node_modules", "__pycache__", ".DS_Store",
                ".ipynb_checkpoints", "docs", ".obsidian", ".idea", ".vscode", ".evolver"}
PROJECT_VISIBLE_HIDDEN = {".agents", ".gitignore"}


def project_visible(child: Path) -> bool:
    if child.name in PROJECT_SKIP:
        return False
    if child.name.startswith(".") and child.name not in PROJECT_VISIBLE_HIDDEN:
        return False
    return True


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


# --------------------------------------------------------------------------------------
# Skills README (Skills subtree only)
# --------------------------------------------------------------------------------------

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


def refresh_skills_readme() -> int:
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


# --------------------------------------------------------------------------------------
# Full project tree (whole visible project)
# --------------------------------------------------------------------------------------

def previous_annotations() -> dict[str, str]:
    """Plan annotations recorded on tree entries in an earlier round.

    They are read from the current file, and from the committed version when the working
    tree no longer carries them, so the plan's per-file trace survives regeneration.
    """
    candidates = []
    if FULL_TREE.is_file():
        candidates.append(FULL_TREE.read_text(encoding="utf-8"))
    try:
        import subprocess
        committed = subprocess.run(["git", "show", f"HEAD:{FULL_TREE.relative_to(ROOT)}"],
                                   cwd=ROOT, capture_output=True, text=True, check=True).stdout
        candidates.append(committed)
    except Exception:
        pass
    merged: dict[str, str] = {}
    for text in candidates:
        for path, desc in _annotations_in(text).items():
            if path not in merged or desc.startswith("【"):
                merged[path] = desc
    return merged


def _annotations_in(text: str) -> dict[str, str]:
    found: dict[str, str] = {}
    stack: list[str] = []
    inside = False
    for line in text.splitlines():
        if line.strip() == "```text":
            inside = True
            continue
        if line.strip() == "```" and inside:
            inside = False
            continue
        if not inside:
            continue
        match = ENTRY.match(line)
        if not match:
            continue
        depth = len(match.group("prefix")) // 4
        raw = match.group("name").strip()
        is_dir = raw.endswith("/")
        name = raw.rstrip("/")
        stack = stack[:depth] + [name]
        desc = (match.group("desc") or "").strip()
        if desc and desc != name:
            found["/".join(stack)] = desc
    return found


def project_lines(directory: Path, prefix: str = "", relative: Path = Path(".")) -> list[str]:
    entries = []
    for child in sorted(directory.iterdir(), key=lambda p: (p.is_file(), p.name)):
        if not project_visible(child):
            continue
        entries.append(child)
    lines: list[str] = []
    for index, child in enumerate(entries):
        last = index == len(entries) - 1
        key = str((relative / child.name)) if relative != Path(".") else child.name
        protected = PROTECTED.get(key)
        label = child.name + ("/" if child.is_dir() else "")
        if protected:
            lines.append(f"{prefix}{'└' if last else '├'}── {label}   {protected}")
            continue
        if child.is_dir():
            lines.append(f"{prefix}{'└' if last else '├'}── {label}")
            lines.extend(project_lines(child, prefix + ("    " if last else "│   "), relative / child.name))
        else:
            lines.append(f"{prefix}{'└' if last else '├'}── {label}")
    return lines


def refresh_full_tree() -> int:
    annotations = previous_annotations()
    header = [
        "# 完整目录树（无省略）",
        "",
        "> 本树由 `scripts/update_skills_readme_tree.py` 从真实磁盘生成，是 ACTUAL 状态，"
        "不是目标图；隐藏缓存、`.git`、虚拟环境和构建产物不入树。",
        "> 私有区（作品项目、输入资料、完整来源库、私有应用原子）只显示保护范围，不逐条列出内容。",
        "> 目标树与逐项去向见 `全库整理方案.md` 与 `全库整理操作清单.json`；"
        "上一版带标注的计划树中，仍然存在的路径标注在下方“本轮变更去向”保留，已撤除的路径逐条列出。",
        "",
        "## 当前实际树",
        "",
        "```text",
        "老胡AI视觉/",
    ]
    body = project_lines(ROOT)
    retired = []
    for path, desc in sorted(annotations.items()):
        if desc.startswith("【"):
            # The earlier tree was rooted at .agents/skills/.
            if not (SKILLS / path).exists() and not (ROOT / path).exists():
                retired.append(f"- .agents/skills/{path}   {desc}")
    trailer = ["```", ""]
    if retired:
        trailer += ["## 本轮变更去向（上一版标注路径中已撤除的条目）", ""] + retired + [""]
    FULL_TREE.write_text("\n".join(header + body + trailer), encoding="utf-8")
    print("updated", FULL_TREE.relative_to(ROOT), f"({len(body)} entries, {len(retired)} retired)")
    return 0


def main() -> int:
    status = refresh_skills_readme()
    return status or refresh_full_tree()


if __name__ == "__main__":
    sys.exit(main())
