import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location('dependencies', Path(__file__).resolve().parents[1] / 'scripts/validate_delivery_dependencies.py')
deps = importlib.util.module_from_spec(spec)
spec.loader.exec_module(deps)


class DependencyTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for name in ('frame.png', 'prompt.md', 'cut.md', 'other.md'):
            (self.root / name).write_text(name)
        self.record = self.root / 'stage.md'
        self.record.write_text('# 阶段记录\n\n已确认的正文。\n')

    def record_one(self, consumer='prompt.md', source='frame.png', role='first_frame'):
        deps.record_review(self.root, self.record, consumer, [(role, source)], '机位与开场一致', '执行者反审')

    def test_change_invalidates_only_affected_consumers_and_propagates(self):
        self.record_one()
        self.record_one('cut.md', 'prompt.md', 'content')
        (self.root / 'separate.png').write_text('unrelated source')
        self.record_one('other.md', 'separate.png', 'style')
        (self.root / 'frame.png').write_text('changed frame')
        results = {r['consumer']: r['status'] for r in deps.check_reviews(self.root, self.record)}
        self.assertEqual(results, {'prompt.md': 'PENDING_REVIEW', 'cut.md': 'PENDING_REVIEW', 'other.md': 'UNCHANGED'})

    def test_changed_source_and_consumer_require_review(self):
        self.record_one()
        self.assertEqual(deps.check_reviews(self.root, self.record)[0]['status'], 'UNCHANGED')
        (self.root / 'frame.png').write_text('different camera')
        self.assertEqual(deps.check_reviews(self.root, self.record)[0]['status'], 'PENDING_REVIEW')
        self.record_one()
        (self.root / 'prompt.md').write_text('different opening')
        self.assertEqual(deps.check_reviews(self.root, self.record)[0]['status'], 'PENDING_REVIEW')

    def test_records_preserve_stage_text_and_require_reason(self):
        before = self.record.read_text()
        with self.assertRaises(ValueError):
            deps.record_review(self.root, self.record, 'prompt.md', [('style', 'frame.png')], '', 'editor')
        self.assertEqual(self.record.read_text(), before)
        self.record_one(role='style')
        self.assertTrue(self.record.read_text().startswith(before))
        self.assertEqual(deps.check_reviews(self.root, self.record)[0]['sources'][0]['role'], 'style')

    def test_missing_and_external_paths_cannot_be_certified(self):
        with self.assertRaises(ValueError):
            self.record_one(source='../outside.png')
        self.record_one()
        (self.root / 'frame.png').unlink()
        self.assertEqual(deps.check_reviews(self.root, self.record)[0]['status'], 'PENDING_REVIEW')

    def test_no_record_is_not_a_pass(self):
        with self.assertRaises(ValueError):
            deps.check_reviews(self.root, self.record)

    def test_self_dependency_is_rejected(self):
        with self.assertRaises(ValueError):
            self.record_one('prompt.md', 'prompt.md', 'content')

    def test_upstream_review_does_not_review_downstream(self):
        self.record_one()
        self.record_one('cut.md', 'prompt.md', 'content')
        (self.root / 'frame.png').write_text('new framing')
        self.record_one()
        results = {r['consumer']: r['status'] for r in deps.check_reviews(self.root, self.record)}
        self.assertEqual(results['cut.md'], 'PENDING_REVIEW')
        self.record_one('cut.md', 'prompt.md', 'content')
        self.assertTrue(all(r['status'] == 'UNCHANGED' for r in deps.check_reviews(self.root, self.record)))

    def test_malformed_records_are_rejected_on_read(self):
        self.record_one()
        text, matches, original = deps.read_record(self.record)
        for field, value in [('reason', ' '), ('reviewer', 1), ('reviewed_at', 'not a date'), ('consumer', './prompt.md'), ('sha256', 'fake')]:
            with self.subTest(field=field):
                data = json.loads(json.dumps(original))
                data['reviews'][0][field] = value
                self.record.write_text(deps.MARKER + '\n```json\n' + json.dumps(data) + '\n```')
                with self.assertRaises(ValueError):
                    deps.check_reviews(self.root, self.record)

    def test_hand_edited_cycle_is_rejected_on_read(self):
        self.record_one()
        self.record_one('cut.md', 'prompt.md', 'content')
        _, _, data = deps.read_record(self.record)
        data['reviews'][0]['sources'][0]['path'] = 'cut.md'
        self.record.write_text(deps.MARKER + '\n```json\n' + json.dumps(data) + '\n```')
        with self.assertRaises(ValueError):
            deps.check_reviews(self.root, self.record)

    def test_case_insensitive_aliases_do_not_bypass_propagation(self):
        if not (self.root / 'PROMPT.MD').exists():
            self.skipTest('case-sensitive filesystem')
        self.record_one('PROMPT.MD')
        self.record_one('cut.md', 'prompt.md', 'content')
        (self.root / 'frame.png').write_text('changed')
        self.assertTrue(all(r['status'] == 'PENDING_REVIEW' for r in deps.check_reviews(self.root, self.record)))
        with self.assertRaises(ValueError):
            self.record_one('prompt.md', 'PROMPT.MD', 'content')


if __name__ == '__main__':
    unittest.main()
