#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
VALIDATOR="$ROOT/skills/laohu-video-prompt/scripts/validate_video_prompt_structure.sh"
fixture_valid="$(mktemp)"
fixture_valid_complex="$(mktemp)"
fixture_timeline="$(mktemp)"
fixture_no_shot="$(mktemp)"
fixture_missing_section="$(mktemp)"
fixture_direct_negative="$(mktemp)"
fixture_author_explanation="$(mktemp)"
fixture_director_intent="$(mktemp)"
fixture_contrastive_explanation="$(mktemp)"
fixture_ambiguous_focus="$(mktemp)"
fixture_detached_dialogue="$(mktemp)"
fixture_weak_shot_header="$(mktemp)"
fixture_weak_shot_body="$(mktemp)"
fixture_portrait_reference="$(mktemp)"
fixture_portrait_reference_alias="$(mktemp)"
fixture_portrait_reference_plain="$(mktemp)"
trap 'rm -f "$fixture_valid" "$fixture_valid_complex" "$fixture_timeline" "$fixture_no_shot" "$fixture_missing_section" "$fixture_direct_negative" "$fixture_author_explanation" "$fixture_director_intent" "$fixture_contrastive_explanation" "$fixture_ambiguous_focus" "$fixture_detached_dialogue" "$fixture_weak_shot_header" "$fixture_weak_shot_body" "$fixture_portrait_reference" "$fixture_portrait_reference_alias" "$fixture_portrait_reference_plain"' EXIT

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
  '固定中近景先看见孩子仍盯着桌边的母亲；母亲说完关键词后，孩子约0.4秒才移开目光，肩线随吸气抬起又落下，椅脚轻响成为唯一同期动作声。焦平面始终锁在双眼，母亲肩部保持低对比前景；孩子最后看向门口，结束构图至少保持0.8秒。'

write_prompt "$fixture_valid_complex" \
  '【镜头01｜中景→近景→全景｜左下低位→右前方平视｜向右横移并旋转上摇→绕过肩线→后撤拉远停稳｜构图：右下受压→中央接触→左侧余韵｜节奏：辨认停顿→移动加速→结果停稳】' \
  '中景先看见女孩站在大厅右下方，近前景门框压住她半边肩线；听到画外脚步后，她抬头，摄影机从左下低位向右横移并缓慢上摇，绕过肩线时进入双眼近景。她向后退开，摄影机沿同一路线后撤拉远，门框退出前景，大厅立柱和出口依次进入背景；女孩最终停在画面左侧，完整大厅在右侧展开，远处脚步回声衰减，结束构图保持稳定。'

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

write_prompt "$fixture_director_intent" \
  '【镜头01｜近景｜平视｜固定机位】' \
  '戏剧任务：孩子必须用沉默承担家庭压力。'

write_prompt "$fixture_contrastive_explanation" \
  '【镜头01｜近景｜平视｜固定机位】' \
  '这不是礼貌进食，而是一次必须完成的任务。'

write_prompt "$fixture_ambiguous_focus" \
  '【镜头01｜近景｜平视｜固定机位】' \
  '焦点从手抬到她失去办法的眼神。'

write_prompt "$fixture_detached_dialogue" \
  '【镜头01｜近景｜平视｜固定机位】' \
  '孩子抬眼看向妈妈。【台词-D1】孩子：“我要救爸爸。”'

write_prompt "$fixture_weak_shot_header" \
  '【镜头01｜孩子决定出发】' \
  '孩子抬眼看向妈妈，随后跑出房间。'

write_prompt "$fixture_weak_shot_body" \
  '【镜头01｜近景｜平视｜固定机位】' \
  '孩子抬头。'

write_prompt "$fixture_portrait_reference" \
  '【镜头01｜近景｜平视｜固定机位】' \
  '【写真参考@F01】锁定人物面孔，孩子抬头看向妈妈。'

write_prompt "$fixture_portrait_reference_alias" \
  '【镜头01｜近景｜平视｜固定机位】' \
  '【人物参考@F01】锁定人物面孔，孩子抬头看向妈妈。'

write_prompt "$fixture_portrait_reference_plain" \
  '【镜头01｜近景｜平视｜固定机位】' \
  '引用F01人物写真，孩子抬头看向妈妈。'

printf '%s\n' \
  '```text' \
  '【基础设定】' \
  '总时长8秒。' \
  '【画面内容】' \
  '【镜头01｜近景｜平视｜固定机位】' \
  '孩子抬头。' \
  '```' > "$fixture_missing_section"

"$VALIDATOR" "$fixture_valid" --limit 10000 >/dev/null
"$VALIDATOR" "$fixture_valid_complex" --limit 10000 >/dev/null

default_output="$("$VALIDATOR" "$fixture_valid")"
printf '%s\n' "$default_output" | rg -q '^block=1 chars=[0-9]+ limit=none shots=1 status=PASS$'

for invalid in "$fixture_timeline" "$fixture_no_shot" "$fixture_missing_section" "$fixture_direct_negative" "$fixture_author_explanation" "$fixture_director_intent" "$fixture_contrastive_explanation" "$fixture_ambiguous_focus" "$fixture_detached_dialogue" "$fixture_weak_shot_header" "$fixture_weak_shot_body" "$fixture_portrait_reference" "$fixture_portrait_reference_alias" "$fixture_portrait_reference_plain"; do
  if "$VALIDATOR" "$invalid" --limit 10000 >/dev/null 2>&1; then
    printf 'expected invalid prompt structure to fail: %s\n' "$invalid" >&2
    exit 1
  fi
done

printf 'validate_video_prompt_structure tests passed\n'
