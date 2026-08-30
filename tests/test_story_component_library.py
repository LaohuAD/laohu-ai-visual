from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills/laohu-script-writer/scripts/story_component_library.py"
DEFAULT_LIBRARY = ROOT / "skills/laohu-script-writer/references/07_故事构件库.jsonl"


def load_component_module():
    if not SCRIPT.is_file():
        raise AssertionError(f"missing component library script: {SCRIPT}")
    spec = importlib.util.spec_from_file_location("story_component_library", SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load story component library module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class StoryComponentLibraryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.module = None

    def store(self):
        if self.module is None:
            self.module = load_component_module()
        return self.module

    def test_default_library_validates(self) -> None:
        store = self.store()
        records = store.load_records(DEFAULT_LIBRARY)
        store.validate_records(records)
        self.assertGreater(len(records), 12)

    def test_seed_library_is_not_a_twelve_archetype_menu(self) -> None:
        records = self.store().load_records(DEFAULT_LIBRARY)
        self.assertGreater(len(records), 12)
        self.assertTrue(all(record["record_type"] == "component" for record in records))
        self.assertTrue(all("archetype" not in record for record in records))
        self.assertTrue(all(record["state_change"]["before"] for record in records))
        self.assertTrue(all(record["state_change"]["after"] for record in records))

    def test_stats_reports_category_and_status_without_details(self) -> None:
        store = self.store()
        result = store.stats(store.load_records(DEFAULT_LIBRARY))
        encoded = json.dumps(result, ensure_ascii=False)
        self.assertIn("categories", result)
        self.assertIn("statuses", result)
        self.assertNotIn("visible_evidence", encoded)
        self.assertNotIn("audience_shift", encoded)
        self.assertNotIn("source_refs", encoded)

    def test_search_returns_compact_records_and_respects_must_filters(self) -> None:
        store = self.store()
        records = store.load_records(DEFAULT_LIBRARY)
        result = store.search(
            records,
            {
                "must": {"category": ["信息"]},
                "prefer": {"dramatic_functions": ["回收"]},
                "limit": 20,
            },
        )
        self.assertTrue(result)
        self.assertTrue(all(item["category"] == "信息" for item in result))
        encoded = json.dumps(result, ensure_ascii=False)
        self.assertNotIn("visible_evidence", encoded)
        self.assertNotIn("audience_shift", encoded)
        self.assertNotIn("source_refs", encoded)

    def test_search_prioritizes_function_over_genre_shell(self) -> None:
        store = self.store()
        records = store.load_records(DEFAULT_LIBRARY)
        result = store.search(
            records,
            {
                "prefer": {
                    "dramatic_functions": ["冲突升级"],
                    "compatible_tags": ["选择收窄"],
                },
                "limit": 8,
            },
        )
        self.assertTrue(result)
        self.assertIn("冲突升级", result[0]["dramatic_functions"])
        self.assertNotIn("genres", json.dumps(result, ensure_ascii=False))

    def test_get_returns_full_component_by_id(self) -> None:
        store = self.store()
        records = store.load_records(DEFAULT_LIBRARY)
        component_id = records[0]["id"]
        detail = store.get_records(records, [component_id])
        self.assertEqual([component_id], [record["id"] for record in detail])
        self.assertIn("visible_evidence", detail[0])
        self.assertIn("audience_shift", detail[0])
        self.assertIn("boundaries", detail[0])

    def test_duplicate_ids_and_private_source_fields_are_rejected(self) -> None:
        store = self.store()
        records = store.load_records(DEFAULT_LIBRARY)
        duplicate = [records[0], dict(records[0])]
        with self.assertRaises(store.ValidationError):
            store.validate_records(duplicate)

        private_record = dict(records[0])
        private_record["original"] = "私人原话不得进入构件库"
        with self.assertRaises(store.ValidationError):
            store.validate_records([private_record])

    def test_paused_components_are_not_callable_by_default(self) -> None:
        store = self.store()
        records = store.load_records(DEFAULT_LIBRARY)
        paused = dict(records[0])
        paused["id"] = "CMP-999"
        paused["status"] = "paused"
        candidates = [*records, paused]
        result = store.search(candidates, {"limit": 200})
        self.assertNotIn("CMP-999", {item["id"] for item in result})
        result_with_paused = store.search(
            candidates,
            {"include_paused": True, "limit": 200},
        )
        self.assertIn("CMP-999", {item["id"] for item in result_with_paused})

    def test_invalid_jsonl_is_rejected_without_rewriting_source(self) -> None:
        store = self.store()
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "invalid.jsonl"
            path.write_text('{"record_type":"component"}\nnot-json\n', encoding="utf-8")
            before = path.read_bytes()
            with self.assertRaises(store.ValidationError):
                store.load_records(path)
            self.assertEqual(before, path.read_bytes())


if __name__ == "__main__":
    unittest.main()
