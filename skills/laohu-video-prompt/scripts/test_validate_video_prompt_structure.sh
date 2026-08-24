#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
VALIDATOR="$ROOT/skills/laohu-video-prompt/scripts/validate_video_prompt_structure.sh"
fixture_valid="$(mktemp)"
fixture_timeline="$(mktemp)"
fixture_no_shot="$(mktemp)"
fixture_missing_section="$(mktemp)"
fixture_direct_negative="$(mktemp)"
fixture_author_explanation="$(mktemp)"
trap 'rm -f "$fixture_valid" "$fixture_timeline" "$fixture_no_shot" "$fixture_missing_section" "$fixture_direct_negative" "$fixture_author_explanation"' EXIT

write_prompt() {
  local target="$1"
  local shot_line="$2"
  local body_line="$3"
  printf '%s\n' \
  '# 测试文件' \
  '```text' \
  '【基础设定】' \
  '总时长8秒；文生视频；声音轨仅由对白、同期动作声和环境声组成。' \
    '【场景状态与氛围画质】' \
    '室内自然光，真实生活质感。' \
    '【画面内容】' \
    "$shot_line" \
    "$body_line" \
    '```' > "$target"
}

write_prompt "$fixture_valid" \
  '【镜头01｜中近景｜平视侧面｜固定机位】' \
  '孩子听到关键词后约0.4秒才移开目光，动作在2秒内完成，结束构图至少保持0.8秒。'

write_prompt "$fixture_timeline" \
  '【反应｜0—2秒】' \
  '孩子抬头。'

write_prompt "$fixture_no_shot" \
  '【反应】' \
  '孩子抬头。'

write_prompt "$fixture_direct_negative" \
  '【镜头01｜近景｜平视｜固定机位】' \
  '孩子抬头；不生成BGM，不新增路人。'

write_prompt "$fixture_author_explanation" \
  '【镜头01｜近景｜平视｜固定机位】' \
  '孩子抬头，让观众明白他已经下定决心。'

printf '%s\n' \
  '```text' \
  '【基础设定】' \
  '总时长8秒。' \
  '【画面内容】' \
  '【镜头01｜近景｜平视｜固定机位】' \
  '孩子抬头。' \
  '```' > "$fixture_missing_section"

"$VALIDATOR" "$fixture_valid" --limit 10000 >/dev/null

for invalid in "$fixture_timeline" "$fixture_no_shot" "$fixture_missing_section" "$fixture_direct_negative" "$fixture_author_explanation"; do
  if "$VALIDATOR" "$invalid" --limit 10000 >/dev/null 2>&1; then
    printf 'expected invalid prompt structure to fail: %s\n' "$invalid" >&2
    exit 1
  fi
done

printf 'validate_video_prompt_structure tests passed\n'
