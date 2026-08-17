#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
COUNTER="$ROOT/skills/laohu-video-prompt/scripts/count_video_prompt_chars.sh"
fixture="$(mktemp)"
trap 'rm -f "$fixture"' EXIT

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
printf '%s\n' "$output" | rg -q '^block=1 chars=33 limit=33 status=PASS$'

second_output="$($COUNTER "$fixture" --limit 33 --block 2)"
printf '%s\n' "$second_output" | rg -q '^block=2 chars=33 limit=33 status=PASS$'

if "$COUNTER" "$fixture" --limit 32 >/dev/null 2>&1; then
  printf 'expected over-limit check to fail\n' >&2
  exit 1
fi

printf 'count_video_prompt_chars tests passed\n'
