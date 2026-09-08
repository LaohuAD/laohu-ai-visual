from __future__ import annotations

import html as html_lib
import re
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.render_delivery_html import render_markdown, render_project


ASSET_SOURCE = """# 测试资产总表

## 可复制图片提示词

### LZ70｜路子宽·35kg阶段素体资产

状态：待生成

```text
【素体参考@B01】锁永久身份。LZ70阶段素体提示词，保留 <身体> 与 & 符号。
```

### W01｜路子宽·学校校服资产

```text
W01人物服装资产，身份场景活动推导完整。
```

### G01｜三名同学关系群像

```text
G01三名同学群像资产。
```
"""

GROUPED_ASSET_SOURCE = """# 分组资产总表

### G01｜三名同学关系群像
```text
G01群像。
```

### F01｜路子宽·人物写真参考资产
```text
F01人物写真参考资产。
```

### S01｜学校食堂场景
```text
S01场景。
```

### W02｜第二套服装
```text
W02服装。
```

### LZ70｜路子宽·35kg阶段素体资产
```text
LZ70阶段素体。
```

### A01｜体重秤道具
```text
A01道具。
```

### M01｜路子宽·校服妆造设计资产
```text
M01妆造。
```

### B01｜路子宽·基础素体资产
```text
B01基础素体。
```

### W01｜第一套服装
```text
W01服装。
```
"""

PORTRAIT_WITH_ACCEPTED_BODY_SOURCE = """# 人物写真母图与已验收素体

### F01｜路子宽·人物写真母图

```text
F01人物写真母图，供B01、W01和M01反向拆解，不直接进入视频。
```

### B01｜路子宽·基础素体资产

状态：实图已验收

```text
B01基础素体。
```
"""

LEGACY_RETIRED_PORTRAIT_SOURCE = PORTRAIT_WITH_ACCEPTED_BODY_SOURCE.replace(
    "### F01｜路子宽·人物写真母图\n",
    "### F01｜路子宽·人物写真母图\n\n状态：已退役（B01实图已验收）\n",
)


class RenderDeliveryHtmlTests(unittest.TestCase):
    def write(self, root: Path, relative: str, content: str) -> Path:
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return path

    def test_asset_heading_becomes_named_card_with_copy_button(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = self.write(root, "assets.md", ASSET_SOURCE)
            rendered = render_markdown(source)

            self.assertIn('data-asset-id="LZ70"', rendered)
            self.assertIn('data-asset-type="LZ"', rendered)
            self.assertIn('data-asset-id="G01"', rendered)
            self.assertIn('data-asset-type="G"', rendered)
            self.assertIn("LZ70｜路子宽·35kg阶段素体资产", rendered)
            self.assertIn("复制提示词", rendered)
            self.assertIn("待生成", rendered)
            self.assertEqual(rendered.count('id="lz70"'), 1)
            self.assertIn('id="lz70-title"', rendered)

    def test_prompt_text_is_preserved_after_html_unescape(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = self.write(root, "assets.md", ASSET_SOURCE)
            rendered = render_markdown(source)
            match = re.search(r'<code class="language-text">(.*?)</code>', rendered, re.S)

            self.assertIsNotNone(match)
            prompt = html_lib.unescape(match.group(1))
            self.assertEqual(
                prompt,
                "【素体参考@B01】锁永久身份。LZ70阶段素体提示词，保留 <身体> 与 & 符号。",
            )

    def test_delivery_page_remains_text_only_even_when_matching_image_exists(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = self.write(root, "文本/assets.md", ASSET_SOURCE)
            image_dir = root / "图片"
            image_dir.mkdir()
            (image_dir / "LZ70_阶段素体.png").write_bytes(b"not-a-real-png")

            rendered = render_markdown(source)

            self.assertNotIn("<img", rendered)
            self.assertNotIn("LZ70_阶段素体.png", rendered)
            self.assertNotIn("asset-placeholder", rendered)

    def test_video_heading_becomes_vid_card(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = self.write(
                root,
                "video.md",
                """# 视频执行单

## VID01｜食堂冲突

模型：Seedance 2.5

```text
【基础设定】总时长12秒。
【场景状态与氛围画质】食堂空间已成立。
【画面内容】【镜头01｜中景｜平视｜缓推】路子宽抬头。
```
""",
            )

            rendered = render_markdown(source)

            self.assertIn('data-asset-id="VID01"', rendered)
            self.assertIn('data-asset-type="VID"', rendered)
            self.assertIn("复制提示词", rendered)

    def test_video_batch_heading_becomes_batch_card(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = self.write(
                root,
                "video.md",
                """# 视频生成批次

## E01-S02-B01｜正侧光追击

源剧本镜头：E01-S02-C01—C03

```text
【基础设定】总时长15秒。
【场景状态与氛围画质】走廊状态已成立。
【画面内容】【镜头01｜中景｜平视｜跟拍】Luna向前。
```
""",
            )

            rendered = render_markdown(source)

            self.assertIn('data-asset-id="E01-S02-B01"', rendered)
            self.assertIn('data-asset-type="BATCH"', rendered)
            self.assertIn("视频生成批次", rendered)
            self.assertIn("复制提示词", rendered)

    def test_generic_markdown_keeps_readable_headings_lists_and_tables(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = self.write(
                root,
                "script.md",
                """# 剧本

- 第一场
- 第二场

| 人物 | 台词 |
|---|---|
| 路子宽 | 我知道。 |
""",
            )

            rendered = render_markdown(source)

            self.assertIn("<h1", rendered)
            self.assertIn("<ul>", rendered)
            self.assertIn("<table>", rendered)
            self.assertIn("路子宽", rendered)

    def test_copy_uses_clipboard_api_with_legacy_fallback(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            source = self.write(Path(tmp), "assets.md", ASSET_SOURCE)
            rendered = render_markdown(source)

            self.assertIn("navigator.clipboard.writeText", rendered)
            self.assertIn("document.execCommand('copy')", rendered)
            self.assertIn("复制成功", rendered)

    def test_asset_page_is_a_compact_multi_column_copy_workspace(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            source = self.write(Path(tmp), "assets.md", ASSET_SOURCE)
            rendered = render_markdown(source)

            self.assertIn("grid-template-columns:repeat(auto-fill,minmax(240px,1fr))", rendered)
            self.assertIn("font-size:13px", rendered)
            self.assertIn("复制提示词", rendered)
            self.assertIn("查看详情", rendered)
            self.assertIn('class="prompt-source"', rendered)

    def test_asset_cards_are_grouped_in_workflow_order_then_sorted_by_id(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            source = self.write(Path(tmp), "assets.md", GROUPED_ASSET_SOURCE)
            rendered = render_markdown(source)

            expected_groups = [
                "人物主视觉图",
                "素体与阶段素体资产",
                "服装资产",
                "妆造设计资产",
                "道具资产",
                "场景资产",
                "群像资产",
            ]
            positions = [rendered.index(f">{label}<") for label in expected_groups]
            self.assertEqual(positions, sorted(positions))
            self.assertEqual(rendered.count('class="asset-group"'), 7)
            self.assertLess(rendered.index('data-asset-id="F01"'), rendered.index('data-asset-id="B01"'))
            self.assertLess(rendered.index('data-asset-id="B01"'), rendered.index('data-asset-id="LZ70"'))
            self.assertLess(rendered.index('data-asset-id="W01"'), rendered.index('data-asset-id="W02"'))

    def test_portrait_mother_card_remains_active_after_body_acceptance(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            source = self.write(Path(tmp), "assets.md", PORTRAIT_WITH_ACCEPTED_BODY_SOURCE)
            rendered = render_markdown(source)
            card = re.search(
                r'<section class="result-card"[^>]*data-asset-id="F01".*?</section>',
                rendered,
                re.S,
            )

            self.assertIsNotNone(card)
            self.assertNotIn('data-asset-status="retired"', card.group(0))
            self.assertNotIn('class="asset-status">已退役</span>', card.group(0))
            self.assertIn('class="copy-button"', card.group(0))
            self.assertIn('class="title-copy-button"', card.group(0))
            self.assertIn('class="detail-button"', card.group(0))

    def test_legacy_retired_portrait_status_no_longer_disables_mother_image(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            source = self.write(Path(tmp), "assets.md", LEGACY_RETIRED_PORTRAIT_SOURCE)
            rendered = render_markdown(source)
            card = re.search(
                r'<section class="result-card"[^>]*data-asset-id="F01".*?</section>',
                rendered,
                re.S,
            )

            self.assertIsNotNone(card)
            self.assertNotIn('data-asset-status="retired"', card.group(0))
            self.assertIn('class="copy-button"', card.group(0))

    def test_asset_card_has_copy_title_button_and_uses_visible_card_title(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            source = self.write(Path(tmp), "assets.md", ASSET_SOURCE)
            rendered = render_markdown(source)

            self.assertEqual(rendered.count('class="title-copy-button"'), 3)
            self.assertIn("getPromptTitle(block)", rendered)
            self.assertIn("标题已复制", rendered)
            self.assertIn("复制标题", rendered)

    def test_generic_code_block_does_not_offer_a_meaningless_copy_title(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            source = self.write(
                Path(tmp),
                "notes.md",
                """# 普通说明

```text
普通代码块。
```
""",
            )
            rendered = render_markdown(source)

            self.assertNotIn('class="title-copy-button"', rendered)

    def test_prompt_body_is_hidden_by_default_and_opens_in_one_detail_dialog(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            source = self.write(Path(tmp), "assets.md", ASSET_SOURCE)
            rendered = render_markdown(source)

            self.assertIn('<template class="prompt-source">', rendered)
            self.assertNotIn('<div class="copy-block"><pre>', rendered)
            self.assertEqual(rendered.count('id="prompt-dialog"'), 1)
            self.assertIn('class="detail-button"', rendered)
            self.assertIn("dialog.showModal()", rendered)
            self.assertIn("detail-code", rendered)

    def test_copy_button_reads_full_prompt_from_hidden_source(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            source = self.write(Path(tmp), "assets.md", ASSET_SOURCE)
            rendered = render_markdown(source)

            self.assertIn("getPromptText(block)", rendered)
            self.assertIn("template.content.querySelector('code')", rendered)
            match = re.search(
                r'<template class="prompt-source"><code class="language-text">(.*?)</code></template>',
                rendered,
                re.S,
            )
            self.assertIsNotNone(match)
            self.assertEqual(
                html_lib.unescape(match.group(1)),
                "【素体参考@B01】锁永久身份。LZ70阶段素体提示词，保留 <身体> 与 & 符号。",
            )

    def test_duplicate_domain_ids_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            source = self.write(
                Path(tmp),
                "duplicate.md",
                """# 重复
### W01｜第一套
```text
第一套
```
### W01｜第二套
```text
第二套
```
""",
            )

            with self.assertRaisesRegex(ValueError, "duplicate domain id: W01"):
                render_markdown(source)

    def test_project_mode_writes_companions_and_portal(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "作品"
            first = self.write(root, "02_剧本/文本/剧本.md", "# 剧本\n\n正文。\n")
            second = self.write(root, "03_视觉资产/文本/资产.md", ASSET_SOURCE)

            outputs = render_project(root)

            first_html = first.with_suffix(".html")
            second_html = second.with_suffix(".html")
            portal = root / "00_作品交付中心.html"
            self.assertEqual(set(outputs), {first_html, second_html, portal})
            self.assertTrue(first_html.is_file())
            self.assertTrue(second_html.is_file())
            self.assertTrue(portal.is_file())
            portal_text = portal.read_text(encoding="utf-8")
            self.assertIn("剧本.html", portal_text)
            self.assertIn("资产.html", portal_text)
            self.assertIn('class="portal-title"', portal_text)
            self.assertNotIn("font-size:clamp(2.4rem,6vw,5rem)", portal_text)

    def test_domain_prompt_requires_a_descriptive_title(self) -> None:
        for heading in ("B01", "B01｜", "KF04-A |   ", "STY-03", "VMB01"):
            with self.subTest(heading=heading), tempfile.TemporaryDirectory() as tmp:
                source = self.write(Path(tmp), "assets.md", f"## {heading}\n```text\n正文。\n```\n")
                with self.assertRaisesRegex(ValueError, "missing domain title"):
                    render_markdown(source)

    def test_domain_card_requires_nonempty_prompt_body(self) -> None:
        for body in ("状态：待生成。", "```text\n  \n```", "```python\nprint('说明代码')\n```"):
            with self.subTest(body=body), tempfile.TemporaryDirectory() as tmp:
                source = self.write(Path(tmp), "assets.md", f"## B01｜素体\n{body}\n")
                with self.assertRaisesRegex(ValueError, "missing prompt body: B01"):
                    render_markdown(source)

    def test_unclosed_prompt_fence_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            source = self.write(Path(tmp), "assets.md", "## B01｜素体\n```text\n未闭合正文。\n")
            with self.assertRaisesRegex(ValueError, "unclosed code fence"):
                render_markdown(source)

    def test_missing_body_cannot_borrow_the_next_cards_prompt(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            source = self.write(Path(tmp), "assets.md", "## B01｜素体\n### W01｜服装\n```text\n服装。\n```\n")
            with self.assertRaisesRegex(ValueError, "missing prompt body: B01"):
                render_markdown(source)

    def test_style_master_and_keyframe_cards_preserve_titles_and_prompt_text(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            ids = ("KF04-A", "KF01", "STY-03", "VMB01")
            prompt = "第一行 <关系> & 材质。  \n\n  第二行保留缩进。"
            source = self.write(root, "assets.md", GROUPED_ASSET_SOURCE + "\n".join(
                f"\n## {asset_id}｜明确名称\n```prompt\n{prompt}\n```\n" for asset_id in ids
            ))
            rendered = render_markdown(source)
            for asset_id in ids:
                card = re.search(rf'<section class="result-card"[^>]*data-asset-id="{asset_id}".*?</section>', rendered, re.S)
                self.assertIsNotNone(card, asset_id)
                self.assertIn(f"{asset_id}｜明确名称", card.group(0))
                self.assertIn('class="title-copy-button"', card.group(0))
                code = re.search(r'<code class="language-prompt">(.*?)</code>', card.group(0), re.S)
                self.assertEqual(html_lib.unescape(code.group(1)), prompt)
            self.assertLess(rendered.index('data-asset-id="KF01"'), rendered.index('data-asset-id="KF04-A"'))
            for label in ("关键帧", "风格定调图", "视觉母板"):
                self.assertIn(f">{label}<", rendered)
            self.assertNotIn("<img", rendered)
            self.assertNotIn('data-asset-group="OTHER"', rendered)

    def test_duplicate_extended_domain_ids_are_rejected(self) -> None:
        for asset_id in ("KF04-A", "STY-03", "VMB01"):
            with self.subTest(asset_id=asset_id), tempfile.TemporaryDirectory() as tmp:
                card = f"## {asset_id}｜明确名称\n```text\n正文。\n```\n"
                source = self.write(Path(tmp), "assets.md", card + card)
                with self.assertRaisesRegex(ValueError, f"duplicate domain id: {asset_id}"):
                    render_markdown(source)

    def test_project_validation_failure_preserves_every_existing_page(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write(root, "01_good.md", "# 新的正文\n")
            self.write(root, "02_new.md", "# 新页面\n")
            duplicate = "## B01｜素体\n```text\n正文。\n```\n"
            self.write(root, "03_bad.md", duplicate + duplicate)
            originals = {
                self.write(root, "01_good.html", "旧的正文"): "旧的正文".encode(),
                self.write(root, "03_bad.html", "旧资产页"): "旧资产页".encode(),
                self.write(root, "00_作品交付中心.html", "旧中心"): "旧中心".encode(),
            }
            before = set(root.rglob("*"))
            with self.assertRaisesRegex(ValueError, "duplicate domain id"):
                render_project(root)
            self.assertEqual(set(root.rglob("*")), before)
            for path, content in originals.items():
                self.assertEqual(path.read_bytes(), content)

    def test_project_io_failure_rolls_back_replaced_pages_and_removes_new_pages(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write(root, "01_existing.md", "# 新内容\n")
            self.write(root, "02_new.md", "# 新页面\n")
            old_page = self.write(root, "01_existing.html", "旧正文")
            portal = self.write(root, "00_作品交付中心.html", "旧中心")
            before = set(root.rglob("*"))
            real_replace = Path.replace
            failed = False

            def fail_portal_once(path: Path, target: Path) -> Path:
                nonlocal failed
                if Path(target) == portal and not failed:
                    failed = True
                    raise OSError("injected portal replace failure")
                return real_replace(path, target)

            with patch.object(Path, "replace", fail_portal_once):
                with self.assertRaisesRegex(OSError, "injected portal replace failure"):
                    render_project(root)
            self.assertEqual(set(root.rglob("*")), before)
            self.assertEqual(old_page.read_text(), "旧正文")
            self.assertEqual(portal.read_text(), "旧中心")

    def test_historical_combined_keyframes_and_asset_indexes_remain_readable(self) -> None:
        # Observed historical shape, with private creative content removed.
        source_text = """# 阶段记录
## 三、STY-03 与 VMB01 真实验收
| 资产 | 状态 |
|---|---|
| STY-03 | 已验收 |
| VMB01 | 已验收 |
### KF04-A／B｜同场的两个状态
```text
起始状态。
```
```text
结果状态。
```
"""
        with tempfile.TemporaryDirectory() as tmp:
            source = self.write(Path(tmp), "history.md", source_text)
            rendered = render_markdown(source)
            self.assertIn("KF04-A／B｜同场的两个状态", rendered)
            self.assertIn("<table>", rendered)
            self.assertEqual(rendered.count('class="copy-button"'), 2)
            self.assertNotIn('class="result-card"', rendered)
            self.assertNotIn('class="title-copy-button"', rendered)

    def test_project_staging_failure_leaves_all_pages_unchanged(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write(root, "01_source.md", "# 新正文\n")
            old_page = self.write(root, "01_source.html", "旧正文")
            portal = self.write(root, "00_作品交付中心.html", "旧中心")
            before = set(root.rglob("*"))
            with patch("scripts.render_delivery_html.shutil.copy2", side_effect=OSError("backup unavailable")):
                with self.assertRaisesRegex(OSError, "backup unavailable"):
                    render_project(root)
            self.assertEqual(set(root.rglob("*")), before)
            self.assertEqual(old_page.read_text(), "旧正文")
            self.assertEqual(portal.read_text(), "旧中心")

    def test_project_incomplete_rollback_reports_and_retains_backup(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write(root, "01_source.md", "# 新正文\n")
            old_page = self.write(root, "01_source.html", "旧正文")
            portal = self.write(root, "00_作品交付中心.html", "旧中心")
            real_replace = Path.replace
            replacement_count = 0

            def fail_after_first_replace(path: Path, target: Path) -> Path:
                nonlocal replacement_count
                replacement_count += 1
                if replacement_count > 1:
                    raise OSError("disk disconnected")
                return real_replace(path, target)

            with patch.object(Path, "replace", fail_after_first_replace):
                with self.assertRaisesRegex(OSError, "rollback incomplete") as raised:
                    render_project(root)
            backups = list(root.glob(".delivery-*"))
            self.assertEqual(len(backups), 1)
            self.assertEqual(backups[0].read_text(), "旧正文")
            self.assertIn(str(backups[0]), str(raised.exception))
            self.assertIn(str(old_page), str(raised.exception))
            self.assertEqual(portal.read_text(), "旧中心")


if __name__ == "__main__":
    unittest.main()
