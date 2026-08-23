#!/usr/bin/env python3
"""Validate that the visual project exposes executable capabilities, not four-layer labels."""

from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCENARIOS = ROOT / "tests" / "capability_scenarios.json"


def fail(message: str, failures: list[str]) -> None:
    failures.append(message)
    print(f"FAIL: {message}")


def passed(message: str) -> None:
    print(f"PASS: {message}")


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    data = json.loads(SCENARIOS.read_text(encoding="utf-8"))
    failures: list[str] = []
    skill_text: dict[str, str] = {}

    for skill, contract in data["skill_contracts"].items():
        path = ROOT / "skills" / skill / "SKILL.md"
        if not path.is_file():
            fail(f"missing owner skill: {skill}", failures)
            continue
        text = path.read_text(encoding="utf-8")
        skill_text[skill] = text

        for heading in contract["headings"]:
            pattern = rf"^##\s+[^\n]*{re.escape(heading)}[^\n]*$"
            if re.search(pattern, text, flags=re.MULTILINE):
                passed(f"{skill} owns domain section: {heading}")
            else:
                fail(f"{skill} missing domain section: {heading}", failures)

        for anchor in contract["anchors"]:
            if anchor in text:
                passed(f"{skill} contains capability anchor: {anchor}")
            else:
                fail(f"{skill} missing capability anchor: {anchor}", failures)

        aphorism_sections = re.findall(
            r"^##\s+[^\n]*箴言[^\n]*\n+([^\n#][^\n]*)",
            text,
            flags=re.MULTILINE,
        )
        if not aphorism_sections:
            fail(f"{skill} has no domain aphorism", failures)
        else:
            aphorism = aphorism_sections[0].strip().strip("*>")
            if len(aphorism) <= 64 and not re.search(r"必须|禁止|不得|需要", aphorism):
                passed(f"{skill} aphorism is compact and directional")
            else:
                fail(f"{skill} aphorism became an instruction or explanation: {aphorism}", failures)

        references = sorted((ROOT / "skills" / skill / "references").glob("*.md"))
        for reference in references:
            if reference.name in text:
                passed(f"{skill} routes reference: {reference.name}")
            else:
                fail(f"{skill} leaves reference unreachable: {reference.name}", failures)

    all_skill_text = "\n".join(skill_text.values())
    if re.search(r"^##\s*(灵魂|筋骨|血肉|表皮)(层)?\s*$", all_skill_text, flags=re.MULTILINE):
        fail("downstream skills expose generic four-layer headings", failures)
    else:
        passed("four-layer reasoning is compiled into domain-native sections")

    agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
    for pattern in data["root_forbidden_patterns"]:
        if pattern in agents:
            fail(f"top-level rules still own execution detail: {pattern}", failures)
        else:
            passed(f"execution detail delegated from top level: {pattern}")

    for migration in data["migration_contracts"]:
        path = ROOT / migration["file"]
        if not path.is_file():
            fail(f"migrated capability has no owner file: {migration['capability']}", failures)
            continue
        text = path.read_text(encoding="utf-8")
        missing = [anchor for anchor in migration["anchors"] if anchor not in text]
        if missing:
            fail(
                f"migrated capability is incomplete: {migration['capability']} -> "
                f"{', '.join(missing)}",
                failures,
            )
        else:
            passed(
                f"legacy capability retained by unique owner: {migration['capability']}"
            )

    registered_sources: set[str] = set()
    for dependency in data["external_dependency_contracts"]:
        source_relative = dependency["canonical_source"]
        registered_sources.add(source_relative)
        source = ROOT / source_relative
        mirror = ROOT / dependency["portable_mirror"]
        adapter = ROOT / dependency["local_adapter"]
        return_owner = ROOT / dependency["return_owner"]

        for role, path in [
            ("canonical source", source),
            ("portable mirror", mirror),
            ("local adapter", adapter),
            ("return owner", return_owner),
        ]:
            if path.is_file():
                passed(f"external dependency has {role}: {dependency['name']}")
            else:
                fail(f"external dependency missing {role}: {dependency['name']}", failures)

        if source.is_file() and mirror.is_file():
            if digest(source) == digest(mirror):
                passed(f"external source mirror is exact: {dependency['name']}")
            else:
                fail(f"external source mirror drifted: {dependency['name']}", failures)

        if adapter.is_file():
            adapter_text = adapter.read_text(encoding="utf-8")
            missing = [
                anchor
                for anchor in dependency["adapter_anchors"]
                if anchor not in adapter_text
            ]
            if missing:
                fail(
                    f"external adapter identity is incomplete: {dependency['name']} -> "
                    f"{', '.join(missing)}",
                    failures,
                )
            else:
                passed(f"external adapter identity is explicit: {dependency['name']}")

        for caller_relative, anchors in dependency["caller_contracts"].items():
            caller = ROOT / caller_relative
            if not caller.is_file():
                fail(f"external dependency caller missing: {caller_relative}", failures)
                continue
            caller_text = caller.read_text(encoding="utf-8")
            missing = [anchor for anchor in anchors if anchor not in caller_text]
            if missing:
                fail(
                    f"external dependency caller is ambiguous: {caller_relative} -> "
                    f"{', '.join(missing)}",
                    failures,
                )
            else:
                passed(f"external dependency caller is explicit: {caller_relative}")

    discovered_sources = {
        path.relative_to(ROOT).as_posix()
        for path in (
            ROOT / "02_共享资产库/05_工具流程/外部优化Skill"
        ).glob("*/SKILL.md")
    }
    unregistered_sources = sorted(discovered_sources - registered_sources)
    stale_sources = sorted(registered_sources - discovered_sources)
    if unregistered_sources:
        fail(
            "unregistered external Skill source: " + ", ".join(unregistered_sources),
            failures,
        )
    else:
        passed("all vendored external Skill sources are registered")
    if stale_sources:
        fail("registered external Skill source missing: " + ", ".join(stale_sources), failures)
    else:
        passed("external Skill registry has no stale source")

    for scenario in data["scenarios"]:
        scenario_ok = True
        for stage in scenario["chain"]:
            owner = stage["owner"]
            owner_text = skill_text.get(owner, "")
            missing = [anchor for anchor in stage["anchors"] if anchor not in owner_text]
            if missing:
                scenario_ok = False
                fail(
                    f"scenario '{scenario['name']}' breaks at {owner}; missing {', '.join(missing)}",
                    failures,
                )
        if scenario_ok:
            passed(f"scenario chain is owned end to end: {scenario['name']}")

    document_contracts = {
        "02_共享资产库/00_核心规则手册.md": {
            "required": ["能力地图", "不承担专业执行规则", "唯一负责人"],
            "forbidden": ["后续创作默认以顶级影视导演"],
            "max_lines": 260,
        },
        "02_共享资产库/05_工具流程/助手执行失败经验与防复发规则.md": {
            "required": ["历史证据库", "不作为当前执行规则"],
            "forbidden": ["是所有后续作品、skill 调用、提示词生成和复盘都必须遵守的执行规则"],
        },
        "02_共享资产库/05_工具流程/laohu_skills能力加厚规范.md": {
            "required": ["原则发现", "行为验证", "唯一负责人"],
            "max_lines": 180,
        },
    }
    for relative, contract in document_contracts.items():
        path = ROOT / relative
        if not path.is_file():
            fail(f"missing architecture document: {relative}", failures)
            continue
        text = path.read_text(encoding="utf-8")
        for anchor in contract["required"]:
            if anchor in text:
                passed(f"architecture document owns role: {relative} -> {anchor}")
            else:
                fail(f"architecture document missing role: {relative} -> {anchor}", failures)
        for forbidden in contract.get("forbidden", []):
            if forbidden in text:
                fail(f"legacy authority still active: {relative} -> {forbidden}", failures)
            else:
                passed(f"legacy authority retired: {relative} -> {forbidden}")
        line_count = len(text.splitlines())
        max_lines = contract.get("max_lines")
        if max_lines is not None:
            if line_count <= max_lines:
                passed(f"architecture document remains navigable: {relative}")
            else:
                fail(
                    f"architecture document exceeds navigation role: {relative} "
                    f"({line_count} > {max_lines})",
                    failures,
                )

    index = (ROOT / "输入输出索引.md").read_text(encoding="utf-8")
    if "2. [laohu-ai-visual]" in index and "按主任务读取唯一负责 Skill" in index:
        passed("public index enters through the router and one owner skill")
    else:
        fail("public index still lacks single-owner routing", failures)

    if failures:
        print(f"Capability architecture validation failed with {len(failures)} issue(s).")
        return 1
    print("Capability architecture validation passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
