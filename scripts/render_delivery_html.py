#!/usr/bin/env python3
"""Compile work Markdown into self-contained, copy-friendly HTML delivery pages."""

from __future__ import annotations

import argparse
import hashlib
import html
import os
import re
import shutil
import sys
import tempfile
from dataclasses import dataclass
from importlib import util as importlib_util
from pathlib import Path
from typing import Sequence


DOMAIN_HEADING = re.compile(
    r"^(?P<id>E\d{2}-S\d{2}-[BP]\d{2,}|KF\d+(?:-[A-Z])?|STY-?\d+|(?:VMB|VID|LZ|[BCFGPWMSA])\d+)(?:\s*[｜|]\s*(?P<title>.*))?$"
)
BATCH_ID = re.compile(r"^E(?P<episode>\d{2})-S(?P<scene>\d{2})-[BP](?P<batch>\d{2,})$")
HEADING = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
TABLE_DIVIDER = re.compile(r"^\s*\|?\s*:?-{3,}:?\s*(?:\|\s*:?-{3,}:?\s*)+\|?\s*$")
RESULT_CARD = re.compile(r'<section class="result-card"[^>]*>.*?</section>', re.S)

# 围栏解析的唯一维护位置是检视包的词法辅助，相对本文件的真实路径为
# ../.agents/skills/laohu-inspection/scripts/video_prompt_lexing.py
# 路径按真实位置计算：仓库布局（本文件位于仓库根 scripts/）直接读取它，
# 渲染器不维护第二套词法；技能包被单独复制或上传时该辅助不在包内，此时按
# 同一规则启用下面的等价最小实现，不冒称共享辅助已经可用。
LEXING_TARGET = (
    Path(__file__).resolve().parent.parent
    / ".agents/skills/laohu-inspection/scripts/video_prompt_lexing.py"
)
LEXING_RELATIVE = os.path.relpath(LEXING_TARGET, Path(__file__).resolve().parent)
LEXING_PATH = Path(__file__).resolve().parent / LEXING_RELATIVE

FENCE_OPEN = re.compile(r"^ {0,3}(`{3,}|~{3,})([^\r\n]*)$")


@dataclass(frozen=True)
class LocalFence:
    """N04 FenceBlock 的同名等价记录，只用于共享辅助不可达的技能包副本。"""

    info: str
    text: str
    opening_line: int
    closing_line: int


class LocalLexError(ValueError):
    pass


def load_lexing(path: Path):
    if not path.is_file():
        return None
    spec = importlib_util.spec_from_file_location("laohu_video_prompt_lexing", path)
    if spec is None or spec.loader is None:
        return None
    module = importlib_util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


LEXING = load_lexing(LEXING_PATH)
# 共享辅助可达时统一使用它自己的异常类型；不可达时才用等价的本地异常。
LexError = LEXING.LexError if LEXING is not None else LocalLexError


def scan_fences(source: str) -> list:
    """与 N04 scan_fences 同规则、同口径的围栏读取入口。"""
    if LEXING is not None:
        return LEXING.scan_fences(source)
    return local_scan_fences(source)


def local_scan_fences(source: str) -> list[LocalFence]:
    """N04 scan_fences 的等价实现：同字符、结束不短于开始、较长外层围栏、未闭合即报错。"""
    lines = source.splitlines(keepends=True)
    result: list[LocalFence] = []
    active: tuple[str, int, str, int, int] | None = None
    offset = 0
    for number, raw_line in enumerate(lines, 1):
        line = raw_line.rstrip("\r\n")
        if active is None:
            match = FENCE_OPEN.fullmatch(line)
            if match:
                run, info = match.groups()
                if run[0] == "`" and "`" in info:
                    offset += len(raw_line)
                    continue
                active = (run[0], len(run), info.strip(), number, offset + len(raw_line))
        else:
            char, minimum, info, opening_line, start = active
            closing = re.fullmatch(r" {0,3}(" + re.escape(char) + r"+)\s*", line)
            if closing and len(closing[1]) >= minimum:
                end = offset
                if source[start:end].endswith("\r\n"):
                    end -= 2
                elif source[start:end].endswith("\n"):
                    end -= 1
                result.append(LocalFence(info, source[start:end], opening_line, number))
                active = None
        offset += len(raw_line)
    if active:
        raise LocalLexError(f"UNCLOSED_FENCE line={active[3]}")
    return result

DOMAIN_GROUPS: tuple[tuple[str, str, tuple[str, ...]], ...] = (
    ("PORTRAIT_REFERENCE", "人物主视觉图", ("F",)),
    ("BODY", "素体与阶段素体资产", ("B", "LZ", "P")),
    ("CLOTHING", "服装资产", ("W",)),
    ("STYLING", "妆造设计资产", ("M",)),
    ("PROP", "道具资产", ("A",)),
    ("SCENE", "场景资产", ("S",)),
    ("ENSEMBLE", "群像资产", ("G",)),
    ("BLOCKING", "镜头调度参考", ("C",)),
    ("VIDEO", "视频分段与提示词", ("BATCH", "VID")),
    ("STYLE", "风格定调图", ("STY",)),
    ("VISUAL_MASTER", "视觉母板", ("VMB",)),
    ("KEYFRAME", "关键帧", ("KF",)),
)


@dataclass(frozen=True)
class HeadingInfo:
    level: int
    text: str
    anchor: str
    domain_id: str | None = None
    domain_type: str | None = None


def slugify(text: str, used: set[str]) -> str:
    base = re.sub(r"[^\w\u3400-\u9fff-]+", "-", text, flags=re.UNICODE).strip("-").lower() or "section"
    candidate = base
    suffix = 2
    while candidate in used:
        candidate = f"{base}-{suffix}"
        suffix += 1
    used.add(candidate)
    return candidate


def domain_type(domain_id: str) -> str:
    if BATCH_ID.fullmatch(domain_id):
        return "BATCH"
    return re.match(r"[A-Z]+", domain_id).group(0)  # type: ignore[union-attr]


UNCLOSED_FENCE_LINE = re.compile(r"UNCLOSED_FENCE line=(\d+)")


def fence_layout(source: str, tolerant: bool = False) -> tuple[dict[int, object], set[int]]:
    """按 U22 同一规则读取围栏：同字符、结束不短于开始、0—3 空格缩进、CRLF、较长外层围栏。

    返回以 0 起算的起始行号到围栏块的映射，以及全部被围栏占用的行号集合；
    正文里较短的同形围栏不结束外层；未闭合围栏在 tolerant 模式下按词法辅助
    报出的起始行把剩余正文整体视为围栏，由正文渲染按卡片上下文拒绝。
    """
    try:
        blocks = scan_fences(source)
    except LexError as error:
        if not tolerant:
            raise
        match = UNCLOSED_FENCE_LINE.search(str(error))
        start = int(match.group(1)) - 1 if match else 0
        return {}, set(range(start, len(source.splitlines())))
    by_open: dict[int, object] = {}
    covered: set[int] = set()
    for block in blocks:
        by_open[block.opening_line - 1] = block
        covered.update(range(block.opening_line - 1, block.closing_line))
    return by_open, covered


def collect_headings(source: str) -> list[HeadingInfo]:
    headings: list[HeadingInfo] = []
    used_anchors: set[str] = set()
    used_domain_ids: set[str] = set()
    _, fenced_lines = fence_layout(source, tolerant=True)
    for line_index, line in enumerate(source.splitlines()):
        if line_index in fenced_lines:
            continue
        match = HEADING.match(line)
        if not match:
            continue
        level = len(match.group(1))
        text = match.group(2).strip()
        domain_match = DOMAIN_HEADING.match(text)
        current_id = domain_match.group("id") if domain_match else None
        if current_id:
            if not (domain_match.group("title") or "").strip():
                raise ValueError(f"missing domain title: {current_id}")
            if current_id in used_domain_ids:
                raise ValueError(f"duplicate domain id: {current_id}")
            used_domain_ids.add(current_id)
        headings.append(
            HeadingInfo(
                level=level,
                text=text,
                anchor=slugify(current_id or text, used_anchors),
                domain_id=current_id,
                domain_type=domain_type(current_id) if current_id else None,
            )
        )
    return headings


def domain_sort_key(domain_id: str) -> tuple[int, int, int, str]:
    batch_match = BATCH_ID.fullmatch(domain_id)
    if batch_match:
        return (
            int(batch_match.group("episode")),
            int(batch_match.group("scene")),
            int(batch_match.group("batch")),
            domain_id,
        )
    prefix_match = re.match(r"[A-Z]+", domain_id)
    number_match = re.search(r"\d+", domain_id)
    prefix = prefix_match.group(0) if prefix_match else domain_id
    number = int(number_match.group(0)) if number_match else 0
    subtype_order = {"B": 0, "LZ": 1, "P": 2}
    return 0, subtype_order.get(prefix, 0), number, domain_id


def card_plain_text(card: str) -> str:
    # 先剥离真实 HTML 结构，再还原用户文本：若先解码，用户字面标签
    # （如 <d>、<Audio 1>、<纸张摩擦声>）会被当成 HTML 一并剥掉。
    return html.unescape(re.sub(r"<[^>]+>", "", card))


def group_domain_cards(rendered_body: str) -> str:
    """Move domain cards into stable workflow groups without changing Markdown."""
    cards = RESULT_CARD.findall(rendered_body)
    if not cards:
        return rendered_body

    parsed_cards: list[tuple[str, str, str]] = []
    for card in cards:
        id_match = re.search(r'data-asset-id="([^"]+)"', card)
        type_match = re.search(r'data-asset-type="([^"]+)"', card)
        if not id_match or not type_match:
            continue
        parsed_cards.append((id_match.group(1), type_match.group(1), card))

    grouped: dict[str, list[tuple[str, str]]] = {}
    for asset_id, asset_type, card in parsed_cards:
        grouped.setdefault(asset_type, []).append((asset_id, card))

    remaining = RESULT_CARD.sub("", rendered_body).rstrip()
    group_sections: list[str] = []
    consumed_types: set[str] = set()
    for group_key, label, member_types in DOMAIN_GROUPS:
        members: list[tuple[str, str]] = []
        for member_type in member_types:
            members.extend(grouped.get(member_type, []))
            consumed_types.add(member_type)
        if not members:
            continue
        members.sort(key=lambda item: domain_sort_key(item[0]))
        group_sections.append(
            f'<section class="asset-group" data-asset-group="{group_key}">'
            '<header class="asset-group-header">'
            f'<h2>{label}</h2><span>{len(members)} 项</span>'
            '</header>'
            f'<div class="asset-group-grid">{"".join(card for _, card in members)}</div>'
            '</section>'
        )

    unknown_members = [
        member
        for member_type, members in grouped.items()
        if member_type not in consumed_types
        for member in members
    ]
    if unknown_members:
        unknown_members.sort(key=lambda item: domain_sort_key(item[0]))
        group_sections.append(
            '<section class="asset-group" data-asset-group="OTHER">'
            '<header class="asset-group-header"><h2>其他资产</h2>'
            f'<span>{len(unknown_members)} 项</span></header>'
            f'<div class="asset-group-grid">{"".join(card for _, card in unknown_members)}</div>'
            '</section>'
        )

    return "\n".join(part for part in (remaining, *group_sections) if part)


def inline_markup(text: str) -> str:
    escaped = html.escape(text, quote=False)
    escaped = re.sub(r"`([^`]+)`", r"<code class=\"inline-code\">\1</code>", escaped)
    escaped = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", escaped)
    escaped = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', escaped)
    return escaped


def split_table_row(line: str) -> list[str]:
    stripped = line.strip().strip("|")
    return [cell.strip() for cell in stripped.split("|")]


def render_body(source: str, headings: Sequence[HeadingInfo]) -> str:
    lines = source.splitlines()
    output: list[str] = []
    notes: list[str] = []
    heading_index = 0
    card_level: int | None = None
    card_id: str | None = None
    card_has_prompt = False
    list_kind: str | None = None
    index = 0
    resolved_fences: dict[str, object] = {}

    def fences():
        """Reading the layout lazily keeps the card context in the unclosed-fence message."""
        if "layout" not in resolved_fences:
            try:
                resolved_fences["layout"] = fence_layout(source)
            except LexError as error:
                raise ValueError(f"unclosed code fence: {card_id or 'document'}") from error
        return resolved_fences["layout"]  # type: ignore[return-value]

    def emit(markup: str) -> None:
        """卡片正文说明与操作清单留在卡内，但不进入「复制提示词」取文本的代码模板。"""
        (notes if card_level is not None else output).append(markup)

    def close_list() -> None:
        nonlocal list_kind
        if list_kind:
            emit(f"</{list_kind}>")
            list_kind = None

    def close_card() -> None:
        nonlocal card_level, card_id, card_has_prompt
        close_list()
        if card_level is not None:
            if not card_has_prompt:
                raise ValueError(f"missing prompt body: {card_id}")
            if notes:
                output.append('<div class="card-notes">' + "".join(notes) + "</div>")
                notes.clear()
            output.append("</section>")
            card_level = None
            card_id = None
            card_has_prompt = False

    while index < len(lines):
        line = lines[index]
        heading_match = HEADING.match(line)
        if heading_match:
            close_list()
            info = headings[heading_index]
            heading_index += 1
            if card_level is not None and (info.level <= card_level or info.domain_id):
                close_card()
            if info.domain_id:
                card_level = info.level
                card_id = info.domain_id
                output.append(
                    f'<section class="result-card" id="{info.anchor}" '
                    f'data-asset-id="{info.domain_id}" data-asset-type="{info.domain_type}">'
                )
                output.append('<div class="card-rail">')
                output.append(f'<span class="asset-id">{info.domain_id}</span>')
                output.append(f'<span class="asset-kind">{info.domain_type}</span>')
                output.append("</div>")
            heading_anchor = f"{info.anchor}-title" if info.domain_id else info.anchor
            heading_class = ' class="card-title"' if info.domain_id else ""
            output.append(
                f'<h{info.level} id="{heading_anchor}"{heading_class}>{inline_markup(info.text)}</h{info.level}>'
            )
            index += 1
            continue

        block = fences()[0].get(index)
        if block is not None:
            close_list()
            language = block.info.strip() or "text"
            code_text = block.text
            if card_level is not None and language in {"text", "prompt"}:
                if not code_text.strip():
                    raise ValueError(f"missing prompt body: {card_id}")
                card_has_prompt = True
            label = "复制提示词" if language in {"text", "prompt"} else "复制代码"
            title_button = (
                '<button class="title-copy-button" type="button">复制标题</button>'
                if card_level is not None
                else ""
            )
            output.append(
                '<div class="copy-block">'
                f'<span class="prompt-format">{html.escape(language.upper())}</span>'
                '<div class="prompt-actions">'
                f'{title_button}'
                f'<button class="copy-button" type="button">{label}</button>'
                '<button class="detail-button" type="button">查看详情</button>'
                '</div>'
                f'<template class="prompt-source"><code class="language-{html.escape(language)}">{html.escape(code_text, quote=False)}</code></template>'
                '</div>'
            )
            index = block.closing_line
            continue

        if index + 1 < len(lines) and "|" in line and TABLE_DIVIDER.match(lines[index + 1]):
            close_list()
            headers = split_table_row(line)
            index += 2
            rows: list[list[str]] = []
            while index < len(lines) and "|" in lines[index] and lines[index].strip():
                rows.append(split_table_row(lines[index]))
                index += 1
            emit('<div class="table-scroll"><table><thead><tr>')
            for cell in headers:
                emit(f"<th>{inline_markup(cell)}</th>")
            emit("</tr></thead><tbody>")
            for row in rows:
                emit("<tr>")
                for cell in row:
                    emit(f"<td>{inline_markup(cell)}</td>")
                emit("</tr>")
            emit("</tbody></table></div>")
            continue

        bullet_match = re.match(r"^\s*[-*+]\s+(.+)$", line)
        ordered_match = re.match(r"^\s*\d+[.)]\s+(.+)$", line)
        if bullet_match or ordered_match:
            desired = "ul" if bullet_match else "ol"
            if list_kind != desired:
                close_list()
                list_kind = desired
                emit(f"<{desired}>")
            value = (bullet_match or ordered_match).group(1)  # type: ignore[union-attr]
            emit(f"<li>{inline_markup(value)}</li>")
            index += 1
            continue

        close_list()
        if not line.strip():
            index += 1
            continue
        if line.startswith("> "):
            emit(f"<blockquote>{inline_markup(line[2:])}</blockquote>")
            index += 1
            continue
        if re.match(r"^---+$", line.strip()):
            emit("<hr>")
            index += 1
            continue

        paragraph_lines = [line.strip()]
        index += 1
        while index < len(lines):
            candidate = lines[index]
            if not candidate.strip() or HEADING.match(candidate) or index in fences()[0]:
                break
            if re.match(r"^\s*[-*+]\s+", candidate) or re.match(r"^\s*\d+[.)]\s+", candidate):
                break
            if index + 1 < len(lines) and "|" in candidate and TABLE_DIVIDER.match(lines[index + 1]):
                break
            paragraph_lines.append(candidate.strip())
            index += 1
        emit(f"<p>{inline_markup(' '.join(paragraph_lines))}</p>")

    close_card()
    close_list()
    return "\n".join(output)


def page_css() -> str:
    return r"""
:root{--paper:#efede8;--panel:#fbfaf7;--ink:#252525;--muted:#77736c;--line:#d3cfc7;--accent:#9c3d32;--accent-dark:#742c25;--ok:#357447;--shadow:0 6px 18px rgba(39,35,29,.08)}
*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;color:var(--ink);background:var(--paper);font:13px/1.48 -apple-system,BlinkMacSystemFont,"PingFang SC","Microsoft YaHei",sans-serif}
.shell{display:grid;grid-template-columns:220px minmax(0,1fr);min-height:100vh}.sidebar{position:sticky;top:0;height:100vh;padding:18px 14px;border-right:1px solid var(--line);background:#e6e2da;overflow:auto}
.brand{font-size:10px;letter-spacing:.16em;color:var(--accent);font-weight:800}.sidebar h1{font-size:15px;line-height:1.35;margin:6px 0 10px}.source-note{font-size:10px;color:var(--muted);word-break:break-all}.search{width:100%;margin:12px 0 8px;border:1px solid var(--line);background:var(--panel);padding:7px 9px;border-radius:4px;font:inherit}.filters{display:flex;flex-wrap:wrap;gap:4px;margin-bottom:10px}.filter{border:1px solid var(--line);background:transparent;padding:3px 8px;border-radius:3px;color:var(--muted);cursor:pointer;font-size:11px}.filter.active,.filter:hover{background:var(--ink);border-color:var(--ink);color:white}.toc{list-style:none;padding:0;margin:10px 0}.toc li{border-top:1px solid rgba(86,80,71,.12);padding:4px 0}.toc a{color:var(--muted);text-decoration:none;font-size:11px}.toc a:hover{color:var(--accent)}
.content{width:100%;min-width:0;padding:22px 20px 72px}.document{max-width:none;display:grid;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));gap:10px;align-items:start}.document>:not(.result-card){grid-column:1/-1}.document>h1:first-child{font-size:20px;line-height:1.2;letter-spacing:-.015em;margin:0 0 2px}.document h2{font-size:14px;margin:12px 0 2px;border-bottom:1px solid var(--line);padding-bottom:5px}.document h3{font-size:13px}.document p{max-width:90ch;margin:6px 0}.document a{color:var(--accent)}blockquote{border-left:2px solid var(--accent);margin:8px 0;padding:6px 9px;background:rgba(255,255,255,.45)}
.asset-group{grid-column:1/-1;margin-top:8px}.asset-group-header{display:flex;align-items:baseline;gap:8px;margin-bottom:7px;border-bottom:1px solid var(--line)}.asset-group-header h2{margin:0;padding:0 0 5px;border:0;font-size:14px}.asset-group-header span{color:var(--muted);font-size:10px}.asset-group-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));gap:10px;align-items:start}
.result-card{position:relative;display:flex;flex-direction:column;min-height:128px;margin:0;padding:0 10px 10px;background:var(--panel);border:1px solid var(--line);box-shadow:var(--shadow);border-radius:5px;overflow:hidden}.result-card:hover{border-color:#a8a198}.result-card>.card-rail{display:flex;gap:6px;align-items:center;margin:0 -10px;padding:6px 10px;background:#343230;color:white;font-family:ui-monospace,SFMono-Regular,Menlo,monospace}.asset-id{font-size:12px;font-weight:800;letter-spacing:.05em}.asset-kind{font-size:9px;letter-spacing:.12em;color:#d8d2c9}.asset-status{margin-left:auto;padding:2px 5px;border:1px solid #c8bfae;border-radius:2px;color:#eee7da;font-size:9px}.retired-card{opacity:.62;background:#e7e3dc}.retired-card:hover{border-color:var(--line)}.result-card>.card-title{border:0;margin:9px 0 8px;padding:0;font-size:13px;line-height:1.38;font-weight:700}.result-card>:not(.card-rail):not(.card-title):not(.copy-block){display:none}.result-card>.card-notes{display:none}
.copy-block{display:flex;align-items:center;gap:7px;margin-top:auto;padding-top:5px}.prompt-format{margin-right:auto;color:var(--muted);font:700 9px/1 ui-monospace,SFMono-Regular,Menlo,monospace;letter-spacing:.1em}.prompt-actions{display:flex;gap:5px}.result-card .copy-block{display:block}.result-card .prompt-format{display:none}.result-card .prompt-actions{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:4px;width:100%}.copy-button,.title-copy-button,.detail-button,.dialog-button{border:1px solid var(--line);background:#fff;color:var(--ink);padding:6px 5px;border-radius:3px;cursor:pointer;white-space:nowrap;font:700 11px/1.1 inherit}.copy-button{background:var(--accent);border-color:var(--accent);color:white}.copy-button:hover{background:var(--accent-dark)}.title-copy-button:hover,.detail-button:hover,.dialog-button:hover{border-color:#918b82}.copy-button.copied,.title-copy-button.copied{background:var(--ok);border-color:var(--ok);color:white}.prompt-source{display:none}.inline-code{background:rgba(156,61,50,.10);color:#7f2e26;padding:1px 3px;border-radius:3px}.table-scroll{overflow:auto;margin:8px 0;border:1px solid var(--line)}table{width:100%;border-collapse:collapse;background:rgba(255,255,255,.38);font-size:12px}th,td{text-align:left;vertical-align:top;padding:6px 7px;border-bottom:1px solid var(--line);border-right:1px solid var(--line)}th{background:#ddd9d1;font-weight:700}hr{border:0;border-top:1px solid var(--line);margin:14px 0}.hidden-card,.hidden-group{display:none}.toast{position:fixed;right:18px;bottom:18px;z-index:30;background:#272522;color:#fff;padding:8px 11px;border-left:3px solid #84af89;box-shadow:var(--shadow);transform:translateY(150%);transition:.2s}.toast.show{transform:translateY(0)}
.prompt-dialog{width:min(1080px,94vw);height:min(88vh,920px);padding:0;border:1px solid #4a4641;border-radius:6px;background:#272522;color:#f7f2e9;box-shadow:0 28px 80px rgba(0,0,0,.35)}.prompt-dialog::backdrop{background:rgba(24,22,20,.72);backdrop-filter:blur(3px)}.dialog-shell{display:grid;grid-template-rows:auto minmax(0,1fr);height:100%}.dialog-toolbar{display:flex;align-items:center;gap:8px;padding:9px 11px;background:#37332f;border-bottom:1px solid #4d4842}.dialog-title{min-width:0;margin-right:auto;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;font-size:12px;font-weight:700}.dialog-button{background:#f1eee8}.dialog-button.primary{background:var(--accent);border-color:var(--accent);color:white}.detail-code{margin:0;padding:18px 20px;overflow:auto;white-space:pre-wrap;word-break:break-word;font:14px/1.75 ui-monospace,SFMono-Regular,Menlo,Consolas,monospace}
.detail-notes{padding:12px 20px 16px;border-top:1px solid #4d4842;background:#2d2925;color:#ded7cb;font-size:12px;line-height:1.62;overflow:auto;max-height:34vh}
.detail-notes .notes-head{margin:0 0 6px;color:#a49b8d;font-size:10px;letter-spacing:.12em;text-transform:uppercase}
.detail-notes>:last-child{margin-bottom:0}.detail-notes table{background:transparent;color:#ded7cb}.detail-notes th{background:#3b3733}.detail-notes a{color:#e0a49b}
.detail-notes h1,.detail-notes h2,.detail-notes h3{font-size:13px;color:#f2ece2;border-color:#4d4842}.detail-notes .inline-code{background:rgba(255,255,255,.10);color:#f0d9d4}
.portal-title{font-size:20px;line-height:1.25;margin:6px 0}.portal-intro{margin:0 0 14px;color:var(--muted)}.portal-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:10px}.portal-card{display:block;padding:12px;background:var(--panel);border:1px solid var(--line);color:var(--ink);text-decoration:none;box-shadow:var(--shadow)}.portal-card:hover{border-color:var(--accent)}.portal-card small{display:block;color:var(--muted);margin-top:5px;word-break:break-all}
@media(max-width:760px){.shell{display:block}.sidebar{position:sticky;z-index:10;height:auto;padding:10px 12px;border-right:0;border-bottom:1px solid var(--line)}.source-note,.toc{display:none}.sidebar h1{margin-bottom:6px}.search{margin:6px 0}.content{padding:14px 10px 60px}.document{grid-template-columns:repeat(auto-fill,minmax(210px,1fr));gap:8px}.document>h1:first-child{font-size:17px}.result-card{min-height:120px}.prompt-dialog{width:100vw;height:100vh;max-width:none;max-height:none;border:0;border-radius:0}.detail-code{padding:14px}}
"""


def page_script() -> str:
    return r"""
const toast=document.getElementById('toast');
const dialog=document.getElementById('prompt-dialog');
const detailTitle=document.getElementById('detail-title');
const detailCode=document.getElementById('detail-code');
const detailNotes=document.getElementById('detail-notes');
const detailCopy=document.getElementById('detail-copy');
function showToast(message){toast.textContent=message;toast.classList.add('show');window.setTimeout(()=>toast.classList.remove('show'),1500)}
async function copyText(text){
  if(navigator.clipboard&&navigator.clipboard.writeText){try{await navigator.clipboard.writeText(text);return}catch(error){}}
  const area=document.createElement('textarea');area.value=text;area.setAttribute('readonly','');area.style.position='fixed';area.style.opacity='0';document.body.appendChild(area);area.select();document.execCommand('copy');area.remove();
}
function getPromptText(block){const template=block.querySelector('.prompt-source');const code=template.content.querySelector('code');return code?.textContent||''}
function getPromptTitle(block){const card=block.closest('.result-card');return card?.querySelector('.card-title')?.textContent?.trim()||'提示词详情'}
document.querySelectorAll('.title-copy-button').forEach(button=>button.addEventListener('click',async()=>{const block=button.closest('.copy-block');await copyText(getPromptTitle(block));button.classList.add('copied');button.textContent='已复制';showToast('标题已复制');window.setTimeout(()=>{button.classList.remove('copied');button.textContent='复制标题'},1300)}));
document.querySelectorAll('.copy-button').forEach(button=>button.addEventListener('click',async()=>{const block=button.closest('.copy-block');await copyText(getPromptText(block));button.classList.add('copied');button.textContent='复制成功';showToast('提示词已复制');window.setTimeout(()=>{button.classList.remove('copied');button.textContent=button.dataset.original||'复制提示词'},1300)}));
document.querySelectorAll('.copy-button').forEach(button=>button.dataset.original=button.textContent);
document.querySelectorAll('.detail-button').forEach(button=>button.addEventListener('click',()=>{const block=button.closest('.copy-block');const card=button.closest('.result-card');const retired=card?.dataset.assetStatus==='retired';detailTitle.textContent=getPromptTitle(block);detailCode.textContent=getPromptText(block);const notes=card?.querySelector('.card-notes');detailNotes.innerHTML=notes?('<p class="notes-head">正文说明与操作清单</p>'+notes.innerHTML):'';detailNotes.hidden=!notes;detailCopy.hidden=retired;detailCopy.disabled=retired;dialog.showModal()}));
document.getElementById('detail-close')?.addEventListener('click',()=>dialog.close());
detailCopy?.addEventListener('click',async()=>{if(detailCopy.hidden||detailCopy.disabled)return;await copyText(detailCode.textContent);showToast('提示词已复制')});
dialog?.addEventListener('click',event=>{if(event.target===dialog)dialog.close()});
let activeFilter='ALL';const search=document.getElementById('search');
function applyFilters(){const query=(search?.value||'').trim().toLowerCase();document.querySelectorAll('.result-card').forEach(card=>{const type=card.dataset.assetType;const prompts=[...card.querySelectorAll('.copy-block')].map(getPromptText).join(' ');const searchable=(card.textContent+' '+prompts).toLowerCase();const matchesType=activeFilter==='ALL'||type===activeFilter;const matchesQuery=!query||searchable.includes(query);card.classList.toggle('hidden-card',!(matchesType&&matchesQuery))});document.querySelectorAll('.asset-group').forEach(group=>{const cards=[...group.querySelectorAll('.result-card')];group.classList.toggle('hidden-group',cards.length>0&&cards.every(card=>card.classList.contains('hidden-card')))})}
document.querySelectorAll('.filter').forEach(button=>button.addEventListener('click',()=>{document.querySelectorAll('.filter').forEach(item=>item.classList.remove('active'));button.classList.add('active');activeFilter=button.dataset.filter;applyFilters()}));
search?.addEventListener('input',applyFilters);
"""


def render_page(source: str, source_path: Path) -> str:
    headings = collect_headings(source)
    title = next((item.text for item in headings if item.level == 1), source_path.stem)
    body = group_domain_cards(render_body(source, headings))
    types = sorted({item.domain_type for item in headings if item.domain_type})
    filters = ['<button class="filter active" type="button" data-filter="ALL">全部</button>']
    filters.extend(f'<button class="filter" type="button" data-filter="{kind}">{kind}</button>' for kind in types)
    toc = "".join(
        f'<li class="toc-level-{item.level}"><a href="#{item.anchor}">{html.escape(item.text)}</a></li>'
        for item in headings
        if item.level <= 3
    )
    digest = hashlib.sha256(source.encode("utf-8")).hexdigest()
    return f"""<!doctype html>
<html lang="zh-CN" data-source-sha256="{digest}">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{html.escape(title)}</title><style>{page_css()}</style></head>
<body><div class="shell"><aside class="sidebar"><div class="brand">LAOHU / DELIVERY</div><h1>{html.escape(title)}</h1><div class="source-note">唯一内容源<br>{html.escape(source_path.name)}</div><input id="search" class="search" type="search" placeholder="搜索编号、标题或提示词"><div class="filters">{''.join(filters)}</div><ul class="toc">{toc}</ul></aside><main class="content"><article class="document">{body}</article></main></div><dialog id="prompt-dialog" class="prompt-dialog"><div class="dialog-shell"><div class="dialog-toolbar"><span id="detail-title" class="dialog-title">提示词详情</span><button id="detail-copy" class="dialog-button primary" type="button">复制提示词</button><button id="detail-close" class="dialog-button" type="button">关闭</button></div><pre id="detail-code" class="detail-code"></pre><div id="detail-notes" class="detail-notes" hidden></div></div></dialog><div id="toast" class="toast" role="status">复制成功</div><script>{page_script()}</script></body></html>"""


def render_markdown(
    source_path: Path,
    output_path: Path | None = None,
) -> str:
    source_path = Path(source_path)
    source = source_path.read_text(encoding="utf-8")
    rendered = render_page(source, source_path)
    if output_path is not None:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(rendered, encoding="utf-8")
    return rendered


def render_portal(project_root: Path, pages: Sequence[Path]) -> str:
    cards: list[str] = []
    for page in sorted(pages, key=lambda item: str(item)):
        relative = page.relative_to(project_root).as_posix()
        label = page.stem
        cards.append(f'<a class="portal-card" href="{html.escape(relative, quote=True)}"><strong>{html.escape(label)}</strong><small>{html.escape(relative)}</small></a>')
    title = f"{project_root.name} · 作品交付中心"
    return f"""<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{html.escape(title)}</title><style>{page_css()}</style></head><body><main class="content" style="width:min(1180px,100%);margin:auto"><div class="brand">LAOHU / PROJECT DELIVERY</div><h1 class="portal-title">{html.escape(title)}</h1><p class="portal-intro">选择阶段交付页，进入后可按编号查找并一键复制。</p><div class="portal-grid">{''.join(cards)}</div></main></body></html>"""


def render_project(project_root: Path) -> list[Path]:
    project_root = Path(project_root)
    if not project_root.is_dir():
        raise FileNotFoundError(f"missing project directory: {project_root}")
    markdown_files = sorted(
        path for path in project_root.rglob("*.md") if not any(part.startswith(".") or part == "__pycache__" for part in path.relative_to(project_root).parts)
    )
    # Compile the entire project before touching any delivery file.
    compiled = {source.with_suffix(".html"): render_markdown(source) for source in markdown_files}
    pages = list(compiled)
    portal_path = project_root / "00_作品交付中心.html"
    compiled[portal_path] = render_portal(project_root, pages)
    write_project_pages(compiled)
    pages.append(portal_path)
    return pages


def write_project_pages(compiled: dict[Path, str]) -> None:
    """Stage pages and restore replacements on caught I/O failures, best effort.

    Each replacement is atomic on its filesystem; the whole project is not a
    crash-safe transaction. Failed rollback backups are retained for recovery.
    """
    staged: dict[Path, Path] = {}
    backups: dict[Path, Path | None] = {}
    temporary_paths: set[Path] = set()
    retained_backups: set[Path] = set()
    replaced: list[Path] = []

    def temporary_file(target: Path) -> Path:
        with tempfile.NamedTemporaryFile(prefix=".delivery-", dir=target.parent, delete=False) as handle:
            path = Path(handle.name)
            temporary_paths.add(path)
        return path

    try:
        for target, content in compiled.items():
            staged[target] = temporary_file(target)
            staged[target].write_text(content, encoding="utf-8")
            backups[target] = None
            if target.exists():
                backups[target] = temporary_file(target)
                shutil.copy2(target, backups[target])
        for target, stage in staged.items():
            stage.replace(target)
            replaced.append(target)
    except OSError as error:
        rollback_errors: list[str] = []
        for target in reversed(replaced):
            backup = backups[target]
            try:
                if backup is None:
                    target.unlink()
                else:
                    backup.replace(target)
            except OSError as rollback_error:
                if backup is not None:
                    retained_backups.add(backup)
                rollback_errors.append(f"{target}: {rollback_error}; backup={backup}")
        if rollback_errors:
            raise OSError(f"{error}; rollback incomplete: {'; '.join(rollback_errors)}") from error
        raise
    finally:
        for path in temporary_paths - retained_backups:
            try:
                path.unlink(missing_ok=True)
            except OSError as cleanup_error:
                print(f"WARNING: cannot remove temporary file {path}: {cleanup_error}", file=sys.stderr)


def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("source", nargs="?", type=Path, help="Markdown source file")
    group.add_argument("--project", type=Path, help="Render all Markdown files below a work directory")
    parser.add_argument("--output", type=Path, help="Output HTML path for single-file mode")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    try:
        if args.project:
            outputs = render_project(args.project)
        else:
            source = args.source.resolve()
            output = (args.output or source.with_suffix(".html")).resolve()
            render_markdown(source, output_path=output)
            outputs = [output]
    except (OSError, ValueError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1
    for output in outputs:
        print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
