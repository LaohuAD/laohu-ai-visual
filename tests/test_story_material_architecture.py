from __future__ import annotations

import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class StoryMaterialArchitectureTests(unittest.TestCase):
    def read(self, relative: str) -> str:
        path = ROOT / relative
        self.assertTrue(path.is_file(), f"missing architecture file: {relative}")
        return path.read_text(encoding="utf-8")

    def test_story_material_is_an_independent_owner(self) -> None:
        skill = self.read("skills/laohu-story-material/SKILL.md")
        for anchor in (
            "素材箴言",
            "明确保存意图",
            "原话只保存一次",
            "source / atom / usage",
            "渐进检索",
            "允许零采用",
            "外部候选确认门",
        ):
            self.assertIn(anchor, skill)

    def test_story_material_uses_layered_authority_and_dynamic_retrieval_sessions(self) -> None:
        skill = self.read("skills/laohu-story-material/SKILL.md")
        reference = self.read(
            "skills/laohu-story-material/references/01_原子记录与渐进检索合同.md"
        )
        for anchor in (
            "分层权威",
            "SQLite",
            "可重建索引",
            "检索会话",
            "story / sequence / scene / beat / texture",
            "单页只是上下文边界",
            "不设固定的总候选数",
            "get-atom",
            "get-source",
            "不得默认返回 source 原话",
        ):
            self.assertIn(anchor, skill + reference)

    def test_script_writer_splits_long_form_retrieval_by_narrative_scope(self) -> None:
        writer = self.read("skills/laohu-script-writer/SKILL.md")
        for anchor in (
            "story / sequence / scene / beat / texture",
            "长篇",
            "有效状态变化",
            "承重 / 支撑 / 纹理",
            "边际增益",
        ):
            self.assertIn(anchor, writer)

    def test_core_contract_routes_layered_material_handoff(self) -> None:
        contract = self.read("02_共享资产库/05_工具流程/laohu_skills核心合约.md")
        for anchor in (
            "动态分页",
            "按 ID 读取原子详情",
            "原始 source 只在语气、证据、权利或归因需要时显式读取",
        ):
            self.assertIn(anchor, contract)

    def test_router_saves_only_when_the_user_expresses_save_intent(self) -> None:
        router = self.read("skills/laohu-ai-visual/SKILL.md")
        self.assertIn("记录灵感", router)
        self.assertIn("laohu-story-material", router)
        self.assertIn("不擅自长期保存", router)

    def test_script_writer_must_query_but_may_adopt_nothing(self) -> None:
        writer = self.read("skills/laohu-script-writer/SKILL.md")
        for anchor in (
            "素材查询合同",
            "严格匹配",
            "放宽表面条件",
            "跨领域类比",
            "允许零采用",
            "素材调用回执",
            "记忆点账本",
        ):
            self.assertIn(anchor, writer)

    def test_external_candidates_cannot_cross_the_confirmation_gate(self) -> None:
        material = self.read("skills/laohu-story-material/SKILL.md")
        self.assertIn("external_candidate / not_approved", material)
        self.assertIn("未经老胡确认不得进入剧本或长期素材库", material)

    def test_review_returns_material_evidence_to_the_material_owner(self) -> None:
        review = self.read("skills/laohu-generation-review/SKILL.md")
        self.assertIn("素材选择", review)
        self.assertIn("laohu-story-material", review)
        self.assertIn("usage", review)

    def test_private_database_is_ignored_and_untracked(self) -> None:
        ignore = self.read(".gitignore")
        self.assertIn("/00_输入原料/故事素材原子库.jsonl", ignore)
        self.assertIn("/00_输入原料/故事素材库/", ignore)
        tracked = subprocess.run(
            ["git", "ls-files", "--error-unmatch", "00_输入原料/故事素材原子库.jsonl"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertNotEqual(0, tracked.returncode)

    def test_project_documents_register_fourteen_owners(self) -> None:
        for relative in (
            "AGENTS.md",
            "README.md",
            "输入输出索引.md",
            "02_共享资产库/00_核心规则手册.md",
            "02_共享资产库/05_工具流程/laohu_skills核心合约.md",
        ):
            text = self.read(relative)
            self.assertIn("laohu-story-material", text, relative)
            self.assertIn("十四", text, relative)


if __name__ == "__main__":
    unittest.main()
