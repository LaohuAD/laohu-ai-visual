"""Exercise actual package isolation, source/application separation and atom integrity."""
from pathlib import Path
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from scripts.validate_skill_packages import check_package, NAMES

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / ".agents/skills"
spec = importlib.util.spec_from_file_location("portable_atoms", BASE / "laohu-script-writer/scripts/story_atoms.py")
atoms = importlib.util.module_from_spec(spec)
spec.loader.exec_module(atoms)


class SkillPackageTests(unittest.TestCase):
    def setUp(self):
        # Outside the project ancestry: no accidental discovery of the private source library.
        volume = next(p for p in ROOT.parents if p.name == "Laohu_Work")
        self.temporary = tempfile.TemporaryDirectory(prefix="laohu-skills-isolated-", dir=volume)
        self.addCleanup(self.temporary.cleanup)
        self.scratch = Path(self.temporary.name)

    def command(self, script, *args):
        return subprocess.run([sys.executable, str(script), *args], cwd=self.scratch,
                              env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1", "TMPDIR": str(self.scratch)},
                              capture_output=True, text=True)

    def test_all_five_packages_remain_reachable_in_isolation(self):
        for name in sorted(NAMES):
            with self.subTest(package=name):
                target = self.scratch / "uploaded"
                shutil.copytree(BASE/name, target, symlinks=True)
                self.assertFalse((self.scratch / "02_共享资产库").exists())
                self.assertEqual(check_package(target), [])
                for script in target.rglob('story_component_library.py'):
                    result = self.command(script, 'stats')
                    self.assertEqual(result.returncode, 0, result.stderr)
                for script in target.rglob('story_material_db.py'):
                    result = self.command(script, '--root', str(self.scratch/'synthetic-sources'), 'stats')
                    self.assertEqual(result.returncode, 0, result.stderr)
                shutil.rmtree(target)

    def test_story_atoms_can_be_searched_and_read_without_sources(self):
        target = self.scratch / "uploaded"
        shutil.copytree(BASE/'laohu-script-writer', target)
        script = target/'scripts/story_atoms.py'
        result = self.command(script, 'stats')
        self.assertEqual(result.returncode, 0, result.stderr)
        metadata = json.loads(result.stdout)
        expected = json.loads((target/'references/故事原子/manifest.json').read_text())
        self.assertEqual(metadata['atom_count'], len(expected['atoms']))
        self.assertFalse(metadata['source_original_included'])
        result = self.command(script, 'search', '--limit', '1')
        self.assertEqual(result.returncode, 0, result.stderr)
        results = json.loads(result.stdout)
        if results['items']:
            result = self.command(script, 'get', results['items'][0]['id'])
            self.assertEqual(result.returncode, 0, result.stderr)
            atom = json.loads(result.stdout)
            self.assertIn('source_id', atom)
            self.assertIn('boundaries', atom)
            self.assertIn('visible_evidence', atom)
            self.assertNotIn('original', atom)
        result = self.command(script, 'sync')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('完整来源库', result.stderr)

    def test_missing_source_does_not_destroy_existing_application(self):
        destination = self.scratch/'atoms'
        destination.mkdir()
        sentinel = destination/'manifest.json'
        sentinel.write_text('{"atoms": []}')
        with self.assertRaises(ValueError):
            atoms.sync(self.scratch/'absent', destination)
        self.assertEqual(sentinel.read_text(), '{"atoms": []}')

    def test_local_capture_automatically_updates_both_libraries_and_availability(self):
        from tests.test_story_material_db import load_store_module, StoryMaterialDatabaseRegressionTests as Fixtures
        target = self.scratch/'.agents/skills/laohu-script-writer'
        shutil.copytree(BASE/'laohu-script-writer', target)
        library = self.scratch/'02_共享资产库/故事素材库'
        store = load_store_module().StoryMaterialStore(library)
        store.stats()  # Initialize a real empty authority before automatic local discovery.
        script = target/'skills/laohu-story-material/scripts/story_material_db.py'

        def capture(command, payload):
            location = self.scratch/'payload.json'
            location.write_text(json.dumps(payload, ensure_ascii=False))
            result = self.command(script, command, '--input', str(location))
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn('application_sync', result.stderr)
            return json.loads(result.stdout)

        original = '这是只保存在来源库的测试原话，不进入应用包。'
        source = capture('add-source', Fixtures.source_payload(original))
        created = capture('add-atoms', [Fixtures.atom_payload(source['id'])])
        self.assertIsInstance(created, list)  # Preserve the existing CLI output contract.
        atom_id = created[0]['id']
        self.assertEqual(store.get_sources([source['id']])[0]['original'], original)
        application = target/'references/故事原子'
        self.assertEqual(atoms.get_atom(application, atom_id)['availability'], 'callable')
        self.assertNotIn(original, (application/f'{atom_id}.md').read_text())
        self.assertEqual(store.get_atoms([atom_id])[0]['atom'], created[0]['atom'])
        for event, expected in [('paused', 'paused'), ('reopened', 'callable')]:
            capture('log-usage', {'atom_ids': [atom_id], 'project': '', 'script_position': '',
                                 'usage_role': 'texture', 'transformation': '', 'result': '',
                                 'evidence_path': '', 'scope': 'library', 'event_type': event})
            self.assertEqual(atoms.get_atom(application, atom_id)['availability'], expected)

    def test_tampered_application_atom_is_rejected(self):
        source = BASE/'laohu-script-writer/references/故事原子'
        target = self.scratch/'atoms'
        shutil.copytree(source, target)
        manifest = atoms.read_manifest(target)
        if not manifest['atoms']:
            self.skipTest('application library is empty')
        record = manifest['atoms'][0]
        (target/record['file']).write_text('altered')
        with self.assertRaises(ValueError):
            atoms.get_atom(target, record['id'])

    def test_reference_escape_and_missing_methods_are_detected(self):
        p = self.scratch/'package'
        p.mkdir()
        (self.scratch/'outside.md').write_text('outside')
        (p/'SKILL.md').write_text('---\nname: example\ndescription: example\n---\n[external](../outside.md)\n[missing](references/missing.md)')
        failures = check_package(p)
        self.assertTrue(any('outside package' in x for x in failures))
        self.assertTrue(any('missing method' in x for x in failures))

    def test_application_keeps_original_atom_semantics_and_boundaries(self):
        library = ROOT/'02_共享资产库/故事素材库'
        app = BASE/'laohu-script-writer/references/故事原子'
        for p in (library/'atoms').rglob('*.json'):
            original = json.loads(p.read_text())
            portable = atoms.get_atom(app, original['id'])
            for field, value in original.items():
                self.assertEqual(portable[field], value, (original['id'], field))
            self.assertFalse(portable['source_context']['original_included'])

    def test_internal_specialists_use_package_language_rules(self):
        for package in BASE.iterdir():
            if not package.is_dir() or package.name == 'laohu-language-mode':
                continue
            self.assertTrue((package/'references/语言表达.md').is_file())
            for entry in package.rglob('SKILL.md'):
                self.assertIn('语言表达', entry.read_text(), entry)


if __name__ == '__main__':
    unittest.main()
