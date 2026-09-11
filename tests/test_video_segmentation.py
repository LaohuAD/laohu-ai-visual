"""Executable checks for source conservation, duration, bindings and P/C delivery."""
import copy
import hashlib
import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('segmentation', ROOT/'skills/laohu-video-segmentation/scripts/validate_plan.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def plan():
    source = '△甲递出笔。\n乙：我不签。\n△甲收回笔。'
    cut = source.index('△甲收回')
    parts = []
    for i,(a,b) in enumerate([(0,cut),(cut,len(source))],1):
        parts.append(dict(id=f'E01-S01-P{i:02}',scene='E01-S01',source_start=a,source_end=b,
            excerpt=source[a:b],seconds=[6,10],timing_basis='递笔和对白同时；收回在拒绝之后',
            asset_refs=['A01'],start_state='笔在甲手' if i==1 else '甲持笔伸出',
            end_state='甲持笔伸出' if i==1 else '笔收回',state_refs=[]))
    parts[1]['continues']=parts[0]['id']
    return dict(source=source,source_sha256=hashlib.sha256(source.encode()).hexdigest(),
        units=[dict(scene='E01-S01',start=0,end=len(source))],parts=parts,
        assets=[dict(id='A01',status='planned')])


class SegmentationTests(unittest.TestCase):
    def test_source_coverage_and_moving_continuation(self):
        self.assertEqual(module.validate(plan()),[])

    def test_missing_or_duplicate_content_is_rejected(self):
        for change in [-1,1]:
            p=plan();p['parts'][1]['source_start']+=change
            self.assertTrue(module.validate(p))

    def test_paraphrase_is_not_original(self):
        p=plan();p['parts'][0]['excerpt']=p['parts'][0]['excerpt'].replace('不签','同意')
        self.assertTrue(any('excerpt' in e for e in module.validate(p)))

    def test_changed_source_reopens_plan(self):
        p=plan();p['source']+='\n新动作'
        self.assertTrue(any('source changed' in e for e in module.validate(p)))

    def test_upper_estimate_and_handles_must_fit(self):
        p=plan();p['parts'][0]['seconds']=[25,29];p['parts'][0]['handles_seconds']=2
        self.assertTrue(any('duration' in e for e in module.validate(p)))

    def test_wrong_namespace_and_order_are_rejected(self):
        p=plan();p['parts'][0]['id']='E01-S01-C01'
        self.assertTrue(any('namespace' in e for e in module.validate(p)))
        p=plan();p['parts'].reverse();self.assertTrue(module.validate(p))

    def test_planned_asset_can_be_listed_but_not_bound(self):
        p=plan();self.assertEqual(module.validate(p),[])
        p['parts'][0]['bound_assets']=['A01']
        self.assertTrue(any('binding' in e for e in module.validate(p)))

    def test_false_tailframe_and_missing_consumer_are_rejected(self):
        p=plan();p['parts'][0]['state_refs']=[dict(method='extract',consumer='E01-S01-P02',status='planned')]
        self.assertEqual(module.validate(p),[])
        p['parts'][0]['state_refs'][0]['status']='verified'
        self.assertTrue(any('passed off' in e for e in module.validate(p)))

    def test_continuity_state_must_match(self):
        p=plan();p['parts'][1]['start_state']='笔凭空在乙手里'
        self.assertTrue(any('state mismatch' in e for e in module.validate(p)))

    def test_renderer_distinguishes_video_part_and_body_asset(self):
        from scripts.render_delivery_html import collect_headings,domain_type
        headings=collect_headings('## E01-S01-P01｜交笔\n\n## P01｜人物状态\n')
        self.assertEqual([h.domain_id for h in headings],['E01-S01-P01','P01'])
        self.assertEqual(domain_type('E01-S01-P01'),'BATCH')
        self.assertEqual(domain_type('P01'),'P')
        self.assertEqual(domain_type('E01-S01-B01'),'BATCH')
        with self.assertRaises(ValueError):
            collect_headings('## E01-S01-P01｜甲\n## E01-S01-P01｜乙\n')

    def test_current_contract_has_source_then_part_then_camera(self):
        writer=(ROOT/'skills/laohu-script-writer/skills/laohu-format-adaptation/references/镜头化剧本与连续性.md').read_text()
        skill=(ROOT/'skills/laohu-video-segmentation/SKILL.md').read_text()
        self.assertIn('先把戏写成立，不承担4—30秒P分段或C摄影',writer)
        self.assertNotIn('所有观众会看到或听到的正文必须归入一个镜号',writer)
        for term in ['ASSET之后','SEGMENT','素材余量','完整音频归属','成片取帧','预制状态图','只读原剧本']:
            self.assertIn(term,skill)


if __name__=='__main__':unittest.main()
