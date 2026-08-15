#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
cd "$ROOT"

failures=0

pass() {
  printf 'PASS: %s\n' "$1"
}

fail() {
  printf 'FAIL: %s\n' "$1" >&2
  failures=$((failures + 1))
}

require_file() {
  local file="$1"
  if [[ -f "$file" ]]; then
    pass "file exists: $file"
  else
    fail "missing file: $file"
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

require_max_lines() {
  local file="$1"
  local maximum="$2"
  local label="$3"
  if [[ ! -f "$file" ]]; then
    fail "$label: missing file $file"
    return
  fi
  local lines
  lines="$(wc -l < "$file" | tr -d ' ')"
  if (( lines <= maximum )); then
    pass "$label ($lines <= $maximum)"
  else
    fail "$label ($lines > $maximum)"
  fi
}

printf 'Checking public laohu AI visual contract in %s\n' "$ROOT"

core_skills=(
  laohu_ai_visual
  laohu_script_writer
  laohu_visual_assets
  laohu_video_prompt
  laohu_vibe_creating_prompt
  laohu_cover_design
  laohu_generation_review
)

video_prompt_references=(
  00_调用路由与机制提炼.md
  01_文戏对白与人物表演.md
  02_动作打斗追逐与力量奇观.md
  03_产品广告品牌宣传与PV.md
  04_MV概念PV与动态图形蒙太奇.md
  05_MG动态图形科普与混合媒介动画.md
  05A_纸拼贴与纸艺定格知识讲解.md
  06_变身世界变化巨物揭示与视觉奇观.md
  07_POV纪实采访UGC与连续路线.md
  08_提示词压缩质检与失败修复.md
  09_速度节奏与时间动力设计.md
)

required_files=(
  AGENTS.md
  README.md
  输入输出索引.md
  02_共享资产库/00_核心规则手册.md
  02_共享资产库/05_工具流程/laohu_skills核心合约.md
  02_共享资产库/05_工具流程/导演级影视创作总控流程.md
  02_共享资产库/05_工具流程/助手执行失败经验与防复发规则.md
  02_共享资产库/01_模板库/图片模板/模板_封面海报创作执行单.md
  02_共享资产库/01_模板库/视频模板/模板_视频提示词_基础设定氛围画面内容.md
  02_共享资产库/01_模板库/视频模板/模板_视频生成质量检查清单.md
)

for file in "${required_files[@]}"; do
  require_file "$file"
done

for skill in "${core_skills[@]}"; do
  require_file "skills/$skill/SKILL.md"
done

for reference in "${video_prompt_references[@]}"; do
  require_file "skills/laohu_video_prompt/references/$reference"
done

actual_skill_count="$(find skills -mindepth 1 -maxdepth 1 -type d -name 'laohu_*' | wc -l | tr -d ' ')"
if [[ "$actual_skill_count" == "7" ]]; then
  pass "exactly 7 laohu core skill directories"
else
  fail "expected exactly 7 laohu skill directories, found $actual_skill_count"
fi

non_laohu_dirs="$(find skills -mindepth 1 -maxdepth 1 -type d ! -name 'laohu_*' -print)"
if [[ -z "$non_laohu_dirs" ]]; then
  pass "all public skill directories use laohu_ prefix"
else
  fail "non-laohu skill directories found: $non_laohu_dirs"
fi

for skill in "${core_skills[@]}"; do
  file="skills/$skill/SKILL.md"
  require_pattern "$file" '^## 能力定位' "$skill has capability positioning"
  require_pattern "$file" '^## 能力加厚纪律' "$skill has capability deepening discipline"
  require_pattern "$file" '^## (能力边界|工作纪律)' "$skill has capability boundary"
  require_pattern "$file" '^## (输出结构|输出契约|路由)' "$skill has output or routing structure"
  require_pattern "$file" '^## (自检|输出后检查|结束前检查)' "$skill has final self-check"
  require_pattern "$file" '交接包|下游字段摘要|下游' "$skill has a downstream handoff"
done

require_max_lines "skills/laohu_video_prompt/SKILL.md" 650 "video prompt skill stays routable"
require_pattern "AGENTS.md" '当前项目只保留 7 个核心 skill 入口' "top-level rules define seven skills"
require_pattern "README.md" '当前只保留 7 个核心 skill' "README documents seven skills"
require_pattern "AGENTS.md" '作品隐私与 Git 边界' "top-level rules protect private works"
require_pattern "README.md" '作品隐私' "README explains local-only works"
require_pattern ".gitignore" '/01_作品项目/进行中/\*' "gitignore excludes active works"
require_pattern ".gitignore" '/01_作品项目/已完成/\*' "gitignore excludes completed works"
require_pattern ".gitignore" '/01_作品项目/已发布/\*' "gitignore excludes published works"
require_pattern ".gitignore" '/output/' "gitignore excludes local generation output"
require_pattern ".gitignore" '/docs/superpowers/' "gitignore excludes local execution plans"

for status in 进行中 已完成 已发布; do
  require_file "01_作品项目/$status/.gitkeep"
done

if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  tracked_work_files="$(git ls-files '01_作品项目/**' | grep -Ev '^01_作品项目/(进行中|已完成|已发布)/\.gitkeep$' || true)"
  if [[ -z "$tracked_work_files" ]]; then
    pass "Git tracks only work-directory placeholders"
  else
    fail "private work files are tracked: $tracked_work_files"
  fi

  tracked_local_results="$(git ls-files 'output/**' 'tmp/**' 'docs/superpowers/**' || true)"
  if [[ -z "$tracked_local_results" ]]; then
    pass "local execution results are not tracked"
  else
    fail "local execution results are tracked: $tracked_local_results"
  fi
fi

require_pattern "skills/laohu_video_prompt/SKILL.md" 'Reference 适配门|完全适配|组合适配|能力缺口' "video prompt skill gates references"
require_pattern "skills/laohu_video_prompt/SKILL.md" '【基础设定】.*【氛围与画质】.*【画面内容】|三段式' "video prompt skill keeps the three-part contract"
require_pattern "skills/laohu_video_prompt/SKILL.md" '相邻单元交接合同|状态等式检查' "video prompt skill protects continuity"
require_pattern "skills/laohu_video_prompt/SKILL.md" '交接载体视觉指纹|双端镜像详述' "video prompt skill mirrors transition carriers"
require_pattern "skills/laohu_video_prompt/references/09_速度节奏与时间动力设计.md" '动作速度.*摄影机速度.*切镜速度.*信息速度.*声音速度' "timing reference separates speed layers"
require_pattern "skills/laohu_video_prompt/references/09_速度节奏与时间动力设计.md" '蓄势.*启动.*加速.*峰值.*接触.*余波.*停点' "timing reference defines action phases"
require_pattern "skills/laohu_video_prompt/references/04_MV概念PV与动态图形蒙太奇.md" '音乐 / 声音时间轴|音乐 / 声音结构' "motion reference uses a shared audio timeline"
require_pattern "skills/laohu_visual_assets/SKILL.md" '依赖图|拓扑顺序|被引用' "visual assets enforce dependency order"
require_pattern "skills/laohu_cover_design/SKILL.md" '中文双引号|直接生成文字' "cover skill locks visible text"
require_pattern "skills/laohu_cover_design/SKILL.md" '3:4.*4:3.*16:9|比例自适应' "cover skill supports adaptive layouts"
require_pattern "skills/laohu_generation_review/SKILL.md" '生成复盘|剪辑验收|发布复盘' "review skill closes the feedback loop"
require_pattern "README.md" 'api\.laohuaimoney\.com/sign-up\?aff=460d' "README contains the AI MONEY referral"

obsolete_skills=(
  laohu_workflow_runner
  laohu_style_director
  laohu_image_asset_prompt
  laohu_video_prompt_assembler
  laohu_editing_review
  laohu_publish_review
)

for skill in "${obsolete_skills[@]}"; do
  require_absent "skills/$skill"
done

if find . -name '.DS_Store' -print -quit | grep -q .; then
  fail ".DS_Store files found"
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

if (( failures > 0 )); then
  printf 'Contract check failed with %d issue(s).\n' "$failures" >&2
  exit 1
fi

printf 'Contract check passed.\n'
