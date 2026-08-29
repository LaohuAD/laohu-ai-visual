from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills/laohu-story-material/scripts/story_material_db.py"


def load_store():
    spec = importlib.util.spec_from_file_location("story_material_db", SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load story material database module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class StoryMaterialDatabaseTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.db = Path(self.tempdir.name) / "materials.jsonl"

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def source_payload(self, original: str = "父亲没说关心，只把坏掉的插座换了。") -> dict:
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

    def atom_payload(self, source_id: str, mechanism: str = "用解决实际问题代替直接表达关心") -> dict:
        return {
            "source_id": source_id,
            "atom": "人物用修理物件代替说出关心",
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

    def test_source_is_saved_once_and_long_original_is_not_truncated(self) -> None:
        store = load_store()
        original = "原话" * 5000
        source = store.add_source(self.db, self.source_payload(original))
        atoms = store.add_atoms(
            self.db,
            [self.atom_payload(source["id"]), self.atom_payload(source["id"], "用劳动掩饰歉意")],
        )
        records = store.load_records(self.db)
        sources = [record for record in records if record["record_type"] == "source"]
        self.assertEqual(1, len(sources))
        self.assertEqual(original, sources[0]["original"])
        self.assertEqual({source["id"]}, {atom["source_id"] for atom in atoms})

    def test_search_returns_compact_index_without_original(self) -> None:
        store = load_store()
        source = store.add_source(self.db, self.source_payload("不能出现在索引里的完整原话"))
        atom = store.add_atoms(self.db, [self.atom_payload(source["id"])])[0]
        result = store.search_records(
            self.db,
            {"prefer": {"mechanisms": ["用解决实际问题代替直接表达关心"]}, "limit": 10},
        )
        encoded = json.dumps(result, ensure_ascii=False)
        self.assertIn(atom["id"], encoded)
        self.assertNotIn("original", encoded)
        self.assertNotIn("不能出现在索引里的完整原话", encoded)
        self.assertNotIn("visible_evidence", encoded)
        overview = json.dumps(store.stats(self.db), ensure_ascii=False)
        self.assertNotIn("不能出现在索引里的完整原话", overview)
        self.assertIn(atom["id"], overview)

    def test_get_loads_only_requested_atom_source_and_usage(self) -> None:
        store = load_store()
        first = store.add_source(self.db, self.source_payload("第一条原话"))
        second = store.add_source(self.db, self.source_payload("第二条原话"))
        first_atom = store.add_atoms(self.db, [self.atom_payload(first["id"])])[0]
        second_atom = store.add_atoms(self.db, [self.atom_payload(second["id"], "用玩笑化解羞耻")])[0]
        store.log_usage(
            self.db,
            {
                "atom_ids": [first_atom["id"]],
                "event_type": "shortlisted",
                "scope": "project",
                "project": "测试作品",
                "script_position": "第一场",
                "usage_role": "texture",
                "transformation": "保留行动替代表达",
                "result": "pending",
                "evidence_path": "",
            },
        )
        detail = store.get_records(self.db, [first_atom["id"]])
        encoded = json.dumps(detail, ensure_ascii=False)
        self.assertIn("第一条原话", encoded)
        self.assertIn("shortlisted", encoded)
        self.assertNotIn(second_atom["id"], encoded)
        self.assertNotIn("第二条原话", encoded)

    def test_project_rejection_does_not_pause_library_but_library_event_does(self) -> None:
        store = load_store()
        source = store.add_source(self.db, self.source_payload())
        atom = store.add_atoms(self.db, [self.atom_payload(source["id"])])[0]
        common = {
            "atom_ids": [atom["id"]],
            "project": "测试作品",
            "script_position": "第二场",
            "usage_role": "texture",
            "transformation": "未采用",
            "result": "not_fit",
            "evidence_path": "",
        }
        store.log_usage(self.db, {**common, "scope": "project", "event_type": "rejected"})
        self.assertEqual("callable", store.search_records(self.db, {"limit": 10})[0]["effective_status"])
        store.log_usage(self.db, {**common, "scope": "library", "event_type": "paused"})
        self.assertEqual([], store.search_records(self.db, {"limit": 10}))
        store.log_usage(self.db, {**common, "scope": "library", "event_type": "reopened"})
        self.assertEqual("callable", store.search_records(self.db, {"limit": 10})[0]["effective_status"])

    def test_invalid_foreign_key_and_unapproved_external_leave_database_unchanged(self) -> None:
        store = load_store()
        source = store.add_source(self.db, self.source_payload())
        before = self.db.read_bytes()
        invalid_atom = self.atom_payload("SRC-20990101-999")
        with self.assertRaises(store.ValidationError):
            store.add_atoms(self.db, [invalid_atom])
        self.assertEqual(before, self.db.read_bytes())
        invalid_source = self.source_payload("网络候选")
        invalid_source["curation_priority"] = "ai_external_candidate"
        with self.assertRaises(store.ValidationError):
            store.add_source(self.db, invalid_source)
        self.assertEqual(before, self.db.read_bytes())
        self.assertEqual(source["id"], store.load_records(self.db)[0]["id"])

    def test_same_source_cannot_fill_the_whole_candidate_set(self) -> None:
        store = load_store()
        first = store.add_source(self.db, self.source_payload("同源案例"))
        second = store.add_source(self.db, self.source_payload("另一案例"))
        store.add_atoms(
            self.db,
            [self.atom_payload(first["id"], f"同源机制{i}") for i in range(4)],
        )
        store.add_atoms(self.db, [self.atom_payload(second["id"], "另一机制")])
        result = store.search_records(self.db, {"limit": 5, "per_source_limit": 2})
        self.assertLessEqual(2, sum(item["source_id"] == first["id"] for item in result))
        self.assertTrue(any(item["source_id"] == second["id"] for item in result))


if __name__ == "__main__":
    unittest.main()
