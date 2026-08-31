from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class MvArchitectureTests(unittest.TestCase):
    def read(self, relative: str) -> str:
        path = ROOT / relative
        self.assertTrue(path.is_file(), f"missing architecture file: {relative}")
        return path.read_text(encoding="utf-8")

    def test_mv_direction_is_an_independent_owner(self) -> None:
        skill = self.read("skills/laohu-mv-director/SKILL.md")

        for anchor in (
            "歌曲箴言",
            "歌曲事实层",
            "MV导演层",
            "生产时间线层",
            "MV导演交接包",
            "底线门",
            "巅峰门",
        ):
            self.assertIn(anchor, skill)

    def test_final_audio_is_authoritative_but_missing_audio_does_not_create_fake_timing(self) -> None:
        skill = self.read("skills/laohu-mv-director/SKILL.md")

        self.assertIn("最终音频是时间权威", skill)
        self.assertIn("待音频校准", skill)
        self.assertIn("不得伪造精确时间码", skill)
        self.assertIn("ASR 只做对齐候选", skill)

    def test_creative_song_structure_is_separate_from_model_production_units(self) -> None:
        skill = self.read("skills/laohu-mv-director/SKILL.md")

        self.assertIn("创作段落不服从模型时长", skill)
        self.assertIn("生成单元不冒充剪辑镜头", skill)
        self.assertIn("不固定四宫格", skill)
        self.assertIn("单帧 / 首尾帧 / 多关键状态", skill)
        self.assertNotIn("10—15 秒整数", skill)

    def test_mv_architecture_is_text_only_and_model_neutral(self) -> None:
        skill = self.read("skills/laohu-mv-director/SKILL.md")

        self.assertIn("只交付文本", skill)
        self.assertIn("不调用外部 API", skill)
        self.assertIn("目标模型能力合同", skill)
        self.assertNotIn("RunningHub", skill)
        self.assertNotIn("h3-prompt-writing", skill)

    def test_mv_owner_is_reachable_and_hands_off_to_existing_image_and_video_skills(self) -> None:
        agents = self.read("AGENTS.md")
        router = self.read("skills/laohu-ai-visual/SKILL.md")
        contract = self.read("02_共享资产库/05_工具流程/laohu_skills核心合约.md")
        assets = self.read("skills/laohu-visual-assets/SKILL.md")
        video = self.read("skills/laohu-video-prompt/SKILL.md")

        for text in (agents, router, contract):
            self.assertIn("laohu-mv-director", text)
        self.assertIn("MV分镜资产任务", assets)
        self.assertIn("MV导演交接包", video)


if __name__ == "__main__":
    unittest.main()
