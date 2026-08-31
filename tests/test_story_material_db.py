from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "skills/laohu-story-material/scripts/story_material_store.py"


def load_store_module():
    spec = importlib.util.spec_from_file_location("story_material_store_regression", MODULE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load story material store module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class StoryMaterialDatabaseRegressionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        module = load_store_module()
        self.ValidationError = module.ValidationError
        self.store = module.StoryMaterialStore(Path(self.tempdir.name) / "materials")

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    @staticmethod
    def source_payload(original: str = "父亲没说关心，只把坏掉的插座换了。") -> dict:
        return {
            "original": original,
            "source_type": "life_observation",
            "source_url": "",
            "source_title": "",
            "fact_status": "personal_observation",
            "curation_priority": "laohu_selected",
            "privacy": "private",
            "rights_note": "",
            "status": "active",
        }

    @staticmethod
    def atom_payload(source_id: str, mechanism: str = "用解决实际问题代替直接表达关心") -> dict:
        return {
            "source_id": source_id,
            "atom": f"人物通过行动表达：{mechanism}",
            "human_truth": ["嘴硬心软"],
            "mechanisms": [mechanism],
            "material_types": ["relationship_detail", "character_action"],
            "dramatic_functions": ["character_setup"],
            "memory_carriers": ["action", "object"],
            "relationships": ["父子"],
            "emotions": ["克制", "温暖"],
            "themes": ["家庭"],
            "visible_evidence": ["换掉坏插座"],
            "extensions": ["改为修好对方每天使用却没开口请求的物件"],
            "non_replaceable": "没有说关心，先修好了插座",
            "boundaries": ["不照搬真实人物身份"],
            "fit": {"formats": ["短片"], "tones": ["现实"], "roles": ["texture"]},
            "fact_confidence": "medium",
            "analysis_confidence": "high",
            "status": "callable",
        }

    @staticmethod
    def query(**overrides) -> dict:
        query = {
            "scope": {"work": "测试作品", "level": "scene", "id": "SC-01"},
            "gap": "人物怎样用行动表达关心",
            "responsibilities": ["人物行为"],
            "must": {},
            "prefer": {},
            "exclude_ids": [],
            "page_budget_chars": 20000,
            "diversity": "open",
            "expand_source_ids": [],
        }
        query.update(overrides)
        return query

    def usage_payload(self, atom_id: str, scope: str, event_type: str) -> dict:
        return {
            "atom_ids": [atom_id],
            "project": "测试作品",
            "script_position": "第二场",
            "usage_role": "texture",
            "transformation": "未采用",
            "result": "not_fit",
            "evidence_path": "",
            "scope": scope,
            "event_type": event_type,
        }

    def test_source_is_saved_once_and_long_original_is_not_truncated(self) -> None:
        original = "原话" * 5000
        source = self.store.add_source(self.source_payload(original))
        atoms = self.store.add_atoms([
            self.atom_payload(source["id"]),
            self.atom_payload(source["id"], "用劳动掩饰歉意"),
        ])

        self.assertEqual(original, self.store.get_sources([source["id"]])[0]["original"])
        self.assertEqual({source["id"]}, {atom["source_id"] for atom in atoms})
        self.assertEqual(1, len(self.store.load_sources()))

    def test_search_returns_compact_index_without_original_or_detail(self) -> None:
        source = self.store.add_source(self.source_payload("不能出现在索引里的完整原话"))
        atom = self.store.add_atoms([self.atom_payload(source["id"])])[0]
        result = self.store.start_search(self.query(
            prefer={"mechanisms": ["用解决实际问题代替直接表达关心"]}
        ))
        encoded = json.dumps(result, ensure_ascii=False)

        self.assertIn(atom["id"], encoded)
        self.assertNotIn("original", encoded)
        self.assertNotIn("不能出现在索引里的完整原话", encoded)
        self.assertNotIn("visible_evidence", encoded)
        self.assertNotIn("不能出现在索引里的完整原话".encode(), self.store.index_path.read_bytes())

    def test_atom_source_and_usage_require_separate_calls(self) -> None:
        first = self.store.add_source(self.source_payload("第一条原话"))
        second = self.store.add_source(self.source_payload("第二条原话"))
        first_atom = self.store.add_atoms([self.atom_payload(first["id"])])[0]
        second_atom = self.store.add_atoms([self.atom_payload(second["id"], "用玩笑化解羞耻")])[0]
        self.store.log_usage(self.usage_payload(first_atom["id"], "project", "shortlisted"))

        atom_text = json.dumps(self.store.get_atoms([first_atom["id"]]), ensure_ascii=False)
        source_text = json.dumps(self.store.get_sources([first["id"]]), ensure_ascii=False)
        usage_text = json.dumps(self.store.get_usage([first_atom["id"]]), ensure_ascii=False)
        self.assertNotIn("第一条原话", atom_text)
        self.assertIn("第一条原话", source_text)
        self.assertIn("shortlisted", usage_text)
        self.assertNotIn(second_atom["id"], atom_text + source_text + usage_text)

    def test_project_rejection_does_not_pause_library_but_library_event_does(self) -> None:
        source = self.store.add_source(self.source_payload())
        atom = self.store.add_atoms([self.atom_payload(source["id"])])[0]
        self.store.log_usage(self.usage_payload(atom["id"], "project", "rejected"))
        self.assertTrue(self.store.start_search(self.query())["cards"])

        self.store.log_usage(self.usage_payload(atom["id"], "library", "paused"))
        self.assertEqual([], self.store.start_search(self.query())["cards"])

        self.store.log_usage(self.usage_payload(atom["id"], "library", "reopened"))
        self.assertTrue(self.store.start_search(self.query())["cards"])

    def test_invalid_foreign_key_and_unapproved_external_leave_authority_unchanged(self) -> None:
        source = self.store.add_source(self.source_payload())
        before = {path: path.read_bytes() for path in self.store.root.rglob("*") if path.is_file()}
        with self.assertRaises(self.ValidationError):
            self.store.add_atoms([self.atom_payload("SRC-20990101-999")])
        invalid_source = self.source_payload("网络候选")
        invalid_source["curation_priority"] = "ai_external_candidate"
        with self.assertRaises(self.ValidationError):
            self.store.add_source(invalid_source)
        after = {path: path.read_bytes() for path in self.store.root.rglob("*") if path.is_file()}

        self.assertEqual(before, after)
        self.assertEqual(source["id"], self.store.load_sources()[0]["id"])

    def test_balanced_first_view_can_expand_to_all_atoms_from_one_source(self) -> None:
        first = self.store.add_source(self.source_payload("同源案例"))
        second = self.store.add_source(self.source_payload("另一案例"))
        self.store.add_atoms([self.atom_payload(first["id"], f"同源机制{i}") for i in range(4)])
        self.store.add_atoms([self.atom_payload(second["id"], "另一机制")])

        balanced = self.store.start_search(self.query(diversity="balanced"))["cards"]
        expanded = self.store.start_search(self.query(
            diversity="open", expand_source_ids=[first["id"]]
        ))["cards"]

        self.assertNotEqual(balanced[0]["source_id"], balanced[1]["source_id"])
        self.assertEqual(4, sum(card["source_id"] == first["id"] for card in expanded))


if __name__ == "__main__":
    unittest.main()
