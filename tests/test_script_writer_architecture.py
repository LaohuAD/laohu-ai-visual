from __future__ import annotations

import re
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

    def test_formal_screenplay_contains_readable_brief_and_numbered_shots(self) -> None:
        text = self.combined(
            "skills/laohu-script-writer/SKILL.md",
            "skills/laohu-script-writer/references/03_体量形态编号与连续性.md",
        )
        for anchor in (
            "【剧本说明】",
            "【作品信息】",
            "【故事说明】",
            "【镜1｜E01-S01-C01｜全景｜固定镜头｜约4秒】",
            "所有观众会看到或听到的正文必须归入一个镜号",
            "景别是镜头属性，不是编号",
        ):
            self.assertIn(anchor, text)
        self.assertNotIn("普通正式剧本不强制焦段、景别和机位", text)

    def test_screen_relationship_constrains_view_without_device_coordinates(self) -> None:
        reference = self.read(
            "skills/laohu-script-writer/references/03_体量形态编号与连续性.md"
        )
        for anchor in (
            "画面位置",
            "身体朝向",
            "视线对象",
            "遮挡",
            "关系距离",
            "设备坐标",
            "POV",
            "过肩",
        ):
            self.assertIn(anchor, reference)
        self.assertIn("读者自然能反推出摄影机的位置", reference)

    def test_performable_psychology_supports_but_never_replaces_screen_evidence(self) -> None:
        reference = self.read(
            "skills/laohu-script-writer/references/05_剧本语言诊断与反向审稿.md"
        )
        self.assertNotIn("不写心理描写，只写能被看见或听见的内容", reference)
        for anchor in (
            "可表演的心理解释",
            "不能代替画面",
            "可见或可听证据",
            "行动后果",
            "普通自然说话可以不标",
        ):
            self.assertIn(anchor, reference)

    def test_storyboard_is_integrated_and_video_prompt_preserves_source_mapping(self) -> None:
        text = self.combined(
            "AGENTS.md",
            "02_共享资产库/05_工具流程/laohu_skills核心合约.md",
            "02_共享资产库/05_工具流程/短剧剧本到视频提示词编号与时长规则.md",
            "skills/laohu-video-prompt/SKILL.md",
        )
        for anchor in (
            "文字分镜并入正式剧本",
            "取消独立分镜宏观表",
            "剧本镜号来源映射",
            "拆镜、并镜",
            "返回编剧",
        ):
            self.assertIn(anchor, text)

    def test_complete_lighting_sample_uses_shots_as_the_only_body_container(self) -> None:
        sample = self.read(
            "04_诊断与系统日志/2026-09-05_镜头化剧本完整验证样例.md"
        )
        first_shot = sample.index("【镜1｜E01-S01-C01")
        first_action = sample.index("△")
        self.assertLess(first_shot, first_action)
        ids = re.findall(r"E01-S01-C(\d{2})", sample)
        self.assertGreaterEqual(len(ids), 8)
        self.assertEqual(ids, [f"{number:02d}" for number in range(1, len(ids) + 1)])
        for anchor in (
            "遥控器一直在露娜右手里",
            "老胡空手",
            "测试摄影机",
            "节目镜头",
            "监视器",
            "三角油光",
            "【场次结果】",
        ):
            self.assertIn(anchor, sample)
        self.assertNotIn("镜头作用：", sample)
        self.assertNotRegex(sample, r"摄影机.{0,12}(45度|\d+(?:\.\d+)?米)")

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

    def test_character_voice_starts_with_perception_and_interpretation(self) -> None:
        text = self.combined(
            "skills/laohu-script-writer/SKILL.md",
            "skills/laohu-script-writer/references/04_口述台词与方言.md",
        )
        for anchor in (
            "人物声音合同",
            "他优先注意什么",
            "他会怎样解释证据",
            "他最不愿直接说出什么",
            "未说出的普通愿望",
        ):
            self.assertIn(anchor, text)
        self.assertIn("口头禅、方言词和金句都不能单独证明人物", text)

    def test_professional_perception_requires_grounded_expertise(self) -> None:
        reference = self.read(
            "skills/laohu-script-writer/references/04_口述台词与方言.md"
        )
        for anchor in (
            "职业化感知",
            "前史、训练或当场证据",
            "普通人不会优先注意",
            "不可信的超能力",
        ):
            self.assertIn(anchor, reference)

    def test_related_words_change_meaning_without_random_metaphor_stacking(self) -> None:
        reference = self.read(
            "skills/laohu-script-writer/references/04_口述台词与方言.md"
        )
        for anchor in (
            "同组词语换义",
            "同一条人物矛盾",
            "新指向",
            "随机更换漂亮意象",
        ):
            self.assertIn(anchor, reference)

    def test_voiceover_adds_information_and_stylish_prose_must_change_scene_state(self) -> None:
        text = self.combined(
            "skills/laohu-script-writer/SKILL.md",
            "skills/laohu-script-writer/references/04_口述台词与方言.md",
            "skills/laohu-script-writer/references/05_剧本语言诊断与反向审稿.md",
        )
        for anchor in (
            "补充 / 对位 / 反差",
            "不同义复述画面",
            "感知证据 → 人物解释 → 当场行动 → 可见后果",
            "删掉漂亮独白",
            "人物选择和场次状态不变",
        ):
            self.assertIn(anchor, text)


if __name__ == "__main__":
    unittest.main()
