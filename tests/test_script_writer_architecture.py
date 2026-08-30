from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class ScriptWriterArchitectureTests(unittest.TestCase):
    def read(self, relative: str) -> str:
        path = ROOT / relative
        self.assertTrue(path.is_file(), f"missing architecture file: {relative}")
        return path.read_text(encoding="utf-8")

    def combined(self, *relatives: str) -> str:
        return "\n".join(self.read(relative) for relative in relatives)

    def test_script_writer_routes_story_gaps_to_component_search(self) -> None:
        writer = self.read("skills/laohu-script-writer/SKILL.md")
        for anchor in (
            "故事构件查询合同",
            "story_component_library.py",
            "stats → search → get",
            "允许零采用并继续原创",
            "构件调用回执",
        ):
            self.assertIn(anchor, writer)

    def test_material_atoms_and_story_components_have_separate_owners(self) -> None:
        text = self.combined(
            "skills/laohu-script-writer/SKILL.md",
            "skills/laohu-story-material/SKILL.md",
            "skills/laohu-script-writer/references/06_故事构件拆解与组合语法.md",
        )
        self.assertIn("素材原子提供生活证据，故事构件提供状态变化方式", text)
        self.assertIn("source / atom / usage", text)
        self.assertIn("不改变素材库", text)
        self.assertIn("不保存私人原话", text)

    def test_component_candidates_require_causal_edges_and_character_intention(self) -> None:
        reference = self.read(
            "skills/laohu-script-writer/references/06_故事构件拆解与组合语法.md"
        )
        for anchor in (
            "前置条件 → 人物行动 → 状态变化 → 观众更新 → 下一压力",
            "人物行动理由",
            "至少三个因果真正不同",
            "替换职业、地点和道具不算因果不同",
            "并排堆叠",
        ):
            self.assertIn(anchor, reference)

    def test_expectation_contract_tracks_evidence_prediction_pressure_and_payoff(self) -> None:
        text = self.combined(
            "skills/laohu-script-writer/SKILL.md",
            "skills/laohu-script-writer/references/04_叙事视角命名与故事因果.md",
        )
        self.assertIn(
            "可见证据 → 暂时判断 → 可预见压力 → 未揭变量 → 部分兑现",
            text,
        )
        for anchor in ("主要注意入口", "承诺—兑现账本", "完成 / 扩大 / 推翻 / 重新解释"):
            self.assertIn(anchor, text)

    def test_scene_fusion_requires_one_bearing_action_and_one_primary_result(self) -> None:
        reference = self.read(
            "skills/laohu-script-writer/references/06_故事构件拆解与组合语法.md"
        )
        for anchor in (
            "场景融合",
            "同一承重行动",
            "一个主要状态结果",
            "争夺主结果",
            "拆场或淘汰",
        ):
            self.assertIn(anchor, reference)

    def test_formal_screenplay_separates_body_from_production_evidence(self) -> None:
        text = self.combined(
            "skills/laohu-script-writer/SKILL.md",
            "skills/laohu-script-writer/references/03_体量形态编号与连续性.md",
        )
        for anchor in (
            "剧本正文",
            "生产证据账本",
            "【声音：声源、发生方式和对行动的影响】",
            "【场次结果】",
            "出现前状态",
            "出现后状态",
            "连续性风险",
        ):
            self.assertIn(anchor, text)

    def test_screenplay_does_not_require_camera_lens_or_shot_size(self) -> None:
        reference = self.read(
            "skills/laohu-script-writer/references/03_体量形态编号与连续性.md"
        )
        self.assertIn("普通正式剧本不强制焦段、景别和机位", reference)
        self.assertIn("分镜与视频提示词", reference)

    def test_low_intensity_story_may_reject_component_stacking(self) -> None:
        text = self.combined(
            "skills/laohu-script-writer/SKILL.md",
            "skills/laohu-script-writer/references/06_故事构件拆解与组合语法.md",
            "skills/laohu-script-writer/references/05_剧本语言诊断与反向审稿.md",
        )
        self.assertIn("低烈度", text)
        self.assertIn("等待、距离、误解、表演", text)
        self.assertIn("不为连续反转强行堆叠", text)

    def test_empty_or_unfit_component_results_allow_original_writing(self) -> None:
        text = self.combined(
            "skills/laohu-script-writer/SKILL.md",
            "skills/laohu-script-writer/references/06_故事构件拆解与组合语法.md",
        )
        self.assertIn("允许零采用并继续原创", text)
        self.assertIn("构件库为空", text)
        self.assertIn("不得自动网络搜索", text)


if __name__ == "__main__":
    unittest.main()
