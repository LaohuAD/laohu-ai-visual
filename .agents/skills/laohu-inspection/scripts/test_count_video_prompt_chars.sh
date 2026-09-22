#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COUNTER="$ROOT/count_video_prompt_chars.sh"
work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT

fixture="$work/two_prompts.md"
fixture_raw="$work/raw_payload.md"
fixture_crlf="$work/crlf.md"
fixture_tilde="$work/tilde.md"
fixture_outer="$work/outer_fence.md"
fixture_unclosed="$work/unclosed.md"
fixture_none="$work/no_prompt.md"

expect_usage_error() {
  local label="$1"
  shift
  local status=0
  "$@" >/dev/null 2>&1 || status=$?
  if [[ $status -ne 2 ]]; then
    printf 'expected parameter or file error with exit 2: %s (exit=%s)\n' "$label" "$status" >&2
    exit 1
  fi
}

printf '%s\n' \
  '# 测试文件' \
  '```text' \
  '不是正式提示词' \
  '```' \
  '```text' \
  '【基础设定】' \
  'A中' \
  '【场景状态与氛围画质】' \
  'B' \
  '【画面内容】' \
  'C🙂' \
  '```' \
  '```text' \
  '【基础设定】' \
  'A中' \
  '【场景状态与氛围画质】' \
  'B' \
  '【画面内容】' \
  'C🙂' \
  '```' > "$fixture"

output="$($COUNTER "$fixture" --limit 33)"
printf '%s\n' "$output" | grep -qE '^block=1 chars=33 limit=33 status=PASS$'
[[ "$(printf '%s\n' "$output" | wc -l | tr -d ' ')" == "2" ]]

info_output="$($COUNTER "$fixture" --block 1)"
printf '%s\n' "$info_output" | grep -qE '^block=1 chars=33 limit=none status=INFO$'

second_output="$($COUNTER "$fixture" --limit 33 --block 2)"
printf '%s\n' "$second_output" | grep -qE '^block=2 chars=33 limit=33 status=PASS$'

if "$COUNTER" "$fixture" --limit 32 >/dev/null 2>&1; then
  printf 'expected over-limit check to fail\n' >&2
  exit 1
fi
limit_status=0
"$COUNTER" "$fixture" --limit 32 >/dev/null 2>&1 || limit_status=$?
[[ "$limit_status" == "1" ]]

# 冻结载荷里的标点、空格、表情符号和花括号都保留，且只统计原始选中提示词。
raw_body='他说：{钥匙留在这里。} 随后停住 🙂  “留”'
raw_lines=('【基础设定】' '总时长8秒。' '【场景状态与氛围画质】' '室内。' '【画面内容】' '【C01｜近景｜平视｜固定机位】')
expected_raw="$(python3 -c 'import sys; print(len("\n".join(sys.argv[1:])))' "${raw_lines[@]}" "$raw_body")"
{
  printf '%s\n' '# 测试文件' '```text'
  printf '%s\n' '这一段是执行卡的内部说明，长度明显超过正式提示词，不应计入统计口径。' \
    '这一段是执行卡的内部说明，长度明显超过正式提示词，不应计入统计口径。' \
    '这一段是执行卡的内部说明，长度明显超过正式提示词，不应计入统计口径。'
  printf '%s\n' '```' '```text'
  printf '%s\n' "${raw_lines[@]}"
  printf '%s\n' "$raw_body"
  printf '%s\n' '```'
} > "$fixture_raw"
raw_output="$($COUNTER "$fixture_raw")"
printf '%s\n' "$raw_output" | grep -qE "^block=1 chars=${expected_raw} limit=none status=INFO$"

# CRLF 只在换行规范化时向调用者说明计数口径。
{ printf '%s\r\n' '```text'; printf '%s\r\n' "${raw_lines[@]}"; printf '%s\r\n' "$raw_body" '```'; } > "$fixture_crlf"
crlf_output="$($COUNTER "$fixture_crlf")"
printf '%s\n' "$crlf_output" | grep -qE '^note=counting_scope=raw-selected-prompt newline=normalized-LF$'
printf '%s\n' "$crlf_output" | grep -qE "^block=1 chars=${expected_raw} limit=none status=INFO$"

lf_output="$($COUNTER "$fixture_raw")"
if printf '%s\n' "$lf_output" | grep -qE '^note='; then
  printf 'LF input must not report newline normalization\n' >&2
  exit 1
fi

# 围栏规则与结构校验同源：波浪线、较长外层围栏都按一个正式块统计。
{ printf '%s\n' '~~~text'; printf '%s\n' "${raw_lines[@]}"; printf '%s\n' "$raw_body" '~~~'; } > "$fixture_tilde"
tilde_output="$($COUNTER "$fixture_tilde")"
printf '%s\n' "$tilde_output" | grep -qE "^block=1 chars=${expected_raw} limit=none status=INFO$"

{
  printf '%s\n' '````text'
  printf '%s\n' "${raw_lines[@]}"
  printf '%s\n' '```'
  printf '%s\n' '正文里这三条反引号短于外层四条，不结束外层围栏。'
  printf '%s\n' "$raw_body"
  printf '%s\n' '````'
} > "$fixture_outer"
outer_expected="$(python3 -c 'import sys; print(len("\n".join(sys.argv[1:])))' "${raw_lines[@]}" '```' '正文里这三条反引号短于外层四条，不结束外层围栏。' "$raw_body")"
outer_output="$($COUNTER "$fixture_outer")"
printf '%s\n' "$outer_output" | grep -qE "^block=1 chars=${outer_expected} limit=none status=INFO$"

printf '%s\n' '```text' '【基础设定】' '未闭合。' > "$fixture_unclosed"
printf '%s\n' '# 说明文件' '```text' '这里没有三段标题。' '```' > "$fixture_none"

expect_usage_error "unclosed fence" "$COUNTER" "$fixture_unclosed"
expect_usage_error "no formal prompt block" "$COUNTER" "$fixture_none"
expect_usage_error "missing file" "$COUNTER" "$work/absent.md"
expect_usage_error "no arguments" "$COUNTER"
expect_usage_error "unknown option" "$COUNTER" "$fixture" --profile seedance
expect_usage_error "bad limit" "$COUNTER" "$fixture" --limit 0
expect_usage_error "bad block" "$COUNTER" "$fixture" --block 0
expect_usage_error "block beyond file" "$COUNTER" "$fixture" --block 9

printf 'count_video_prompt_chars tests passed\n'
