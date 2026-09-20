"""Discover the five real packages and preserve registered nested specialists."""
import json
import unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
class SkillDiscoveryTests(unittest.TestCase):
    def test_entries_exactly_match_registry(self):
        nodes=json.loads((ROOT/'.agents/skills/laohu-ai-visual/references/能力注册表.json').read_text())['skills']
        entries={n['name']:n for n in nodes if n['parent'] is None}
        actual={p.name:p for p in (ROOT/'.agents/skills').iterdir() if p.is_dir() and (p/'SKILL.md').is_file()}
        self.assertEqual(set(actual),set(entries))
        self.assertEqual(len(entries),5)
        self.assertFalse((ROOT/'skills').exists())
        for name,path in actual.items():
            self.assertFalse(path.is_symlink())
            self.assertEqual(path/'SKILL.md',ROOT/entries[name]['path'])
    def test_nested_specialists_remain_under_their_parent(self):
        nodes=json.loads((ROOT/'.agents/skills/laohu-ai-visual/references/能力注册表.json').read_text())['skills']
        by={n['name']:n for n in nodes}
        for node in nodes:
            self.assertTrue((ROOT/node['path']).is_file())
            if node['parent']:
                self.assertTrue((ROOT/node['path']).is_relative_to((ROOT/by[node['parent']]['path']).parent/'skills'))
