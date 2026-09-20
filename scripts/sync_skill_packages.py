#!/usr/bin/env python3
"""Maintain real package-local methods. Never required by package consumers or uploaders."""
from pathlib import Path
import argparse
import ast
import hashlib
import json
import os
import re

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = ROOT / "04_诊断与系统日志/五包迁移清单.json"


def digest(data):
    return hashlib.sha256(data).hexdigest()


def synchronize(manifest, check=False):
    data = json.loads(Path(manifest).read_text())
    records = data["copies"]
    by_target = {r["target"]: r["source"] for r in records}

    def package(path):
        return "/".join(Path(path).parts[:3])

    by_pair = {(package(r["target"]), r["source"]): r["target"] for r in records}

    def original(path):
        seen = set()
        while path in by_target and path not in seen:
            seen.add(path)
            path = by_target[path]
        return path

    def local_target(target, owner):
        target = original(target)
        if target.startswith(owner + "/"):
            return target
        if target in {"AGENTS.md", "README.md", "输入输出索引.md"}:
            return owner + "/references/独立使用与交接.md"
        if target.endswith(("能力注册表.json", "能力协作图谱.md", "外部能力依赖清单.md", "laohu_skills核心合约.md")):
            return owner + "/references/独立使用与交接.md"
        if target.endswith("/SKILL.md"):
            # An embedded method must not recursively import another complete department.
            return by_pair.get((owner, target))
        if not target.startswith((".agents/skills/", "scripts/")):
            return None
        if (owner, target) not in by_pair:
            destination = owner + "/references/内置方法/" + target.removeprefix(".agents/skills/")
            by_pair[owner, target] = destination
            by_target[destination] = target
            records.append({"source": target, "target": destination})
        return by_pair[owner, target]

    def render(record):
        source = ROOT / record["source"]
        if not source.is_file():
            raise ValueError("Missing authoritative method: " + str(source))
        raw = source.read_bytes()
        if source.suffix == ".py":
            # A real script copy also needs its local imports; stdlib imports add nothing.
            for node in ast.walk(ast.parse(raw.decode())):
                modules = [n.name for n in node.names] if isinstance(node, ast.Import) else [node.module] if isinstance(node, ast.ImportFrom) and node.module else []
                for module in modules:
                    dependency = source.parent / (module + ".py")
                    if dependency.is_file():
                        local_target(str(dependency.relative_to(ROOT)), package(record["target"]))
            if source.name == "story_material_db.py":
                helper = source.parents[3] / "scripts/story_atoms.py"
                local_target(str(helper.relative_to(ROOT)), package(record["target"]))
        if source.suffix != ".md" or record.get("mode") == "file":
            return raw, raw
        text = raw.decode()
        if source.name == "SKILL.md":
            text = re.sub(r"\A---\n.*?\n---\n", "", text, count=1, flags=re.S)
        dest = ROOT / record["target"]
        owner = package(record["target"])

        def remap(raw_target):
            value, sep, anchor = raw_target.strip("<>").partition("#")
            if not value or re.match(r"^[a-z]+:", value):
                return raw_target
            resolved = (source.parent / value).resolve()
            if not resolved.is_relative_to(ROOT) or not resolved.exists():
                return None
            target = local_target(str(resolved.relative_to(ROOT)), owner)
            return (os.path.relpath(ROOT / target, dest.parent) + (sep + anchor if sep else "")) if target else None

        protected = []
        def hold(value):
            protected.append(value)
            return "\x00REF" + str(len(protected)-1) + "\x00"

        def link(match):
            label, raw_target = match[1], match[2]
            target = remap(raw_target)
            return hold("[" + label + "](" + target + ")" if target else label + "（按本包任务交接，非必需外部文件）")

        text = re.sub(r"\[([^\]\n]*)\]\(([^)\n]+)\)", link, text)
        def code(match):
            value = match[1]
            if re.match(r"^[a-z]+:", value):
                return match[0]
            file = (source.parent / value).resolve()
            if not file.is_file():
                return match[0]
            target = remap(value)
            return "`" + target + "`" if target else "由使用者提供的作品输入或交接材料"

        text = re.sub(r"(?<!`)`([^`\n]+)`(?!`)", code, text)
        text = re.sub(r"\x00REF(\d+)\x00", lambda m: protected[int(m[1])], text)
        return raw, text.encode()

    errors = []
    for record in records:
        source, expected = render(record)
        target = ROOT / record["target"]
        if check:
            if not target.is_file() or target.read_bytes() != expected:
                errors.append(record["target"])
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(expected)
            record["source_sha256"] = digest(source)
            record["target_sha256"] = digest(expected)
    if not check:
        Path(manifest).write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")
    return errors


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    errors = synchronize(args.manifest, args.check)
    print(json.dumps({"ok": not errors, "stale_methods": errors}, ensure_ascii=False))
    raise SystemExit(bool(errors))
