#!/usr/bin/env bash
set -euo pipefail

ROOT="/Users/a1/Documents/老胡/老胡自媒体/老胡AI视觉"
cd "$ROOT"

failures=0

fail() {
  printf 'FAIL: %s\n' "$1" >&2
  failures=$((failures + 1))
}

pass() {
  printf 'PASS: %s\n' "$1"
}

require_file() {
  local file="$1"
  if [[ -f "$file" ]]; then
    pass "file exists: $file"
  else
    fail "missing file: $file"
  fi
}

require_script_text() {
  local file="$1"
  local text="$2"
  local label="$3"
  if [[ ! -f "$file" ]]; then
    fail "$label: missing file $file"
    return
  fi
  if grep -Fq "$text" "$file"; then
    pass "$label"
  else
    fail "$label"
  fi
}

require_absent() {
  local path="$1"
  if [[ -e "$path" ]]; then
    fail "obsolete path still exists: $path"
  else
    pass "obsolete path absent: $path"
  fi
}

require_pattern() {
  local file="$1"
  local pattern="$2"
  local label="$3"
  if [[ ! -f "$file" ]]; then
    fail "$label: missing file $file"
    return
  fi
  if rg -q "$pattern" "$file"; then
    pass "$label"
  else
    fail "$label"
  fi
}

core_skills=(
  laohu_ai_visual
  laohu_script_writer
  laohu_visual_assets
  laohu_video_prompt
  laohu_generation_review
)

obsolete_skills=(
  laohu_workflow_runner
  laohu_style_director
  laohu_image_asset_prompt
  laohu_image_generate
  laohu_image_batch_review
  laohu_cover_prompt
  laohu_video_base_setup
  laohu_video_mood_quality
  laohu_emotion_performance
  laohu_video_shot_content
  laohu_video_prompt_assembler
  laohu_editing_review
  laohu_publish_review
)

obsolete_docs=(
  "02_共享资产库/05_工具流程/laohu_skills能力编排说明.md"
  "02_共享资产库/05_工具流程/laohu_skills能力接口与交接字段.md"
  "02_共享资产库/05_工具流程/laohu_skills单项启动语清单.md"
  "02_共享资产库/05_工具流程/laohu_skills验证用例与验收标准.md"
  "02_共享资产库/05_工具流程/laohu_skills原始目标逐项验收矩阵.md"
)

printf 'Checking laohu core skill contract in %s\n' "$ROOT"

require_file "AGENTS.md"
require_file "README.md"
require_file "输入输出索引.md"
require_file "02_共享资产库/00_核心规则手册.md"
require_file "02_共享资产库/05_工具流程/laohu_skills核心合约.md"
require_file "02_共享资产库/05_工具流程/助手执行失败经验与防复发规则.md"
require_file "02_共享资产库/05_工具流程/短剧剧本到视频提示词编号与时长规则.md"

for skill in "${core_skills[@]}"; do
  require_file "skills/$skill/SKILL.md"
done

for skill in "${obsolete_skills[@]}"; do
  require_absent "skills/$skill"
done

for doc in "${obsolete_docs[@]}"; do
  require_absent "$doc"
done

non_laohu_dirs="$(find skills -mindepth 1 -maxdepth 1 -type d ! -name 'laohu_*' -print)"
if [[ -z "$non_laohu_dirs" ]]; then
  pass "all project skill directories use laohu_ prefix"
else
  fail "non-laohu skill directories found:"
  printf '%s\n' "$non_laohu_dirs" >&2
fi

actual_skill_count="$(find skills -mindepth 1 -maxdepth 1 -type d -name 'laohu_*' | wc -l | tr -d ' ')"
if [[ "$actual_skill_count" == "5" ]]; then
  pass "exactly 5 laohu core skill directories"
else
  fail "expected exactly 5 laohu skill directories, found $actual_skill_count"
fi

for skill in "${core_skills[@]}"; do
  file="skills/$skill/SKILL.md"
  require_pattern "$file" "^## 能力定位" "$skill has capability positioning"
  require_pattern "$file" "^## 能力加厚纪律" "$skill has capability deepening discipline"
  require_pattern "$file" "^## (能力边界|工作纪律)" "$skill has capability boundary"
  require_pattern "$file" "^## (输出结构|输出契约|路由)" "$skill has output or routing structure"
  require_pattern "$file" "^## (自检|输出后检查|结束前检查)" "$skill has final self-check"
  require_pattern "$file" "交接包|下游字段摘要|下游" "$skill has handoff contract"
done

require_pattern "AGENTS.md" "00_核心规则手册|5 个核心 skill|laohu_video_prompt|laohu_generation_review" "top-level rules reference core manual and 5 skills"
require_pattern "README.md" "00_核心规则手册|只保留 5 个核心 skill|laohu_skills核心合约" "README references simplified entry"
require_pattern "02_共享资产库/00_核心规则手册.md" "只保留 5 个主要执行入口|laohu_video_prompt|不要再为基础设定" "core manual enforces simplified skill set"
require_pattern "02_共享资产库/05_工具流程/laohu_skills核心合约.md" "只保留 5 个核心 skill|通用交接字段|启动语|验证标准" "core contract consolidates old skill docs"

require_pattern "skills/laohu_ai_visual/SKILL.md" "只保留 5 个核心执行 skill|laohu_script_writer|laohu_visual_assets|laohu_video_prompt|laohu_generation_review" "entry skill routes only to core skills"
require_pattern "skills/laohu_ai_visual/SKILL.md" "正式创作产物默认必须写入文件|输出文件|阶段摘要、文件链接|00_阶段确认记录" "entry skill enforces file-backed staged workflow"
require_pattern "skills/laohu_ai_visual/SKILL.md" "具体结果文件链接|不能只给目录链接|只有老胡明确说.*目录" "entry skill enforces direct result file links"
require_pattern "skills/laohu_ai_visual/SKILL.md" "默认只维护一个当前输出文件|不要自动新建 v1/v2/v3|新增版本、另存一版、保留旧版" "entry skill enforces single-file iteration"
require_pattern "skills/laohu_script_writer/SKILL.md" "剧本阶段的正式结果必须写入文件|01_世界观故事/文本/00_故事确认.md|02_剧本/文本/yyyy-mm-dd_剧本" "script writer enforces staged media file output"
require_pattern "skills/laohu_script_writer/SKILL.md" "默认覆盖同一个剧本输出文件|不自动新建 v1/v2/v3" "script writer enforces single-file iteration"
require_pattern "skills/laohu_visual_assets/SKILL.md" "风格|图片生成执行单|A/B/C/D|封面|laohu_video_prompt" "visual assets covers merged image and cover work"
require_pattern "skills/laohu_visual_assets/SKILL.md" "视觉资产、资产图片提示词、封面提示词和图片验收结论都必须写入文件|资产图片提示词输出文件|封面提示词输出文件" "visual assets enforces file output"
require_pattern "skills/laohu_visual_assets/SKILL.md" "可复用资产|单次画面元素|不默认叫资产|资产判定表" "visual assets distinguishes reusable assets from one-off elements"
require_pattern "skills/laohu_visual_assets/SKILL.md" "图片资产.*固定具体形象|文本资产 / 提示词资产.*固定氛围|资产类型" "visual assets distinguishes image assets and text prompt assets"
require_pattern "skills/laohu_visual_assets/SKILL.md" "人物素体资产|人物定装资产|服装 / 妆造资产|组合形象资产|场景图片资产|物品图片资产" "visual assets defines image asset subtypes"
require_pattern "skills/laohu_visual_assets/SKILL.md" "A1.*人物素体资产|A2.*服装 / 妆造资产|A3.*组合形象资产" "visual assets enforces asset composition numbering"
require_pattern "skills/laohu_visual_assets/SKILL.md" "16:9 横幅|左侧.*脸部特写|右侧.*全身三视图|三宫格 / 四宫格 / 多角度" "visual assets enforces practical asset image layouts"
require_pattern "skills/laohu_visual_assets/SKILL.md" "默认在同一个阶段文件上迭代|不自动新建 v1/v2/v3" "visual assets enforces single-file iteration"
require_pattern "skills/laohu_video_prompt/SKILL.md" "单场次剧本|基础设定|氛围与画质|画面内容|E1-S1-C1|表情占用时长|完整可复制" "video prompt covers script-first three-part exact-duration workflow"
require_pattern "skills/laohu_video_prompt/SKILL.md" "正式视频提示词必须严格按照.*模板_视频提示词_基础设定氛围画面内容|正式提示词正文只允许使用以下三块|不得混入正式提示词正文" "video prompt enforces strict three-block template output"
require_pattern "skills/laohu_video_prompt/SKILL.md" "每条正式视频提示词必须按独立生成请求处理|不能写.*沿用全片|15 秒|图片资产" "video prompt enforces independent prompts and asset consistency"
require_pattern "skills/laohu_video_prompt/SKILL.md" "转场写法用画面行为表达|遮挡转场|明暗转场|运动转场|匹配转场" "video prompt enforces in-frame transitions"
require_pattern "skills/laohu_video_prompt/SKILL.md" "画面内容.*主体动作.*环境变化.*镜头路径|画面内容.*执行稿详细度" "video prompt enforces detailed画面内容"
require_pattern "skills/laohu_video_prompt/SKILL.md" "2000 字以内|分镜编号.*所属场次.*镜头任务|基础设定.*全片统一层|画面内容不默认逐秒拆死" "video prompt enforces concise model-facing prompts"
require_pattern "skills/laohu_video_prompt/SKILL.md" "分镜表格输出文件|第一个分镜的视频提示词展示文件|所有分镜视频提示词结果输出文件|对话里不要贴长篇" "video prompt enforces staged file outputs"
require_pattern "skills/laohu_video_prompt/SKILL.md" "默认在同一个阶段文件上迭代更新|不自动新建 v1/v2/v3" "video prompt enforces single-file iteration"
require_pattern "skills/laohu_generation_review/SKILL.md" "生成诊断|剪辑验收|发布复盘|最多 3 个返修动作|下一版修正提示词" "generation review covers merged review work"
require_pattern "skills/laohu_generation_review/SKILL.md" "归档、复盘、生成结果诊断和发布复盘必须写入文件|生成复盘文件|发布复盘文件" "generation review enforces file output"
require_pattern "skills/laohu_generation_review/SKILL.md" "默认在同一个当前文件上更新|不自动新建 v1/v2/v3" "generation review enforces single-file iteration"
require_pattern "02_共享资产库/00_核心规则手册.md" "正式视频提示词必须严格使用.*模板_视频提示词_基础设定氛围画面内容|不能混进正式视频提示词正文" "core manual enforces strict video prompt template"
require_pattern "02_共享资产库/00_核心规则手册.md" "每条正式视频提示词 = 一次独立投喂|不能写.*沿用全片|图片资产|15 秒内同场合并规则" "core manual enforces independent prompt and merge rules"
require_pattern "02_共享资产库/00_核心规则手册.md" "转场不是.*后期备注|遮挡转场|明暗转场|运镜转场|匹配转场" "core manual enforces in-frame transitions"
require_pattern "02_共享资产库/00_核心规则手册.md" "画面内容.*主体动作.*环境运动.*镜头路径.*构图层次" "core manual enforces detailed画面内容"
require_pattern "02_共享资产库/00_核心规则手册.md" "2000 字以内|分镜编号.*所属场次.*镜头任务|基础设定.*全片统一层|画面内容不默认逐秒拆死" "core manual enforces concise model-facing video prompts"
require_pattern "02_共享资产库/00_核心规则手册.md" "正式产物默认不直接塞在聊天里，必须写成文件|标准阶段门|00_阶段确认记录|对话里不要输出很长" "core manual enforces file-backed stage gates"
require_pattern "02_共享资产库/00_核心规则手册.md" "具体结果文件链接|不能只给目录链接|只有老胡明确说.*目录" "core manual enforces direct result file links"
require_pattern "02_共享资产库/00_核心规则手册.md" "资产 = 需要复用和一致性锁定|画面元素 = 只在单个镜头|不默认叫资产" "core manual defines reusable assets vs one-off elements"
require_pattern "02_共享资产库/00_核心规则手册.md" "图片资产：用图片固定具体形象|文本资产 / 提示词资产：用文字固定氛围" "core manual defines image assets and text prompt assets"
require_pattern "02_共享资产库/00_核心规则手册.md" "人物素体资产|人物定装资产|服装 / 妆造资产|组合形象资产|场景图片资产|物品图片资产" "core manual defines detailed asset subtypes"
require_pattern "02_共享资产库/00_核心规则手册.md" "A1 = 人物素体资产|A2 = 服装 / 妆造资产|A3 = A1 穿着 A2" "core manual defines asset composition numbering"
require_pattern "02_共享资产库/00_核心规则手册.md" "00_原始输入.*01_世界观故事.*02_剧本.*03_视觉资产.*04_分镜.*05_视频|文本 / 图片 / 视频 / 音频" "core manual enforces staged media project directories"
require_pattern "02_共享资产库/00_核心规则手册.md" "每个阶段默认只维护一个当前输出文件|不要自动新建.*v1|文件命名默认不带版本号" "core manual enforces single-file iteration"
require_pattern "skills/laohu_ai_visual/scripts/create_work_project.sh" "00_阶段确认记录.md|灵感沟通|剧本结果输出文件|所有分镜视频提示词结果输出文件|制作完成后封面" "new project script creates staged confirmation record"
require_pattern "AGENTS.md" "00_阶段确认记录.md|00_首轮验证看板.md|00_原始输入|01_世界观故事|02_剧本|03_视觉资产|04_分镜|05_视频" "top-level rules document numbered work project structure"
require_pattern "AGENTS.md" "结果交付链接规则|具体结果文件链接|不能只给目录链接|只有老胡明确说.*目录" "top-level rules enforce direct result file links"

stage_dirs=(
  "00_原始输入"
  "01_世界观故事"
  "02_剧本"
  "03_视觉资产"
  "04_分镜"
  "05_视频"
)

media_dirs=(
  "文本"
  "图片"
  "视频"
  "音频"
)

for stage in "${stage_dirs[@]}"; do
  for media in "${media_dirs[@]}"; do
    require_script_text \
      "skills/laohu_ai_visual/scripts/create_work_project.sh" \
      "\$project_dir/$stage/$media" \
      "new project script creates $stage/$media"
  done
done

while IFS= read -r project_dir; do
  [[ -z "$project_dir" ]] && continue
  for stage in "${stage_dirs[@]}"; do
    if [[ ! -d "$project_dir/$stage" ]]; then
      continue
    fi
    for media in "${media_dirs[@]}"; do
      if [[ -d "$project_dir/$stage/$media" ]]; then
        pass "existing project has $project_dir/$stage/$media"
      else
        fail "existing project missing media dir: $project_dir/$stage/$media"
      fi
    done
  done
done < <(find 01_作品项目 -mindepth 2 -maxdepth 2 -type d | sort)

old_active_pattern='laohu_(workflow_runner|style_director|image_asset_prompt|image_generate|image_batch_review|cover_prompt|video_base_setup|video_mood_quality|emotion_performance|video_shot_content|video_prompt_assembler|editing_review|publish_review)'
if rg -n "$old_active_pattern" \
  AGENTS.md \
  README.md \
  skills \
  02_共享资产库/00_核心规则手册.md \
  02_共享资产库/05_工具流程 \
  02_共享资产库/01_模板库 \
  02_共享资产库/02_视觉语言资产 \
  02_共享资产库/03_模型适配 \
  --glob '!skills/laohu_ai_visual/scripts/check_laohu_skills.sh'; then
  fail "obsolete skill reference found in active files"
else
  pass "no obsolete skill references in active files"
fi

ambiguous_duration_pattern='^(时间段|时长|核心镜头时长)：[0-9]+-[0-9]+ 秒'
if rg -n "$ambiguous_duration_pattern" \
  AGENTS.md \
  README.md \
  skills \
  02_共享资产库/00_核心规则手册.md \
  02_共享资产库/01_模板库/视频模板/模板_视频提示词_基础设定氛围画面内容.md \
  02_共享资产库/02_视觉语言资产/镜头语言库/短剧短片分镜生成字段规范.md \
  02_共享资产库/03_模型适配/Seedance2/Seedance2视频提示词书写规范.md \
  02_共享资产库/03_模型适配/通用规范/多模型AI视频提示词通用规范.md; then
  fail "ambiguous video duration found in active rules or templates"
else
  pass "no ambiguous video duration in active rules or templates"
fi

if rg -n "基础设定是否沿用全片|氛围与画质是否沿用全片|【前置判断】|后期备注：" \
  "02_共享资产库/01_模板库/视频模板/模板_视频提示词_基础设定氛围画面内容.md" \
  "01_作品项目/进行中/2026-06-06_请登仙界/05_视频/文本"; then
  fail "obsolete formal prompt field found in template, video skill, or current video prompts"
else
  pass "no obsolete formal prompt field in template, video skill, or current video prompts"
fi

if rg -n "本条是否独立完整|复制本条|前一个镜头|下一个镜头|上一镜头|下一镜头|接 E1-|为下一条|为下一镜头|全片说明|项目说明|后期衔接" \
  "01_作品项目/进行中/2026-06-06_请登仙界/05_视频/文本"; then
  fail "out-of-frame author/editor instruction found in current video prompts"
else
  pass "no out-of-frame author/editor instruction in current video prompts"
fi

if rg -n "^(分镜编号|所属场次|镜头任务)：" \
  "01_作品项目/进行中/2026-06-06_请登仙界/05_视频/文本"; then
  fail "author-facing fields found inside current video prompts"
else
  pass "no author-facing fields in current video prompts"
fi

if python3 - <<'PY'
from pathlib import Path
import re
import sys

paths = [
    Path("01_作品项目/进行中/2026-06-06_请登仙界/05_视频/文本/2026-06-06_视频提示词_E1-S1-C1_展示.md"),
    Path("01_作品项目/进行中/2026-06-06_请登仙界/05_视频/文本/2026-06-06_视频提示词_请登仙界.md"),
]
ok = True
for path in paths:
    if not path.exists():
        continue
    text = path.read_text()
    for i, block in enumerate(re.findall(r"```text\n(.*?)\n```", text, flags=re.S), start=1):
        chars = len(block)
        if chars > 2000:
            print(f"FAIL: prompt block exceeds 2000 chars: {path} block {i} has {chars}", file=sys.stderr)
            ok = False
if ok:
    print("PASS: current video prompt blocks are under 2000 chars")
else:
    sys.exit(1)
PY
then
  pass "current video prompt block length check"
else
  fail "current video prompt block length check"
fi

require_pattern "02_共享资产库/01_模板库/视频模板/模板_视频提示词_基础设定氛围画面内容.md" "【基础设定】|【氛围与画质】|【画面内容】" "video prompt template uses three formal blocks"
if python3 - <<'PY'
from pathlib import Path
import re
import sys

text = Path("02_共享资产库/01_模板库/视频模板/模板_视频提示词_基础设定氛围画面内容.md").read_text()
blocks = re.findall(r"```text\n(.*?)\n```", text, flags=re.S)
bad = re.compile(r"【前置判断】|本条是否独立完整|本镜头一致性资产|本镜头非资产画面元素|后期备注|分镜编号：|所属场次：|镜头任务：")
ok = True
for i, block in enumerate(blocks, start=1):
    if bad.search(block):
        print(f"FAIL: video prompt template code block {i} contains out-of-frame metadata", file=sys.stderr)
        ok = False
if ok:
    print("PASS: video prompt template code blocks have no out-of-frame metadata")
else:
    sys.exit(1)
PY
then
  pass "video prompt template has no out-of-frame metadata"
else
  fail "video prompt template has no out-of-frame metadata"
fi
require_pattern "02_共享资产库/05_工具流程/短剧剧本到视频提示词编号与时长规则.md" "正式生成平台按单条提示词独立执行|15 秒合并规则|图片资产" "duration rules enforce independent prompt asset merge logic"
require_pattern "02_共享资产库/05_工具流程/短剧剧本到视频提示词编号与时长规则.md" "只保留.*【基础设定】.*【氛围与画质】.*【画面内容】|遮挡转场|明暗转场|运镜转场|匹配转场" "duration rules enforce three-block prompts and in-frame transitions"
require_pattern "02_共享资产库/02_视觉语言资产/镜头语言库/短剧短片分镜生成字段规范.md" "独立生成与合并规则|不超过 15 秒|图片资产" "shot list field spec enforces independent generation merge logic"
require_pattern "02_共享资产库/05_工具流程/剧本到AI视觉资产转换规则.md" "人物素体资产|人物定装资产|服装 / 妆造资产|组合形象资产|场景图片资产|物品图片资产" "asset conversion rules define detailed asset subtypes"
require_pattern "02_共享资产库/05_工具流程/剧本到AI视觉资产转换规则.md" "A1 = 人物素体资产|A2 = 服装 / 妆造资产|A3 = A1 穿着 A2" "asset conversion rules define asset composition numbering"
require_pattern "02_共享资产库/01_模板库/图片模板/模板_AI图片提示词_资产型通用结构.md" "人物素体资产|人物定装资产|服装 / 妆造资产|场景图片资产|物品图片资产|组合资产记录" "image asset prompt template covers asset subtypes"
require_pattern "02_共享资产库/01_模板库/图片模板/模板_角色一致性网格图.md" "人物素体资产|人物定装资产|16:9 横幅|全身三视图" "character grid template supports body and styled character assets"

obsolete_project_dir_pattern='01_原始输入(/|`|$)|02_世界观故事(/|`|$)|03_剧本(/|`|$)|04_视觉资产(/|`|$)|05_分镜(/|`|$)|06_视频(/|`|$)|05_提示词(/|`|$)|05_视频提示词(/|`|$)|02_剧本/00_故事总览|02_剧本/02_分场剧本|00_原始输入/口述与需求|06_生成素材|10_经验沉淀|09_发布复盘'
if rg -n "$obsolete_project_dir_pattern" \
  AGENTS.md \
  README.md \
  输入输出索引.md \
  skills \
  02_共享资产库 \
  01_作品项目/进行中 \
  --glob '!skills/laohu_ai_visual/scripts/check_laohu_skills.sh'; then
  fail "obsolete project directory reference found in active files"
else
  pass "no obsolete project directory references in active files"
fi

find . -name .DS_Store -delete
if find . -name .DS_Store -print -quit | grep -q .; then
  fail ".DS_Store file exists"
else
  pass "no .DS_Store files"
fi

if bash -n skills/laohu_ai_visual/scripts/create_work_project.sh; then
  pass "create_work_project.sh syntax"
else
  fail "create_work_project.sh syntax"
fi

if bash -n skills/laohu_ai_visual/scripts/check_laohu_skills.sh; then
  pass "check_laohu_skills.sh syntax"
else
  fail "check_laohu_skills.sh syntax"
fi

if [[ "$failures" -gt 0 ]]; then
  printf 'Contract check failed with %d issue(s).\n' "$failures" >&2
  exit 1
fi

printf 'Contract check passed.\n'
