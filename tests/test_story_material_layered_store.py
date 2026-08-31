from __future__ import annotations

import importlib.util
import json
import stat
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "skills/laohu-story-material/scripts/story_material_store.py"
CLI_PATH = ROOT / "skills/laohu-story-material/scripts/story_material_db.py"


def load_store_module():
    if not MODULE_PATH.is_file():
        raise AssertionError(f"missing layered story material store: {MODULE_PATH}")
    spec = importlib.util.spec_from_file_location("story_material_store", MODULE_PATH)
    if spec is None or spec.loader is None:
        raise AssertionError("cannot load layered story material store")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class StoryMaterialLayeredStoreTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tempdir.name) / "故事素材库"

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def source_payload(self, original: str = "只应留在source文件里的独特原话") -> dict:
        return {
            "original": original,
            "source_type": "personal_idea",
            "source_url": "",
            "source_title": "测试来源",
            "fact_status": "fiction",
            "curation_priority": "laohu_selected",
            "privacy": "private",
            "rights_note": "测试",
            "status": "active",
        }

    def atom_payload(self, source_id: str, label: str = "人物用行动代替直接表达") -> dict:
        return {
            "source_id": source_id,
            "atom": label,
            "human_truth": ["人会用自己熟悉的方式表达关心"],
            "mechanisms": ["修好对方每天使用的物件，代替说出关心"],
            "material_types": ["relationship_action"],
            "dramatic_functions": ["character_setup"],
            "memory_carriers": ["被修好的物件"],
            "relationships": ["父子"],
            "emotions": ["克制"],
            "themes": ["家庭"],
            "visible_evidence": ["坏插座被默默换掉"],
            "extensions": ["换成其他每日使用的物件"],
            "boundaries": ["不照搬真实人物身份"],
            "non_replaceable": "原话不照搬",
            "fit": {"formats": ["短片"], "roles": ["texture"]},
            "fact_confidence": "medium",
            "analysis_confidence": "high",
            "status": "callable",
        }

    def make_store(self):
        module = load_store_module()
        return module.StoryMaterialStore(self.root)

    def test_source_atom_and_usage_are_physically_separated(self) -> None:
        store = self.make_store()
        source = store.add_source(self.source_payload())
        atom = store.add_atoms([self.atom_payload(source["id"])])[0]
        usage = store.log_usage({
            "atom_ids": [atom["id"]],
            "event_type": "used",
            "scope": "project",
            "project": "测试作品",
            "script_position": "第一场",
            "usage_role": "texture",
            "transformation": "保留行动替代表达",
            "result": "pending_real_result",
            "evidence_path": "",
        })

        self.assertTrue(store.source_path(source["id"]).is_file())
        self.assertTrue(store.atom_path(atom["id"]).is_file())
        self.assertTrue(store.usage_path(usage["created_at"]).is_file())
        self.assertEqual(
            0o600,
            stat.S_IMODE(store.usage_path(usage["created_at"]).stat().st_mode),
        )
        self.assertNotEqual(
            store.source_path(source["id"]).parent,
            store.atom_path(atom["id"]).parent,
        )
        self.assertNotIn(
            "只应留在source文件里的独特原话".encode("utf-8"),
            store.index_path.read_bytes(),
        )

    def test_get_atom_does_not_load_source_but_get_source_can(self) -> None:
        store = self.make_store()
        source = store.add_source(self.source_payload())
        atom = store.add_atoms([self.atom_payload(source["id"])])[0]

        atom_result = store.get_atoms([atom["id"]])
        source_result = store.get_sources([source["id"]])

        self.assertEqual([atom["id"]], [item["id"] for item in atom_result])
        self.assertNotIn("original", json.dumps(atom_result, ensure_ascii=False))
        self.assertEqual(source["original"], source_result[0]["original"])

    def test_legacy_migration_preserves_ids_original_and_references(self) -> None:
        original = "长原话" * 200
        source = {
            **self.source_payload(original),
            "record_type": "source",
            "id": "SRC-20260830-001",
            "created_at": "2026-08-30T10:00:00+08:00",
        }
        atom = {
            **self.atom_payload(source["id"]),
            "record_type": "atom",
            "id": "ATM-20260830-001",
            "created_at": "2026-08-30T10:01:00+08:00",
        }
        legacy = Path(self.tempdir.name) / "legacy.jsonl"
        legacy.write_text(
            "\n".join(json.dumps(item, ensure_ascii=False) for item in (source, atom)) + "\n",
            encoding="utf-8",
        )
        store = self.make_store()

        report = store.migrate_legacy(legacy)

        self.assertEqual(1, report["source_count"])
        self.assertEqual(1, report["atom_count"])
        self.assertTrue(report["equivalent"])
        self.assertEqual(original, store.get_sources([source["id"]])[0]["original"])
        self.assertEqual(source["id"], store.get_atoms([atom["id"]])[0]["source_id"])
        self.assertEqual({"ok": True, "source_count": 1, "atom_count": 1, "usage_count": 0}, store.validate())

    def test_cli_reads_layered_store_and_keeps_atom_source_interfaces_separate(self) -> None:
        store = self.make_store()
        source = store.add_source(self.source_payload())
        atom = store.add_atoms([self.atom_payload(source["id"])])[0]

        atom_call = subprocess.run(
            ["python3", str(CLI_PATH), "--root", str(self.root), "get-atom", "--id", atom["id"]],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        source_call = subprocess.run(
            ["python3", str(CLI_PATH), "--root", str(self.root), "get-source", "--id", source["id"]],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

        self.assertEqual(0, atom_call.returncode, atom_call.stderr)
        self.assertEqual(0, source_call.returncode, source_call.stderr)
        self.assertNotIn("original", atom_call.stdout)
        self.assertIn("只应留在source文件里的独特原话", source_call.stdout)


if __name__ == "__main__":
    unittest.main()
