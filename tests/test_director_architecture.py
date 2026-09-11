from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class DirectorArchitectureTests(unittest.TestCase):
    def read(self, relative: str) -> str:
        path = ROOT / relative
        self.assertTrue(path.is_file(), f"missing architecture file: {relative}")
        return path.read_text(encoding="utf-8")

    def combined(self, *relatives: str) -> str:
        return "\n".join(self.read(relative) for relative in relatives)

    def test_general_director_is_an_independent_owner(self) -> None:
        director = self.read("skills/laohu-director/SKILL.md")
        for anchor in (
            "导演阐述",
            "观众经历",
            "主推进力",
            "部门任务",
            "保护项",
            "不产生第二份剧本",
            "底线门",
            "巅峰门",
        ):
            self.assertIn(anchor, director)

    def test_director_aphorism_is_a_choice_not_a_compressed_job_description(self) -> None:
        director = self.read("skills/laohu-director/SKILL.md")
        self.assertIn("手段可以万千，戏只能往一处去。", director)
        self.assertNotIn("作品不是把部门排成一队", director)
        self.assertNotIn("编剧把戏写出来，导演让观众经历它", director)

    def test_role_contract_separates_decision_direction_performance_and_reception(self) -> None:
        text = self.combined(
            "skills/laohu-director/SKILL.md",
            "skills/laohu-director/references/01_导演判断与协作网络.md",
        )
        for anchor in (
            "请求者 / 出品与决定者",
            "总导演",
            "演员 / 执行者",
            "最终观众",
            "一人可以兼任",
            "权限不能混写",
        ):
            self.assertIn(anchor, text)

    def test_network_uses_typed_edges_without_transferring_ownership(self) -> None:
        graph = self.read("02_共享资产库/05_工具流程/能力协作图谱.md")
        for edge in ("HANDOFF", "CONSULT", "REVIEW", "RETURN", "SHARED_SOURCE"):
            self.assertIn(edge, graph)
        for anchor in (
            "CONSULT ≠ HANDOFF",
            "调用不转移主责",
            "禁止覆盖项",
            "调用回执",
            "不默认读取所有文件",
        ):
            self.assertIn(anchor, graph)

    def test_router_calls_director_only_for_directorial_gaps(self) -> None:
        text = self.combined(
            "AGENTS.md",
            "skills/laohu-ai-visual/SKILL.md",
            "02_共享资产库/05_工具流程/laohu_skills核心合约.md",
            "输入输出索引.md",
        )
        self.assertIn("二十二个", text)
        self.assertIn("laohu-director", text)
        for anchor in (
            "公开作品",
            "跨多个专业节点",
            "局部机械返工",
            "顺序生产、网状会商、按根因返工",
        ):
            self.assertIn(anchor, text)

    def test_script_writer_is_director_literate_but_keeps_script_authority(self) -> None:
        writer = self.read("skills/laohu-script-writer/SKILL.md")
        for anchor in (
            "调度专业",
            "导演阐述",
            "正式剧本仍是唯一完整内容母版",
            "继承有效导演阐述",
            "不得私自更换全片胜负手",
            "CONSULT",
        ):
            self.assertIn(anchor, writer)

    def test_downstream_nodes_inherit_intent_and_return_upstream_gaps(self) -> None:
        text = self.combined(
            "skills/laohu-art-direction/SKILL.md",
            "skills/laohu-character-design/SKILL.md",
            "skills/laohu-costume-design/SKILL.md",
            "skills/laohu-set-design/SKILL.md",
            "skills/laohu-audio-design/SKILL.md",
            "skills/laohu-visual-assets/SKILL.md",
            "skills/laohu-video-prompt/SKILL.md",
            "skills/laohu-video-prompt/references/交接与验收.md",
            "skills/laohu-generation-review/SKILL.md",
            "skills/laohu-mv-director/SKILL.md",
        )
        for anchor in (
            "导演协作接口",
            "导演阐述",
            "调用不转移主责",
            "返回最早负责人",
        ):
            self.assertIn(anchor, text)
        self.assertIn("不得补编上游没有确定的戏", text)

    def test_behavior_scenarios_cover_transfer_and_counterexamples(self) -> None:
        capability = json.loads(self.read("tests/capability_scenarios.json"))
        evolution = json.loads(self.read("tests/evolution_scenarios.json"))
        names = {
            scenario["name"]
            for payload in (capability, evolution)
            for scenario in payload["scenarios"]
        }
        expected = {
            "同一题材不同目的必须重做导演判断",
            "不同题材可以共享观众变化机制",
            "用户兼任演员时权限仍须分离",
            "专业咨询不转移主责",
            "内部机械任务可以跳过总导演",
            "伪箴言不能进入执行接口",
        }
        self.assertTrue(expected.issubset(names), expected - names)

    def test_director_craft_compares_real_alternatives_before_selecting(self) -> None:
        text = self.combined(
            "skills/laohu-director/SKILL.md",
            "skills/laohu-director/references/01_导演判断与协作网络.md",
        )
        for anchor in (
            "导演问题单",
            "证据 / 假设 / 待确认",
            "候选方向卡",
            "差异轴",
            "受众等价测试",
            "机制差异测试",
            "同约束下成立",
            "淘汰理由",
            "反转条件",
        ):
            self.assertIn(anchor, text)

    def test_director_statement_exposes_choice_evidence_without_becoming_script(self) -> None:
        director = self.read("skills/laohu-director/SKILL.md")
        current = self.read(
            "04_诊断与系统日志/2026-09-06_总导演跨题材行为验证.md"
        )
        self.assertIn("【候选竞争】", director)
        for anchor in (
            "候选 A",
            "候选 B",
            "候选 C",
            "胜出方向",
            "淘汰理由",
        ):
            self.assertIn(anchor, director)
            self.assertIn(anchor, current)
        self.assertIn("导演阐述是取舍合同，不是内容摘要", director)

    def test_director_has_inspectable_cross_genre_behavior_evidence(self) -> None:
        evidence = self.read(
            "04_诊断与系统日志/2026-09-06_总导演跨题材行为验证.md"
        )
        for anchor in (
            "同材料异目的",
            "异题同机制",
            "低冲突治愈",
            "普通但正确的候选",
            "不强塞争吵或反转",
            "当前场景",
            "相邻场景",
            "保真场景",
            "失败场景",
        ):
            self.assertIn(anchor, evidence)

    def test_static_registry_declares_director_intermediate_results(self) -> None:
        capability = json.loads(self.read("tests/capability_scenarios.json"))
        cases = [
            scenario
            for scenario in capability["runtime_reachability_scenarios"]
            if scenario["owner"] == "laohu-director"
        ]
        self.assertGreaterEqual(len(cases), 3)
        required = {
            "同材料异目的的候选竞争",
            "低冲突治愈不强塞高烈度",
            "普通但正确的有效对手允许胜出",
        }
        self.assertTrue(required.issubset({case["name"] for case in cases}))


if __name__ == "__main__":
    unittest.main()
