#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VALIDATOR="$ROOT/validate_video_prompt_structure.sh"
work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT

fixture_valid="$work/valid.md"
fixture_valid_complex="$work/valid_complex.md"
fixture_timeline="$work/timeline.md"
fixture_no_shot="$work/no_shot.md"
fixture_missing_section="$work/missing_section.md"
fixture_direct_negative="$work/direct_negative.md"
fixture_author_explanation="$work/author_explanation.md"
fixture_director_intent="$work/director_intent.md"
fixture_contrastive_explanation="$work/contrastive_explanation.md"
fixture_ambiguous_focus="$work/ambiguous_focus.md"
fixture_detached_dialogue="$work/detached_dialogue.md"
fixture_weak_shot_header="$work/weak_shot_header.md"
fixture_weak_shot_body="$work/weak_shot_body.md"
fixture_portrait_reference="$work/portrait_reference.md"
fixture_portrait_reference_alias="$work/portrait_reference_alias.md"
fixture_portrait_reference_plain="$work/portrait_reference_plain.md"
fixture_f_frozen="$work/f_frozen.md"
fixture_f_substitute="$work/f_substitute.md"
fixture_intrashot_cut="$work/intrashot_cut.md"
fixture_compound_camera_setup="$work/compound_camera_setup.md"
fixture_music_policy="$work/music_policy.md"
fixture_frozen_ban="$work/frozen_ban.md"
fixture_aperture="$work/aperture.md"
fixture_many_shots="$work/many_shots.md"
fixture_tilde="$work/tilde.md"
fixture_long_outer_fence="$work/long_outer_fence.md"
fixture_crlf="$work/crlf.md"
fixture_two_blocks="$work/two_blocks.md"
fixture_two_blocks_bad="$work/two_blocks_bad.md"
fixture_card="$work/card.md"
fixture_card_incomplete_second="$work/card_incomplete_second.md"
fixture_card_without_block="$work/card_without_block.md"
fixture_absolute_time="$work/absolute_time.md"
fixture_timing_policy="$work/timing_policy.md"
fixture_timing_no_evidence="$work/timing_no_evidence.md"
fixture_unclosed="$work/unclosed.md"
fixture_seedance="$work/seedance.md"
fixture_h3="$work/h3.md"
fixture_kling="$work/kling.md"
fixture_kling_undefined="$work/kling_undefined.md"

BASIC='总时长8秒；文生视频；声音轨仅由对白、同期动作声和环境声组成。'
ATMOSPHERE='室内自然光，真实生活质感。'
SHOT_HEADER='【镜头01｜中近景｜平视侧面｜固定机位】'
SHOT_BODY='固定中近景先看见孩子仍盯着桌边的母亲；母亲说完关键词后，孩子约0.4秒才移开目光，肩线随吸气抬起又落下，椅脚轻响成为唯一同期动作声。焦平面始终锁在双眼，母亲肩部保持低对比前景；孩子最后看向门口，结束构图至少保持0.8秒。'

write_prompt() {
  local target="$1"
  local shot_line="$2"
  local body_line="$3"
  printf '%s\n' \
  '# 测试文件' \
  '```text' \
  '【基础设定】' \
  "$BASIC" \
    '【场景状态与氛围画质】' \
    "$ATMOSPHERE" \
    '【画面内容】' \
    "$shot_line" \
    "$body_line" \
    '```' > "$target"
}

write_prompt_full() {
  local target="$1"
  local basic="$2"
  local atmosphere="$3"
  local shot_line="$4"
  local body_line="$5"
  printf '%s\n' \
  '# 测试文件' \
  '```text' \
  '【基础设定】' \
  "$basic" \
    '【场景状态与氛围画质】' \
    "$atmosphere" \
    '【画面内容】' \
    "$shot_line" \
    "$body_line" \
    '```' > "$target"
}

expect_ok() {
  local label="$1"
  shift
  if ! "$@" >/dev/null 2>&1; then
    printf 'expected valid prompt to pass: %s\n' "$label" >&2
    exit 1
  fi
}

expect_fail() {
  local label="$1"
  shift
  local status=0
  "$@" >/dev/null 2>&1 || status=$?
  if [[ $status -ne 1 ]]; then
    printf 'expected structure failure with exit 1: %s (exit=%s)\n' "$label" "$status" >&2
    exit 1
  fi
}

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

# 冻结台词里的 F01 不是资产引用；正文以 F 资产替代正式视频输入仍然失败。
write_prompt "$fixture_f_frozen" \
  '【镜头01｜近景｜平视｜固定机位】' \
  '画面先看见孩子抬眼看向妈妈，随后他说：{用F01替代正式视频输入}，孩子最后停在门口。'

write_prompt "$fixture_f_substitute" \
  '【镜头01｜近景｜平视｜固定机位】' \
  '画面先看见孩子抬眼看向妈妈，随后以F01人物写真作为正式视频输入，孩子最后停在门口。'

write_prompt "$fixture_intrashot_cut" \
  '【镜头01｜驾驶员近景｜副驾驶侧平视｜固定机位】' \
  '画面先看见司机盯着后视镜，随后他按响喇叭，最后停在得意笑脸。画面硬切到车外大全景，车辆滑进泥沟并停住。'

write_prompt "$fixture_compound_camera_setup" \
  '【镜头01｜前挡风主观视角切车外大全景｜先车内正前方再切弯道外侧｜急进后硬切并横向跟摇】' \
  '画面先看见警示架逼近，司机随后急刹，车辆最后斜停在泥沟里。'

printf '%s\n' \
  '```text' \
  '【基础设定】' \
  '总时长8秒。' \
  '【画面内容】' \
  '【镜头01｜近景｜平视｜固定机位】' \
  '孩子抬头。' \
  '```' > "$fixture_missing_section"

# 有范围的音乐政策：基础设定内允许“不生成BGM”，不是无对象的负向禁令。
write_prompt_full "$fixture_music_policy" \
  '总时长8秒；文生视频；声音轨仅由对白、同期动作声和环境声组成，不生成BGM。' \
  "$ATMOSPHERE" \
  "$SHOT_HEADER" \
  "$SHOT_BODY"

# 冻结载荷里的禁令文字、结构标题字样和模型标签都不触发控制命令。
write_prompt "$fixture_frozen_ban" \
  '【镜头01｜近景｜平视｜固定机位】' \
  '画面先看见孩子抬眼看向妈妈，随后他说：{不要出现字幕，让观众自己看【基础设定】和<Audio 1>。} 孩子最后停在门口。'

# 摄影光圈 F1.4 不是 F 资产引用。
write_prompt "$fixture_aperture" \
  '【镜头01｜近景｜平视｜固定机位】' \
  '画面先看见孩子抬眼看向妈妈，随后摄影机收小到 F1.4 光圈，孩子的肩线随呼吸抬起又落下，最后停在门口。'

printf '%s\n' \
  '# 测试文件' \
  '```text' \
  '【基础设定】' \
  "$BASIC" \
  '【场景状态与氛围画质】' \
  "$ATMOSPHERE" \
  '【画面内容】' > "$fixture_many_shots"
index=1
while [[ $index -le 101 ]]; do
  printf '【C%02d｜近景｜平视｜固定机位】\n' "$index" >> "$fixture_many_shots"
  printf '%s\n' '画面先看见人物停住，随后听到门声，最后停在门上。' >> "$fixture_many_shots"
  index=$((index + 1))
done
printf '%s\n' '```' >> "$fixture_many_shots"

printf '%s\n' \
  '# 测试文件' \
  '~~~text' \
  '【基础设定】' \
  "$BASIC" \
  '【场景状态与氛围画质】' \
  "$ATMOSPHERE" \
  '【画面内容】' \
  "$SHOT_HEADER" \
  "$SHOT_BODY" \
  '~~~' > "$fixture_tilde"

printf '%s\n' \
  '# 测试文件' \
  '````text' \
  '【基础设定】' \
  "$BASIC" \
  '【场景状态与氛围画质】' \
  "$ATMOSPHERE" \
  '【画面内容】' \
  '```' \
  '正文里这三条反引号短于外层四条，不结束外层围栏。' \
  "$SHOT_HEADER" \
  "$SHOT_BODY" \
  '````' > "$fixture_long_outer_fence"

printf '%s\r\n' \
  '# 测试文件' \
  '```text' \
  '【基础设定】' \
  "$BASIC" \
  '【场景状态与氛围画质】' \
  "$ATMOSPHERE" \
  '【画面内容】' \
  "$SHOT_HEADER" \
  "$SHOT_BODY" \
  '```' > "$fixture_crlf"

printf '%s\n' \
  '# 测试文件' \
  '```text' \
  '【基础设定】' \
  "$BASIC" \
  '【场景状态与氛围画质】' \
  "$ATMOSPHERE" \
  '【画面内容】' \
  "$SHOT_HEADER" \
  "$SHOT_BODY" \
  '```' \
  '```text' \
  '【基础设定】' \
  "$BASIC" \
  '【场景状态与氛围画质】' \
  "$ATMOSPHERE" \
  '【画面内容】' \
  '【C01｜近景｜平视｜固定机位】' \
  '画面先看见人物停住，随后听到门声，最后停在门上。' \
  '```' > "$fixture_two_blocks"

printf '%s\n' \
  '# 测试文件' \
  '```text' \
  '【基础设定】' \
  "$BASIC" \
  '【场景状态与氛围画质】' \
  "$ATMOSPHERE" \
  '【画面内容】' \
  "$SHOT_HEADER" \
  "$SHOT_BODY" \
  '```' \
  '```text' \
  '【基础设定】' \
  "$BASIC" \
  '【场景状态与氛围画质】' \
  "$ATMOSPHERE" \
  '【画面内容】' \
  '【C01｜近景｜平视｜固定机位】' \
  '画面先看见人物停住，随后听到门声，最后停在门上。' \
  '```' \
  '```text' \
  '【基础设定】' \
  "$BASIC" \
  '【场景状态与氛围画质】' \
  "$ATMOSPHERE" \
  '```' > "$fixture_two_blocks_bad"

# 生产执行卡：卡内说明代码块不是提示词，只有真正带三段标题的块才提交。
printf '%s\n' \
  '# 执行单' \
  '' \
  '## E01-S02-P03｜双人交锋' \
  '' \
  '卡内说明（不提交）：' \
  '' \
  '```text' \
  '本卡片时长、镜头数与资产需求见分段卡，这段是执行卡内部说明。' \
  '```' \
  '' \
  '```text' \
  '【基础设定】' \
  "$BASIC" \
  '【场景状态与氛围画质】' \
  "$ATMOSPHERE" \
  '【画面内容】' \
  "$SHOT_HEADER" \
  "$SHOT_BODY" \
  '```' > "$fixture_card"

printf '%s\n' \
  '# 执行单' \
  '' \
  '## E01-S02-P01｜第一段' \
  '' \
  '```text' \
  '【基础设定】' \
  "$BASIC" \
  '【场景状态与氛围画质】' \
  "$ATMOSPHERE" \
  '【画面内容】' \
  "$SHOT_HEADER" \
  "$SHOT_BODY" \
  '```' \
  '' \
  '## E01-S02-P02｜第二段' \
  '' \
  '```text' \
  '【基础设定】' \
  "$BASIC" \
  '【场景状态与氛围画质】' \
  "$ATMOSPHERE" \
  '```' > "$fixture_card_incomplete_second"

printf '%s\n' \
  '# 执行单' \
  '' \
  '## E01-S02-P09｜待提交' \
  '' \
  '本卡片的正式提示词见下方。' > "$fixture_card_without_block"

write_prompt "$fixture_absolute_time" \
  "$SHOT_HEADER" \
  '画面先看见孩子抬眼看向妈妈；母亲说完后，同期动作声在0—1秒内出现。孩子最后停在门口，结束构图保持0.8秒。'

printf '%s\n' \
  '# 测试文件' \
  '' \
  'timing_policy: locked_audio' \
  'timing_evidence: 音频1 lin_voice.wav 已锁定真实时间码 00:00:12.480' \
  '' \
  '```text' \
  '【基础设定】' \
  "$BASIC" \
  '【场景状态与氛围画质】' \
  "$ATMOSPHERE" \
  '【画面内容】' \
  "$SHOT_HEADER" \
  '画面先看见孩子抬眼看向妈妈；母亲说完后，同期动作声在0—1秒内出现。孩子最后停在门口，结束构图保持0.8秒。' \
  '```' > "$fixture_timing_policy"

printf '%s\n' \
  '# 测试文件' \
  '' \
  'timing_policy: locked_audio' \
  '' \
  '```text' \
  '【基础设定】' \
  "$BASIC" \
  '【场景状态与氛围画质】' \
  "$ATMOSPHERE" \
  '【画面内容】' \
  "$SHOT_HEADER" \
  '画面先看见孩子抬眼看向妈妈；母亲说完后，同期动作声在0—1秒内出现。孩子最后停在门口，结束构图保持0.8秒。' \
  '```' > "$fixture_timing_no_evidence"

printf '%s\n' \
  '# 测试文件' \
  '```text' \
  '【基础设定】' \
  "$BASIC" \
  '【场景状态与氛围画质】' \
  "$ATMOSPHERE" \
  '【画面内容】' \
  "$SHOT_HEADER" \
  "$SHOT_BODY" > "$fixture_unclosed"

cat > "$fixture_seedance" <<'EOF'
# 测试文件
```text
【基础设定】
本段采用图生视频；@图片2是开场位置与构图参考，@图片1中的林和周分别提供已确认身份，不接管开场站位；@音频1仅参考林的音色和发声质地，不复用原台词或伴奏。林保持已确认的中低音区、偏干声线、清楚咬字；声音由对白、钥匙落桌声和室内底声组成，无配乐。

【场景状态与氛围画质】
方桌位于门前；林在画面左侧，右手握着钥匙，周在右侧，右手搭在尚未转动的门把上；两人都在门内。左后方窗光擦亮衣袖和桌面，门旁保持低亮；写实生活质感，柔和高光、可辨皮肤与布料纹理。

【画面内容】
林把同一把钥匙留在桌上，周听见这句话后停住开门动作，两人都没有离开。
【C01｜双人中景｜桌南侧朝北平视｜固定机位】
画面先看见林的右手仍握钥匙、周的右手停在门把上；林将钥匙放到桌面，指尖离开后才抬眼看向周。<钥匙接触木桌的短促轻响> 林用@音频1的音色低声说：{钥匙留在这里。} 重音轻落在“留”，句尾收住；周听到“这里”时压住原本准备下转的手腕，目光停在钥匙上。
【C02｜周的手与面部中近景｜仍在轴线南侧偏林肩后｜硬切，固定机位】
周的右手仍搭着未转动的门把，林的肩缘低对比地留在左前景；周的指尖先放松，目光随后从桌上的钥匙移回林的脸，肩线没有后退。室内底声持续，门没有打开，镜尾保留这次未完成的离开。
```
EOF

cat > "$fixture_h3" <<'EOF'
# 测试文件
```text
【基础设定】
本段采用首帧锚定；<Picture 2>控制开场位置与构图。<Subject 1>是<Picture 1>中的林，<Subject 2>是同图中的周，二者仅提供已确认身份，不接管开场站位；对应身份职责fully_preserved。<Audio 1>：林(S1)的音色与发声质地参考，reference；不复制原台词、伴奏或整条波形。林保持已确认的中低音区、偏干声线、清楚咬字；声音由对白、钥匙落桌声和室内底声组成，无配乐。

【场景状态与氛围画质】
方桌位于门前；林在画面左侧，右手握着钥匙，周在右侧，右手搭在尚未转动的门把上；两人都在门内。左后方窗光擦亮衣袖和桌面，门旁保持低亮；写实生活质感，柔和高光、可辨皮肤与布料纹理。

【画面内容】
林把同一把钥匙留在桌上，周听见这句话后停住开门动作，两人都没有离开。
【C01｜双人中景｜桌南侧朝北平视｜固定机位】
画面从<Picture 2>的开场状态开始：<Subject 1>右手仍握钥匙，<Subject 2>右手搭在门把上。林将钥匙放到桌面，指尖离开后才抬眼看向周，钥匙接触木桌发出短促轻响。<Subject 1>(S1)使用<Audio 1>的音色低声说：<d>[Chinese]钥匙留在这里。</d> 重音轻落在“留”，句尾收住；周听到“这里”时压住原本准备下转的手腕，目光停在钥匙上。
【C02｜周的手与面部中近景｜仍在轴线南侧偏林肩后｜硬切，固定机位】
<Subject 2>右手仍搭着未转动的门把，林的肩缘低对比地留在左前景；周的指尖先放松，目光随后从桌上的钥匙移回林的脸，肩线没有后退。室内底声持续，门没有打开，镜尾保留这次未完成的离开。
```
EOF

cat > "$fixture_kling" <<'EOF'
# 测试文件
```text
【基础设定】
本段采用图生视频；输入图片2控制开场位置与构图，输入图片1提供两人已确认身份，不接管站位。
[Character A: 林；沿用输入图片1中的林；中低音区、偏干声线、清楚咬字]
[Character B: 周；沿用输入图片1中的周；本段不发声]
输入音频1仅参考Character A的音色与发声质地，不复用原台词或伴奏；声音由对白、钥匙落桌声和室内底声组成，无配乐。

【场景状态与氛围画质】
方桌位于门前；林在画面左侧，右手握着钥匙，周在右侧，右手搭在尚未转动的门把上；两人都在门内。左后方窗光擦亮衣袖和桌面，门旁保持低亮；写实生活质感，柔和高光、可辨皮肤与布料纹理。

【画面内容】
Character A把同一把钥匙留在桌上，Character B听见这句话后停住开门动作，两人都没有离开。
【C01｜双人中景｜桌南侧朝北平视｜固定机位】
画面先看见Character A的右手仍握钥匙、Character B的右手搭在门把上；Character A将钥匙放到桌面，指尖离开后才抬眼看向Character B，钥匙接触木桌发出短促轻响。Character A参考输入音频1的音色，用普通话低声说：“钥匙留在这里。” 重音轻落在“留”，句尾收住；Character B听到“这里”时压住原本准备下转的手腕，目光停在钥匙上。
【C02｜周的手与面部中近景｜仍在轴线南侧偏林肩后｜硬切，固定机位】
Character B的右手仍搭着未转动的门把，Character A的肩缘低对比地留在左前景；Character B的指尖先放松，目光随后从桌上的钥匙移回Character A的脸，肩线没有后退。室内底声持续，门没有打开，镜尾保留这次未完成的离开。
```
EOF

sed 's/两人都没有离开。/两人都没有离开。 Character C站在门外。/' "$fixture_kling" > "$fixture_kling_undefined"

"$VALIDATOR" "$fixture_valid" --limit 10000 >/dev/null 2>&1
"$VALIDATOR" "$fixture_valid_complex" --limit 10000 >/dev/null 2>&1

default_output="$("$VALIDATOR" "$fixture_valid" 2>/dev/null)"
printf '%s\n' "$default_output" | grep -qE '^block=1 chars=[0-9]+ limit=none shots=1 status=PASS$'

# 词法通过只声明结构与分区检查；引用/语义/平台/媒体四项仍是 NOT_CHECKED。
boundary_output="$("$VALIDATOR" "$fixture_valid" 2>&1 >/dev/null)"
printf '%s\n' "$boundary_output" | grep -qE '^note=syntax_only reference=NOT_CHECKED semantic=NOT_CHECKED provider=NOT_CHECKED media=NOT_CHECKED$'
[[ "$(printf '%s\n' "$default_output" | wc -l | tr -d ' ')" == "1" ]]

for invalid in "$fixture_timeline" "$fixture_no_shot" "$fixture_missing_section" "$fixture_direct_negative" "$fixture_author_explanation" "$fixture_director_intent" "$fixture_contrastive_explanation" "$fixture_ambiguous_focus" "$fixture_detached_dialogue" "$fixture_weak_shot_header" "$fixture_weak_shot_body" "$fixture_portrait_reference" "$fixture_portrait_reference_alias" "$fixture_portrait_reference_plain" "$fixture_intrashot_cut" "$fixture_compound_camera_setup"; do
  expect_fail "$invalid" "$VALIDATOR" "$invalid" --limit 10000
done

# 原“直接负向”用例仍失败，并按真实不合格原因失败：新增路人禁令与极薄正文。
negative_output="$("$VALIDATOR" "$fixture_direct_negative" 2>&1 || true)"
printf '%s\n' "$negative_output" | grep -qE 'direct negative generation instruction found'
printf '%s\n' "$negative_output" | grep -qE 'missing triggered screen/sound change'
printf '%s\n' "$negative_output" | grep -qE 'missing visible/audible endpoint'

expect_ok "music policy in basic setup" "$VALIDATOR" "$fixture_music_policy"
expect_ok "frozen dialogue containing ban words" "$VALIDATOR" "$fixture_frozen_ban"
expect_ok "aperture F1.4 is not an F asset reference" "$VALIDATOR" "$fixture_aperture"
expect_ok "frozen dialogue keeps literal F01" "$VALIDATOR" "$fixture_f_frozen"
expect_fail "F asset replacing the formal video input" "$VALIDATOR" "$fixture_f_substitute"
expect_ok "more than 99 shots keep integer order" "$VALIDATOR" "$fixture_many_shots"
expect_ok "tilde fence" "$VALIDATOR" "$fixture_tilde"
expect_ok "long outer fence with shorter inner fence" "$VALIDATOR" "$fixture_long_outer_fence"

crlf_output="$("$VALIDATOR" "$fixture_crlf" 2>/dev/null)"
printf '%s\n' "$crlf_output" | grep -qE '^block=1 chars=[0-9]+ limit=none shots=1 status=PASS$'

many_output="$("$VALIDATOR" "$fixture_many_shots" 2>/dev/null)"
printf '%s\n' "$many_output" | grep -qE 'shots=101 status=PASS'

# 多块文件全部选中时逐块输出；任何一块失败总退出 1。
two_output="$("$VALIDATOR" "$fixture_two_blocks" 2>/dev/null)"
[[ "$(printf '%s\n' "$two_output" | wc -l | tr -d ' ')" == "2" ]]
printf '%s\n' "$two_output" | grep -qE '^block=1 chars=[0-9]+ limit=none shots=1 status=PASS$'
printf '%s\n' "$two_output" | grep -qE '^block=2 chars=[0-9]+ limit=none shots=1 status=PASS$'

expect_fail "second selected block is incomplete" "$VALIDATOR" "$fixture_two_blocks_bad"
bad_output="$("$VALIDATOR" "$fixture_two_blocks_bad" 2>&1 || true)"
printf '%s\n' "$bad_output" | grep -qE '^block=1 chars=[0-9]+ limit=none shots=1 status=PASS$'
printf '%s\n' "$bad_output" | grep -qE '^block=3 chars=[0-9]+ limit=none shots=0 status=FAIL'

# 生产文档按 E-S-P 卡片选块：卡内说明代码块不当作提示词。
card_output="$("$VALIDATOR" "$fixture_card" 2>/dev/null)"
[[ "$(printf '%s\n' "$card_output" | wc -l | tr -d ' ')" == "1" ]]
printf '%s\n' "$card_output" | grep -qE '^block=2 chars=[0-9]+ limit=none shots=1 status=PASS$'

expect_fail "second card declares an incomplete prompt" "$VALIDATOR" "$fixture_card_incomplete_second"
incomplete_output="$("$VALIDATOR" "$fixture_card_incomplete_second" 2>&1 || true)"
printf '%s\n' "$incomplete_output" | grep -qE '^block=1 chars=[0-9]+ limit=none shots=1 status=PASS$'
printf '%s\n' "$incomplete_output" | grep -qE '^block=2 chars=[0-9]+ limit=none shots=0 status=FAIL'
printf '%s\n' "$incomplete_output" | grep -qE '【画面内容】 count=0'

expect_fail "card declares a prompt without a code block" "$VALIDATOR" "$fixture_card_without_block"
without_block_output="$("$VALIDATOR" "$fixture_card_without_block" 2>&1 || true)"
printf '%s\n' "$without_block_output" | grep -qE 'declares a prompt but has no code block'

# 显式 --block 指向全文件第几个围栏，而不是第几个合格提示词。
expect_fail "explicit --block selects the whole-file fence" "$VALIDATOR" "$fixture_card" --block 1
block_output="$("$VALIDATOR" "$fixture_card" --block 2 2>/dev/null)"
printf '%s\n' "$block_output" | grep -qE '^block=2 chars=[0-9]+ limit=none shots=1 status=PASS$'
expect_fail "explicit --block 3 is the incomplete block" "$VALIDATOR" "$fixture_two_blocks_bad" --block 3

expect_fail "h3 tags are not seedance tags" "$VALIDATOR" "$fixture_h3"
expect_fail "seedance payload is not h3" "$VALIDATOR" "$fixture_seedance" --profile h3
expect_fail "kling alias must be defined first" "$VALIDATOR" "$fixture_kling_undefined" --profile kling
expect_ok "h3 profile" "$VALIDATOR" "$fixture_h3" --profile h3
expect_ok "seedance profile" "$VALIDATOR" "$fixture_seedance" --profile seedance
expect_ok "kling profile" "$VALIDATOR" "$fixture_kling" --profile kling

expect_fail "absolute second range without contract" "$VALIDATOR" "$fixture_absolute_time"
expect_ok "absolute second range with timing policy and evidence" "$VALIDATOR" "$fixture_timing_policy"
policy_output="$("$VALIDATOR" "$fixture_timing_policy" 2>/dev/null)"
printf '%s\n' "$policy_output" | grep -qE 'status=PASS timing_policy=locked_audio$'
expect_fail "timing policy without evidence" "$VALIDATOR" "$fixture_timing_no_evidence"

expect_fail "char limit" "$VALIDATOR" "$fixture_valid" --limit 10
limit_output="$("$VALIDATOR" "$fixture_valid" --limit 10000 2>/dev/null)"
printf '%s\n' "$limit_output" | grep -qE "limit=10000 shots=1 status=PASS$"

expect_usage_error "unknown profile" "$VALIDATOR" "$fixture_valid" --profile magic
expect_usage_error "missing profile value" "$VALIDATOR" "$fixture_valid" --profile
expect_usage_error "bad limit" "$VALIDATOR" "$fixture_valid" --limit 0
expect_usage_error "bad block" "$VALIDATOR" "$fixture_valid" --block x
expect_usage_error "missing file" "$VALIDATOR" "$work/absent.md"
expect_usage_error "no arguments" "$VALIDATOR"
expect_usage_error "unknown option" "$VALIDATOR" "$fixture_valid" --profile=seedance
expect_usage_error "unclosed fence" "$VALIDATOR" "$fixture_unclosed"
expect_usage_error "block index beyond file" "$VALIDATOR" "$fixture_valid" --block 9
expect_usage_error "duplicate block index" "$VALIDATOR" "$fixture_two_blocks" --block 1 --block 1

repeat_output="$("$VALIDATOR" "$fixture_two_blocks" --block 1 --block 2 2>/dev/null)"
printf '%s\n' "$repeat_output" | grep -qE '^block=1 chars=[0-9]+ limit=none shots=1 status=PASS$'
printf '%s\n' "$repeat_output" | grep -qE '^block=2 chars=[0-9]+ limit=none shots=1 status=PASS$'

printf 'validate_video_prompt_structure tests passed\n'
