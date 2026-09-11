"""Regression of registry, source conservation and protected ownership boundaries.
These tests do not claim real image/video quality or host-native skill discovery.
"""
from pathlib import Path
import json
import subprocess
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from validate_visual_restructure import check
from scripts.validate_segmentation_migration import read_before

class VisualRestructureTests(unittest.TestCase):
    def test_registered_files_layers_references_and_links(self):
        self.assertEqual(check(require_manifest=False),[])

    def test_all_baseline_units_preserved_and_current_targets_match(self):
        self.assertEqual(check(),[])

    def test_prior_screenwriting_baseline_is_preserved_before_authorized_segmentation(self):
        m=json.loads((ROOT/'04_诊断与系统日志/视觉能力重构迁移清单.json').read_text())
        for entry in m['baseline_files']:
            if entry['path'].startswith('skills/laohu-script-writer/'):
                original=subprocess.check_output(['git','show',m['baseline_ref']+':'+entry['path']],cwd=ROOT)
                self.assertEqual(read_before(entry['path']).encode(),original,entry['path'])

    def test_each_specialist_has_a_real_parent_route(self):
        nodes=json.loads((ROOT/'02_共享资产库/05_工具流程/能力注册表.json').read_text())['skills']
        by={n['name']:n for n in nodes}
        for node in nodes:
            if node['parent']:
                parent=(ROOT/by[node['parent']]['path']).read_text()
                self.assertIn('skills/'+node['name']+'/SKILL.md',parent,node['name'])

    def test_asset_parent_does_not_own_fixed_body_board_tutorial(self):
        parent=(ROOT/'skills/laohu-visual-assets/SKILL.md').read_text()
        self.assertNotIn('左栏约占画面宽度36%',parent)
        specialist=(ROOT/'skills/laohu-visual-assets/skills/laohu-body-assets/references/资产规格与编译.md').read_text()
        self.assertIn('左栏约占画面宽度36%',specialist)
        self.assertIn('中栏约占45%',specialist)
        self.assertIn('右栏约占19%',specialist)

    def test_retired_source_references_are_not_empty_redirects(self):
        m=json.loads((ROOT/'04_诊断与系统日志/视觉能力重构迁移清单.json').read_text())
        for source in m.get('retired_reference_paths',[]):
            self.assertFalse((ROOT/source).exists(),source)

    def test_native_discovery_is_not_assumed_by_registry(self):
        text=(ROOT/'02_共享资产库/05_工具流程/laohu_skills核心合约.md').read_text()
        self.assertIn('原生发现范围取决于具体运行时安装与扫描',text)
        self.assertIn('不声称所有子Skill已被宿主原生发现',text)

if __name__=='__main__': unittest.main()
