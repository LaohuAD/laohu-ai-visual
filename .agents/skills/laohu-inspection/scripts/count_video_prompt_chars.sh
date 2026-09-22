#!/usr/bin/env bash
# 正式视频提示词字符统计：只统计原始选中的提示词正文，不统计 JSON、HTML 转义后长度
# 或剥离标签后的长度。围栏与字面载荷范围由同目录 video_prompt_lexing.py 提供，
# 本文件不复制第二份已漂移的围栏解析。
set -euo pipefail

usage() {
  printf 'Usage: %s <markdown-file> [--limit N] [--block N]\n' "$(basename "$0")" >&2
  printf '  --block N selects the Nth formal prompt block (1-based among selected blocks)\n' >&2
  printf '  chars are counted as unicode code points of the raw prompt; CRLF is normalized to LF and reported\n' >&2
}

if [[ $# -lt 1 ]]; then
  usage
  exit 2
fi

file="$1"
shift
limit=""
block=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --limit)
      [[ $# -ge 2 && "$2" =~ ^[1-9][0-9]*$ ]] || { usage; exit 2; }
      limit="$2"
      shift 2
      ;;
    --block)
      [[ $# -ge 2 && "$2" =~ ^[1-9][0-9]*$ ]] || { usage; exit 2; }
      block="$2"
      shift 2
      ;;
    *)
      usage
      exit 2
      ;;
  esac
done

[[ -f "$file" ]] || { printf 'File not found: %s\n' "$file" >&2; exit 2; }

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LEXING="$ROOT/video_prompt_lexing.py"
[[ -f "$LEXING" ]] || { printf 'Missing lexical helper: %s\n' "$LEXING" >&2; exit 2; }

status=0
python3 - "$LEXING" "$file" "$limit" "$block" <<'PY' || status=$?
"""Count the raw text of every selected formal prompt block.

Selection keeps the legacy counting contract: only a fence that really carries all
three section headings is a formal prompt block, and --block N refers to the Nth
such block. Payload masking is used for heading detection only, never for the
counted text, so dialogue punctuation, spaces and emoji are all preserved.
"""
import re
import sys
from importlib import util as importlib_util
from pathlib import Path

HEADINGS = ("【基础设定】", "【场景状态与氛围画质】", "【画面内容】")


def load_lexing(path: str):
    spec = importlib_util.spec_from_file_location("laohu_video_prompt_lexing", path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load lexical helper: {path}")
    module = importlib_util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def main(argv):
    lexing_path, file_path, limit_raw, block_raw = argv
    lex = load_lexing(lexing_path)
    limit = int(limit_raw) if limit_raw else None
    try:
        # Read bytes, not text mode: universal-newline translation would hide
        # whether the file actually used CRLF, and the caller must be told.
        raw = Path(file_path).read_bytes().decode("utf-8")
    except (OSError, UnicodeError) as exc:
        print(f"Cannot read {file_path}: {exc}", file=sys.stderr)
        return 2
    # One counting rule for every caller: line endings are normalized before the
    # code-point count, and the caller is told whenever that normalization happened.
    source = raw.replace("\r\n", "\n").replace("\r", "\n")
    if source != raw:
        print("note=counting_scope=raw-selected-prompt newline=normalized-LF")
    try:
        blocks = lex.scan_fences(source)
    except lex.LexError:
        print(f"Unclosed code block found: {file_path}", file=sys.stderr)
        return 2

    prompt_blocks = []
    for item in blocks:
        spans, _ = lex.payload_spans(item.text, "seedance")
        masked = lex.mask_spans(item.text, spans)
        if all(re.search(r"^" + re.escape(h) + r"\s*$", masked, re.M) for h in HEADINGS):
            prompt_blocks.append(item.text)
    if not prompt_blocks:
        print(f"No formal video prompt text block found: {file_path}", file=sys.stderr)
        return 2

    selected = list(enumerate(prompt_blocks, 1))
    if block_raw:
        position = int(block_raw) - 1
        if position < 0 or position >= len(selected):
            print(f"Requested prompt block does not exist: {block_raw}", file=sys.stderr)
            return 2
        selected = [selected[position]]

    failed = 0
    for ordinal, text in selected:
        chars = len(text)
        shown_limit = "none"
        status = "INFO"
        if limit is not None:
            shown_limit = str(limit)
            status = "PASS" if chars <= limit else "FAIL"
            failed = 1 if status == "FAIL" else failed
        print(f"block={ordinal} chars={chars} limit={shown_limit} status={status}")
    return failed


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:5]))
PY
exit "$status"
