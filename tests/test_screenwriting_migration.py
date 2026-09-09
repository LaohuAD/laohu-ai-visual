"""Verify source conservation and executable routes; these checks do not score writing quality."""
import hashlib
import json
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
PARENT = ROOT / 'skills/laohu-script-writer'
MANIFEST = ROOT / '04_诊断与系统日志/编剧能力完整迁移清单.json'

def sha(value):
    return hashlib.sha256(value.encode() if isinstance(value, str) else value).hexdigest()

class ScreenwritingMigrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(MANIFEST.read_text())

    def test_twelve_unique_professionals_are_reachable_from_parent(self):
        actual = {p.parent.name for p in (PARENT / 'skills').glob('*/SKILL.md')}
        expected = {m['module'] for m in self.data['modules']}
        self.assertEqual(len(actual), 12)
        self.assertEqual(actual, expected)
        self.assertNotIn('laohu-workflow', actual)
        parent = (PARENT / 'SKILL.md').read_text()
        for name in actual:
            self.assertIn(f'[{name}](skills/{name}/SKILL.md)', parent)

    def test_complete_methods_and_original_references(self):
        for m in self.data['modules']:
            with self.subTest(module=m['module']):
                dst = ROOT / m['dst']; text = dst.read_text(); heading = m['methods_start_heading']
                body = text[text.index(heading):]
                self.assertEqual(sha(body), m['body_sha256'])
                source = ROOT / m['src']
                if source.exists():
                    self.assertEqual(sha(source.read_bytes()), m['sourcehash'])
                    original = source.read_text(); original = original[original.index(heading):]
                    self.assertEqual(sha(original), m['source_body_sha256'])
                    for edit in m['allowed_edits']:
                        self.assertIn(edit['from'], original)
                        original = original.replace(edit['from'], edit['to'])
                    self.assertEqual(body, original)
                ref = dst.parent / 'reference.md'
                if m['reference_sha256']:
                    self.assertEqual(sha(ref.read_bytes()), m['reference_sha256'])
                else:
                    self.assertFalse(ref.exists(), 'Do not invent an upstream Reference')

    def test_local_methods_have_exact_active_owners(self):
        spans = {}
        for unit in self.data['local_units']:
            target = (ROOT / unit['target']).read_text()
            start = target.index(unit['target_start'])
            chunk = target[start:start + unit['character_count']]
            self.assertEqual(sha(chunk), unit['sha256'])
            spans.setdefault(unit['source'], []).append((unit['source_start_offset'], unit['source_end_offset']))
        for source, coverage in self.data['source_coverage'].items():
            ranges = sorted(spans[source])
            self.assertEqual(ranges[-1][1], coverage['character_count'])
            self.assertEqual(ranges[0][0], coverage['professional_start'])
            for previous, current in zip(ranges, ranges[1:]):
                self.assertEqual(previous[1], current[0], 'No lost or doubly owned method span')

    def test_oral_input_keeps_its_own_methods_without_duplicate_dialogue(self):
        oral = self.data['oral_retained']
        text = (ROOT / oral['target']).read_text()
        body = text[text.index(oral['start']):]
        self.assertEqual(len(body), oral['character_count'])
        self.assertEqual(sha(body), oral['sha256'])
        self.assertNotIn('## 台词口气与方言', text)

    def test_every_internal_link_resolves_and_metadata_stays_out(self):
        for f in (PARENT / 'skills').rglob('*.md'):
            text = f.read_text()
            for target in re.findall(r'\]\(([^)]+)\)', text):
                if target.startswith(('http:', 'https:', '#', 'mailto:')):
                    continue
                self.assertTrue((f.parent / target.split('#', 1)[0]).is_file(), f'{f}: {target}')
            if f.name != 'SKILL.md':
                continue
            description = text.split('description:', 1)[1].split('\n---', 1)[0]
            self.assertLessEqual(len(description.strip()), 1024)
            for token in ['SOURCE-BEGIN', 'SOURCE-END', '旧入口', '本样板', 'jtydhr88', '迁移与验证']:
                self.assertNotIn(token, text)
            self.assertNotIn('来源', description)
            self.assertNotRegex(text, r'`sw-[a-z-]+`')
            for layer in ['灵魂', '筋骨', '血肉', '表皮']:
                self.assertRegex(text, r'(?m)^## '+layer+'：.+$')

    def test_formal_production_contract_is_unchanged(self):
        contract = self.data['workflow_refactor']
        text = (ROOT / contract['output_contract_owner']).read_text()
        start = text.index(contract['output_contract_start'])
        block = text[start:start + contract['output_contract_characters']]
        self.assertEqual(sha(block), self.data['formal_output_sha256'])

    def test_router_delegates_methods_and_preserves_moved_units(self):
        from scripts.validate_capability_architecture import reachable_documents
        reachable = reachable_documents(PARENT / 'SKILL.md')
        parent = (PARENT / 'SKILL.md').read_text()
        for heading in ['### 人物选择', '### 教学喜剧的对白场景合同', '### 文戏与武戏', '### 语言与材料', '### 相邻单元', '### 输出合同']:
            self.assertNotIn(heading, parent)
        data = self.data['workflow_refactor']
        units = [u for section in data['sections'] for u in section['units']] + data['additional_units']
        for unit in units:
            target = ROOT / unit['target']
            self.assertIn(target.resolve(), reachable, str(target))
            self.assertEqual(sha(unit['text']), unit['text_sha256'])
            self.assertIn(unit['text'], target.read_text())

    def test_active_routes_do_not_return_to_retired_mixed_sources(self):
        files = [PARENT / 'SKILL.md', PARENT / 'references/05_剧本语言诊断与反向审稿.md']
        files.extend((PARENT / 'skills').rglob('*.md'))
        for source in self.data['retired_sources']:
            self.assertFalse((ROOT / source).exists(), 'Retired duplicate must not remain in runtime tree')
            old_name = Path(source).name
            for file in files:
                self.assertNotIn(old_name, file.read_text(), str(file))

if __name__ == '__main__':
    unittest.main()
