"""The internal dialogue pilot preserves complete source units and production output."""
import hashlib
import json
from pathlib import Path
import re
import unittest
from scripts.validate_segmentation_migration import read_before

ROOT = Path(__file__).resolve().parents[1]
PILOT = ROOT / 'skills/laohu-script-writer/skills/laohu-dialogue'

class DialoguePilotTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.skill = (PILOT / 'SKILL.md').read_text()
        cls.manifest = json.loads(re.search(r'```json\n(.*?)\n```', (ROOT / '04_诊断与系统日志/对白能力迁移与验证.md').read_text(), re.S)[1])

    def test_complete_original_blocks_are_unique_and_exact(self):
        body = self.skill[self.skill.index('## 一、对白是什么'):]
        migration = json.loads((ROOT / '04_诊断与系统日志/编剧能力完整迁移清单.json').read_text())
        module = next(m for m in migration['modules'] if m['module'] == 'laohu-dialogue')
        for insertion in module.get('scope_insertions', []):
            self.assertEqual(body.count(insertion), 1)
            body = body.replace(insertion, '', 1)
        parts = re.split(r'(?=^## [一二三四五六七八九十]+、)', body, flags=re.M)
        parts = [p for p in parts if p]
        self.assertEqual(len(parts), 10)
        actual = {f'D{i:02d}': hashlib.sha256(value.encode()).hexdigest() for i, value in enumerate(parts, 1)}
        self.assertEqual(actual, {key: value for key, value in self.manifest['blocks'].items() if key != 'D00'})

    def test_creative_entry_excludes_migration_scaffolding(self):
        description = self.skill.split('description:', 1)[1].split('\n---', 1)[0]
        for token in ['sw-dialogue', 'jtydhr88', 'SOURCE-BEGIN', '旧入口', '迁移与验证', '本样板']:
            self.assertNotIn(token, self.skill)
        self.assertNotIn('来源', description)
        for layer in ['灵魂', '筋骨', '血肉', '表皮']:
            self.assertIn('## ' + layer + '：', self.skill)

    def test_full_reference_and_local_material_preserved(self):
        self.assertEqual(hashlib.sha256((PILOT / 'reference.md').read_bytes()).hexdigest(), self.manifest['reference_sha256'])
        local_text = (PILOT / 'references/本地对白与表演补充.md').read_text()
        local = local_text[local_text.index('## 台词口气与方言'):]
        migration = json.loads((ROOT / '04_诊断与系统日志/编剧能力完整迁移清单.json').read_text())
        unit = next(u for u in migration['local_units'] if u['target'].endswith('本地对白与表演补充.md'))
        local = local[:unit['character_count']]
        self.assertEqual(hashlib.sha256(local.encode()).hexdigest(), self.manifest['local_sha256'])

    def test_caller_and_local_links_resolve(self):
        caller = (ROOT / 'skills/laohu-script-writer/SKILL.md').read_text()
        self.assertIn('[laohu-dialogue](skills/laohu-dialogue/SKILL.md)', caller)
        for target in re.findall(r'\]\(([^)]+)\)', self.skill):
            if not target.startswith(('https:', 'http:', '#')):
                self.assertTrue((PILOT / target.split("#", 1)[0]).is_file(), target)
        self.assertIn('EXT-SKILL-002', (ROOT / '02_共享资产库/05_工具流程/外部能力依赖清单.md').read_text())

    def test_formal_output_contract_unchanged(self):
        migration = json.loads((ROOT / '04_诊断与系统日志/编剧能力完整迁移清单.json').read_text())['workflow_refactor']
        text = read_before(migration['output_contract_owner'])
        start = text.index(migration['output_contract_start'])
        block = text[start:start + migration['output_contract_characters']]
        self.assertEqual(hashlib.sha256(block.encode()).hexdigest(), '0323f969c45effb5dcb60c4e3326f0fffc546db2929b46d6247ac20b6adddaa7')

if __name__ == '__main__':
    unittest.main()
