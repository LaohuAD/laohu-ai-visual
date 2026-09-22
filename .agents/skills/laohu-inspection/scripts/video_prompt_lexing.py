#!/usr/bin/env python3
"""Read-only lexical checks for Laohu three-section prompts.

This module validates text structure, not screenplay truth, physical plausibility,
actual uploads, provider compatibility, or generated-media quality.
Python 3.10+, standard library only.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

HEADINGS = ("【基础设定】", "【场景状态与氛围画质】", "【画面内容】")
PROFILES = ("seedance", "h3", "kling")
FENCE_OPEN = re.compile(r"^ {0,3}(`{3,}|~{3,})([^\r\n]*)$")
SHOT = re.compile(r"^【(?:C|镜头)(\d{2,})｜([^\n】]+)】\s*$", re.M)
H3_REFERENCE = re.compile(r"<(Subject|Picture|Video|Audio) ([1-9]\d*)>")
SPEAKER = re.compile(r"\(S([1-9]\d*(?:,S[1-9]\d*)*)\)")
CHARACTER = re.compile(r"\[Character ([A-Z]+)\s*[:：]([^\]\n]+)\]")
FOREIGN_FIELD = re.compile(
    r"^(?:subject_definitions|summary|retention_analysis|detailed_description|"
    r"integrated_multimodal_description|overall_soundscape|non_diegetic_music)\s*:", re.M
)


@dataclass(frozen=True)
class FenceBlock:
    info: str
    text: str
    opening_line: int
    closing_line: int
    # Offsets refer to original Markdown; text excludes the newline before closing fence.
    start: int
    end: int


@dataclass(frozen=True)
class Span:
    start: int
    end: int
    kind: str
    payload: str


class LexError(ValueError):
    pass


def scan_fences(markdown: str) -> list[FenceBlock]:
    """Read fenced blocks without confusing a longer outer fence with an inner one."""
    lines = markdown.splitlines(keepends=True)
    result: list[FenceBlock] = []
    active: tuple[str, int, str, int, int] | None = None
    offset = 0
    for number, raw_line in enumerate(lines, 1):
        line = raw_line.rstrip("\r\n")
        if active is None:
            m = FENCE_OPEN.fullmatch(line)
            if m:
                run, info = m.groups()
                if run[0] == "`" and "`" in info:
                    offset += len(raw_line)
                    continue
                active = (run[0], len(run), info.strip(), number, offset + len(raw_line))
        else:
            char, minimum, info, opening_line, start = active
            closing = re.fullmatch(r" {0,3}(" + re.escape(char) + r"+)\s*", line)
            if closing and len(closing[1]) >= minimum:
                end = offset
                if markdown[start:end].endswith("\r\n"):
                    end -= 2
                elif markdown[start:end].endswith("\n"):
                    end -= 1
                result.append(FenceBlock(info, markdown[start:end], opening_line, number, start, end))
                active = None
        offset += len(raw_line)
    if active:
        raise LexError(f"UNCLOSED_FENCE line={active[3]}")
    return result


def _escaped(text: str, position: int) -> bool:
    n = 0
    position -= 1
    while position >= 0 and text[position] == "\\":
        n += 1
        position -= 1
    return bool(n % 2)


def payload_spans(text: str, profile: str) -> tuple[list[Span], list[str]]:
    """Locate opaque dialogue/literal payloads. Never edit or normalize their text."""
    if profile not in PROFILES:
        raise ValueError(f"unknown profile: {profile}")
    spans: list[Span] = []
    errors: list[str] = []
    pairs = {"“": "”", "「": "」", "『": "』", '"': '"', "〖": "〗"}
    i = 0
    while i < len(text):
        if text.startswith("<d>", i):
            end = text.find("</d>", i + 3)
            if end < 0:
                errors.append("UNCLOSED_DIALOGUE_TAG")
                break
            inner = text[i + 3:end]
            if "<d>" in inner:
                errors.append("DIALOGUE_DELIMITER_COLLISION")
            m = re.match(r"^\[([^\]\n]+)\]", inner)
            if not m:
                errors.append("MISSING_DIALOGUE_LANGUAGE")
                payload = inner
            else:
                # No strip: spaces and original punctuation belong to the payload.
                payload = inner[m.end():]
            if profile != "h3":
                errors.append("WRONG_PROFILE_DIALOGUE_TAG")
            spans.append(Span(i, end + 4, "dialogue", payload))
            i = end + 4
            continue
        if text.startswith("</d>", i):
            errors.append("ORPHAN_DIALOGUE_CLOSE")
            i += 4
            continue
        if text[i] == "{" and not _escaped(text, i):
            depth, j = 1, i + 1
            while j < len(text) and depth:
                if not _escaped(text, j):
                    depth += (text[j] == "{") - (text[j] == "}")
                j += 1
            if depth:
                errors.append("UNCLOSED_DIALOGUE_BRACE")
                break
            if profile != "seedance":
                errors.append("WRONG_PROFILE_DIALOGUE_BRACE")
            spans.append(Span(i, j, "dialogue", text[i + 1:j - 1]))
            i = j
            continue
        if text[i] == "}" and not _escaped(text, i):
            errors.append("ORPHAN_DIALOGUE_BRACE")
        if text[i] in pairs and not _escaped(text, i):
            close = pairs[text[i]]
            j = i + 1
            while j < len(text) and (text[j] != close or _escaped(text, j)):
                j += 1
            if j == len(text):
                errors.append("UNCLOSED_LITERAL")
                break
            spans.append(Span(i, j + 1, "literal", text[i + 1:j]))
            i = j + 1
            continue
        i += 1
    return spans, errors


def mask_spans(text: str, spans: list[Span]) -> str:
    """Replace opaque characters by spaces, preserving original offsets/newlines."""
    chars = list(text)
    for s in spans:
        if not (0 <= s.start <= s.end <= len(text)):
            raise ValueError("span outside text")
        for i in range(s.start, s.end):
            if chars[i] not in "\r\n":
                chars[i] = " "
    return "".join(chars)


def _angle_tokens(view: str) -> tuple[list[str], list[str]]:
    tokens, errors = [], []
    i = 0
    while i < len(view):
        if view[i] == "<":
            j = view.find(">", i + 1)
            if j < 0 or "\n" in view[i:j] or "<" in view[i + 1:j]:
                errors.append("MALFORMED_ANGLE_TOKEN")
                i += 1
                continue
            tokens.append(view[i:j + 1])
            i = j + 1
        elif view[i] == ">":
            errors.append("ORPHAN_ANGLE_CLOSE")
            i += 1
        else:
            i += 1
    return tokens, errors


def inspect_prompt(text: str, profile: str = "seedance", limit: int | None = None) -> dict:
    """Check one raw prompt. LEGAL SYNTAX does not imply reference/semantic closure."""
    if profile not in PROFILES:
        raise ValueError(f"unknown profile: {profile}")
    if limit is not None and (type(limit) is not int or limit < 1):
        raise ValueError("limit must be a positive integer")
    spans, errors = payload_spans(text, profile)
    view = mask_spans(text, spans)
    heading_matches = list(re.finditer(r"^(【[^\n】]+】)\s*$", view, re.M))
    positions: list[int] = []
    for h in HEADINGS:
        hits = [m.start() for m in heading_matches if m[1] == h]
        if len(hits) != 1:
            errors.append(f"HEADING_COUNT:{h}:{len(hits)}")
        positions.extend(hits)
    complete = len(positions) == 3 and all(sum(m[1] == h for m in heading_matches) == 1 for h in HEADINGS)
    if complete and positions != sorted(positions):
        errors.append("HEADING_ORDER")
    cuts = list(SHOT.finditer(view))
    if not cuts:
        errors.append("MISSING_SHOT_HEADER")
    for expected, match in enumerate(cuts, 1):
        if int(match[1]) != expected:
            errors.append(f"SHOT_SEQUENCE:{expected}:{match[1]}")
        fields = match[2].split("｜")
        if len(fields) < 3 or any(not f.strip() for f in fields):
            errors.append(f"SHOT_FIELDS:{match[1]}")
        if complete and positions == sorted(positions) and match.start() < positions[2]:
            errors.append("SHOT_OUTSIDE_PICTURE_SECTION")
    allowed_rail = re.compile(r"【(?:VFX|环境音|动作音|音乐(?:\s*/\s*节拍)?)(?:-[^】]+)?】")
    for m in heading_matches:
        h = m[1]
        if h in HEADINGS or SHOT.fullmatch(h) or allowed_rail.fullmatch(h):
            continue
        errors.append(f"UNRECOGNIZED_STRUCTURAL_HEADING:{h}")
    if FOREIGN_FIELD.search(view):
        errors.append("FOREIGN_TOP_LEVEL_SHELL")
    angle, angle_errors = _angle_tokens(view)
    errors.extend(angle_errors)
    h3_refs: list[str] = []
    for token in angle:
        if H3_REFERENCE.fullmatch(token):
            if profile != "h3":
                errors.append("WRONG_PROFILE_REFERENCE_TAG")
            h3_refs.append(token)
        elif token in {"<scenetrans>", "<cutoff>"}:
            if profile != "h3":
                errors.append("WRONG_PROFILE_CONTINUITY_TAG")
        elif profile != "seedance":
            errors.append(f"UNRECOGNIZED_ANGLE_TOKEN:{token}")
        elif not token[1:-1].strip():
            errors.append("EMPTY_SOUND_TOKEN")
    if profile != "h3" and SPEAKER.search(view):
        errors.append("WRONG_PROFILE_SPEAKER_ID")
    if profile != "kling" and CHARACTER.search(view):
        errors.append("WRONG_PROFILE_CHARACTER_TAG")
    if profile == "kling":
        defined = [m[1] for m in CHARACTER.finditer(view)]
        if len(defined) != len(set(defined)):
            errors.append("DUPLICATE_CHARACTER_DEFINITION")
        used = set(re.findall(r"(?<![A-Za-z])Character ([A-Z]+)(?![A-Za-z])", view))
        for label in sorted(used - set(defined)):
            errors.append(f"UNDEFINED_CHARACTER:{label}")
    # H3 input numbers can appear only as Subject sources; external mapping must
    # validate them, so repeated mention is NOT treated as duplicate definition.
    if limit is not None and len(text) > limit:
        errors.append(f"CHARACTER_LIMIT:{len(text)}:{limit}")
    errors = list(dict.fromkeys(errors))
    return {
        "profile": profile, "characters": len(text), "shots": len(cuts),
        "syntax_status": "FAIL" if errors else "PASS", "errors": errors,
        "payloads": [asdict(s) for s in spans], "h3_references": sorted(set(h3_refs)),
        "control_view": view,
        "reference_status": "NOT_CHECKED", "semantic_status": "NOT_CHECKED",
        "provider_status": "NOT_CHECKED", "media_status": "NOT_CHECKED",
    }


def inspect_markdown(markdown: str, profile: str = "seedance", limit: int | None = None,
                     block_indices: list[int] | None = None) -> list[dict]:
    """Explicit indices refer to all fences (1-based). Auto selects text/prompt
    fences and any fence with a real three-section heading. Selected malformed
    blocks cannot disappear merely because a heading is missing.
    """
    blocks = scan_fences(markdown)
    if block_indices is not None:
        if len(set(block_indices)) != len(block_indices) or any(i < 1 or i > len(blocks) for i in block_indices):
            raise LexError("INVALID_OR_DUPLICATE_BLOCK_INDEX")
        selected = [(i, blocks[i - 1]) for i in block_indices]
    else:
        selected = []
        for index, block in enumerate(blocks, 1):
            name = block.info.split()[0].lower() if block.info else ""
            spans, _ = payload_spans(block.text, profile)
            masked = mask_spans(block.text, spans)
            structural = any(re.search(r"^" + re.escape(h) + r"\s*$", masked, re.M) for h in HEADINGS)
            if name in {"text", "prompt"} or structural:
                selected.append((index, block))
    if not selected:
        raise LexError("NO_SELECTED_PROMPT_BLOCK")
    output = []
    for index, block in selected:
        result = inspect_prompt(block.text, profile, limit)
        result.update(block=index, opening_line=block.opening_line)
        output.append(result)
    return output


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("file", type=Path)
    p.add_argument("--profile", choices=PROFILES, default="seedance")
    p.add_argument("--limit", type=int)
    p.add_argument("--block", type=int, action="append")
    p.add_argument("--include-control-view", action="store_true")
    args = p.parse_args()
    try:
        data = inspect_markdown(args.file.read_text(encoding="utf-8"), args.profile, args.limit, args.block)
    except (OSError, UnicodeError, ValueError) as exc:
        print(json.dumps({"syntax_status": "ERROR", "message": str(exc)}, ensure_ascii=False))
        return 2
    if not args.include_control_view:
        for item in data:
            item.pop("control_view", None)
    print(json.dumps(data, ensure_ascii=False, indent=2))
    return 1 if any(r["syntax_status"] == "FAIL" for r in data) else 0


if __name__ == "__main__":
    raise SystemExit(main())
