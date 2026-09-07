from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class VideoBatchArchitectureTests(unittest.TestCase):
    def read(self, relative: str) -> str:
        path = ROOT / relative
        self.assertTrue(path.is_file(), f"missing architecture file: {relative}")
        return path.read_text(encoding="utf-8")

    def combined(self, *relatives: str) -> str:
        return "\n".join(self.read(relative) for relative in relatives)

    def test_batch_is_the_canonical_generation_request(self) -> None:
        text = self.combined(
            "AGENTS.md",
            "02_共享资产库/05_工具流程/laohu_skills核心合约.md",
            "skills/laohu-video-prompt/SKILL.md",
        )
        for anchor in (
            "E01-S02-B01",
            "Batch",
            "一次实际提交给目标视频模型",
            "每个新场次的 `B` 从 `01` 重新开始",
            "历史 `VID`",
        ):
            self.assertIn(anchor, text)

    def test_batch_never_crosses_a_scene(self) -> None:
        video_skill = self.read("skills/laohu-video-prompt/SKILL.md")
        workflow = self.read(
            "02_共享资产库/05_工具流程/短剧剧本到视频提示词编号与时长规则.md"
        )
        combined = video_skill + workflow
        self.assertIn("一个批次只能属于一个场次", combined)
        self.assertIn("跨场双端转场", combined)
        self.assertIn("上一场最后一批", combined)
        self.assertIn("下一场 `B01`", combined)
        self.assertNotIn("场景簇允许在同一叙事段落里经过少量地点切换", video_skill)

    def test_batch_partition_uses_hard_and_fusion_gates(self) -> None:
        text = self.combined(
            "skills/laohu-video-prompt/SKILL.md",
            "02_共享资产库/05_工具流程/短剧剧本到视频提示词编号与时长规则.md",
        )
        for anchor in (
            "硬边界门",
            "融合质量门",
            "时长上限不是必须填满的配额",
            "目标入口能力合同",
            "前一镜的结果",
            "后半段遗忘",
        ):
            self.assertIn(anchor, text)

    def test_batch_prompt_keeps_source_mapping_and_local_shots(self) -> None:
        text = self.combined(
            "skills/laohu-video-prompt/SKILL.md",
            "02_共享资产库/01_模板库/视频模板/模板_视频提示词_基础设定氛围画面内容.md",
        )
        for anchor in (
            "源剧本镜头",
            "E-S-C",
            "镜头01",
            "开场状态",
            "结束状态",
            "交接载体",
            "合并理由",
        ):
            self.assertIn(anchor, text)


if __name__ == "__main__":
    unittest.main()
