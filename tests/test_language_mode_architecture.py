from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class LanguageModeArchitectureTests(unittest.TestCase):
    def read(self, relative: str) -> str:
        path = ROOT / relative
        self.assertTrue(path.is_file(), f"missing architecture file: {relative}")
        return path.read_text(encoding="utf-8")

    def combined(self, *relatives: str) -> str:
        return "\n".join(self.read(relative) for relative in relatives)

    def test_language_mode_skill_has_all_primary_modes(self) -> None:
        text = self.combined(
            "skills/laohu-language-mode/SKILL.md",
            "skills/laohu-language-mode/references/01_模式判定与块级切换.md",
            "skills/laohu-language-mode/references/02_用户沟通与制作说明.md",
            "skills/laohu-language-mode/references/03_剧本文本块语言.md",
            "skills/laohu-language-mode/references/04_资产图片视频与声音提示词桥接.md",
            "skills/laohu-language-mode/references/05_有效信息与冗余裁决.md",
        )
        payload = json.loads(self.read("tests/language_mode_scenarios.json"))
        self.assertEqual(11, len(payload["allowed_modes"]))
        for mode in payload["allowed_modes"]:
            self.assertIn(mode, text)

    def test_language_mode_is_shared_router_not_content_owner(self) -> None:
        text = self.read("skills/laohu-language-mode/SKILL.md")
        for anchor in (
            "不拥有内容权",
            "不新增生产阶段",
            "文本块改变时重新判定",
            "返回内容负责人",
            "不因顺口改动锁定台词",
        ):
            self.assertIn(anchor, text)

    def test_resolver_uses_receiver_purpose_and_block_before_voice(self) -> None:
        text = self.read(
            "skills/laohu-language-mode/references/01_模式判定与块级切换.md"
        )
        for anchor in (
            "current_role",
            "work_phase",
            "block_type",
            "speaker",
            "receiver",
            "purpose",
            "domain_authority",
            "fixed_facts",
            "forbidden_leakage",
            "return_owner",
            "先判接收者与任务",
            "再叠加人物声音与场景状态",
        ):
            self.assertIn(anchor, text)

    def test_screenplay_modes_separate_action_cue_dialogue_and_note(self) -> None:
        text = self.read(
            "skills/laohu-language-mode/references/03_剧本文本块语言.md"
        )
        for anchor in (
            "镜头方头只负责定位",
            "动作正文只写可见可听",
            "每句有声台词",
            "情绪阶段",
            "压制或释放",
            "可听语气",
            "关系态度",
            "声音放低",
            "人物说话是在做事",
            "知识卡",
            "剧本说明不冒充镜头事件",
        ):
            self.assertIn(anchor, text)

    def test_prompt_modes_return_to_domain_authorities(self) -> None:
        text = self.read(
            "skills/laohu-language-mode/references/04_资产图片视频与声音提示词桥接.md"
        )
        for anchor in (
            "ASSET_SPEC / IMAGE_PROMPT → laohu-visual-assets",
            "VIDEO_PROMPT → laohu-video-prompt",
            "AUDIO_PROMPT → laohu-audio-design",
            "不得复制",
            "静态时刻",
            "时间因果",
            "锁定台词",
        ):
            self.assertIn(anchor, text)

    def test_existing_owners_call_language_mode_without_losing_authority(self) -> None:
        text = self.combined(
            "AGENTS.md",
            "skills/laohu-ai-visual/SKILL.md",
            "skills/laohu-script-writer/SKILL.md",
            "skills/laohu-visual-assets/SKILL.md",
            "skills/laohu-video-prompt/SKILL.md",
            "skills/laohu-audio-design/SKILL.md",
            "02_共享资产库/05_工具流程/laohu_skills核心合约.md",
            "02_共享资产库/05_工具流程/能力协作图谱.md",
            "输入输出索引.md",
        )
        self.assertIn("十七个", text)
        self.assertIn("laohu-language-mode", text)
        for anchor in (
            "调用不转移主责",
            "文本块",
            "内容不足",
            "返回原负责人",
        ):
            self.assertIn(anchor, text)

    def test_music_v4_is_research_source_not_runtime_dependency(self) -> None:
        text = self.combined(
            "skills/laohu-language-mode/SKILL.md",
            "skills/laohu-language-mode/references/02_用户沟通与制作说明.md",
            "04_诊断与系统日志/语言模式语义迁移台账.json",
        )
        self.assertIn("研究来源", text)
        self.assertIn('"runtime_dependency": false', text)
        self.assertNotIn(
            "/Volumes/Laohu_Work/项目/老胡/老胡自媒体/老胡音乐V4", text
        )

    def test_migration_ledger_covers_all_decisions(self) -> None:
        payload = json.loads(
            self.read("04_诊断与系统日志/语言模式语义迁移台账.json")
        )
        decisions = {item["decision"] for item in payload["records"]}
        self.assertEqual({"KEEP", "REWRITE", "MOVE", "EXCLUDE"}, decisions)
        self.assertTrue(all(not item["runtime_dependency"] for item in payload["records"]))

    def test_behavior_scenarios_cover_current_adjacent_and_failure_cases(self) -> None:
        payload = json.loads(self.read("tests/language_mode_scenarios.json"))
        names = {scenario["name"] for scenario in payload["scenarios"]}
        expected = {
            "同一镜头按文本块连续换挡",
            "Luna教学喜剧不把知识卡塞进逃跑台词",
            "温暖爱情故事不继承打斗和曲解",
            "安静治愈故事允许克制与留白",
            "动作缺因果时返回编剧而非语言润色",
        }
        self.assertTrue(expected.issubset(names), expected - names)
        failure = next(
            scenario
            for scenario in payload["scenarios"]
            if scenario["name"] == "动作缺因果时返回编剧而非语言润色"
        )
        self.assertEqual("laohu-script-writer", failure["expected_return_owner"])

    def test_agent_metadata_is_discoverable_and_implicitly_callable(self) -> None:
        text = self.read("skills/laohu-language-mode/agents/openai.yaml")
        for anchor in (
            'display_name: "老胡语言模式与身份切换"',
            "$laohu-language-mode",
            "allow_implicit_invocation: true",
        ):
            self.assertIn(anchor, text)

    def test_effective_information_contract_is_reachable_and_has_two_gates(self) -> None:
        skill = self.read("skills/laohu-language-mode/SKILL.md")
        self.assertIn("references/05_有效信息与冗余裁决.md", skill)
        text = self.read(
            "skills/laohu-language-mode/references/05_有效信息与冗余裁决.md"
        )
        for anchor in (
            "receiver_before",
            "target_delta",
            "contribution",
            "evidence_of_change",
            "removal_cost",
            "best_carrier",
            "decision",
            "必要信息保护门",
            "边际作用门",
            "KEEP",
            "MERGE",
            "MOVE",
            "DELETE",
            "RETURN",
        ):
            self.assertIn(anchor, text)

    def test_each_language_mode_defines_its_own_effective_change(self) -> None:
        payload = json.loads(self.read("tests/language_mode_scenarios.json"))
        text = self.read(
            "skills/laohu-language-mode/references/05_有效信息与冗余裁决.md"
        )
        for mode in payload["allowed_modes"]:
            self.assertIn(f"`{mode}`", text)
        for forbidden in ("统一字数上限", "统一句长阈值", "形容词数量阈值"):
            self.assertIn(f"禁止：{forbidden}", text)

    def test_dialogue_effectiveness_is_action_and_consequence_not_length(self) -> None:
        text = self.combined(
            "skills/laohu-language-mode/references/03_剧本文本块语言.md",
            "skills/laohu-language-mode/references/05_有效信息与冗余裁决.md",
        )
        for anchor in (
            "开口资格",
            "语言动作",
            "新增作用",
            "话后结果",
            "呼吸容量",
            "尾部检查",
            "必要重复",
            "沉默",
        ):
            self.assertIn(anchor, text)

    def test_full_document_revision_covers_every_active_block_type(self) -> None:
        text = self.combined(
            "skills/laohu-language-mode/SKILL.md",
            "skills/laohu-language-mode/references/03_剧本文本块语言.md",
            "skills/laohu-language-mode/references/05_有效信息与冗余裁决.md",
        )
        for anchor in (
            "整稿覆盖门",
            "已出现的每种文本块",
            "不能只改台词",
            "块级处理回执",
        ):
            self.assertIn(anchor, text)

    def test_effectiveness_contract_is_wired_to_domain_owners(self) -> None:
        text = self.combined(
            "skills/laohu-script-writer/SKILL.md",
            "skills/laohu-visual-assets/SKILL.md",
            "skills/laohu-video-prompt/SKILL.md",
            "skills/laohu-audio-design/SKILL.md",
            "02_共享资产库/05_工具流程/laohu_skills核心合约.md",
            "输入输出索引.md",
        )
        for anchor in (
            "有效信息与冗余裁决",
            "必要信息保护门",
            "边际作用门",
            "返回原负责人",
        ):
            self.assertIn(anchor, text)

    def test_effectiveness_scenarios_cover_long_short_repeat_move_and_return(self) -> None:
        payload = json.loads(self.read("tests/language_mode_scenarios.json"))
        scenarios = payload["effectiveness_scenarios"]
        names = {scenario["name"] for scenario in scenarios}
        expected = {
            "追逐台词把重复用途迁移到屏幕文字",
            "正侧光重复因澄清与笑点继续有效",
            "短台词没有语言动作仍然无效",
            "爱情故事重复问句因关系变化而保留",
            "复杂动作因果不得为简短而删除",
            "资产形容词不能排错则删除或合并",
            "图片中的时间过程迁移到视频",
            "视频保留空间锚点并删除同义审美词",
            "声音删除不能改变可听结果的视觉说明",
            "缺少专业内容时返回原负责人",
        }
        self.assertTrue(expected.issubset(names), expected - names)
        decisions = {
            decision
            for scenario in scenarios
            for decision in scenario["expected_decisions"]
        }
        self.assertEqual({"KEEP", "MERGE", "MOVE", "DELETE", "RETURN"}, decisions)


if __name__ == "__main__":
    unittest.main()
