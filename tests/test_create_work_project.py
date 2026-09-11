from __future__ import annotations

import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = Path("skills/laohu-ai-visual/scripts/create_work_project.sh")
TEMPLATES = Path("02_共享资产库/01_模板库/项目启动模板")


class CreateWorkProjectTests(unittest.TestCase):
    def setUp(self):
        # Never read private works or use the system temporary directory.
        scratch = ROOT / "tmp"
        scratch.mkdir(exist_ok=True)
        self.tmp = tempfile.TemporaryDirectory(prefix="create-work-test-", dir=scratch)
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / SCRIPT).parent.mkdir(parents=True)
        shutil.copy2(ROOT / SCRIPT, self.root / SCRIPT)
        shutil.copytree(ROOT / TEMPLATES, self.root / TEMPLATES)
        (self.root / "scripts").mkdir()
        shutil.copy2(ROOT / "scripts/render_delivery_html.py", self.root / "scripts")

    def run_creator(self, *args):
        return subprocess.run(
            ["bash", str(self.root / SCRIPT), *args], cwd=self.root,
            env={**os.environ, "TMPDIR": str(self.root), "PYTHONDONTWRITEBYTECODE": "1"},
            text=True, capture_output=True,
        )

    def create(self, *args):
        result = self.run_creator(*args)
        self.assertEqual(result.returncode, 0, result.stderr)
        project = Path(result.stdout.strip())
        self.assertTrue(project.is_dir(), result.stdout)
        return project

    def test_legacy_arguments_keep_directory_status_separate_from_progress(self):
        project = self.create("隔离故事", "2026-09-08", "已完成")
        self.assertEqual(project.parent.name, "已完成")
        overview = (project / "00_项目总览.md").read_text()
        self.assertIn("目录状态：已完成", overview)
        self.assertIn("生产状态：IDEA", overview)
        self.assertIn("作品类型：story", overview)

    def test_story_creates_only_entry_directories_and_two_current_records(self):
        project = self.create("最小故事", "2026-09-08")
        directories = {p.relative_to(project).as_posix() for p in project.rglob("*") if p.is_dir()}
        self.assertEqual(directories, {"00_原始输入", "00_原始输入/文本"})
        self.assertEqual({p.name for p in project.rglob("*.md")}, {"00_项目总览.md", "00_阶段确认记录.md"})
        overview = (project / "00_项目总览.md").read_text()
        self.assertIn("laohu-director", overview)
        self.assertIn("完整E-S正式剧本", overview)
        self.assertIn("E-S", overview)
        self.assertIn("E-S-P", overview)
        self.assertIn("SHOT", overview)
        self.assertNotIn("E1-S1-C1", overview)
        self.assertNotIn("12 秒", overview)

    def test_image_branch_does_not_require_story_or_video(self):
        project = self.create("单张成品", "--kind", "image", "2026-09-08")
        overview = (project / "00_项目总览.md").read_text()
        self.assertIn("作品类型：image", overview)
        self.assertIn("单张成品图", overview)
        self.assertIn("laohu-visual-assets", overview)
        self.assertNotIn("laohu-script-writer", overview)
        self.assertNotIn("E-S-P", overview)
        self.assertFalse((project / "02_剧本").exists())

    def test_mv_requires_final_audio_evidence_without_invented_timing(self):
        project = self.create("--kind", "mv", "歌曲视觉", "2026-09-08")
        self.assertTrue((project / "00_原始输入/音频").is_dir())
        overview = (project / "00_项目总览.md").read_text()
        for expected in ("作品类型：mv", "最终音频", "时间证据", "laohu-mv-director", "SHOT"):
            self.assertIn(expected, overview)
        self.assertNotIn("12 秒", overview)
        self.assertNotIn("E1-S1-C1", overview)
        self.assertFalse((project / "04_分镜").exists())

    def test_registered_human_gates_remain_conditional(self):
        project = self.create("确认边界", "2026-09-08")
        record = (project / "00_阶段确认记录.md").read_text()
        for gate in ("服装方向", "F", "STY", "VMB", "人工定案", "高成本", "公开发布"):
            self.assertIn(gate, record)
        self.assertIn("未触发", record)
        self.assertNotIn("| 待确认 |", record)
        self.assertNotIn("分镜表格输出文件", record)

    def test_creation_renders_current_records_and_delivery_center(self):
        project = self.create("交付入口", "2026-09-08")
        for name in ("00_项目总览.html", "00_阶段确认记录.html", "00_作品交付中心.html"):
            self.assertTrue((project / name).is_file(), name)
        self.assertIn("交付入口", (project / "00_项目总览.html").read_text())

    def test_invalid_cli_leaves_no_project_tree(self):
        cases = [(), ("",), (" ",), (".",), ("..",), (" 名字",), ("名字 ",),
                 ("../逃逸",), ("a/b",), ("a\\b",), ("坏\n名字",), ("长" * 90,),
                 ("样例", "../2026"), ("样例", "2026-02-30"), ("样例", "2026-9-8"),
                 ("样例", "2026-09-08", "错误状态"), ("样例", "--kind", "bad"),
                 ("样例", "--kind"), ("样例", "--unknown"), ("a", "b", "c", "d")]
        for args in cases:
            with self.subTest(args=args):
                try:
                    result = self.run_creator(*args)
                    self.assertNotEqual(result.returncode, 0)
                    self.assertFalse((self.root / "01_作品项目").exists())
                finally:
                    # Keep failures independent within this isolated fixture.
                    shutil.rmtree(self.root / "01_作品项目", ignore_errors=True)

    def test_default_date_and_help(self):
        from datetime import date
        result = self.run_creator("--help")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse((self.root / "01_作品项目").exists())
        self.assertEqual(self.create("中文 空格").name, f"{date.today().isoformat()}_中文 空格")

    def test_existing_work_is_preserved(self):
        project = self.create("保留", "2026-09-08")
        overview = project / "00_项目总览.md"
        overview.write_text("已确认内容")
        result = self.run_creator("保留", "2026-09-08")
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(overview.read_text(), "已确认内容")

    def test_missing_template_fails_before_writing(self):
        (self.root / TEMPLATES / "模板_作品项目启动包.md").unlink()
        result = self.run_creator("缺模板", "2026-09-08")
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse((self.root / "01_作品项目").exists())

    def test_render_failure_removes_only_the_new_work(self):
        existing = self.create("已有作品", "2026-09-08")
        (self.root / "scripts/render_delivery_html.py").write_text("raise SystemExit('render failed')")
        result = self.run_creator("渲染失败", "2026-09-08")
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(list(existing.parent.iterdir()), [existing])

    def test_missing_template_section_fails_before_writing(self):
        path = self.root / TEMPLATES / "模板_作品项目启动包.md"
        path.write_text(path.read_text().replace("<!-- image -->", "<!-- unavailable -->"))
        result = self.run_creator("缺分支", "--kind=image")
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse((self.root / "01_作品项目").exists())


if __name__ == "__main__":
    unittest.main()
