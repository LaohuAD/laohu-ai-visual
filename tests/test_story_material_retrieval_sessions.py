from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "skills/laohu-story-material/scripts/story_material_store.py"


def load_store_module():
    spec = importlib.util.spec_from_file_location("story_material_store", MODULE_PATH)
    if spec is None or spec.loader is None:
        raise AssertionError("cannot load layered story material store")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class StoryMaterialRetrievalSessionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        module = load_store_module()
        self.ValidationError = module.ValidationError
        self.store = module.StoryMaterialStore(Path(self.tempdir.name) / "materials")
        first = self.store.add_source(self.source_payload("父亲的行动"))
        second = self.store.add_source(self.source_payload("母亲的行动"))
        self.first_source_id = first["id"]
        self.second_source_id = second["id"]
        self.store.add_atoms([
            self.atom_payload(first["id"], index, "父子") for index in range(4)
        ])
        self.store.add_atoms([
            self.atom_payload(second["id"], index + 4, "母子") for index in range(3)
        ])
        self.assertTrue(
            hasattr(self.store, "start_search"),
            "dynamic retrieval session API is not implemented",
        )

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    @staticmethod
    def source_payload(title: str) -> dict:
        return {
            "original": title,
            "source_type": "life_observation",
            "source_url": "",
            "source_title": title,
            "fact_status": "personal_observation",
            "curation_priority": "laohu_selected",
            "privacy": "private",
            "rights_note": "",
            "status": "active",
        }

    @staticmethod
    def atom_payload(source_id: str, index: int, relationship: str) -> dict:
        return {
            "source_id": source_id,
            "atom": f"人物用第{index}种可见行动表达关心",
            "human_truth": ["人会用熟悉动作代替直接表达"],
            "mechanisms": [f"第{index}种机制：通过改变物件状态改变关系"],
            "material_types": ["relationship_action"],
            "dramatic_functions": ["character_setup", "relationship_shift"],
            "memory_carriers": [f"第{index}个物件"],
            "relationships": [relationship],
            "emotions": ["克制"],
            "themes": ["家庭"],
            "visible_evidence": [f"第{index}个物件被修好"],
            "extensions": ["迁移到其他关系"],
            "boundaries": ["不照搬身份"],
            "non_replaceable": "",
            "fit": {"formats": ["短片", "长片"]},
            "fact_confidence": "medium",
            "analysis_confidence": "high",
            "status": "callable",
        }

    @staticmethod
    def query(
        *,
        level: str = "scene",
        scope_id: str = "SC-01",
        page_budget_chars: int = 800,
        diversity: str = "open",
        expand_source_ids: list[str] | None = None,
    ) -> dict:
        return {
            "scope": {
                "work": "测试长片",
                "level": level,
                "id": scope_id,
            },
            "gap": "人物怎样用行动证明关心",
            "responsibilities": ["人物行为", "关系变化"],
            "must": {},
            "prefer": {"dramatic_functions": ["relationship_shift"]},
            "exclude_ids": [],
            "page_budget_chars": page_budget_chars,
            "diversity": diversity,
            "expand_source_ids": expand_source_ids or [],
        }

    def test_page_is_packed_by_character_budget_and_cursor_can_continue(self) -> None:
        first = self.store.start_search(self.query(page_budget_chars=800))
        second = self.store.continue_search({
            "session_id": first["session_id"],
            "shortlist_ids": [first["cards"][0]["id"]],
            "rejected_summaries": [],
            "covered_directions": ["行动代替表达"],
            "remaining_gaps": ["需要不同的关系后果"],
        })

        first_ids = {card["id"] for card in first["cards"]}
        second_ids = {card["id"] for card in second["cards"]}
        self.assertTrue(first["cards"])
        self.assertTrue(first["has_more"])
        self.assertTrue(first_ids.isdisjoint(second_ids))
        self.assertGreater(second["next_cursor"], first["next_cursor"])
        self.assertLessEqual(first["page_char_count"], 800)
        self.assertEqual([first["cards"][0]["id"]], second["session_summary"]["shortlist_ids"])
        self.assertNotIn("父亲的行动", str(first["cards"]))

    def test_long_form_scopes_keep_independent_retrieval_state(self) -> None:
        story = self.store.start_search(self.query(level="story", scope_id="STORY"))
        sequence = self.store.start_search(self.query(level="sequence", scope_id="SEQ-02"))
        scene = self.store.start_search(self.query(level="scene", scope_id="SC-12"))

        self.assertEqual(3, len({story["session_id"], sequence["session_id"], scene["session_id"]}))
        self.assertEqual("story", self.store.get_session(story["session_id"])["scope"]["level"])
        self.assertEqual("sequence", self.store.get_session(sequence["session_id"])["scope"]["level"])
        self.assertEqual("scene", self.store.get_session(scene["session_id"])["scope"]["level"])

    def test_pagination_eventually_returns_every_matching_atom_once(self) -> None:
        page = self.store.start_search(self.query(page_budget_chars=650))
        returned = [card["id"] for card in page["cards"]]
        while page["has_more"]:
            page = self.store.continue_search({"session_id": page["session_id"]})
            returned.extend(card["id"] for card in page["cards"])

        self.assertEqual(7, len(returned))
        self.assertEqual(7, len(set(returned)))
        self.assertEqual(
            {atom["id"] for atom in self.store.load_atoms()},
            set(returned),
        )

    def test_balanced_is_a_first_view_and_open_can_expand_all_same_source_atoms(self) -> None:
        balanced = self.store.start_search(self.query(
            page_budget_chars=20000,
            diversity="balanced",
        ))
        open_result = self.store.start_search(self.query(
            page_budget_chars=20000,
            diversity="open",
            expand_source_ids=[self.first_source_id],
        ))

        self.assertNotEqual(
            balanced["cards"][0]["source_id"],
            balanced["cards"][1]["source_id"],
        )
        first_source_cards = [
            card for card in open_result["cards"]
            if card["source_id"] == self.first_source_id
        ]
        self.assertEqual(4, len(first_source_cards))
        self.assertFalse(open_result["has_more"])

    def test_get_atom_source_and_usage_are_separate_interfaces(self) -> None:
        atom_id = self.store.load_atoms()[0]["id"]
        source_id = self.store.load_atoms()[0]["source_id"]

        atom_result = self.store.get_atoms([atom_id])
        source_result = self.store.get_sources([source_id])
        usage_result = self.store.get_usage([atom_id])

        self.assertIn("source_id", atom_result[0])
        self.assertNotIn("original", atom_result[0])
        self.assertIn("original", source_result[0])
        self.assertEqual([], usage_result)

    def test_facet_overview_can_page_through_the_long_tail_without_top_n_cap(self) -> None:
        self.assertTrue(
            hasattr(self.store, "list_facet"),
            "facet long-tail pagination is not implemented",
        )
        page = self.store.list_facet("mechanisms", page_budget_chars=180)
        values = [item["value"] for item in page["items"]]
        while page["has_more"]:
            page = self.store.list_facet(
                "mechanisms",
                cursor=page["next_cursor"],
                page_budget_chars=180,
            )
            values.extend(item["value"] for item in page["items"])

        expected = {atom["mechanisms"][0] for atom in self.store.load_atoms()}
        self.assertEqual(expected, set(values))
        self.assertEqual(len(values), len(set(values)))

    def test_invalid_scope_and_budget_do_not_create_a_session(self) -> None:
        with self.assertRaises(self.ValidationError):
            self.store.start_search(self.query(level="movie"))
        with self.assertRaises(self.ValidationError):
            self.store.start_search(self.query(page_budget_chars=0))
        self.assertEqual([], list((self.store.root / "sessions").glob("*/*/*.json")))

    def test_closed_session_cannot_continue(self) -> None:
        page = self.store.start_search(self.query(page_budget_chars=650))
        self.store.close_session(page["session_id"])
        with self.assertRaises(self.ValidationError):
            self.store.continue_search({"session_id": page["session_id"]})

    def test_one_oversized_card_is_returned_instead_of_deadlocking_cursor(self) -> None:
        page = self.store.start_search(self.query(page_budget_chars=1))
        self.assertEqual(1, len(page["cards"]))
        self.assertGreater(page["page_char_count"], 1)
        self.assertGreater(page["next_cursor"], 0)


if __name__ == "__main__":
    unittest.main()
