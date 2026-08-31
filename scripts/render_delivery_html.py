#!/usr/bin/env python3
"""Compile work Markdown into self-contained, copy-friendly HTML delivery pages."""

from __future__ import annotations

import argparse
import hashlib
import html
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence


DOMAIN_HEADING = re.compile(r"^(?P<id>(?:VID|LZ|[BCFGPWMSA])\d+)(?:\s*[｜|]\s*(?P<title>.*))?$")
HEADING = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
FENCE = re.compile(r"^```([^`]*)$")
TABLE_DIVIDER = re.compile(r"^\s*\|?\s*:?-{3,}:?\s*(?:\|\s*:?-{3,}:?\s*)+\|?\s*$")
RESULT_CARD = re.compile(r'<section class="result-card"[^>]*>.*?</section>', re.S)

DOMAIN_GROUPS: tuple[tuple[str, str, tuple[str, ...]], ...] = (
    ("PORTRAIT_REFERENCE", "人物主视觉图", ("F",)),
    ("BODY", "素体与阶段素体资产", ("B", "LZ", "P")),
    ("CLOTHING", "服装资产", ("W",)),
    ("STYLING", "妆造设计资产", ("M",)),
    ("PROP", "道具资产", ("A",)),
    ("SCENE", "场景资产", ("S",)),
    ("ENSEMBLE", "群像资产", ("G",)),
    ("BLOCKING", "镜头调度参考", ("C",)),
    ("VIDEO", "视频提示词", ("VID",)),
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
    return re.match(r"[A-Z]+", domain_id).group(0)  # type: ignore[union-attr]


def collect_headings(source: str) -> list[HeadingInfo]:
    headings: list[HeadingInfo] = []
    used_anchors: set[str] = set()
    used_domain_ids: set[str] = set()
    in_fence = False
    for line in source.splitlines():
        if FENCE.match(line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        match = HEADING.match(line)
        if not match:
            continue
        level = len(match.group(1))
        text = match.group(2).strip()
        domain_match = DOMAIN_HEADING.match(text)
        current_id = domain_match.group("id") if domain_match else None
        if current_id:
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


def domain_sort_key(domain_id: str) -> tuple[int, int, str]:
    prefix_match = re.match(r"[A-Z]+", domain_id)
    number_match = re.search(r"\d+", domain_id)
    prefix = prefix_match.group(0) if prefix_match else domain_id
    number = int(number_match.group(0)) if number_match else 0
    subtype_order = {"B": 0, "LZ": 1, "P": 2}
    return subtype_order.get(prefix, 0), number, domain_id


def card_plain_text(card: str) -> str:
    return re.sub(r"<[^>]+>", "", html.unescape(card))


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
    heading_index = 0
    card_level: int | None = None
    list_kind: str | None = None
    index = 0

    def close_list() -> None:
        nonlocal list_kind
        if list_kind:
            output.append(f"</{list_kind}>")
            list_kind = None

    def close_card() -> None:
        nonlocal card_level
        close_list()
        if card_level is not None:
            output.append("</section>")
            card_level = None

    while index < len(lines):
        line = lines[index]
        heading_match = HEADING.match(line)
        if heading_match:
            close_list()
            info = headings[heading_index]
            heading_index += 1
            if card_level is not None and info.level <= card_level:
                close_card()
            if info.domain_id:
                card_level = info.level
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

        fence_match = FENCE.match(line)
        if fence_match:
            close_list()
            language = fence_match.group(1).strip() or "text"
            code_lines: list[str] = []
            index += 1
            while index < len(lines) and not FENCE.match(lines[index]):
                code_lines.append(lines[index])
                index += 1
            code_text = "\n".join(code_lines)
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
            index += 1
            continue

        if index + 1 < len(lines) and "|" in line and TABLE_DIVIDER.match(lines[index + 1]):
            close_list()
            headers = split_table_row(line)
            index += 2
            rows: list[list[str]] = []
            while index < len(lines) and "|" in lines[index] and lines[index].strip():
                rows.append(split_table_row(lines[index]))
                index += 1
            output.append('<div class="table-scroll"><table><thead><tr>')
            output.extend(f"<th>{inline_markup(cell)}</th>" for cell in headers)
            output.append("</tr></thead><tbody>")
            for row in rows:
                output.append("<tr>")
                output.extend(f"<td>{inline_markup(cell)}</td>" for cell in row)
                output.append("</tr>")
            output.append("</tbody></table></div>")
            continue

        bullet_match = re.match(r"^\s*[-*+]\s+(.+)$", line)
        ordered_match = re.match(r"^\s*\d+[.)]\s+(.+)$", line)
        if bullet_match or ordered_match:
            desired = "ul" if bullet_match else "ol"
            if list_kind != desired:
                close_list()
                list_kind = desired
                output.append(f"<{desired}>")
            value = (bullet_match or ordered_match).group(1)  # type: ignore[union-attr]
            output.append(f"<li>{inline_markup(value)}</li>")
            index += 1
            continue

        close_list()
        if not line.strip():
            index += 1
            continue
        if line.startswith("> "):
            output.append(f"<blockquote>{inline_markup(line[2:])}</blockquote>")
            index += 1
            continue
        if re.match(r"^---+$", line.strip()):
            output.append("<hr>")
            index += 1
            continue

        paragraph_lines = [line.strip()]
        index += 1
        while index < len(lines):
            candidate = lines[index]
            if not candidate.strip() or HEADING.match(candidate) or FENCE.match(candidate):
                break
            if re.match(r"^\s*[-*+]\s+", candidate) or re.match(r"^\s*\d+[.)]\s+", candidate):
                break
            if index + 1 < len(lines) and "|" in candidate and TABLE_DIVIDER.match(lines[index + 1]):
                break
            paragraph_lines.append(candidate.strip())
            index += 1
        output.append(f"<p>{inline_markup(' '.join(paragraph_lines))}</p>")

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
.result-card{position:relative;display:flex;flex-direction:column;min-height:128px;margin:0;padding:0 10px 10px;background:var(--panel);border:1px solid var(--line);box-shadow:var(--shadow);border-radius:5px;overflow:hidden}.result-card:hover{border-color:#a8a198}.result-card>.card-rail{display:flex;gap:6px;align-items:center;margin:0 -10px;padding:6px 10px;background:#343230;color:white;font-family:ui-monospace,SFMono-Regular,Menlo,monospace}.asset-id{font-size:12px;font-weight:800;letter-spacing:.05em}.asset-kind{font-size:9px;letter-spacing:.12em;color:#d8d2c9}.asset-status{margin-left:auto;padding:2px 5px;border:1px solid #c8bfae;border-radius:2px;color:#eee7da;font-size:9px}.retired-card{opacity:.62;background:#e7e3dc}.retired-card:hover{border-color:var(--line)}.result-card>.card-title{border:0;margin:9px 0 8px;padding:0;font-size:13px;line-height:1.38;font-weight:700}.result-card>:not(.card-rail):not(.card-title):not(.copy-block){display:none}
.copy-block{display:flex;align-items:center;gap:7px;margin-top:auto;padding-top:5px}.prompt-format{margin-right:auto;color:var(--muted);font:700 9px/1 ui-monospace,SFMono-Regular,Menlo,monospace;letter-spacing:.1em}.prompt-actions{display:flex;gap:5px}.result-card .copy-block{display:block}.result-card .prompt-format{display:none}.result-card .prompt-actions{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:4px;width:100%}.copy-button,.title-copy-button,.detail-button,.dialog-button{border:1px solid var(--line);background:#fff;color:var(--ink);padding:6px 5px;border-radius:3px;cursor:pointer;white-space:nowrap;font:700 11px/1.1 inherit}.copy-button{background:var(--accent);border-color:var(--accent);color:white}.copy-button:hover{background:var(--accent-dark)}.title-copy-button:hover,.detail-button:hover,.dialog-button:hover{border-color:#918b82}.copy-button.copied,.title-copy-button.copied{background:var(--ok);border-color:var(--ok);color:white}.prompt-source{display:none}.inline-code{background:rgba(156,61,50,.10);color:#7f2e26;padding:1px 3px;border-radius:3px}.table-scroll{overflow:auto;margin:8px 0;border:1px solid var(--line)}table{width:100%;border-collapse:collapse;background:rgba(255,255,255,.38);font-size:12px}th,td{text-align:left;vertical-align:top;padding:6px 7px;border-bottom:1px solid var(--line);border-right:1px solid var(--line)}th{background:#ddd9d1;font-weight:700}hr{border:0;border-top:1px solid var(--line);margin:14px 0}.hidden-card,.hidden-group{display:none}.toast{position:fixed;right:18px;bottom:18px;z-index:30;background:#272522;color:#fff;padding:8px 11px;border-left:3px solid #84af89;box-shadow:var(--shadow);transform:translateY(150%);transition:.2s}.toast.show{transform:translateY(0)}
.prompt-dialog{width:min(1080px,94vw);height:min(88vh,920px);padding:0;border:1px solid #4a4641;border-radius:6px;background:#272522;color:#f7f2e9;box-shadow:0 28px 80px rgba(0,0,0,.35)}.prompt-dialog::backdrop{background:rgba(24,22,20,.72);backdrop-filter:blur(3px)}.dialog-shell{display:grid;grid-template-rows:auto minmax(0,1fr);height:100%}.dialog-toolbar{display:flex;align-items:center;gap:8px;padding:9px 11px;background:#37332f;border-bottom:1px solid #4d4842}.dialog-title{min-width:0;margin-right:auto;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;font-size:12px;font-weight:700}.dialog-button{background:#f1eee8}.dialog-button.primary{background:var(--accent);border-color:var(--accent);color:white}.detail-code{margin:0;padding:18px 20px;overflow:auto;white-space:pre-wrap;word-break:break-word;font:14px/1.75 ui-monospace,SFMono-Regular,Menlo,Consolas,monospace}
.portal-title{font-size:20px;line-height:1.25;margin:6px 0}.portal-intro{margin:0 0 14px;color:var(--muted)}.portal-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:10px}.portal-card{display:block;padding:12px;background:var(--panel);border:1px solid var(--line);color:var(--ink);text-decoration:none;box-shadow:var(--shadow)}.portal-card:hover{border-color:var(--accent)}.portal-card small{display:block;color:var(--muted);margin-top:5px;word-break:break-all}
@media(max-width:760px){.shell{display:block}.sidebar{position:sticky;z-index:10;height:auto;padding:10px 12px;border-right:0;border-bottom:1px solid var(--line)}.source-note,.toc{display:none}.sidebar h1{margin-bottom:6px}.search{margin:6px 0}.content{padding:14px 10px 60px}.document{grid-template-columns:repeat(auto-fill,minmax(210px,1fr));gap:8px}.document>h1:first-child{font-size:17px}.result-card{min-height:120px}.prompt-dialog{width:100vw;height:100vh;max-width:none;max-height:none;border:0;border-radius:0}.detail-code{padding:14px}}
"""


def page_script() -> str:
    return r"""
const toast=document.getElementById('toast');
const dialog=document.getElementById('prompt-dialog');
const detailTitle=document.getElementById('detail-title');
const detailCode=document.getElementById('detail-code');
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
document.querySelectorAll('.detail-button').forEach(button=>button.addEventListener('click',()=>{const block=button.closest('.copy-block');const card=button.closest('.result-card');const retired=card?.dataset.assetStatus==='retired';detailTitle.textContent=getPromptTitle(block);detailCode.textContent=getPromptText(block);detailCopy.hidden=retired;detailCopy.disabled=retired;dialog.showModal()}));
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
<body><div class="shell"><aside class="sidebar"><div class="brand">LAOHU / DELIVERY</div><h1>{html.escape(title)}</h1><div class="source-note">唯一内容源<br>{html.escape(source_path.name)}</div><input id="search" class="search" type="search" placeholder="搜索编号、标题或提示词"><div class="filters">{''.join(filters)}</div><ul class="toc">{toc}</ul></aside><main class="content"><article class="document">{body}</article></main></div><dialog id="prompt-dialog" class="prompt-dialog"><div class="dialog-shell"><div class="dialog-toolbar"><span id="detail-title" class="dialog-title">提示词详情</span><button id="detail-copy" class="dialog-button primary" type="button">复制提示词</button><button id="detail-close" class="dialog-button" type="button">关闭</button></div><pre id="detail-code" class="detail-code"></pre></div></dialog><div id="toast" class="toast" role="status">复制成功</div><script>{page_script()}</script></body></html>"""


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
    pages: list[Path] = []
    for source_path in markdown_files:
        output_path = source_path.with_suffix(".html")
        render_markdown(source_path, output_path=output_path)
        pages.append(output_path)
    portal_path = project_root / "00_作品交付中心.html"
    portal_path.write_text(render_portal(project_root, pages), encoding="utf-8")
    pages.append(portal_path)
    return pages


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
