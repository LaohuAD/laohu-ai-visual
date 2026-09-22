"""Isolated regression tests; no network, media, or repository writes."""
from __future__ import annotations

import html
import importlib.util
import re
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
CANDIDATES = (
    HERE / "video_prompt_lexing.py",
    HERE.parent / ".agents/skills/laohu-inspection/scripts/video_prompt_lexing.py",
)
MODULE_FILE = next((p for p in CANDIDATES if p.is_file()), None)
if MODULE_FILE is None:
    raise ImportError("video_prompt_lexing.py not found in support folder or project")
spec = importlib.util.spec_from_file_location("laohu_prompt_lexing", MODULE_FILE)
assert spec and spec.loader
lex = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = lex
spec.loader.exec_module(lex)

SEED = '''【基础设定】
总时长8秒；文生视频；对白、同期动作声与环境声；无配乐。
【场景状态与氛围画质】
窗在左后方，钥匙置于桌面，周站在门内。
【画面内容】
【C01｜中景｜桌南侧平视｜固定机位】
画面先看见林把钥匙放到桌上，随后周的手停在门把处。林说：{钥匙留在这里。} <金属落在木桌上的短响> 最后两人的目光停在钥匙上。'''
H3 = '''【基础设定】
<Subject 1>：<Picture 1>中的林，仅锁人物身份。
<Subject 2>：<Picture 1>中的周，仅锁人物身份。
<Audio 1>：林(S1)的音色参考；reference；原台词不复用。
【场景状态与氛围画质】
窗在左后方，钥匙置于桌面，周站在门内。
【画面内容】
【C01｜中景｜桌南侧平视｜固定机位】
画面先看见<Subject 1>把钥匙放到桌上，随后<Subject 2>的手停在门把处。林(S1)使用<Audio 1>的音色说：<d>[Chinese]钥匙留在这里。</d> 金属轻响后，两人的目光停在钥匙上。'''
KLING = '''【基础设定】
[Character A: 林，蓝色外套；沿用已确认人物身份]
[Character B: 周，棕色上衣；沿用已确认人物身份]
【场景状态与氛围画质】
窗在左后方，钥匙置于桌面，周站在门内。
【画面内容】
【C01｜中景｜桌南侧平视｜固定机位】
画面先看见Character A把钥匙放到桌上，随后Character B的手停在门把处。Character A用普通话说：“钥匙留在这里。” 金属轻响后，两人的目光停在钥匙上。'''


def fence(body: str, run: str = "```", info: str = "text") -> str:
    return f"{run}{info}\n{body}\n{run}\n"


class TestThreeSectionLexing(unittest.TestCase):
    def check(self, text, profile="seedance", expected="PASS"):
        r = lex.inspect_prompt(text, profile)
        self.assertEqual(r["syntax_status"], expected, r["errors"])
        return r

    def test_01_seedance(self): self.check(SEED)
    def test_02_h3(self): self.check(H3, "h3")
    def test_03_kling(self): self.check(KLING, "kling")
    def test_04_wrong_heading_order(self):
        self.check(SEED.replace("【基础设定】", "TMP").replace("【场景状态与氛围画质】", "【基础设定】").replace("TMP", "【场景状态与氛围画质】"), expected="FAIL")
    def test_05_missing_heading(self): self.check(SEED.replace("【基础设定】", ""), expected="FAIL")
    def test_06_duplicate_heading(self): self.check(SEED + "\n【基础设定】", expected="FAIL")
    def test_07_fourth_heading(self): self.check(SEED + "\n【保留分析】\n内容", expected="FAIL")
    def test_08_missing_shot(self): self.check(SEED.replace("【C01｜中景｜桌南侧平视｜固定机位】", ""), expected="FAIL")
    def test_09_skipped_shot(self): self.check(SEED.replace("C01", "C02"), expected="FAIL")
    def test_10_duplicate_shot(self): self.check(SEED + "\n【C01｜近景｜桌侧｜固定】\n手停住。", expected="FAIL")
    def test_11_weak_shot_fields(self): self.check(SEED.replace("C01｜中景｜桌南侧平视｜固定机位", "C01｜中景"), expected="FAIL")
    def test_12_legacy_shot_alias(self): self.check(SEED.replace("C01", "镜头01"))
    def test_13_complex_shot_header(self): self.check(SEED.replace("固定机位】", "固定机位｜构图：左→右｜节奏：等→停】"))
    def test_14_shot_in_wrong_section(self):
        text = SEED.replace("【C01｜中景｜桌南侧平视｜固定机位】", "").replace("【基础设定】", "【基础设定】\n【C01｜中景｜桌侧｜固定】")
        self.check(text, expected="FAIL")
    def test_15_h3_in_seedance(self): self.check(SEED + " <Audio 1>", expected="FAIL")
    def test_16_seedance_in_h3(self): self.check(H3 + " {另一个声音。}", "h3", "FAIL")
    def test_17_seedance_sfx_in_h3(self): self.check(H3 + " <玻璃轻响>", "h3", "FAIL")
    def test_18_speaker_in_seedance(self): self.check(SEED + " (S1)", expected="FAIL")
    def test_19_kling_in_seedance(self): self.check(SEED + " [Character A: 林]", expected="FAIL")
    def test_20_foreign_six_field(self): self.check(H3 + "\nretention_analysis: 内容", "h3", "FAIL")
    def test_21_h3_dialogue_with_author_words(self):
        self.check(H3.replace("钥匙留在这里。</d>", "不要出现，让观众看到【基础设定】。</d>"), "h3")
    def test_22_brace_dialogue_with_fake_h3(self): self.check(SEED.replace("钥匙留在这里。", "请解释<Audio 1>，不要出现字幕。"))
    def test_23_kling_literal_with_tags(self): self.check(KLING.replace("钥匙留在这里。", "请解释<Subject 1>和【画面内容】。"), "kling")
    def test_24_h3_unclosed_d(self): self.check(H3.replace("</d>", ""), "h3", "FAIL")
    def test_25_orphan_d_close(self): self.check(H3 + " </d>", "h3", "FAIL")
    def test_26_missing_language(self): self.check(H3.replace("[Chinese]", ""), "h3", "FAIL")
    def test_27_nested_d_collision(self): self.check(H3.replace("钥匙留", "<d>钥匙留"), "h3", "FAIL")
    def test_28_brace_unclosed(self): self.check(SEED.replace("。}", "。"), expected="FAIL")
    def test_29_brace_orphan_close(self): self.check(SEED + " }", expected="FAIL")
    def test_30_balanced_nested_literal_braces(self): self.check(SEED.replace("钥匙留在这里。", '代码中的{"a":1}保留。'))
    def test_31_payload_verbatim(self):
        r = self.check(H3.replace("钥匙留在这里。", " 钥匙……留在这里！  "), "h3")
        self.assertEqual([s["payload"] for s in r["payloads"] if s["kind"] == "dialogue"], [" 钥匙……留在这里！  "])
    def test_32_character_count_raw(self): self.assertEqual(self.check(H3, "h3")["characters"], len(H3))
    def test_33_exact_limit(self): self.assertEqual(lex.inspect_prompt(H3, "h3", len(H3))["syntax_status"], "PASS")
    def test_34_over_limit(self): self.assertEqual(lex.inspect_prompt(H3, "h3", len(H3)-1)["syntax_status"], "FAIL")
    def test_35_unknown_profile(self):
        with self.assertRaises(ValueError): lex.inspect_prompt(SEED, "magic")
    def test_36_bad_limit(self):
        with self.assertRaises(ValueError): lex.inspect_prompt(SEED, limit=0)
    def test_37_tilde_fence(self): self.assertEqual(lex.scan_fences(fence(SEED, "~~~"))[0].text, SEED)
    def test_38_long_outer_fence(self): self.assertEqual(len(lex.scan_fences(fence("```text\nhello\n```", "````"))), 1)
    def test_39_unclosed_fence(self):
        with self.assertRaises(lex.LexError): lex.scan_fences("```text\nhello")
    def test_40_wrong_fence_character(self):
        with self.assertRaises(lex.LexError): lex.scan_fences("```text\nhello\n~~~")
    def test_41_longer_closing_fence(self): self.assertEqual(len(lex.scan_fences("```text\nhello\n`````\n")), 1)
    def test_42_crlf(self): self.assertEqual(lex.scan_fences("```text\r\n中文\r\n```\r\n")[0].text, "中文")
    def test_43_two_blocks_second_missing_heading(self):
        r = lex.inspect_markdown(fence(SEED) + fence(SEED.replace("【基础设定】", "")))
        self.assertEqual([i["syntax_status"] for i in r], ["PASS", "FAIL"])
    def test_44_select_blocks(self):
        r = lex.inspect_markdown(fence("说明", info="note") + fence(H3), "h3", block_indices=[2])
        self.assertEqual(r[0]["block"], 2)
    def test_45_duplicate_block_index(self):
        with self.assertRaises(lex.LexError): lex.inspect_markdown(fence(SEED), block_indices=[1,1])
    def test_46_missing_block_index(self):
        with self.assertRaises(lex.LexError): lex.inspect_markdown(fence(SEED), block_indices=[2])
    def test_47_no_selected_block(self):
        with self.assertRaises(lex.LexError): lex.inspect_markdown("没有提示词")
    def test_48_mask_preserves_offsets(self):
        spans, _ = lex.payload_spans(H3, "h3"); view = lex.mask_spans(H3, spans)
        self.assertEqual(len(view), len(H3)); self.assertEqual([i for i,c in enumerate(view) if c == "\n"], [i for i,c in enumerate(H3) if c == "\n"])
    def test_49_undefined_kling_character(self): self.check(KLING + " Character C站在门外。", "kling", "FAIL")
    def test_50_duplicate_kling_definition(self): self.check(KLING + " [Character A: 另一人]", "kling", "FAIL")
    def test_51_h3_references_independent(self): self.check(H3.replace("<Subject 1>", "<Subject 3>").replace("<Audio 1>", "<Audio 2>"), "h3")
    def test_52_no_fake_semantic_pass(self):
        r = self.check(H3, "h3")
        for k in ("semantic_status", "reference_status", "provider_status", "media_status"): self.assertEqual(r[k], "NOT_CHECKED")
    def test_53_plaintext_tag_roundtrip(self):
        raw = '<Subject 1>说：<d>[Chinese]A & B。</d>'
        rendered = '<code>' + html.escape(raw, quote=False) + '</code>'
        old = re.sub(r'<[^>]+>', '', html.unescape(rendered))
        new = html.unescape(re.sub(r'<[^>]+>', '', rendered))
        self.assertNotEqual(old, raw); self.assertEqual(new, raw)
    def test_54_literal_markup_is_not_html(self):
        raw = '<script>alert("示例")</script> <Audio 1>'
        rendered = '<code>' + html.escape(raw, quote=False) + '</code>'
        self.assertNotIn('<script>', rendered)
        self.assertEqual(html.unescape(re.sub(r'<[^>]+>', '', rendered)), raw)
    def test_55_more_than_99_shots(self):
        s = '【基础设定】\n文生\n【场景状态与氛围画质】\n室内\n【画面内容】\n' + '\n'.join(f'【C{i:02d}｜中景｜侧面｜固定】\n人物停住。' for i in range(1,102))
        self.check(s)
    def test_56_header_literal_not_structure(self): self.check(SEED.replace("钥匙留在这里。", "第一行\n【基础设定】\n第三行。"))
    def test_57_unclosed_quote(self): self.check(KLING + ' “未闭合', "kling", "FAIL")
    def test_58_unclosed_angle(self): self.check(H3 + ' <Audio 2', "h3", "FAIL")
    def test_59_music_parentheses_not_speaker(self): self.check(SEED + ' (低音在钥匙落桌时进入)')
    def test_60_no_score_policy_lexically_valid(self): self.check(SEED.replace('无配乐。', '不生成BGM。'))


if __name__ == '__main__': unittest.main(verbosity=2)
