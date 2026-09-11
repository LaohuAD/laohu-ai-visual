"""Check repository discovery links without duplicating or flattening skill sources."""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

class SkillDiscoveryTests(unittest.TestCase):
    def test_entry_links_exactly_match_registry(self):
        nodes = json.loads((ROOT/'02_共享资产库/05_工具流程/能力注册表.json').read_text())['skills']
        entries = {n['name']: n for n in nodes if n['parent'] is None}
        links = {p.name:p for p in (ROOT/'.agents/skills').iterdir()}
        self.assertEqual(set(links), set(entries))
        for name, link in links.items():
            self.assertTrue(link.is_symlink(), name)
            self.assertEqual(link.readlink(), Path('../../skills')/name)
            self.assertEqual((link/'SKILL.md').resolve(), (ROOT/entries[name]['path']).resolve())

    def test_nested_specialists_remain_under_their_parent(self):
        nodes = json.loads((ROOT/'02_共享资产库/05_工具流程/能力注册表.json').read_text())['skills']
        for node in nodes:
            if node['parent']:
                self.assertFalse((ROOT/'.agents/skills'/node['name']).exists())
                self.assertTrue((ROOT/node['path']).is_file())
