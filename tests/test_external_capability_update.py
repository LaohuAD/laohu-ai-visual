"""Check pinned upstream fidelity, preserved local material and executable discovery links.
These checks do not establish animation generation quality or writing quality.
"""
import hashlib
import json
from pathlib import Path
import re
import unittest
from scripts.package_history import read_pre_package, physical_path

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'04_诊断与系统日志/外部能力同步清单.json'

def sha(value):
    return hashlib.sha256(value if isinstance(value,bytes) else value.encode()).hexdigest()

def mapped(text, aliases):
    for old,new in sorted(aliases.items(),key=lambda p:-len(p[0])):
        text=re.sub(r'(?<![\w-])'+re.escape(old)+r'(?![\w-])',new,text)
    return text

class ExternalCapabilityUpdateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.data=json.loads(DATA.read_text())

    def test_complete_current_upstream_body_and_references(self):
        self.assertEqual(len(self.data['screenwriting']),20)
        for item in self.data['screenwriting']:
            with self.subTest(module=item['module']):
                text=read_pre_package(item['target'],ROOT)[1]
                prefix,body=text.split('<!-- upstream-body:start -->\n',1)
                self.assertEqual(sha(prefix),item['prefix_sha256'])
                self.assertEqual(sha(body),item['mapped_body_sha256'])
                src=ROOT/item['source']
                if src.exists():
                    raw=src.read_text();self.assertEqual(sha(raw),item['source_sha256'])
                    original=raw.split('---',2)[2].lstrip('\n')
                    self.assertEqual(sha(original),item['source_body_sha256'])
                    expected=mapped(original,self.data['aliases'])
                    if item['source_name']=='sw-workflow':
                        expected=expected.replace('](reference.md)','](外部编剧工作流案例.md)')
                    self.assertEqual(body,expected)
                for ref in item['references']:
                    current=read_pre_package(ref['target'],ROOT)[1]
                    self.assertEqual(sha(current),ref['mapped_sha256'])
                    original=ROOT/ref['source']
                    if original.exists():
                        self.assertEqual(sha(original.read_bytes()),ref['source_sha256'])
                        self.assertEqual(current,mapped(original.read_text(),self.data['aliases']))

    def test_complete_stickman_and_portrait_methods(self):
        for item in self.data['source_copies']:
            text=read_pre_package(item['target'],ROOT)[1].encode()
            if item['preservation']=='original-after-attribution':text=text.decode().split('\n\n',1)[1].encode()
            self.assertEqual(sha(text),item['sha256'],item['target'])

    def test_current_registry_and_native_entry_links(self):
        d=json.loads((ROOT/'.agents/skills/laohu-ai-visual/references/能力注册表.json').read_text())
        self.assertEqual(d['entry_count'],6)
        self.assertEqual(d['specialist_count'],117)
        by={n['name']:n for n in d['skills']}
        for name in self.data['new_modules']+['laohu-stickman-explainer','laohu-editorial-explainer']:
            node=by[name];parent=ROOT/by[node['parent']]['path']
            self.assertIn('skills/'+name+'/SKILL.md',parent.read_text())
            entry='laohu-script-writer' if name in self.data['new_modules'] else 'laohu-video-prompt'
            relative=Path(node['path']).relative_to('.agents/skills/'+entry)
            self.assertTrue((ROOT/'.agents/skills'/entry/relative).is_file())

    def test_authorized_changes_are_reversible_for_historical_audits(self):
        for item in self.data['evolution_files']:
            after=read_pre_package(item['path'],ROOT)[1]
            self.assertEqual(sha(after),item['after_sha256'],item['path'])
            for edit in reversed(item['edits']):
                after=after[:edit['after_start']]+edit['before_text']+after[edit['after_end']:]
            self.assertEqual(sha(after),item['before_sha256'],item['path'])

    def test_five_foundation_routes_are_explicit_and_specialists_are_conditional(self):
        doc=ROOT/'.agents/skills/laohu-video-prompt/references/基础运动与专项路由.md'
        text=doc.read_text()
        for name in ['camera-movement','animation','motion-design','editing','audiovisual']:
            self.assertIn('../skills/laohu-'+name+'/SKILL.md',text)
        for link in re.findall(r'\]\(([^)]+)\)',text):self.assertTrue((doc.parent/link).is_file())
        self.assertIn('纯火柴人格斗',text)
        self.assertIn('普通纸艺剧情',text)
        self.assertIn('同一上下文中已读且未变',text)

if __name__=='__main__':unittest.main()
