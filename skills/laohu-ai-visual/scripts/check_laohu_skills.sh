#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
cd "$ROOT"

failures=0

pass() { printf 'PASS: %s\n' "$1"; }
fail() { printf 'FAIL: %s\n' "$1" >&2; failures=$((failures + 1)); }

require_file() {
  if [[ -f "$1" ]]; then pass "file exists: $1"; else fail "missing file: $1"; fi
}

core_skills=(
  laohu-ai-visual
  laohu-language-mode
  laohu-director
  laohu-story-material
  laohu-script-writer
  laohu-mv-director
  laohu-creative-development
  laohu-makeup-design
  laohu-prop-design
  laohu-image-creation
  laohu-art-direction
  laohu-character-design
  laohu-audio-design
  laohu-costume-design
  laohu-set-design
  laohu-visual-assets
  laohu-video-prompt
  laohu-vibe-creating-prompt
  laohu-cover-design
  laohu-generation-review
  laohu-capability-evolution
)

required_files=(
  AGENTS.md
  README.md
  输入输出索引.md
  02_共享资产库/00_核心规则手册.md
  02_共享资产库/05_工具流程/laohu_skills核心合约.md
  02_共享资产库/05_工具流程/能力协作图谱.md
  02_共享资产库/05_工具流程/外部能力依赖清单.md
  scripts/validate_capability_architecture.py
  scripts/validate_visual_restructure.py
  02_共享资产库/05_工具流程/能力注册表.json
  04_诊断与系统日志/视觉能力重构迁移清单.json
  tests/capability_scenarios.json
  tests/evolution_scenarios.json
  tests/language_mode_scenarios.json
  04_诊断与系统日志/能力进化台账.md
  04_诊断与系统日志/语言模式语义迁移台账.json
  04_诊断与系统日志/服装设计能力语义迁移台账.json
  skills/laohu-video-prompt/scripts/count_video_prompt_chars.sh
  skills/laohu-video-prompt/scripts/test_count_video_prompt_chars.sh
)

for file in "${required_files[@]}"; do require_file "$file"; done

for skill in "${core_skills[@]}"; do
  file="skills/$skill/SKILL.md"
  require_file "$file"
  require_file "skills/$skill/agents/openai.yaml"
  metadata_name="$(sed -n 's/^name: //p' "$file" | head -n 1)"
  if [[ "$metadata_name" == "$skill" && "$metadata_name" =~ ^[a-z0-9]+(-[a-z0-9]+)*$ ]]; then
    pass "$skill metadata and directory match"
  else
    fail "$skill metadata mismatch: $metadata_name"
  fi

  if find "skills/$skill/references" -maxdepth 1 -type f -name '*.md' -print -quit 2>/dev/null | grep -q .; then
    while IFS= read -r reference; do
      reference_name="$(basename "$reference")"
      if rg -Fq "$reference_name" "$file"; then
        pass "$skill routes reference: $reference_name"
      elif python3 - "$file" "$reference" <<'PY'
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd() / 'scripts'))
from validate_capability_architecture import reachable_documents
entry, reference = (Path(p).resolve() for p in sys.argv[1:])
reachable = reachable_documents(entry)
sys.exit(0 if reference in reachable else 1)
PY
      then
        pass "$skill routes reference through verified professional owners: $reference_name"
      else
        fail "$skill leaves reference unreachable: $reference_name"
      fi
    done < <(find "skills/$skill/references" -maxdepth 1 -type f -name '*.md' | sort)
  fi
done

actual_skill_count="$(find skills -mindepth 1 -maxdepth 1 -type d -name 'laohu-*' | wc -l | tr -d ' ')"
if [[ "$actual_skill_count" == "22" ]]; then pass "exactly twenty-two public skills"; else fail "expected 22 skills, found $actual_skill_count"; fi

if rg -n '^##[[:space:]]*(灵魂|筋骨|血肉|表皮)(层)?[[:space:]]*$' skills/*/SKILL.md >/dev/null; then
  fail "generic four-layer headings leaked into downstream skills"
else
  pass "four-layer intent is compiled into domain-native sections"
fi

if python3 scripts/validate_capability_architecture.py; then
  pass "static scenario declarations and ownership anchors (not model execution)"
else
  fail "static scenario declarations or ownership anchors"
fi

if python3 scripts/validate_visual_restructure.py; then
  pass "full specialist registry, routes and preserved baseline units"
else
  fail "specialist registry or preserved baseline drift"
fi

for status in 进行中 已完成 已发布; do require_file "01_作品项目/$status/.gitkeep"; done

if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  tracked_work_files="$(git ls-files '01_作品项目/**' | grep -Ev '^01_作品项目/(进行中|已完成|已发布)/\.gitkeep$' || true)"
  if [[ -z "$tracked_work_files" ]]; then pass "Git tracks only work placeholders"; else fail "private work files tracked: $tracked_work_files"; fi

  tracked_local_results="$(git ls-files 'output/**' 'tmp/**' 'docs/superpowers/**' || true)"
  if [[ -z "$tracked_local_results" ]]; then pass "local results remain untracked"; else fail "local results tracked: $tracked_local_results"; fi
fi

if cmp -s \
  "02_共享资产库/05_工具流程/外部优化Skill/vibe-creating-prompt/SKILL.md" \
  "skills/laohu-vibe-creating-prompt/references/01_外部Vibe_Creating原文.md"; then
  pass "external Vibe source remains verbatim"
else
  fail "external Vibe source was altered"
fi

if bash -n skills/laohu-ai-visual/scripts/create_work_project.sh; then pass "project creation script syntax"; else fail "project creation script syntax"; fi
if bash -n skills/laohu-ai-visual/scripts/check_laohu_skills.sh; then pass "contract script syntax"; else fail "contract script syntax"; fi

if bash -n skills/laohu-video-prompt/scripts/count_video_prompt_chars.sh && \
   bash skills/laohu-video-prompt/scripts/test_count_video_prompt_chars.sh; then
  pass "video prompt character counter"
else
  fail "video prompt character counter"
fi

if bash -n skills/laohu-video-prompt/scripts/validate_video_prompt_structure.sh && \
   bash skills/laohu-video-prompt/scripts/test_validate_video_prompt_structure.sh; then
  pass "video prompt structure and failure fixtures"
else
  fail "video prompt structure or failure fixtures"
fi

if bash skills/laohu-visual-assets/scripts/test_validate_character_asset_structure.sh; then
  pass "character asset structure and failure fixtures"
else
  fail "character asset structure or failure fixtures"
fi

if find . -path './01_作品项目' -prune -o -name '.DS_Store' -print -quit | grep -q .; then
  fail ".DS_Store files found in public project"
else
  pass "no .DS_Store files in public project"
fi

if (( failures > 0 )); then
  printf 'Contract check failed with %d issue(s).\n' "$failures" >&2
  exit 1
fi

printf 'Contract check passed.\n'

python3 "$ROOT/scripts/validate_segmentation_migration.py"
