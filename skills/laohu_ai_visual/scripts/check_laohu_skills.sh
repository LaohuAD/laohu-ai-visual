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
  laohu_vibe_creating_prompt
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
require_file "02_共享资产库/05_工具流程/导演级影视创作总控流程.md"

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
if [[ "$actual_skill_count" == "6" ]]; then
  pass "exactly 6 laohu core skill directories"
else
  fail "expected exactly 6 laohu skill directories, found $actual_skill_count"
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

require_pattern "AGENTS.md" "00_核心规则手册|6 个核心 skill|laohu_vibe_creating_prompt|laohu_generation_review" "top-level rules reference core manual and 6 skills"
require_pattern "README.md" "00_核心规则手册|只保留 6 个核心 skill|laohu_vibe_creating_prompt|laohu_skills核心合约" "README references simplified entry"
require_pattern "02_共享资产库/00_核心规则手册.md" "只保留 6 个主要执行入口|laohu_vibe_creating_prompt|不要再为基础设定" "core manual enforces simplified skill set"
require_pattern "02_共享资产库/05_工具流程/laohu_skills核心合约.md" "只保留 6 个核心 skill|laohu_vibe_creating_prompt|通用交接字段|启动语|验证标准" "core contract consolidates skill docs"

require_pattern "skills/laohu_ai_visual/SKILL.md" "只保留 6 个核心执行 skill|laohu_script_writer|laohu_visual_assets|laohu_video_prompt|laohu_vibe_creating_prompt|laohu_generation_review" "entry skill routes only to core skills"
require_pattern "skills/laohu_ai_visual/SKILL.md" "正式创作产物默认必须写入文件|输出文件|阶段摘要、文件链接|00_阶段确认记录" "entry skill enforces file-backed staged workflow"
require_pattern "skills/laohu_ai_visual/SKILL.md" "具体结果文件链接|不能只给目录链接|只有老胡明确说.*目录" "entry skill enforces direct result file links"
require_pattern "skills/laohu_ai_visual/SKILL.md" "默认只维护一个当前输出文件|不要自动新建 v1/v2/v3|新增版本、另存一版、保留旧版" "entry skill enforces single-file iteration"
require_pattern "skills/laohu_script_writer/SKILL.md" "剧本阶段的正式结果必须写入文件|01_世界观故事/文本/00_故事确认.md|02_剧本/文本/yyyy-mm-dd_剧本" "script writer enforces staged media file output"
require_pattern "skills/laohu_script_writer/SKILL.md" "默认覆盖同一个剧本输出文件|不自动新建 v1/v2/v3" "script writer enforces single-file iteration"
require_pattern "skills/laohu_script_writer/SKILL.md" "确定性命名|生产命名|大人.*主角|群仙.*群体类别|神兽.*生物类别" "script writer enforces deterministic role naming"
require_pattern "skills/laohu_script_writer/SKILL.md" "故事设计稿.*不是小说|观众等待的问题|首画面|尾画面|资产预判|生成风险" "script writer enforces story design before screenplay when needed"
require_pattern "skills/laohu_script_writer/SKILL.md" "灵感解构与价值脑洞|影射议题|正向价值|观众误判|反转机制|开场特写钩子|隐喻物" "script writer enforces value ideation before story design"
require_pattern "02_共享资产库/05_工具流程/导演级影视创作总控流程.md" "身份门|价值门|故事门|节奏门|文戏门|武戏门|画面门|剪辑门" "director control flow defines eight gates"
require_pattern "02_共享资产库/05_工具流程/导演级影视创作总控流程.md" "关键台词在关系里的目的.*可读后果|候选通道：潜台词 / 表情 / 停顿 / 关系距离 / 反应镜头" "director control flow defines contribution-based dialogue system"
require_pattern "02_共享资产库/05_工具流程/导演级影视创作总控流程.md" "故事任务.*主情绪.*力量来源.*运动路径.*接触点.*动作结果|候选节拍：起势 / 发力 / 受力 / 反应 / 爆点 / 停帧" "director control flow defines contribution-based action system"
require_pattern "02_共享资产库/00_核心规则手册.md" "导演级影视创作.*导演级影视创作总控流程|节奏不是只写.*开头钩子.*中段升级.*结尾评论|文戏.*武戏" "core manual enforces director control chain"
require_pattern "skills/laohu_script_writer/SKILL.md" "节奏密度.*15 秒.*30 秒.*60 秒|文戏.*关键台词.*关系.*目的.*可读后果|武戏.*力量来源.*运动路径.*接触点.*动作结果" "script writer enforces contribution-based pacing and dialogue/action systems"
require_pattern "02_共享资产库/01_模板库/剧本模板/模板_阶段门控剧本开发.md" "导演总控判断|主导身份|节奏网格|文戏.*武戏" "script template includes director control, pacing and dialogue/action gates"
require_pattern "skills/laohu_visual_assets/SKILL.md" "风格|图片生成执行单|A/B/C/D|封面|laohu_video_prompt" "visual assets covers merged image and cover work"
require_pattern "skills/laohu_visual_assets/SKILL.md" "透视、纵深、线性节奏、影调、色彩透视和柔化介质.*开放控制杆.*不是.*必填" "visual assets treats photographic controls as optional levers"
require_pattern "skills/laohu_visual_assets/SKILL.md" "美.*不是漂亮元素堆叠|第一眼.*视线.*主体.*光.*颜色.*前景.*材质.*留白" "visual assets defines aesthetic order beyond pretty elements"
require_pattern "skills/laohu_visual_assets/SKILL.md" "人物写真摆姿层|镜头互动层|景别机位.*身体朝向.*头颈角度.*眼神关系.*手部任务.*重心腿线.*环境接触.*服装发丝反应" "visual assets enforces portrait posing and camera interaction layer"
require_pattern "skills/laohu_visual_assets/SKILL.md" "视觉资产、资产图片提示词、封面提示词和图片验收结论都必须写入文件|资产图片提示词输出文件|封面提示词输出文件" "visual assets enforces file output"
require_pattern "skills/laohu_visual_assets/SKILL.md" "可复用资产|单次画面元素|不默认叫资产|资产判定表" "visual assets distinguishes reusable assets from one-off elements"
require_pattern "skills/laohu_visual_assets/SKILL.md" "确定性命名审计|剧本显示称呼|生产命名|群仙.*不是人物图片资产|神兽.*不是固定资产" "visual assets enforces deterministic asset naming"
require_pattern "skills/laohu_visual_assets/SKILL.md" "图片资产.*固定具体形象|文本资产 / 提示词资产.*固定氛围|资产类型" "visual assets distinguishes image assets and text prompt assets"
require_pattern "skills/laohu_visual_assets/SKILL.md" "人物形象资产|人物素体资产|人物设计资产|人物定装资产|服装 / 妆造资产|组合形象资产|场景图片资产|物品图片资产" "visual assets defines image asset subtypes"
require_pattern "skills/laohu_visual_assets/SKILL.md" "A1.*人物素体资产|A2.*服装 / 妆造资产|A3.*组合形象资产" "visual assets enforces asset composition numbering"
require_pattern "skills/laohu_visual_assets/SKILL.md" "人物形象资产和人物设计资产必须分开输出|旧版混合图|人物形象资产：环境内电影级|人物设计资产：白底|不拆成两个资产编号" "visual assets rejects mixed character asset prompts and sub-numbering"
require_pattern "skills/laohu_visual_assets/SKILL.md" "形象资产.*设计资产|环境内艺术照|白色素衣|组合设计资产|四区制作参考图" "visual assets enforces character image/design/wardrobe chain"
require_pattern "skills/laohu_visual_assets/SKILL.md" "人物参考图.*服装参考图|主视觉区.*补充信息区.*局部细节区.*比例照|内 / 中 / 外 / 腰 / 下 / 足" "visual assets enforces character reference sheet and clothing layering"
require_pattern "skills/laohu_visual_assets/SKILL.md" "左手特写.*右手特写|音色文字说明区|【形象参考@.*【音色参考@" "visual assets enforces hand closeups and voice reference handoff"
require_pattern "skills/laohu_visual_assets/SKILL.md" "主角色人物设计资产默认只固定中性常见表情|不做.*多格情绪表情|情绪表演.*视频提示词" "visual assets avoids default multi-expression character assets"
require_pattern "skills/laohu_visual_assets/SKILL.md" "衣服如何穿在这个身体上|肩线.*胸口.*腰侧.*高腰线|修身但不紧绷" "visual assets enforces body-fit clothing adaptation"
require_pattern "skills/laohu_visual_assets/SKILL.md" "服装参考不能只继承单品名称|穿法逻辑.*视觉重心.*比例关系|鞋头形状.*闭口 / 露趾.*踝带.*跟高" "visual assets enforces clothing styling logic and shoe design"
require_pattern "skills/laohu_visual_assets/SKILL.md" "造型账本|三视图.*手部特写.*局部细节.*比例照|发圈.*手腕|鞋履|标签.*物件" "visual assets enforces character styling ledger consistency"
require_pattern "skills/laohu_visual_assets/SKILL.md" "代表性基准体态|不是统一套挺拔站姿|左手.*右手.*拇指" "visual assets preserves identity-specific posture and correct left-right hands"
require_pattern "skills/laohu_visual_assets/SKILL.md" "信息优先级.*三视图.*脸部.*比例图|手模级|十六进制 RGB|厘米测量线" "visual assets enforces character asset layout information priority"
require_pattern "skills/laohu_visual_assets/SKILL.md" "人物设计资产本身会反向影响后续视频肤色|角色自己的肤色、气色、妆效|冷白偏中性.*只是林栀案例|暖肤、深肤、晒痕" "visual assets preserves identity-specific complexion before video reference"
require_pattern "02_共享资产库/00_核心规则手册.md" "人物设计资产本身会反向影响后续视频肤色|角色自己的肤色、气色、妆效|冷白偏中性.*只是林栀案例|暖肤、深肤、晒痕" "core manual preserves identity-specific complexion before video reference"
require_pattern "02_共享资产库/01_模板库/图片模板/模板_AI图片提示词_资产型通用结构.md" "角色自己的肤色、气色、妆效|冷白偏中性.*只作为林栀案例|不是美女角色默认值" "image asset template preserves identity-specific complexion"
require_pattern "02_共享资产库/05_工具流程/助手执行失败经验与防复发规则.md" "人物资产肤色会反向污染视频生成|角色自己的肤色|冷白偏中性.*案例|暖肤|深肤" "failure rules record identity-specific complexion contamination"
require_pattern "skills/laohu_visual_assets/SKILL.md" "场景四视图设定图|正面视角.*左侧视角.*右侧视角.*正面反打图|物体空间逻辑" "visual assets enforces scene four-view spatial consistency"
require_pattern "skills/laohu_visual_assets/SKILL.md" "可复制图片提示词|代码块里只放模型投喂内容|代码块外写给人看的说明" "visual assets enforces copyable image prompt code blocks"
require_pattern "skills/laohu_visual_assets/SKILL.md" "图片模型代码块里的引号只保留给画面里真实需要出现的文字|标签文字为：左手、右手|标题文字为：音色说明" "visual assets enforces image-prompt quote discipline"
require_pattern "AGENTS.md" "所有需要老胡手动上传、替换、绑定、参考或调用的外部内容.*【】|【参考图1：用途】.*【参考图2：用途】|裸写.*参考图 1.*不够清楚" "top-level rules enforce bracketed external reference placeholders"
require_pattern "02_共享资产库/00_核心规则手册.md" "所有需要老胡手动上传、替换、绑定、参考或调用的外部内容.*【】|【参考图1：用途】.*【参考图2：用途】|不要裸写.*参考图 1" "core manual enforces bracketed external reference placeholders"
require_pattern "skills/laohu_visual_assets/SKILL.md" "需要老胡手动上传、替换、绑定、参考或调用的外部内容.*【】|【参考图1：用途】.*【参考图2：用途】|不要裸写.*参考图 1" "visual assets enforces bracketed external reference placeholders"
require_pattern "02_共享资产库/01_模板库/图片模板/模板_AI图片提示词_资产型通用结构.md" "需要老胡手动上传、替换、绑定、参考或调用的外部内容.*【】|【参考图1：用途】.*【参考图2：用途】|【参考图1：人物肖像】.*【参考图2：服装穿搭】" "image asset template enforces bracketed external reference placeholders"
require_pattern "02_共享资产库/05_工具流程/剧本到AI视觉资产转换规则.md" "需要老胡手动上传、替换、绑定、参考或调用的外部内容.*【】|【参考图1：用途】.*【参考图2：用途】|不要裸写.*参考图 1" "asset conversion rules enforce bracketed external reference placeholders"
require_pattern "skills/laohu_visual_assets/SKILL.md" "默认在同一个阶段文件上迭代|不自动新建 v1/v2/v3" "visual assets enforces single-file iteration"
require_pattern "skills/laohu_video_prompt/SKILL.md" "单场次剧本|基础设定|氛围与画质|画面内容|E1-S1-C1|表情占用时长|完整可复制" "video prompt covers script-first three-part exact-duration workflow"
require_pattern "skills/laohu_video_prompt/SKILL.md" "视频美学的根本不是单帧漂亮.*关系在时间里有秩序地变化|时间关系链.*起点状态.*触发事件.*动作路径.*表演变化.*镜头路径.*光影变化.*声音进入和退出.*峰值停点.*尾帧接续" "video prompt enforces temporal relationship chain"
require_pattern "skills/laohu_video_prompt/SKILL.md" "正式视频提示词必须严格按照.*模板_视频提示词_基础设定氛围画面内容|正式提示词正文只允许使用以下三块|不得混入正式提示词正文" "video prompt enforces strict three-block template output"
require_pattern "skills/laohu_video_prompt/SKILL.md" "每条正式视频提示词必须按独立生成请求处理|不能写.*沿用全片|15 秒|图片资产" "video prompt enforces independent prompts and asset consistency"
require_pattern "skills/laohu_video_prompt/SKILL.md" "命名检查|大人.*主角|群仙.*群体画面元素|神兽.*白鹿.*云龙.*青鸾" "video prompt enforces deterministic object naming"
require_pattern "skills/laohu_video_prompt/SKILL.md" "laohu_vibe_creating_prompt|正式视频提示词初稿完成后|VC 优化|重新落回【基础设定】【氛围与画质】【画面内容】三块" "video prompt calls VC optimization skill"
require_pattern "skills/laohu_vibe_creating_prompt/SKILL.md" "Vibe Creating|外部优化Skill/vibe-creating-prompt/SKILL.md|不能改变三段模板|不能改变确定总时长|下游" "VC optimization skill preserves hard constraints"
require_pattern "skills/laohu_video_prompt/SKILL.md" "转场写法用画面行为表达|遮挡转场|明暗转场|运动转场|匹配转场" "video prompt enforces in-frame transitions"
require_pattern "skills/laohu_video_prompt/SKILL.md" "画面内容.*主体动作.*环境变化.*镜头路径|画面内容.*执行稿详细度" "video prompt enforces detailed画面内容"
require_pattern "skills/laohu_video_prompt/SKILL.md" "关键发声镜头.*音色例外|短视频开场钩子.*本镜声线|冷感磁性女中音.*近麦干声|不甜.*不夹.*不软" "video prompt skill enforces key-voice shot timbre restatement"
require_pattern "skills/laohu_video_prompt/SKILL.md" "台词、旁白、画外音和脑内 VO.*声音参数|音高 / 音区.*响度 / 音量.*语速 / 节奏.*停顿 / 气口.*重音位置.*气息状态.*咬字 / 吐字.*距离感.*混响和衰减" "video prompt skill enforces parameterized voice performance"
require_pattern "skills/laohu_video_prompt/SKILL.md" "情绪曲线型短片.*主要 VO.*阶段性声音表演|初识.*热恋.*平淡期.*猜忌期.*争吵期.*决裂期|普通年轻男声" "video prompt skill enforces staged VO emotional curve"
require_pattern "skills/laohu_video_prompt/SKILL.md" "人物情绪开场.*肌肉路径|单侧嘴角.*呼吸.*停顿|皮肤.*妆效.*曝光|服装.*首饰.*环境运动" "video prompt skill enforces emotional portrait expression, skin and environment interaction"
require_pattern "skills/laohu_video_prompt/SKILL.md" "角色自己的肤色|地域、年龄、职业、年代、健康|冷白偏中性.*案例|不.*所有人物" "video prompt skill preserves identity-specific complexion and makeup"
require_pattern "skills/laohu_video_prompt/SKILL.md" "风格交集|主风格.*辅助风格|反众数|同题材可替换性" "video prompt skill uses distinctive style reasoning without fixed style recipes"
require_pattern "skills/laohu_video_prompt/SKILL.md" "承重字段选择|生成必需信息|不要求每镜.*全部|开放控制杆" "video prompt skill selects cinematography controls by contribution"
require_pattern "skills/laohu_video_prompt/SKILL.md" "主体细节承担身份、状态、动作因果或主情绪时|颜色、材质、纹理、反光、破损、湿度、瑕疵和边缘状态中选择必要证据|不要求组成完整细节束" "video prompt skill selects subject detail by contribution"
require_pattern "skills/laohu_video_prompt/SKILL.md" "使用动态光源时必须写出来源、运动原因|焦段、景深.*只在承重时展开|不固定为某组.*参数" "video prompt skill selects motivated light and optics by contribution"
require_pattern "skills/laohu_video_prompt/SKILL.md" "透视和视觉重心|灭点.*画内.*画外|色彩透视|影调透视" "video prompt skill enforces perspective, tone and color depth controls"
require_pattern "02_共享资产库/00_核心规则手册.md" "风格交集|主风格母体.*辅助风格|同题材可替换性|反众数" "core manual enforces distinctive style reasoning without fixed recipes"
require_pattern "02_共享资产库/00_核心规则手册.md" "开放控制杆|只选择能加强主情绪、主体识别或生成稳定性的部分|未承担职责的不要" "core manual treats photographic controls as conditional"
require_pattern "02_共享资产库/00_核心规则手册.md" "画面美学的根本不是.*元素漂亮.*关系有秩序|美不是一个形容词.*可见关系" "core manual defines aesthetic order beyond pretty elements"
require_pattern "02_共享资产库/00_核心规则手册.md" "视频提示词要在图片美学上再加一层时间秩序|视频的美是关系在时间里有秩序地变化|起点状态.*触发.*动作.*表情.*镜头.*光影.*声音.*峰值.*尾帧" "core manual defines video temporal aesthetic order"
require_pattern "02_共享资产库/00_核心规则手册.md" "人物写真类图片必须补.*镜头互动层|景别机位.*身体朝向.*头颈.*眼神.*手部.*重心.*服装.*发丝" "core manual enforces portrait posing and camera interaction layer"
require_pattern "02_共享资产库/00_核心规则手册.md" "开放控制杆|只选择能加强主情绪、主体识别或生成稳定性的部分|未承担职责的不要" "core manual selects cinematography controls by contribution"
require_pattern "02_共享资产库/01_模板库/视频模板/模板_视频提示词_基础设定氛围画面内容.md" "写作前建立风格交集|正式.*氛围与画质.*主风格.*摄影介质.*宏观色彩基线|肤色妆效.*具体光影.*对应镜头" "video prompt template enforces style intersection with concise global output"
require_pattern "02_共享资产库/01_模板库/视频模板/模板_视频提示词_基础设定氛围画面内容.md" "效果系统按本镜实际需要|不要求每个镜头机械填满|景别、机位、运镜、光影、HEX、材质、环境、同期声、切换和停点不要求同时写满" "video prompt template selects cinematography controls by contribution"
require_pattern "02_共享资产库/05_工具流程/助手执行失败经验与防复发规则.md" "专业字段不是必填清单|情绪目的|固定情绪映射" "failure rules record contribution-based cinematography selection"
require_pattern "skills/laohu_video_prompt/SKILL.md" "正式视频提示词代码块里禁止写作者意图|让观众懂|表现孩子不冷漠|避免误读|模型不知道上下文|屏幕证据" "video prompt blocks author-intent and process explanations in formal prompts"
require_pattern "skills/laohu_video_prompt/SKILL.md" "氛围与画质.*1-3 句|跨本条全部镜头|局部.*对应镜头|删除某句后如果只影响一个镜头" "video prompt keeps global vibe concise and moves local direction into shots"
require_pattern "skills/laohu_video_prompt/SKILL.md" "基础设定.*实际上传或绑定|【@A1 人物】.*【@S1 场景】|只生成对白、同期动作音效和环境声，不生成 BGM" "video prompt limits basic setting to actual references and sync sound"
require_pattern "skills/laohu_video_prompt/SKILL.md" "【形象参考@xx】|【音色参考@xx】|双参考占位|不要在每条视频提示词里重复长篇基础声线" "video prompt enforces character image and voice reference placeholders"
require_pattern "skills/laohu_video_prompt/SKILL.md" "正向收束|目标画面|排除句|抽象质量边界|代码块外" "video prompt enforces positive model-facing prompt convergence"
require_pattern "skills/laohu_video_prompt/SKILL.md" "提示词资产.*基础设定.*氛围与画质|图片资产 / 固定资产.*画面内容.*交互|未资产化元素.*画面内容.*详细描述" "video prompt enforces asset-aware画面内容 description budget"
require_pattern "skills/laohu_video_prompt/SKILL.md" "【@资产名】|资产占位|固定实体|资产图片引用" "video prompt supports explicit asset placeholders"
require_pattern "skills/laohu_video_prompt/SKILL.md" "动作链|因果链|冲击结果|连锁反应|动作段落" "video prompt enforces benchmark-level action choreography"
require_pattern "skills/laohu_video_prompt/SKILL.md" "丁达尔效应|轮廓光|侧逆光|体积光|明暗交错" "video prompt includes concrete lighting vocabulary"
require_pattern "skills/laohu_video_prompt/SKILL.md" "没有项目统一字数目标和硬上限|默认不精简、不主动压缩|最高质量和最高有效信息密度" "video prompt prioritizes complete high-density prompts over project length limits"
require_pattern "skills/laohu_video_prompt/SKILL.md" "连续镜头叙事|正式正文.*不写.*镜头编号|动作.*遮挡.*视线.*焦点.*声音.*光色峰值.*运动方向|总时长.*平台参数" "video prompt uses continuous shot narrative without labels or timestamps"
require_pattern "skills/laohu_video_prompt/SKILL.md" "投射物 / 高速运动空间闭环|场景坐标与通行净空|摄影机位于主体哪一侧|主体屏幕运动方向|攻击或物体来源|主体避让方向|最终出画或撞击位置|环境受力反馈" "video prompt enforces projectile spatial closure"
require_pattern "skills/laohu_video_prompt/SKILL.md" "状态账本：对象进入状态|知觉账本：客观事件|观众信息账本：观众领先|完整入鞘 / 顶开护手 / 部分出鞘 / 完全出鞘 / 回鞘 / 脱手落地" "video prompt enforces object-state and perception continuity"
require_pattern "skills/laohu_video_prompt/SKILL.md" "速度设计按.*参照物.*相对位移.*材料响应.*摄影机响应.*声音响应.*关键清晰点|近处竹竿反向掠过|马鬃衣摆被风压向后|水花后抛|箭速" "video prompt requires visible and audible speed evidence"
require_pattern "skills/laohu_video_prompt/SKILL.md" "能力基线：世界允许的能力|超常物理：来源与发力|空气折射.*雨珠.*雾气.*竹叶.*衣料.*湿土.*石块.*竹根|大威力与高控制" "video prompt enforces grounded superhuman physics"
require_pattern "skills/laohu_video_prompt/SKILL.md" "多主体运动账本|世界起点.*屏幕起点.*朝向.*速度向量.*相对顺序.*出画顺序|世界坐标和屏幕相对运动" "video prompt enforces multi-subject motion continuity"
require_pattern "skills/laohu_video_prompt/SKILL.md" "事件传播账本|命中点与入射角|材料失效顺序|碎片大小分组与飞散锥|永久终态" "video prompt enforces event propagation continuity"
require_pattern "skills/laohu_vibe_creating_prompt/SKILL.md" "不能压缩或改乱多主体运动账本|世界 / 屏幕方向|相对顺序|摄影机速度 / 轴线|事件传播账本" "VC optimization preserves multi-subject and event-propagation constraints"
require_pattern "skills/laohu_generation_review/SKILL.md" "多主体运动连续性|无因倒退、超车、瞬移、换层|事件传播连续性|材料失效.*碎片落点" "generation review diagnoses multi-subject and event-propagation failures"
require_pattern "AGENTS.md" "人体姿势变换账本|原支撑点|肩胸骨盆|重心轨迹|旋转轴|首次落地接触点|缓冲 / 卸力顺序" "top-level rules define body-pose transition continuity"
require_pattern "skills/laohu_video_prompt/SKILL.md" "人体姿势变换账本|双脚先脱镫|手掌按在可承重的鞍桥 / 鞍座|骨盆离鞍|哪只脚 / 髋 / 前臂 / 肩依次落地" "video prompt expands body-pose transitions into visible phases"
require_pattern "skills/laohu_video_prompt/SKILL.md" "下一镜先重建主体、攻击来源、地面 / 道路边界和摄影机观看侧|帅点捕捉|危险逼近速度|提前半拍占位|接触瞬间让关键轮廓短暂清晰" "video prompt re-establishes action space and captures stylish beats"
require_pattern "AGENTS.md" "角色动作语法.*距离.*起势.*攻击线.*防守与借位.*场景.*回收.*能力边界|决定性瞬间.*动作段.*压迫段.*关系与情绪段" "top-level rules define character action grammar and decisive moments"
require_pattern "skills/laohu_video_prompt/SKILL.md" "角色动作语法卡.*能力等级.*距离偏好.*起势线索.*攻击几何.*防守 / 借位.*场景利用.*回收方式|上一招造成的遮挡、失衡、空位、掉落物或反作用力" "video prompt preserves character-specific continuous choreography"
require_pattern "skills/laohu_vibe_creating_prompt/SKILL.md" "不能删改角色动作语法|不能把攻击来路、逼近速度、提前占位、接触瞬间短暂清晰、结果高速余势和决定性瞬间" "VC optimization preserves action identity and stylish-beat evidence"
require_pattern "skills/laohu_generation_review/SKILL.md" "动作物理完整但不刺激、不像高手|角色动作语法、攻击来路、逼近加速、提前占位、接触瞬间短暂清晰、结果高速余势和决定性瞬间" "generation review diagnoses complete but unwatchable action"
require_pattern "skills/laohu_vibe_creating_prompt/SKILL.md" "不能在正式模型正文中重新加入.*镜头01 / 镜头02 / 镜头N|动作、遮挡、视线、焦点、声音、光色峰值和运动方向.*切换桥梁|姿势、道具状态、动作余势、空间方向和声场继承" "VC optimization preserves continuous shot bridges"
require_pattern "skills/laohu_generation_review/SKILL.md" "多镜头内容都正确但切换生硬|镜头01 / 镜头02.*独立切块|去掉正式正文编号.*动作 / 遮挡 / 视线 / 焦点 / 声音 / 运动方向" "generation review diagnoses isolated shot blocks"
require_pattern "skills/laohu_vibe_creating_prompt/SKILL.md" "不能把人体姿势变换账本|支撑点转换|重心 / 旋转轴|四肢净空|卸力顺序" "VC optimization preserves body-pose transition phases"
require_pattern "skills/laohu_generation_review/SKILL.md" "人体姿势变换连续性|动作名直接跳到结果|支撑转换.*关节链.*重心 / 旋转轴.*四肢净空.*落地卸力" "generation review diagnoses body-pose transition failures"
require_pattern "02_共享资产库/05_工具流程/助手执行失败经验与防复发规则.md" "### 120\. 运动路径正确不等于人物会表演动作|人体姿势变换账本|双脚依次抽出马镫|骨盆顶离鞍座|左脚外缘" "failure rules record body-pose transition correction"
require_pattern "02_共享资产库/05_工具流程/助手执行失败经验与防复发规则.md" "### 121\. 动作完整不等于有观赏性|角色动作语法决定|攻击空间决定|速度反差决定|决定性瞬间决定" "failure rules record action spectacle and identity correction"
require_pattern "02_共享资产库/05_工具流程/助手执行失败经验与防复发规则.md" "### 122\. 镜头内容正确不等于切换连续|连续镜头叙事|分镜表、预演板和内部导演判断可以保留镜头编号|删除编号只是第一步" "failure rules record continuous shot narrative correction"
require_pattern "01_作品项目/进行中/2026-07-15_一寸之外/05_视频/文本/2026-07-15_一体化视频执行单_一寸之外.md" "左脚和右脚依次从两侧马镫中抽出|骨盆被双臂推离鞍座|右腿屈膝后从马臀上方|右手先离开后鞍座|左脚外缘先斜擦湿土|刀鞘尾端斜向前上方" "current wuxia VID-01 locks body-pose phases and scabbard clearance"
require_pattern "01_作品项目/进行中/2026-07-15_一寸之外/05_视频/文本/2026-07-15_一体化视频执行单_一寸之外.md" "沈青棠是高段实战刀客|第一枚暗器随后从右上竹影|第二枚暗器以胸口高度从竹竿间射出|第三枚暗器从左后来路" "current wuxia VID-02 locks ability level and three attack origins"
require_pattern "01_作品项目/进行中/2026-07-15_一寸之外/05_视频/文本/2026-07-15_一体化视频执行单_一寸之外.md" "敌人起势加速、她提前半拍进入短路径|接触的一瞬立刻停止横移|上一击的余势直接变成下一次借竹起势|朝向右前的侧脸、贴肋横刀、后撞刀柄" "current wuxia group fight captures speed contrast and decisive moments"
if rg -n '^镜头[0-9]+｜|镜头01继续｜' "01_作品项目/进行中/2026-07-15_一寸之外/05_视频/文本/2026-07-15_一体化视频执行单_一寸之外.md" >/dev/null; then
  fail "current wuxia formal prompts must not use numbered shot labels"
else
  pass "current wuxia formal prompts use continuous shot narrative without numbered labels"
fi
require_pattern "01_作品项目/进行中/2026-07-15_一寸之外/05_视频/文本/2026-07-15_一体化视频执行单_一寸之外.md" "水花扫过前景形成短暂遮挡|落泥的闷响立即触发摄影机|肩背顺势贴满画面形成自然遮挡|金属轻鸣作为切换触发|第一滴泪滑到下颌时" "current wuxia prompts use visible and audible transition bridges"
require_pattern "skills/laohu_video_prompt/SKILL.md" "N 由观看任务决定|一个长镜头.*若干切镜.*快闪蒙太奇|镜头很多.*拆成多条素材后期剪辑" "video prompt chooses dynamic shot count and production mode"
require_pattern "skills/laohu_video_prompt/SKILL.md" "剧本.*语气 / 神态.*视频提示词|表情来源|表情占用时长|眼神.*眉头.*嘴角.*呼吸|POV.*手部.*呼吸.*声音" "video prompt inherits script demeanor annotations into visible performance"
require_pattern "skills/laohu_video_prompt/SKILL.md" "视频提示词不得擅自改剧本台词|台词原文.*旁白原文.*VO 原文.*字幕原文|不能改句子.*删关键词.*加新句|VID-27" "video prompt locks confirmed script dialogue"
require_pattern "skills/laohu_video_prompt/SKILL.md" "单点反馈.*全局扫描同类问题|指出某一个镜头.*默认.*通用失败模式|抽取剧本全部对白.*全分镜视频提示词" "video prompt enforces global scan after single-shot feedback"
require_pattern "02_共享资产库/01_模板库/视频模板/模板_视频提示词_基础设定氛围画面内容.md" "单点反馈必须触发全局同类扫描|台词问题扫所有对白.*VO.*OS.*画外音|POV 问题扫所有主观镜头|VID-27" "video prompt template enforces global scan after single-shot feedback"
require_pattern "skills/laohu_video_prompt/SKILL.md" "分镜表格输出文件|第一个分镜的视频提示词展示文件|所有分镜视频提示词结果输出文件|对话里不要贴长篇" "video prompt enforces staged file outputs"
require_pattern "skills/laohu_video_prompt/SKILL.md" "视频提示词交付必须方便老胡直接复制|代码块里只放可直接投喂视频模型|代码块外" "video prompt enforces copyable video prompt code blocks"
require_pattern "skills/laohu_video_prompt/SKILL.md" "镜头预演板.*给图片模型和人工|不强制生成预演板|不自动写成.*故事板参考|干净首帧 / 构图图" "video prompt treats storyboard as optional human-facing previsualization"
require_pattern "skills/laohu_video_prompt/SKILL.md" "镜头节奏|短切.*长镜头.*特写进.*跟踪镜头.*甩镜|文戏.*关键台词.*关系.*可见 / 可听后果|武戏.*力量来源.*运动路径.*接触点.*动作结果" "video prompt enforces contribution-based shot rhythm and dialogue/action systems"
require_pattern "02_共享资产库/01_模板库/视频模板/模板_视频生成质量检查清单.md" "节奏密度|文戏表演|武戏受力|镜头切换是否有任务" "video QA checklist includes director pacing, dialogue, action and cut-task checks"
require_pattern "skills/laohu_video_prompt/SKILL.md" "首帧参考@VID-A尾帧|同一景别.*构图.*光源方向.*人物姿态.*表情余韵.*背景锚点|不要写.*第0秒" "video prompt enforces tail-frame continuity in natural shot language"
require_pattern "skills/laohu_video_prompt/SKILL.md" "对镜头情绪表演|声音方向|镜头前方.*脑海|眼线.*镜头|风景只做留白" "video prompt enforces direct-to-camera emotional performance"
require_pattern "skills/laohu_video_prompt/SKILL.md" "默认在同一个阶段文件上迭代更新|不自动新建 v1/v2/v3" "video prompt enforces single-file iteration"
require_pattern "skills/laohu_generation_review/SKILL.md" "生成诊断|剪辑验收|发布复盘|最多 3 个返修动作|下一版修正提示词" "generation review covers merged review work"
require_pattern "skills/laohu_generation_review/SKILL.md" "灵感价值不够|故事引擎弱|节奏密度不够|文戏表演没写透|武戏动作没受力|镜头切换没任务|标题封面没有承接反转" "generation review diagnoses the full director chain"
require_pattern "skills/laohu_generation_review/SKILL.md" "节奏密度|文戏表演|武戏受力" "generation review scores pacing, dialogue performance and action force"
require_pattern "skills/laohu_generation_review/SKILL.md" "归档、复盘、生成结果诊断和发布复盘必须写入文件|生成复盘文件|发布复盘文件" "generation review enforces file output"
require_pattern "skills/laohu_generation_review/SKILL.md" "默认在同一个当前文件上更新|不自动新建 v1/v2/v3" "generation review enforces single-file iteration"
require_pattern "skills/laohu_generation_review/SKILL.md" "人物皮肤油|脸像塑料|人物身份和目标肤质|不把冷白、裸妆和柔雾奶油肌套给所有角色" "generation review diagnoses skin against identity and intended finish"
require_pattern "02_共享资产库/01_模板库/负面提示词模板/模板_通用负面提示词.md" "通用质量边界|正向正文负责生成目标|抽象质量边界|身份稳定|动作自然" "negative prompt template is downgraded to abstract positive quality boundaries"
require_pattern "02_共享资产库/00_核心规则手册.md" "正式视频提示词必须严格使用.*模板_视频提示词_基础设定氛围画面内容|不能混进正式视频提示词正文" "core manual enforces strict video prompt template"
require_pattern "02_共享资产库/00_核心规则手册.md" "镜头预演板 / 分镜预演图|低成本人审工具|不默认作为 Seedance 输入|干净首帧 / 构图参考图" "core manual defines optional human-facing shot previsualization"
require_pattern "02_共享资产库/00_核心规则手册.md" "角色自己的肤色、气色、妆效|冷白偏中性.*林栀|暖肤、深肤、晒痕" "core manual preserves character-specific complexion"
require_pattern "02_共享资产库/01_模板库/视频模板/模板_视频提示词_基础设定氛围画面内容.md" "角色自己的肤色、气色、妆效|地域、年龄、职业、年代、健康|冷白.*案例" "video prompt template preserves character-specific complexion"
require_pattern "02_共享资产库/05_工具流程/助手执行失败经验与防复发规则.md" "人物资产肤色会反向污染视频生成|角色自己的肤色|冷白.*案例" "failure rules record character-specific complexion lesson"
require_pattern "02_共享资产库/00_核心规则手册.md" "首帧参考@VID-A尾帧|同一景别.*构图.*光源方向.*人物姿态.*表情余韵.*背景锚点|不要写.*第0秒" "core manual enforces tail-frame continuity without timestamps"
require_pattern "02_共享资产库/00_核心规则手册.md" "对镜头情绪表演|镜头.*对话对象|声音方向|视线箭头指向镜头|风景.*不能成为主要表演对象" "core manual enforces direct-to-camera emotional performance"
require_pattern "02_共享资产库/00_核心规则手册.md" "每条正式视频提示词 = 一次独立投喂|不能写.*沿用全片|图片资产|15 秒内同场合并规则" "core manual enforces independent prompt and merge rules"
require_pattern "02_共享资产库/00_核心规则手册.md" "laohu_vibe_creating_prompt|视频提示词生成结果在输出呈现前|外部原文 skill|重新落回" "core manual enforces VC optimization pass"
require_pattern "02_共享资产库/00_核心规则手册.md" "转场不是.*后期备注|遮挡转场|明暗转场|运镜转场|匹配转场" "core manual enforces in-frame transitions"
require_pattern "02_共享资产库/00_核心规则手册.md" "画面内容.*详细度由镜头职责决定|主体、变化和主情绪证据|没有发生的内容不必补齐" "core manual scopes画面内容 detail by shot duty"
require_pattern "02_共享资产库/00_核心规则手册.md" "关键发声镜头不能只依赖.*【音色参考@xx】|短视频开场钩子.*本镜声线|冷感磁性女中音.*近麦干声" "core manual enforces key-voice shot timbre restatement"
require_pattern "02_共享资产库/00_核心规则手册.md" "台词、旁白、画外音和脑内 VO.*声音参数|音高 / 音区.*响度 / 音量.*语速 / 节奏.*停顿 / 气口.*重音位置.*气息状态.*咬字 / 吐字.*混响和衰减" "core manual enforces parameterized voice performance"
require_pattern "02_共享资产库/00_核心规则手册.md" "VO 是推动人物表情变化的主要触发器|按情绪阶段设计声音曲线|初识.*热恋.*平淡.*猜忌.*争吵.*决裂" "core manual enforces staged VO emotional curve"
require_pattern "02_共享资产库/00_核心规则手册.md" "人物情绪开场.*肌肉路径|单侧嘴角.*呼吸.*停顿|皮肤.*曝光.*雾面底妆.*真实毛孔|服装.*耳坠.*海风" "core manual enforces emotional portrait expression, skin and environment interaction"
require_pattern "02_共享资产库/00_核心规则手册.md" "正式视频提示词正文不能写作者意图|让观众懂|表现孩子不冷漠|防误读说明|生成流程解释|可见 / 可听证据" "core manual blocks author-intent and process explanations in formal prompts"
require_pattern "02_共享资产库/00_核心规则手册.md" "氛围与画质.*1-3 句|跨本条全部镜头|局部规则归属判断|只影响某一个镜头" "core manual keeps global vibe concise"
require_pattern "02_共享资产库/00_核心规则手册.md" "基础设定.*实际上传或绑定|人物、场景、道具、色卡、首帧、动作与音色参考|一句话写声音策略" "core manual limits basic setting to actual references"
require_pattern "02_共享资产库/00_核心规则手册.md" "左手特写.*右手特写|音色文字说明区|【形象参考@.*【音色参考@" "core manual enforces hand closeups and voice placeholders"
require_pattern "02_共享资产库/00_核心规则手册.md" "服装参考不能只继承单品名称|穿法逻辑.*视觉重心.*比例关系|鞋头形状.*闭口 / 露趾.*踝带.*跟高" "core manual enforces clothing styling logic and shoe design"
require_pattern "02_共享资产库/00_核心规则手册.md" "信息优先级.*三视图.*脸部特写.*全身比例图|手模级|十六进制 RGB|厘米测量线" "core manual enforces character asset layout information priority"
require_pattern "02_共享资产库/00_核心规则手册.md" "任何生成模型|正向描述目标结果|不能用排除句替代正向描述|抽象质量问题|代码块外" "core manual enforces positive model-facing prompt convergence"
require_pattern "02_共享资产库/00_核心规则手册.md" "可复制投喂正文.*text.*代码块|代码块的职责只有一个|视频提示词代码块只能包含" "core manual enforces copyable prompt code blocks"
require_pattern "02_共享资产库/00_核心规则手册.md" "提示词资产.*基础设定.*氛围与画质|图片资产 / 固定资产.*画面内容.*交互|未资产化画面元素.*画面内容.*详细描述|未资产化元素.*画面内容.*详细描述" "core manual enforces asset-aware画面内容 description budget"
require_pattern "02_共享资产库/00_核心规则手册.md" "【@资产名】|资产占位|固定实体|资产图片引用" "core manual supports explicit asset placeholders"
require_pattern "02_共享资产库/00_核心规则手册.md" "动作链|因果链|冲击结果|连锁反应|动作段落" "core manual enforces benchmark-level action choreography"
require_pattern "02_共享资产库/00_核心规则手册.md" "丁达尔效应|轮廓光|侧逆光|体积光|明暗交错" "core manual includes concrete lighting vocabulary"
require_pattern "skills/laohu_video_prompt/SKILL.md" "场景关系图|出场人物.*出场物品|人物和物品.*物品和物品.*人物和人物|交互方式.*接触点.*作用力大小轻重.*受力方向.*可见结果|光源位置.*光线方向.*照射对象" "video prompt skill enforces scene relationship, interaction force, motion and lighting causality"
require_pattern "02_共享资产库/00_核心规则手册.md" "场景关系图|出场人物.*出场物品|人物和物品.*物品和物品.*人物和人物|交互方式.*作用力大小轻重.*受力方向|光源位置.*光线方向.*照到谁" "core manual enforces scene relationship, interaction force, motion and lighting causality"
require_pattern "02_共享资产库/01_模板库/视频模板/模板_视频提示词_基础设定氛围画面内容.md" "场景关系图|出场人物.*出场物品|人物和物品.*物品和物品.*人物和人物|交互方式.*接触点.*作用力大小轻重.*方向.*可见结果|光源位置.*光线方向.*照射对象" "video prompt template enforces scene relationship, interaction force, motion and lighting causality"
require_pattern "02_共享资产库/01_模板库/视频模板/模板_视频提示词_基础设定氛围画面内容.md" "关键发声镜头不能只依赖.*【音色参考@xx】|本镜声线.*音区.*共鸣.*颗粒|停顿.*气口.*回响.*对应镜头" "video prompt template enforces shot-level key voice performance"
require_pattern "02_共享资产库/01_模板库/视频模板/模板_视频提示词_基础设定氛围画面内容.md" "台词、旁白、画外音和脑内 VO.*参数化|音高 / 音区.*响度 / 音量.*语速 / 节奏.*停顿 / 气口.*重音位置.*气息状态.*咬字 / 吐字.*混响和衰减" "video prompt template enforces parameterized voice performance"
require_pattern "02_共享资产库/02_视觉语言资产/声音与同期声库/声音提示词规范.md" "台词与 VO 表演参数|音高 / 音区.*响度 / 音量.*语速 / 节奏.*停顿 / 气口.*重音 / 强调.*气息 / 发声状态.*咬字 / 吐字.*距离 / 空间.*混响 / 衰减" "sound guide defines voice performance parameters"
require_pattern "02_共享资产库/01_模板库/视频模板/模板_视频提示词_基础设定氛围画面内容.md" "首帧参考@VID-A尾帧|相同景别.*构图.*光源方向.*人物姿态.*表情余韵.*背景锚点|不写.*第0秒" "video prompt template enforces tail-frame continuity in natural language"
require_pattern "02_共享资产库/01_模板库/视频模板/模板_视频提示词_基础设定氛围画面内容.md" "对镜头情绪表演规则|眼线箭头指向镜头中心|声音方向|看向海面|看向天空" "video prompt template enforces direct-to-camera storyboard and prompt checks"
require_pattern "02_共享资产库/05_工具流程/助手执行失败经验与防复发规则.md" "复杂画面先建立必要关系图|多人物、多物件、复杂空间或存在交互|单主体静态特写.*只锁定主体" "failure rules scope scene relationship maps to complex shots"
require_pattern "02_共享资产库/05_工具流程/助手执行失败经验与防复发规则.md" "多个 15 秒以内视频拼成一镜到底|首帧参考@上一条VID尾帧|自然语言.*同一景别.*构图.*光源方向.*人物姿态.*表情余韵.*背景锚点" "failure rules record tail-frame continuity without timestamps"
require_pattern "02_共享资产库/05_工具流程/助手执行失败经验与防复发规则.md" "关键发声和情绪开场不能只格式正确|冷感磁性女中音.*近麦干声|表情肌肉路径|雾面底妆.*真实毛孔|服装、首饰和环境必须参与情绪" "failure rules record key voice and emotional portrait detail"
require_pattern "02_共享资产库/05_工具流程/助手执行失败经验与防复发规则.md" "关键 VO 不能只写抽象情绪词|音高 / 音区.*响度 / 音量.*语速 / 节奏.*停顿 / 气口.*重音位置.*气息状态.*咬字 / 吐字.*距离感.*混响和衰减|男声温柔深情，带压迫感" "failure rules record parameterized VO performance regression"
require_pattern "02_共享资产库/05_工具流程/助手执行失败经验与防复发规则.md" "对镜头情绪表演不能写成看向风景或声音方向|镜头就是对话对象|从镜头位置进入她脑海|视线箭头指向镜头" "failure rules record direct-to-camera emotional performance regression"
require_pattern "skills/laohu_video_prompt/SKILL.md" "承担视觉记忆的镜头.*审美停点 / 情绪停点|功能型插入镜头.*不强制壁纸帧|只选择能承重的要素" "video prompt skill scopes aesthetic stopping points by shot duty"
require_pattern "02_共享资产库/00_核心规则手册.md" "承担人物第一眼、情绪峰值、段落记忆、封面候选或传播视觉职责|功能型插入镜头.*不强制壁纸帧|停点只选择真正承重" "core manual scopes aesthetic stopping points by shot duty"
require_pattern "02_共享资产库/01_模板库/视频模板/模板_视频提示词_基础设定氛围画面内容.md" "面向观众且承担视觉记忆的镜头.*审美停点|功能型镜头.*不强制壁纸帧|停点只保留加强主情绪" "video prompt template scopes aesthetic stopping points by shot duty"
require_pattern "02_共享资产库/01_模板库/视频模板/模板_视频生成质量检查清单.md" "功能型镜头.*不强制壁纸帧|停点是否只使用加强主情绪" "video QA checks stopping points by shot duty"
require_pattern "02_共享资产库/02_视觉语言资产/画面风格库/画面氛围与画质规范.md" "承担人物第一眼、情绪峰值、段落记忆、封面候选或传播视觉职责|功能型插入.*只需形成清楚可剪辑|不要求全部出现" "visual style guide scopes aesthetic stopping points by shot duty"
require_pattern "skills/laohu_video_prompt/SKILL.md" "构图承担主情绪或信息引导时|不要求每镜点名专业术语|失衡可以.*情绪" "video prompt skill selects composition by emotional duty"
require_pattern "02_共享资产库/00_核心规则手册.md" "构图承担主情绪、主体识别或关系展示时|只是候选.*不要求每镜点名术语|不强行腾出空白" "core manual selects composition by emotional duty"
require_pattern "02_共享资产库/01_模板库/视频模板/模板_视频提示词_基础设定氛围画面内容.md" "构图承担主情绪或视线引导时|不要求每镜点名构图术语|失衡可以是有意情绪手段" "video prompt template selects composition by emotional duty"
require_pattern "02_共享资产库/02_视觉语言资产/画面风格库/画面氛围与画质规范.md" "构图承担主情绪、主体识别或关系展示时|候选问题库.*不是必填清单|拥挤、遮挡和失衡.*服务" "visual style guide treats composition as conditional controls"
require_pattern "skills/laohu_video_prompt/SKILL.md" "光影承担主情绪、主体塑形或动作可读性时|不强制主光、辅光、轮廓光全部出现|单一硬光.*也可以成立" "video prompt skill selects lighting by emotional duty"
require_pattern "02_共享资产库/00_核心规则手册.md" "光影承担主情绪、主体塑形、动作可读性或连续性时|不强制主光、辅光、轮廓光|不规定.*层数" "core manual selects lighting by emotional duty"
require_pattern "02_共享资产库/01_模板库/视频模板/模板_视频提示词_基础设定氛围画面内容.md" "局部光影承担主情绪、动作可读性或空间变化时|不要求同时写光型.*丁达尔|自然光足够时" "video prompt template selects lighting by emotional duty"
require_pattern "02_共享资产库/02_视觉语言资产/画面风格库/画面氛围与画质规范.md" "光影承担主情绪、主体塑形、动作可读性或连续性时|自然光已经准确时|不规定层数" "visual style guide treats lighting as conditional controls"
require_pattern "skills/laohu_video_prompt/SKILL.md" "色彩承担主情绪、身份识别或连续性时|不是每镜都需要完整色彩体系|单色、近无色或自然综合色" "video prompt skill selects color by emotional duty"
require_pattern "02_共享资产库/00_核心规则手册.md" "色彩承担主情绪、身份识别或连续性时|不是每镜都需要完整色彩体系|黑白、近无色、单色" "core manual selects color by emotional duty"
require_pattern "02_共享资产库/01_模板库/视频模板/模板_视频提示词_基础设定氛围画面内容.md" "色彩承担情绪、身份或连续性时|单色、近无色和自然综合色可以成立|不强制完整调色体系" "video prompt template selects color by emotional duty"
require_pattern "02_共享资产库/02_视觉语言资产/画面风格库/画面氛围与画质规范.md" "色彩承担主情绪、身份识别或连续性时|黑白、单色、近无色和自然综合色|不默认低饱和等于高级" "visual style guide treats color as conditional controls"
require_pattern "skills/laohu_video_prompt/SKILL.md" "景深与空间层次承担主情绪、空间因果或注意力控制时|深景深、平面化和无前景.*有意选择|不强制前中后景齐全" "video prompt skill selects depth by emotional duty"
require_pattern "02_共享资产库/00_核心规则手册.md" "景深与空间层次承担主情绪、空间因果或注意力控制时|不强制前中后景齐全|不能为了层次遮住" "core manual selects depth by emotional duty"
require_pattern "02_共享资产库/02_视觉语言资产/画面风格库/画面氛围与画质规范.md" "景深与空间层次承担主情绪、空间因果或注意力控制时|深景深、平面化和无前景.*有意结果" "visual style guide treats depth as conditional controls"
require_pattern "02_共享资产库/00_核心规则手册.md" "画质与材质只围绕本镜主注意力目标和交付用途|快速连接镜头、梦境或主观失焦可以有意降低细节|不能把所有表面纹理" "core manual selects material detail by shot duty"
require_pattern "02_共享资产库/02_视觉语言资产/画面风格库/画面氛围与画质规范.md" "画质与材质围绕主注意力证据和交付用途|主观失焦和高速连接镜头可以有意牺牲|关键证据被无意模糊" "visual style guide treats material detail as conditional controls"
require_pattern "skills/laohu_video_prompt/SKILL.md" "氛围环境元素只有在加强主情绪、空间真实或动作反馈时|不是质量标配|没有来源或不承担情绪.*删除" "video prompt skill selects atmosphere by emotional duty"
require_pattern "02_共享资产库/00_核心规则手册.md" "氛围环境元素只有在加强主情绪、空间真实感或运动层次时|不是必填层|干净空气、静止背景和无特效环境" "core manual selects atmosphere by emotional duty"
require_pattern "02_共享资产库/02_视觉语言资产/画面风格库/画面氛围与画质规范.md" "氛围环境元素只有在加强主情绪、空间真实感或运动层次时|干净空气、静止背景和无微粒环境" "visual style guide treats atmosphere as conditional controls"
require_pattern "02_共享资产库/00_核心规则手册.md" "镜头运动先服务观看意图和主情绪|稳定画面、持续运动、故意失衡或短促颠簸都可以成立|停留时间.*倒推" "core manual selects camera motion by emotional duty"
require_pattern "02_共享资产库/02_视觉语言资产/画面风格库/画面氛围与画质规范.md" "镜头运动先服务观看意图和主情绪|持续运动、稳定凝视、故意失衡和短促颠簸都可以成立|不把静态截图当唯一标准" "visual style guide treats camera motion as conditional controls"
require_pattern "02_共享资产库/05_工具流程/助手执行失败经验与防复发规则.md" "专业字段不是必填清单|情绪承重项、生成必需项、专业展示项|满足触发条件才启用" "failure rules record system-wide field-packing correction"
require_pattern "02_共享资产库/00_核心规则手册.md" "没有项目统一字数目标和硬上限|默认不精简、不主动压缩|最高质量和最高有效信息密度" "core manual prioritizes complete high-density prompts over project length limits"
require_pattern "02_共享资产库/00_核心规则手册.md" "连续镜头叙事|正式模型正文.*不写.*镜头编号|动作.*遮挡.*视线.*焦点.*声音.*光色峰值.*运动方向|总时长.*平台参数" "core manual uses continuous shot narrative without labels or timestamps"
require_pattern "02_共享资产库/00_核心规则手册.md" "高速物体和复杂调度必须通过空间闭环检查|场景坐标与通行净空|主体感知时点|避让方向|最终出画 / 撞击位置|撞击目标不承担剧情时" "core manual enforces projectile spatial closure"
require_pattern "02_共享资产库/00_核心规则手册.md" "状态账本.*进入状态.*触发.*接触部位.*操作路径.*中间状态.*结果状态|知觉账本.*客观事件|观众信息账本.*领先.*同步.*落后" "core manual enforces state, perception and audience-information ledgers"
require_pattern "02_共享资产库/00_核心规则手册.md" "速度证据不能由.*高速.*疾驰.*迅速.*突然.*独自承担|近景反向掠过|中远景视差|摄影机惯性与低频震动" "core manual requires embodied speed evidence"
require_pattern "02_共享资产库/00_核心规则手册.md" "能力基线真实|超常物理真实|刀气、剑气、冲击波、念力、激光|空气折射.*雨珠.*竹叶.*湿土.*石块.*竹根" "core manual enforces grounded superhuman physics"
require_pattern "02_共享资产库/00_核心规则手册.md" "多主体运动账本|世界坐标起点.*屏幕坐标起点.*朝向.*速度向量.*相对顺序.*出画顺序|摄影机.*速度.*轴线" "core manual enforces multi-subject motion continuity"
require_pattern "02_共享资产库/00_核心规则手册.md" "事件传播账本|命中点 / 入射角|材料失效顺序|碎片分组、速度锥和落点|永久终态" "core manual enforces event propagation continuity"
require_pattern "02_共享资产库/00_核心规则手册.md" "N 没有固定上限.*观看任务决定|长镜头.*少量切镜.*快闪蒙太奇|精确多切.*后期剪辑" "core manual chooses dynamic shot count and production mode"
require_pattern "02_共享资产库/00_核心规则手册.md" "剧本.*语气 / 神态.*下游|表情来源|人物表演库|眼神.*眉头.*嘴角.*呼吸|POV.*手部.*呼吸.*声音" "core manual inherits script demeanor annotations downstream"
require_pattern "02_共享资产库/00_核心规则手册.md" "视频提示词阶段不得擅自改剧本台词|台词原文.*旁白原文.*VO 原文.*字幕原文|原文照搬 \\+ 表演状态|VID-27" "core manual locks confirmed script dialogue downstream"
require_pattern "02_共享资产库/00_核心规则手册.md" "单点反馈必须触发全局同类扫描|默认.*同类问题的样本|台词问题扫所有对白 / VO / OS|VID-27.*其他 38 条" "core manual enforces global scan after single-point feedback"
require_pattern "02_共享资产库/00_核心规则手册.md" "正式产物默认不直接塞在聊天里，必须写成文件|标准阶段门|00_阶段确认记录|对话里不要输出很长" "core manual enforces file-backed stage gates"
require_pattern "02_共享资产库/00_核心规则手册.md" "具体结果文件链接|不能只给目录链接|只有老胡明确说.*目录" "core manual enforces direct result file links"
require_pattern "02_共享资产库/00_核心规则手册.md" "资产 = 需要复用和一致性锁定|画面元素 = 只在单个镜头|不默认叫资产" "core manual defines reusable assets vs one-off elements"
require_pattern "02_共享资产库/00_核心规则手册.md" "确定性命名规则|剧本显示称呼.*生产命名.*资产编号|群仙.*群体类别|神兽.*生物类别" "core manual enforces deterministic naming before assets"
require_pattern "02_共享资产库/00_核心规则手册.md" "图片资产：用图片固定具体形象|文本资产 / 提示词资产：用文字固定氛围" "core manual defines image assets and text prompt assets"
require_pattern "02_共享资产库/00_核心规则手册.md" "人物素体资产|人物定装资产|服装 / 妆造资产|组合形象资产|场景图片资产|物品图片资产" "core manual defines detailed asset subtypes"
require_pattern "02_共享资产库/00_核心规则手册.md" "A1 = 人物素体资产|A2 = 服装 / 妆造资产|A3 = A1 穿着 A2" "core manual defines asset composition numbering"
require_pattern "02_共享资产库/00_核心规则手册.md" "00_原始输入.*01_世界观故事.*02_剧本.*03_视觉资产.*04_分镜.*05_视频|文本 / 图片 / 视频 / 音频" "core manual enforces staged media project directories"
require_pattern "02_共享资产库/00_核心规则手册.md" "每个阶段默认只维护一个当前输出文件|不要自动新建.*v1|文件命名默认不带版本号" "core manual enforces single-file iteration"
require_pattern "skills/laohu_ai_visual/scripts/create_work_project.sh" "00_阶段确认记录.md|灵感沟通|剧本结果输出文件|所有分镜视频提示词结果输出文件|制作完成后封面" "new project script creates staged confirmation record"
require_pattern "AGENTS.md" "00_阶段确认记录.md|00_首轮验证看板.md|00_原始输入|01_世界观故事|02_剧本|03_视觉资产|04_分镜|05_视频" "top-level rules document numbered work project structure"
require_pattern "AGENTS.md" "结果交付链接规则|具体结果文件链接|不能只给目录链接|只有老胡明确说.*目录" "top-level rules enforce direct result file links"
require_pattern "AGENTS.md" "角色与资产确定性命名|生产命名|大人.*主角|群仙.*不应被当作一个固定人物资产|神兽.*类别" "top-level rules enforce deterministic role and asset naming"
require_pattern "AGENTS.md" "口述故事.*创意留白.*编剧主动补全|互相排斥的核心故事方向.*一次追问一个最关键问题" "top-level rules separate oral-story facts from creative gaps"
require_pattern "02_共享资产库/00_核心规则手册.md" "创意留白.*编剧主动补全并记录|互相排斥的核心方向.*才进入逐项追问" "core manual separates oral-story facts from creative gaps"
require_pattern "skills/laohu_script_writer/SKILL.md" "已明确事实、可自主补全的创意留白、确实互斥的核心问题|创意留白由编剧主动完成并记录|只有互斥核心问题.*一次追问一个关键问题" "script writer actively completes oral-story creative gaps"
require_pattern "02_共享资产库/05_工具流程/助手执行失败经验与防复发规则.md" "口述故事不能直接套剧本.*创意留白应由编剧主动补完|硬约束 / 创意补全 / 仍需人工取舍" "failure rules record calibrated oral-story autonomy"
require_pattern "02_共享资产库/00_核心规则手册.md" "台词口气与方言|重庆话|川渝口语|书面普通话" "core manual enforces dialect oral dialogue"
require_pattern "02_共享资产库/00_核心规则手册.md" "结尾片名.*静态画面|物件动作.*环境运动.*镜头运动|轻物.*拉高" "core manual enforces image-born ending titles"
require_pattern "skills/laohu_script_writer/SKILL.md" "结尾片名.*画面动作|木轮.*枯叶 / 纸灰|镜头.*拉高|片名.*情绪命名" "script writer enforces image-born ending titles"
require_pattern "02_共享资产库/00_核心规则手册.md" "已确认设定默认必须保留|没有明确拒绝.*不能.*删掉|故事确认文件.*阶段确认记录" "core manual protects confirmed settings during rewrites"
require_pattern "skills/laohu_script_writer/SKILL.md" "保护已确认设定|没有明确拒绝.*默认仍然有效|从小没了妈" "script writer protects confirmed settings during rewrites"
require_pattern "skills/laohu_script_writer/SKILL.md" "台词口气与方言|重庆话|川渝口语|书面普通话" "script writer enforces dialect oral dialogue"
require_pattern "02_共享资产库/05_工具流程/助手执行失败经验与防复发规则.md" "台词不能写成书面普通话|重庆话 / 川渝口语|地域、年龄、文化程度" "failure rules record dialect oral dialogue"
require_pattern "02_共享资产库/00_核心规则手册.md" "情感因果链|误解 / 嫌弃|愿望 / 缺口|亲人记住|遗物回收" "core manual enforces family regret emotional causality"
require_pattern "skills/laohu_script_writer/SKILL.md" "情感因果链|误解 / 嫌弃|愿望 / 缺口|亲人记住|遗物回收" "script writer enforces family regret emotional causality"
require_pattern "02_共享资产库/05_工具流程/助手执行失败经验与防复发规则.md" "亲情遗憾故事不能写成温馨素材堆叠|情感因果链|缺点引爆|遗物回收" "failure rules record family regret emotional causality"
require_pattern "02_共享资产库/00_核心规则手册.md" "情绪台词不能像完成任务|生活动作|环境阻力|打火机几次打不燃|纸房飘带" "core manual enforces emotion staging through action and environment"
require_pattern "02_共享资产库/00_核心规则手册.md" "工具劳动动作|工作面.*工具.*材料.*受力.*结果.*收尾位置|劈柴.*木墩|斧刃卡住" "core manual enforces tool-labor material causality"
require_pattern "skills/laohu_video_prompt/SKILL.md" "工具劳动动作|工作面.*工具.*材料.*受力.*收尾位置|劈柴.*木墩|斧刃卡住" "video prompt skill enforces tool-labor material causality"
require_pattern "02_共享资产库/01_模板库/视频模板/模板_视频提示词_基础设定氛围画面内容.md" "工具劳动动作|工作面.*工具.*材料.*受力.*结果.*收尾位置|劈柴.*木墩|斧刃卡" "video prompt template enforces tool-labor material causality"
require_pattern "02_共享资产库/05_工具流程/助手执行失败经验与防复发规则.md" "工具劳动动作必须写工作面、受力和材料变化|父亲在柴堆上劈柴|短柴竖在木墩" "failure rules record tool-labor material causality"
require_pattern "02_共享资产库/00_核心规则手册.md" "歧义动作必须写清工具、接触方式和顺序|工具 \\+ 手 \\+ 材料 \\+ 接触面 \\+ 顺序 \\+ 结果|小木勺.*黑芝麻馅.*手指只接触白糯米皮" "core manual enforces ambiguous action tool/contact sequencing"
require_pattern "skills/laohu_video_prompt/SKILL.md" "歧义动作必须写清工具、接触方式和顺序|加一点.*取一点.*放进去.*抹上去|小木勺.*黑芝麻馅.*手指只接触白糯米皮" "video prompt skill enforces ambiguous action tool/contact sequencing"
require_pattern "02_共享资产库/01_模板库/视频模板/模板_视频提示词_基础设定氛围画面内容.md" "歧义动作必须写清工具、接触方式和顺序|工具.*材料.*接触面.*顺序.*结果|小木勺.*黑芝麻馅.*手指只接触白糯米皮" "video prompt template enforces ambiguous action tool/contact sequencing"
require_pattern "02_共享资产库/05_工具流程/助手执行失败经验与防复发规则.md" "歧义动作必须写工具和接触方式|加一点黑芝麻馅|小木勺.*勺背.*手指只接触糯米皮" "failure rules record ambiguous action tool/contact sequencing"
require_pattern "02_共享资产库/00_核心规则手册.md" "人物资产必须区分稳定身份、固定定装、场景配件和动作道具|书包.*放学路 / 报丧|不背书包" "core manual enforces character asset accessory separation"
require_pattern "skills/laohu_visual_assets/SKILL.md" "稳定身份、固定定装、场景配件和动作道具|A5 姐姐.*书包.*放学路 / 报丧|不能成为.*常驻外观" "visual assets skill enforces accessory separation"
require_pattern "skills/laohu_video_prompt/SKILL.md" "人物资产里的场景配件不能被机械继承|A5 姐姐.*E1-S6.*不背书包|E1-S9.*书包滑落" "video prompt skill enforces per-shot accessory state"
require_pattern "02_共享资产库/05_工具流程/助手执行失败经验与防复发规则.md" "人物资产里的场景配件不能常驻化|A5 姐姐.*书包|元宵包汤圆.*不背书包" "failure rules record accessory separation"
require_pattern "02_共享资产库/00_核心规则手册.md" "冲突动作必须有前置动机、靠近路径和身体位置|爷爷先撑桌起身|弯腰想擦眼泪" "core manual enforces conflict action setup and body causality"
require_pattern "skills/laohu_video_prompt/SKILL.md" "冲突动作必须补齐前置动机、靠近路径和身体受力|E1-S7-C3.*弯腰拿小布巾擦眼泪|跌坐柴火边" "video prompt skill enforces conflict action setup and body causality"
require_pattern "02_共享资产库/01_模板库/视频模板/模板_视频提示词_基础设定氛围画面内容.md" "冲突动作必须有前置动机、靠近路径和身体受力|推开.*抢夺.*摔倒|小布巾.*擦眼泪" "video prompt template enforces conflict action setup and body causality"
require_pattern "02_共享资产库/05_工具流程/助手执行失败经验与防复发规则.md" "冲突动作必须有前置动机和身体位置|爷爷撑桌起身|小布巾.*擦眼泪|脚跟撞到右侧小木凳" "failure rules record conflict action setup and body causality"
require_pattern "02_共享资产库/05_工具流程/助手执行失败经验与防复发规则.md" "视频提示词不得擅自改剧本台词|小安（还记着）：长大了就没人管我了|爷爷（缓慢认真）：哪个说的|VID-27 已改回剧本原台词" "failure rules record script dialogue lock failure"
require_pattern "02_共享资产库/05_工具流程/助手执行失败经验与防复发规则.md" "正式提示词正文不能写作者意图、观众理解说明和流程解释|画面让观众懂孩子不懂|禁止把小安拍成冷漠|模型不知道上下文|屏幕证据" "failure rules record author-intent and process explanation failure"
require_pattern "skills/laohu_video_prompt/SKILL.md" "镜头主语.*导演语言|镜头中出现|镜头固定在|镜头推进到|镜头摇移到|镜头下压到|镜头抬起后|镜头被.*遮满" "video prompt skill enforces camera-subject director language"
require_pattern "02_共享资产库/00_核心规则手册.md" "镜头主语.*导演语言|镜头中出现|镜头固定在|镜头推进到|镜头摇移到|镜头下压到|镜头抬起后|镜头被.*遮满" "core manual enforces camera-subject director language"
require_pattern "02_共享资产库/05_工具流程/助手执行失败经验与防复发规则.md" "视频提示词要优先使用镜头主语的导演语言|镜头中出现|镜头下压到|镜头被.*遮满|镜头后方传来" "failure rules record camera-subject director language"
require_pattern "02_共享资产库/02_视觉语言资产/镜头语言库/镜头语言词典.md" "四类开放控制杆.*不是每镜四项必填" "shot language dictionary treats camera controls as optional levers"
require_pattern "skills/laohu_video_prompt/SKILL.md" "四类控制杆.*不把它们当四项必填" "video prompt skill treats camera controls as optional levers"
require_pattern "02_共享资产库/00_核心规则手册.md" "四类镜头控制杆.*不是四项必填" "core manual treats camera controls as optional levers"
require_pattern "02_共享资产库/01_模板库/视频模板/模板_视频提示词_基础设定氛围画面内容.md" "四类控制杆.*不把它们当四项必填" "video prompt template treats camera controls as optional levers"
require_pattern "02_共享资产库/05_工具流程/助手执行失败经验与防复发规则.md" "景别、机位、运镜和光学质感.*只把对本镜目的有贡献的选择写进正文" "failure rules record optional camera-control selection"
require_pattern "输入输出索引.md" "四类开放控制杆.*不要求四项齐全" "index records optional camera-control selection"
require_pattern "02_共享资产库/02_视觉语言资产/镜头语言库/镜头语言词典.md" "内部检索表.*不是保证每条都填满" "shot language dictionary treats layers as a question bank"
require_pattern "skills/laohu_video_prompt/SKILL.md" "开放问题库.*不.*逐层检查齐全" "video prompt skill treats layers as a question bank"
require_pattern "02_共享资产库/00_核心规则手册.md" "开放问题库.*不.*逐层检查齐全" "core manual treats layers as a question bank"
require_pattern "02_共享资产库/01_模板库/视频模板/模板_视频提示词_基础设定氛围画面内容.md" "开放问题库.*不.*逐层检查齐全" "video prompt template treats layers as a question bank"
require_pattern "02_共享资产库/05_工具流程/助手执行失败经验与防复发规则.md" "开放问题库.*不按固定顺序逐层填满" "failure rules record contribution-based layer selection"
require_pattern "输入输出索引.md" "开放问题库.*不逐层填满" "index records contribution-based layer selection"
require_pattern "02_共享资产库/02_视觉语言资产/镜头语言库/镜头语言词典.md" "专业运镜术语扩展|Dolly / Track.*机身整体移动|Pan / Tilt.*原地转动|希区柯克.*机身向前推进.*光学变焦拉远.*主体大小基本保持不变.*背景空间拉伸畸变" "shot language dictionary records professional camera movement mechanics"
require_pattern "skills/laohu_video_prompt/SKILL.md" "专业运镜术语必须先区分物理机制|Dolly / Track.*机身整体移动|Pan / Tilt.*原地转动|希区柯克变焦.*机身向前推进.*光学变焦拉远" "video prompt skill enforces professional camera movement mechanics"
require_pattern "02_共享资产库/00_核心规则手册.md" "专业运镜术语必须先区分物理机制|Dolly / Track.*机身整体移动|Pan / Tilt.*原地转动|希区柯克变焦.*机身向前推进.*光学变焦拉远" "core manual enforces professional camera movement mechanics"
require_pattern "02_共享资产库/01_模板库/视频模板/模板_视频提示词_基础设定氛围画面内容.md" "专业运镜术语必须先区分物理机制|Dolly / Track.*机身整体移动|Pan / Tilt.*原地转动|希区柯克变焦.*机身向前推进.*光学变焦拉远" "video prompt template enforces professional camera movement mechanics"
require_pattern "02_共享资产库/05_工具流程/助手执行失败经验与防复发规则.md" "专业运镜术语必须先区分物理机制|Dolly / Track / Tracking Dolly 是机身整体移动|希区柯克变焦 / Vertigo Shot 必须同时写.*机身向前推进.*光学变焦拉远" "failure rules record professional camera movement mechanics"
require_pattern "输入输出索引.md" "专业运镜术语.*Dolly / Track.*机身整体移动|Pan / Tilt.*原地转动|希区柯克变焦必须同时写机身向前推进.*光学变焦拉远.*主体大小基本保持不变.*背景空间拉伸畸变" "index records professional camera movement mechanics"
require_pattern "02_共享资产库/00_核心规则手册.md" "镜头预演板 / 分镜预演图|给导演、作者和生成操作者|镜头 / 关键画面|不默认作为 Seedance 输入" "core manual defines human-facing shot previsualization"
require_pattern "skills/laohu_visual_assets/SKILL.md" "低保真故事板不属于图片资产|不调用具体资产图|火柴人或简化剪影|几何块|04_分镜/文本" "visual assets skill separates low-fidelity storyboard from image assets"
require_pattern "skills/laohu_video_prompt/SKILL.md" "镜头预演板.*同源但服务对象不同|给图片模型和人工|不强制生成预演板|干净首帧 / 构图图" "video prompt skill treats previsualization as optional human review"
require_pattern "02_共享资产库/01_模板库/视频模板/模板_视频提示词_基础设定氛围画面内容.md" "配套镜头预演板提示词模板|导演和作者审片|不是 Seedance 默认输入|镜头 / 关键画面" "video prompt template defines human-facing previsualization"
require_pattern "02_共享资产库/01_模板库/视频模板/模板_视频生成质量检查清单.md" "镜头预演板|默认给人审|干净首帧 / 构图参考图|无表格、无箭头、无文字" "video QA checklist checks human-facing previsualization and clean model reference"
require_pattern "02_共享资产库/05_工具流程/laohu_skills核心合约.md" "镜头预演板交接包|VID 编号|使用镜头节点|人审内容.*构图 / 景别 / 机位|不锁内容.*人物外观|干净首帧 / 构图参考图" "core skill contract defines human-facing previsualization handoff"
require_pattern "02_共享资产库/05_工具流程/剧本到AI视觉资产转换规则.md" "镜头预演板也不进入资产表|04_分镜/文本|默认不作为 Seedance 输入|镜头 / 关键画面|干净首帧 / 构图参考图" "asset conversion rules define previsualization as non-asset human review"
require_pattern "02_共享资产库/05_工具流程/助手执行失败经验与防复发规则.md" "Seedance 2 提示词要按导演镜头组织|镜头预演板.*默认给人审构图|不自动作为 Seedance 输入|干净首帧 / 构图参考图" "failure rules record Seedance shot-language and previsualization workflow"
require_pattern "02_共享资产库/02_视觉语言资产/镜头语言库/镜头语言词典.md" "POV 光学质感从角色此刻能看见多少|焦段与景深不负责证明 POV|不固定.*人眼等效" "shot language dictionary selects POV optics by perception"
require_pattern "skills/laohu_video_prompt/SKILL.md" "严格 POV 不只贴.*标签.*不套全字段公式|具体人物.*画面呈现.*眼前所见|选择足以证明来源的证据" "video prompt skill enforces sufficient POV evidence"
require_pattern "02_共享资产库/00_核心规则手册.md" "严格 POV 只有一个不可省略的功能条件|开放证据链|POV 前景锚点是高效证据之一，不是每镜必填" "core manual enforces contribution-based POV evidence"
require_pattern "02_共享资产库/01_模板库/视频模板/模板_视频提示词_基础设定氛围画面内容.md" "严格 POV 必须证明画面来源，但不套全字段公式|POV 前景锚点是候选证据，不是每镜必填" "video prompt template enforces contribution-based POV evidence"
require_pattern "02_共享资产库/05_工具流程/助手执行失败经验与防复发规则.md" "POV 不是标签，必须有足够的画面来源证据|不要求全部出现|小安床上 POV" "failure rules record sufficient POV evidence"
require_pattern "输入输出索引.md" "严格 POV 不能只写标签|选择足够的来源证据|前景锚点、环境光影、焦段和景深都不是全体必填" "index records contribution-based POV evidence"
require_pattern "skills/laohu_video_prompt/SKILL.md" "严格 POV 不能用群体外部关系词|姐弟俩|村民看到姐弟俩|画面下方两只小手" "video prompt blocks external relation nouns in strict POV"
require_pattern "02_共享资产库/00_核心规则手册.md" "严格 POV 不能用群体外部关系词|姐弟俩|村民看到姐弟俩|两只小手伸出去" "core manual blocks external relation nouns in strict POV"
require_pattern "02_共享资产库/05_工具流程/助手执行失败经验与防复发规则.md" "严格 POV 不能写外部关系词和第三人称动作摘要|村民看到姐弟俩|小安弯腰把姐姐书包抱起来" "failure rules record external relation noun POV failure"
require_pattern "skills/laohu_video_prompt/SKILL.md" "遮挡式时间跳切本质上是遮挡转场|满屏遮挡转场点|旧墙、白布、桌面、蒲团位置不变|只有桌中央黑白遗像从爷爷换成奶奶" "video prompt skill enforces occlusion-transition time-jump evidence"
require_pattern "02_共享资产库/00_核心规则手册.md" "遮挡转场|蒲团纹理满屏|旧墙、白布、桌面、蒲团位置保持不变|只有桌中央黑白遗像从爷爷换成奶奶" "core manual enforces occlusion-transition time-jump evidence"
require_pattern "02_共享资产库/05_工具流程/助手执行失败经验与防复发规则.md" "遮挡式时间跳切要写成遮挡转场|蒲团纹理遮满画面形成遮挡转场|旧墙、白布、桌面、蒲团位置都和低头前保持一致" "failure rules record occlusion-transition time-jump failure"
require_pattern "skills/laohu_video_prompt/SKILL.md" "严格 POV 不能把.*正面 / 背面 / 侧面 / 正面构图.*接在 POV 主体后面|面向遗像桌方向|视线停在爷爷遗像上" "video prompt skill blocks POV subject front/side/back ambiguity"
require_pattern "02_共享资产库/00_核心规则手册.md" "严格 POV 不能把.*正面 / 背面 / 侧面 / 正面构图.*接在 POV 主体后面|面向遗像桌方向|视线停在爷爷遗像上" "core manual blocks POV subject front/side/back ambiguity"
require_pattern "02_共享资产库/05_工具流程/助手执行失败经验与防复发规则.md" "严格 POV 不能把正面 / 侧面 / 背面写成视点主体视角|小安第一人称 POV 低视线正面|面向遗像桌方向的低视线构图" "failure rules record POV subject front/side/back ambiguity"
require_pattern "skills/laohu_video_prompt/SKILL.md" "旧话 VO 可以视觉化为二次曝光 / 三重曝光记忆层|现实层.*曝光层|E1-S11-C2.*P11 半成品木马车架现实层.*爷爷半透明记忆层二次曝光" "video prompt skill enforces double/triple exposure memory layers"
require_pattern "02_共享资产库/00_核心规则手册.md" "曝光记忆层|二次曝光层|三重曝光层|E1-S10-C4.*火盆纸钱.*E1-S11-C2.*P11 半成品木马车架现实层.*二次曝光" "core manual enforces double/triple exposure memory layers"
require_pattern "02_共享资产库/05_工具流程/助手执行失败经验与防复发规则.md" "旧话回响可以用二次曝光 / 三重曝光变成画面事件|现实层.*讲话人记忆层|E1-S11-C2.*P11 半成品木马车架现实层.*爷爷半透明影像二次曝光" "failure rules record double/triple exposure memory layers"
require_pattern "02_共享资产库/00_核心规则手册.md" "病床触碰动作必须做床侧、输液侧和可达性排练|小安站在旧木床靠输液手这一侧|不翻身.*不抬另一只远侧手" "core manual enforces sickbed touch physical reachability"
require_pattern "skills/laohu_video_prompt/SKILL.md" "病床触碰动作必须做床侧、输液侧和可达性排练|输液针扎在哪只手|不翻身.*不抬另一只远侧手" "video prompt skill enforces sickbed touch physical reachability"

if python3 - <<'PY'
from pathlib import Path
import re

path = Path("01_作品项目/进行中/2026-06-18_不想长大/05_视频/文本/2026-06-19_视频提示词_全分镜_不想长大.md")
if not path.exists():
    raise SystemExit(0)

text = path.read_text()
blocks = re.findall(r"```text\n(.*?)```", text, flags=re.S)
bad_patterns = [
    r"让观众懂",
    r"观众理解",
    r"避免误读",
    r"表现[^。\n]*不是[^。\n]*冷漠",
    r"不是冷漠",
    r"禁止把[^。\n]*拍成[^。\n]*",
    r"禁止让观众",
    r"模型不知道上下文",
    r"模型不知[^。\n]*上下文",
    r"发给模型",
    r"投喂给模型",
    r"独立生成",
    r"单条提示词",
]
bad = []
for i, block in enumerate(blocks, 1):
    for pattern in bad_patterns:
        for m in re.finditer(pattern, block):
            line = block[:m.start()].count("\n") + 1
            bad.append(f"code block {i}, line {line}: {m.group(0)}")

if bad:
    print(f"{path}: formal video prompt contains author-intent / viewer-understanding explanation:")
    for item in bad:
        print(item)
    raise SystemExit(1)
PY
then
  pass "current formal video prompt has no author-intent / viewer-understanding explanation phrases"
else
  fail "current formal video prompt contains author-intent / viewer-understanding explanation phrases"
fi

if python3 - <<'PY'
from pathlib import Path
import re

path = Path("01_作品项目/进行中/2026-06-18_不想长大/05_视频/文本/2026-06-19_视频提示词_全分镜_不想长大.md")
if not path.exists():
    raise SystemExit(0)

text = path.read_text()
blocks = re.findall(r"```text\n(.*?)```", text, flags=re.S)
bad_patterns = [
    r"姐弟俩",
    r"父子俩",
    r"小安和姐姐",
    r"村民看到",
    r"看到姐弟俩",
    r"小安弯腰",
    r"小安抱",
    r"小安追(上|着|姐姐|过去|出去|向)",
]
bad = []
for i, block in enumerate(blocks, 1):
    if "小安第一人称 POV" not in block:
        continue
    for pattern in bad_patterns:
        for m in re.finditer(pattern, block):
            line = block[:m.start()].count("\n") + 1
            bad.append(f"code block {i}, line {line}: {m.group(0)}")

if bad:
    print(f"{path}: strict POV block contains external relation noun or third-person action summary:")
    for item in bad:
        print(item)
    raise SystemExit(1)
PY
then
  pass "current strict POV prompt blocks avoid external relation nouns and third-person action summaries"
else
  fail "current strict POV prompt blocks contain external relation nouns or third-person action summaries"
fi

if python3 - <<'PY'
from pathlib import Path
import re

path = Path("01_作品项目/进行中/2026-06-18_不想长大/05_视频/文本/2026-06-19_视频提示词_全分镜_不想长大.md")
if not path.exists():
    raise SystemExit(0)

text = path.read_text()
blocks = re.findall(r"```text\n(.*?)```", text, flags=re.S)
bad_patterns = [
    r"同一构图变成奶奶黑白遗像",
    r"黑白照片变成了奶奶",
    r"抬头后[^。\n]*变成奶奶",
    r"袖口更长",
    r"袖口已经换成",
    r"手掌比刚才",
    r"供品位置换",
    r"白布垂得更低",
    r"旧墙边多了一层",
    r"视线高度都有变化",
]
bad = []
for i, block in enumerate(blocks, 1):
    if "E1-S10-C2" not in text and "奶奶黑白遗像" not in block:
        continue
    for pattern in bad_patterns:
        for m in re.finditer(pattern, block):
            line = block[:m.start()].count("\n") + 1
            bad.append(f"code block {i}, line {line}: {m.group(0)}")

if bad:
    print(f"{path}: occlusion time-jump prompt still uses direct transformation wording:")
    for item in bad:
        print(item)
    raise SystemExit(1)
PY
then
  pass "current funeral time-jump prompt avoids direct portrait-transformation wording"
else
  fail "current funeral time-jump prompt still uses direct portrait-transformation wording"
fi

if python3 - <<'PY'
from pathlib import Path
import re

path = Path("01_作品项目/进行中/2026-06-18_不想长大/05_视频/文本/2026-06-19_视频提示词_全分镜_不想长大.md")
if not path.exists():
    raise SystemExit(0)

text = path.read_text()
m = re.search(r"## VID-32｜E1-S10-C2｜.*?(?=\n## VID-|\Z)", text, flags=re.S)
if not m:
    print(f"{path}: missing VID-32 / E1-S10-C2 block")
    raise SystemExit(1)
block = m.group(0)
required = [
    "白色孝布在画面上沿压住一点视线",
    "满屏蒲团纹理停住半拍",
    "形成遮挡转场",
    "旧墙、白布、桌面、蒲团前沿位置都和遮挡前一致",
    "桌中央同一木框位置里呈现奶奶黑白遗像",
]
missing = [item for item in required if item not in block]
if missing:
    print(f"{path}: VID-32 occlusion transition is missing required anchors:")
    for item in missing:
        print(item)
    raise SystemExit(1)
PY
then
  pass "VID-32 occlusion transition preserves scene anchors and changes only portrait subject"
else
  fail "VID-32 occlusion transition missing stable scene anchors or portrait-only change"
fi

if python3 - <<'PY'
from pathlib import Path
import re

path = Path("01_作品项目/进行中/2026-06-18_不想长大/05_视频/文本/2026-06-19_视频提示词_全分镜_不想长大.md")
if not path.exists():
    raise SystemExit(0)

text = path.read_text()
m = re.search(r"## VID-32｜E1-S10-C2｜.*?(?=\n## VID-|\Z)", text, flags=re.S)
if not m:
    print(f"{path}: missing VID-32 / E1-S10-C2 block")
    raise SystemExit(1)
block = m.group(0)
required = [
    "镜头固定在爷爷遗像和遗像桌方向",
    "镜头缓慢下压",
    "画面只剩蒲团粗布纹理和孝布边缘投下的暗影",
    "镜头缓慢抬起",
    "镜头后方呼吸轻轻断了一下",
]
missing = [item for item in required if item not in block]
if missing:
    print(f"{path}: VID-32 must use camera-subject director language:")
    for item in missing:
        print(item)
    raise SystemExit(1)
PY
then
  pass "VID-32 uses camera-subject director language"
else
  fail "VID-32 missing camera-subject director language"
fi

if python3 - <<'PY'
from pathlib import Path
import re

path = Path("01_作品项目/进行中/2026-06-18_不想长大/05_视频/文本/2026-06-19_视频提示词_全分镜_不想长大.md")
if not path.exists():
    raise SystemExit(0)

text = path.read_text()
blocks = re.findall(r"```text\n(.*?)```", text, flags=re.S)
bad = []
for i, block in enumerate(blocks, 1):
    if "第一人称 POV" not in block:
        continue
    for line_no, line in enumerate(block.splitlines(), 1):
        compact = line.replace(" ", "")
        risky = (
            re.search(r"第一人称POV[^。\n]*(低视线正面|正面构图|背面构图|侧面构图|正面视角|背面视角|侧面视角|正面镜头|背面镜头|侧面镜头)", compact)
            or "低视线正面" in compact
            or re.search(r"POV[^。\n]*正面构图", compact)
            or "抬回遗像桌正面" in compact
            or "回到同一张遗像桌正面" in compact
        )
        if risky:
            bad.append(f"code block {i}, line {line_no}: {line}")

if bad:
    print(f"{path}: strict POV wording may bind front/side/back to the POV subject:")
    for item in bad:
        print(item)
    raise SystemExit(1)
PY
then
  pass "current strict POV prompts avoid front/side/back ambiguity on POV subject"
else
  fail "current strict POV prompts contain front/side/back ambiguity on POV subject"
fi

if python3 - <<'PY'
from pathlib import Path
import re

path = Path("01_作品项目/进行中/2026-06-18_不想长大/05_视频/文本/2026-06-19_视频提示词_全分镜_不想长大.md")
if not path.exists():
    raise SystemExit(0)

text = path.read_text()
checks = {
    "VID-34｜E1-S10-C4": [
        "奶奶半透明",
        "二次曝光",
        "火盆",
    ],
    "VID-36｜E1-S10-C6": [
        "爷爷半透明",
        "奶奶半透明",
        "二次曝光",
        "火光",
    ],
    "VID-38｜E1-S11-C2": [
        "P11 半成品车架",
        "二次曝光",
        "爷爷半透明",
        "指尖先碰到悬空后轮",
        "粗糙木轴",
        "未完成的坐板",
    ],
}
missing_report = []
for heading, required in checks.items():
    m = re.search(rf"## {re.escape(heading)}.*?(?=\n## VID-|\Z)", text, flags=re.S)
    if not m:
        missing_report.append(f"missing block: {heading}")
        continue
    block = m.group(0)
    for item in required:
        if item not in block:
            missing_report.append(f"{heading}: missing {item}")
if missing_report:
    print(f"{path}: memory VO exposure layers incomplete:")
    for item in missing_report:
        print(item)
    raise SystemExit(1)
PY
then
  pass "current memory VO prompts use required double/triple exposure layers"
else
  fail "current memory VO prompts missing required double/triple exposure layers"
fi
require_pattern "02_共享资产库/01_模板库/视频模板/模板_视频提示词_基础设定氛围画面内容.md" "病床触碰动作必须做床侧、输液侧和可达性排练|输液针扎在哪只手|不翻身.*不抬远侧手" "video prompt template enforces sickbed touch physical reachability"
require_pattern "02_共享资产库/05_工具流程/助手执行失败经验与防复发规则.md" "病床触碰动作必须先排练床侧、输液侧和翻身成本|远侧手|输液管轻轻晃一下" "failure rules record sickbed touch physical reachability"
require_pattern "02_共享资产库/00_核心规则手册.md" "多人群像.*围桌.*座位图 / 站位图|小安坐饭桌近侧中间|爷爷坐小安右手边" "core manual enforces group blocking and table seating"
require_pattern "skills/laohu_video_prompt/SKILL.md" "多人群像.*围桌.*座位图 / 站位图|小安坐饭桌近侧中间|爷爷坐小安右手边" "video prompt skill enforces group blocking and table seating"
require_pattern "02_共享资产库/01_模板库/视频模板/模板_视频提示词_基础设定氛围画面内容.md" "多人群像.*围桌.*座位图 / 站位图|小安坐饭桌近侧中间|爷爷坐小安右手边" "video prompt template enforces group blocking and table seating"
require_pattern "02_共享资产库/05_工具流程/助手执行失败经验与防复发规则.md" "多人群像和围桌戏必须先固定座位图|爷爷坐小安右手边|画面右前方近旁" "failure rules record group blocking and table seating"
require_pattern "02_共享资产库/00_核心规则手册.md" "实际不进入本镜画面结果的资产.*不能写进|资产引用不是备注.*模型召回指令|E1-S8-C1.*移除 P6" "core manual enforces unused asset no-reference rule"
require_pattern "skills/laohu_video_prompt/SKILL.md" "资产行还必须经过.*本镜实际使用|资产引用不是给作者看的备注.*召回指令|E1-S8-C1.*不能引用 P6" "video prompt skill enforces unused asset no-reference rule"
require_pattern "02_共享资产库/01_模板库/视频模板/模板_视频提示词_基础设定氛围画面内容.md" "本镜实际使用.*资产引用是模型召回指令|门缝医生画外音.*爷爷输液瓶|输液瓶留到进屋病床镜头" "video prompt template enforces unused asset no-reference rule"
require_pattern "02_共享资产库/05_工具流程/助手执行失败经验与防复发规则.md" "未实际进入本镜画面结果的资产不能引用|E1-S8-C1.*P6 爷爷输液瓶|E1-S8-C2 才调用 P6" "failure rules record unused asset no-reference rule"
require_pattern "skills/laohu_script_writer/SKILL.md" "情绪台词不能像完成任务|量衣服|改袖口|环境阻力|火苗打不着|父亲.*沉默寡言" "script writer enforces emotion staging through action and environment"
require_pattern "02_共享资产库/05_工具流程/助手执行失败经验与防复发规则.md" "关键对白不能像完成任务|量衣服|改袖口|纸房飘带|火点不着|情绪阻力" "failure rules record emotion staging through action and environment"
require_pattern "02_共享资产库/00_核心规则手册.md" "回忆、POV 与突发消息|回忆.*台词.*物件.*触碰.*声音.*气味|第一人称 / 儿童 POV|报丧.*突发性" "core manual enforces triggered memory, POV feasibility, and sudden news logic"
require_pattern "skills/laohu_script_writer/SKILL.md" "回忆不能悬空插入|第一人称 / 儿童 POV.*视角可行性|报丧.*突发性|你们爷爷死喽|叩首抬头.*遗像切换" "script writer enforces triggered memory and POV funeral transition rules"
require_pattern "02_共享资产库/05_工具流程/助手执行失败经验与防复发规则.md" "回忆、儿童 POV 和报丧突发性不能按普通场景硬写|回忆必须有当前触发点|POV.*可见.*可听.*可感|消息前不提前展示白布" "failure rules record POV and triggered flashback failures"
require_pattern "02_共享资产库/00_核心规则手册.md" "角色名（语气 / 神态）|角色名（OS）|角色名 VO|闪回 / 闪回结束|插入镜头" "core manual enforces full short-drama script notation"
require_pattern "skills/laohu_script_writer/SKILL.md" "角色名（语气 / 神态）|角色名（OS）|角色名 VO|闪回 / 闪回结束|插入镜头|语气和神态标注不是给台词加装饰" "script writer enforces full short-drama script notation"
require_pattern "02_共享资产库/05_工具流程/助手执行失败经验与防复发规则.md" "短剧剧本格式不能只保留基础符号|语气 / 神态|OS|VO|闪回 / 闪回结束|插入镜头" "failure rules record full short-drama script notation"
require_pattern "02_共享资产库/05_工具流程/助手执行失败经验与防复发规则.md" "剧本神态标注不能断在剧本阶段|表情来源|表情占用时长|眼神.*眉头.*嘴角.*呼吸|POV.*手部.*呼吸.*声音" "failure rules record script demeanor inheritance"
require_pattern "02_共享资产库/05_工具流程/短剧剧本到视频提示词编号与时长规则.md" "剧本.*语气 / 神态.*表情来源|表情占用时长|忍着哭|压着火|眼神.*眉头.*嘴角.*呼吸" "duration rules inherit script demeanor annotations"
require_pattern "02_共享资产库/02_视觉语言资产/镜头语言库/短剧短片分镜生成字段规范.md" "表情来源|剧本神态标注|表情占用时长|POV.*手部.*呼吸.*声音" "shot field spec tracks script demeanor source"
require_pattern "02_共享资产库/01_模板库/视频模板/模板_视频提示词_基础设定氛围画面内容.md" "剧本.*语气 / 神态.*画面内容|眼神.*眉头.*嘴角.*呼吸|POV.*手部.*呼吸.*声音" "video prompt template embeds script demeanor in画面内容"
require_pattern "输入输出索引.md" "剧本神态标注向分镜和视频提示词继承|表情来源|可见表演结果" "index records script demeanor inheritance learning"

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

if rg -n "^(全局禁止|禁止方向|正向生成边界|画面风格|画质介质|质感颗粒|风格融合边界|风格收束)：" \
  "02_共享资产库/01_模板库/视频模板/模板_视频提示词_基础设定氛围画面内容.md" \
  "01_作品项目/进行中/2026-06-06_请登仙界/05_视频/文本"; then
  fail "obsolete formal prompt field label found in template or current video prompts"
else
  pass "no obsolete formal prompt field label in template or current video prompts"
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
bad = re.compile(r"不要|不能|不需要|不是|不得|避免|没有|不出现|不露脸|不直视|不加入|不晃动|不突然|不乱|不抢|不过曝|不糊|不塑料|不花乱|不硬曝|不吞")
ok = True
for path in paths:
    if not path.exists():
        continue
    text = path.read_text()
    for i, block in enumerate(re.findall(r"```text\n(.*?)\n```", text, flags=re.S), start=1):
        if not all(marker in block for marker in ("【基础设定】", "【氛围与画质】", "【画面内容】")):
            continue
        basic = re.search(r"【基础设定】(.*?)【氛围与画质】", block, flags=re.S)
        if basic and re.search(r"^(固定角色 / 生物 / 人群规则|固定场景 / 建筑 / 道具规则|正向生成边界)：", basic.group(1), flags=re.M):
            print(f"FAIL: obsolete basic-setting field in formal video prompt: {path} block {i}", file=sys.stderr)
            ok = False
        vibe = re.search(r"【氛围与画质】(.*?)【画面内容】", block, flags=re.S)
        if vibe:
            old_vibe = re.compile(r"^(画面风格|画质介质|质感颗粒|风格融合边界|风格收束)：", flags=re.M)
            required_vibe = ("风格核心：", "视觉基调：", "色彩与影调：")
            if old_vibe.search(vibe.group(1)) or not all(label in vibe.group(1) for label in required_vibe):
                print(f"FAIL: obsolete vibe fields in formal video prompt: {path} block {i}", file=sys.stderr)
                ok = False
        match = bad.search(block)
        if match:
            print(f"FAIL: negative wording in formal video prompt: {path} block {i}: {match.group(0)}", file=sys.stderr)
            ok = False
if ok:
    print("PASS: formal video prompt blocks use positive wording")
else:
    sys.exit(1)
PY
then
  pass "formal video prompt positive wording check"
else
  fail "formal video prompt positive wording check"
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
        if not all(marker in block for marker in ("【基础设定】", "【氛围与画质】", "【画面内容】")):
            continue
        match = re.search(r"^时长：([0-9]+) 秒。?$", block, flags=re.M)
        if not match:
            print(f"FAIL: missing exact duration in formal video prompt: {path} block {i}", file=sys.stderr)
            ok = False
            continue
        seconds = int(match.group(1))
        if not 4 <= seconds <= 15:
            print(f"FAIL: formal video prompt duration outside 4-15 seconds: {path} block {i} has {seconds}s", file=sys.stderr)
            ok = False
if ok:
    print("PASS: formal video prompt durations are within 4-15 seconds")
else:
    sys.exit(1)
PY
then
  pass "formal video prompt duration range check"
else
  fail "formal video prompt duration range check"
fi

require_pattern "02_共享资产库/01_模板库/视频模板/模板_视频提示词_基础设定氛围画面内容.md" "【基础设定】|【氛围与画质】|【画面内容】" "video prompt template uses three formal blocks"
require_pattern "02_共享资产库/01_模板库/视频模板/模板_视频提示词_基础设定氛围画面内容.md" "1-3 句|主风格母体|全局摄影介质|宏观色彩基线|局部.*对应镜头" "video prompt template keeps global vibe concise"
require_pattern "02_共享资产库/01_模板库/视频模板/模板_视频提示词_基础设定氛围画面内容.md" "【@A1 人物】|【@S1 场景】|【@C1 色卡】|不生成 BGM" "video prompt template uses actual reference list and sync-sound policy"
require_pattern "02_共享资产库/01_模板库/视频模板/模板_视频提示词_基础设定氛围画面内容.md" "4-15 秒|情绪|动作因果|奇观|展示时间" "video prompt template enforces 4-15 second duration strategy"
require_pattern "02_共享资产库/01_模板库/视频模板/模板_视频提示词_基础设定氛围画面内容.md" "时长预演|动作单元|估算|装不下|加时长|删内容|拆镜头" "video prompt template enforces duration previsualization"
require_pattern "02_共享资产库/01_模板库/视频模板/模板_视频提示词_基础设定氛围画面内容.md" "【@资产名】|资产占位|固定实体|动作链|冲击结果" "video prompt template includes asset placeholders and action-density rules"
require_pattern "02_共享资产库/03_模型适配/Seedance2/Seedance2视频提示词书写规范.md" "720p|不生成 BGM|连续镜头叙事|不显示镜头编号|镜头预演板|不默认上传给 Seedance 2|没有项目统一字数目标和硬上限|默认不精简、不主动压缩" "Seedance profile defines production defaults and continuous shot-language structure"
require_pattern "02_共享资产库/01_模板库/视频模板/模板_视频提示词_基础设定氛围画面内容.md" "高速人物穿过画面|场景坐标与通行净空|摄影机侧别|主体屏幕方向|最终出画 / 撞击位置|画外撞击声" "video prompt template enforces projectile spatial closure"
require_pattern "02_共享资产库/05_工具流程/助手执行失败经验与防复发规则.md" "投射物空间闭环|道路中央.*连续净空|远离箭源.*箭路|画外.*撞木声" "failure rules record projectile spatial-closure correction"
require_pattern "02_共享资产库/01_模板库/视频模板/模板_视频提示词_基础设定氛围画面内容.md" "跨镜头对象先建状态账本|人物反应先过知觉因果|参照物反向位移|超常效果按来源 / 发力.*材质分层响应" "video prompt template enforces state, perception, speed and superhuman-physics reasoning"
require_pattern "02_共享资产库/03_模型适配/Seedance2/Seedance2视频提示词书写规范.md" "完整入鞘、部分出鞘、完全出鞘、回鞘和脱手|相对运动和材料反馈|写实高武、玄幻和科幻|空气折射.*雨珠.*竹叶.*湿土.*石块.*竹根" "Seedance profile grounds state transitions, speed and superhuman effects"
require_pattern "02_共享资产库/05_工具流程/助手执行失败经验与防复发规则.md" "### 118\. 空间闭环仍不等于真实|状态账本、知觉账本、观众信息账本、速度证据和超常物理闭环|马耳先转|拔刀弧线直接磕开" "failure rules record state, perception, speed and grounded-superhuman correction"
require_pattern "02_共享资产库/05_工具流程/助手执行失败经验与防复发规则.md" "### 119\. 单体路径正确仍可能群体运动错误|多主体运动账本与事件传播账本|马头始终朝画面右侧|横向间距持续扩大" "failure rules record multi-subject and event-propagation correction"
require_pattern "02_共享资产库/01_模板库/视频模板/模板_视频生成质量检查清单.md" "多主体运动.*世界坐标.*屏幕坐标.*相对顺序.*出画顺序|事件.*来源.*命中点.*材料失效顺序.*飞散锥.*永久终态" "video QA checks multi-subject motion and event propagation"
require_pattern "02_共享资产库/03_模型适配/Seedance2/Seedance2视频提示词书写规范.md" "多主体运动不能只分别写|跟随镜头中对象相对后移不代表世界坐标反向|爆炸、楼体坍塌、炮击、飞船受击" "Seedance profile distinguishes camera-relative motion and event propagation"
require_pattern "01_作品项目/进行中/2026-07-15_一寸之外/05_视频/文本/2026-07-15_一体化视频执行单_一寸之外.md" "人马分离后.*马头持续朝右.*马尾持续朝左|横向间距连续扩大|乌骓马.*先从右侧完整出画|摄影机全程位于人马运动轴左侧" "current wuxia VID-01 locks horse-rider relative motion"
require_pattern "01_作品项目/进行中/2026-07-15_一寸之外/05_视频/文本/2026-07-15_一体化视频执行单_一寸之外.md" "P2 青棠横刀状态连续.*VID-01 全程完整入鞘.*VID-02 第一枚暗器触发完整拔刀.*VID-09" "current wuxia project tracks P2 state across every video unit"
require_pattern "01_作品项目/进行中/2026-07-15_一寸之外/05_视频/文本/2026-07-15_一体化视频执行单_一寸之外.md" "真人写实高武世界|超常预判与身体控制|空气折射.*雨珠排开.*竹叶压弯.*泥层剥离.*竹根切面" "current wuxia project uses grounded high-martial physics"
require_pattern "02_共享资产库/02_视觉语言资产/画面风格库/画面氛围与画质规范.md" "画面风格 = 风格母体 \\+ 画质介质 \\+ 色彩影调|日系小清新|35mm电影胶片|90年代王家卫港风|赛博朋克|自然纪实原生风" "画面风格库 stores composable style vocabulary"
if rg -n "影像风格：" \
  AGENTS.md \
  "02_共享资产库/00_核心规则手册.md" \
  "02_共享资产库/01_模板库/视频模板/模板_视频提示词_基础设定氛围画面内容.md" \
  skills/laohu_video_prompt/SKILL.md \
  "01_作品项目/进行中/2026-06-06_请登仙界/05_视频/文本"; then
  fail "obsolete field name 影像风格 found"
else
  pass "obsolete field name 影像风格 absent"
fi
if python3 - <<'PY'
from pathlib import Path
import re
import sys

text = Path("02_共享资产库/01_模板库/视频模板/模板_视频提示词_基础设定氛围画面内容.md").read_text()
blocks = re.findall(r"```text\n(.*?)\n```", text, flags=re.S)
bad = re.compile(r"【前置判断】|本条是否独立完整|本镜头一致性资产|本镜头非资产画面元素|后期备注|分镜编号：|所属场次：|镜头任务：")
ok = True
for i, block in enumerate(blocks, start=1):
    if not all(marker in block for marker in ("【基础设定】", "【氛围与画质】", "【画面内容】")):
        continue
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

if python3 - <<'PY'
from pathlib import Path
import re
import sys

text = Path("02_共享资产库/01_模板库/视频模板/模板_视频提示词_基础设定氛围画面内容.md").read_text()
blocks = [b for b in re.findall(r"```text\n(.*?)\n```", text, flags=re.S)
          if all(m in b for m in ("【基础设定】", "【氛围与画质】", "【画面内容】"))]
if not blocks:
    print("FAIL: no formal three-block Seedance template found", file=sys.stderr)
    sys.exit(1)
formal = blocks[0]
bad = re.compile(r"^时长：|^镜头[0-9]+｜|\[[0-9]+-[0-9]+秒\]|第\s*0\s*秒|动作段1（0-", flags=re.M)
required = ("不生成 BGM", "720p", "当【前一动作 / 遮挡物掠过 / 人物视线")
if bad.search(formal) or not all(item in formal for item in required):
    print("FAIL: formal Seedance template must use continuous shot language without shot labels or internal timestamps", file=sys.stderr)
    sys.exit(1)
print("PASS: formal Seedance template uses continuous shot language without shot labels or internal timestamps")
PY
then
  pass "formal Seedance template shot-language check"
else
  fail "formal Seedance template shot-language check"
fi
require_pattern "02_共享资产库/05_工具流程/短剧剧本到视频提示词编号与时长规则.md" "正式生成平台按单条提示词独立执行|15 秒合并规则|图片资产" "duration rules enforce independent prompt asset merge logic"
require_pattern "02_共享资产库/05_工具流程/短剧剧本到视频提示词编号与时长规则.md" "只保留.*【基础设定】.*【氛围与画质】.*【画面内容】|遮挡转场|明暗转场|运镜转场|匹配转场" "duration rules enforce three-block prompts and in-frame transitions"
require_pattern "02_共享资产库/05_工具流程/短剧剧本到视频提示词编号与时长规则.md" "时长预演|动作单元|估算|装不下|加时长|删内容|拆镜头" "duration rules enforce content-driven duration estimation"
require_pattern "02_共享资产库/02_视觉语言资产/镜头语言库/短剧短片分镜生成字段规范.md" "独立生成与合并规则|不超过 15 秒|图片资产" "shot list field spec enforces independent generation merge logic"
require_pattern "02_共享资产库/05_工具流程/剧本到AI视觉资产转换规则.md" "人物形象资产|人物素体资产|人物设计资产|人物定装资产|服装 / 妆造资产|组合形象资产|场景图片资产|物品图片资产" "asset conversion rules define detailed asset subtypes"
require_pattern "02_共享资产库/05_工具流程/剧本到AI视觉资产转换规则.md" "A1 = 人物素体资产|A2 = 服装 / 妆造资产|A3 = A1 穿着 A2" "asset conversion rules define asset composition numbering"
require_pattern "02_共享资产库/05_工具流程/剧本到AI视觉资产转换规则.md" "剧本显示称呼|生产命名|资产命名|群仙.*群体画面元素|神兽.*白鹿.*云龙.*青鸾" "asset conversion rules enforce deterministic naming"
require_pattern "02_共享资产库/05_工具流程/剧本到AI视觉资产转换规则.md" "人物形象资产.*人物素体资产.*服装 / 妆造资产.*组合设计资产|白色素衣" "asset conversion rules enforce character image/design/wardrobe chain"
require_pattern "02_共享资产库/05_工具流程/剧本到AI视觉资产转换规则.md" "人物形象资产和人物设计资产必须作为两套提示词输出|禁止用.*旧版混合图|两套提示词不拆成两个资产编号|视频提示词只调用" "asset conversion rules reject mixed character asset prompts and sub-numbering"
require_pattern "02_共享资产库/05_工具流程/剧本到AI视觉资产转换规则.md" "人物参考图.*服装参考图|四区版式|上方.*正面.*侧面.*背面|内 / 中 / 外 / 腰 / 下 / 足" "asset conversion rules enforce character sheet layout and clothing reference split"
require_pattern "02_共享资产库/05_工具流程/剧本到AI视觉资产转换规则.md" "POV 主体.*正常人物资产|年龄.*身高.*头身比.*上下身比例|手部.*鞋.*书包.*视线高度" "asset conversion rules enforce full character assets for POV subjects"
require_pattern "02_共享资产库/05_工具流程/剧本到AI视觉资产转换规则.md" "场景四视图设定图|左侧视角.*向左转动 90 度|右侧视角.*向右转动 90 度|正面反打图" "asset conversion rules enforce scene four-view setting sheets"
require_pattern "02_共享资产库/01_模板库/图片模板/模板_AI图片提示词_资产型通用结构.md" "人物形象资产|人物素体资产|人物设计资产|人物定装资产|服装 / 妆造资产|场景图片资产|物品图片资产|组合资产记录" "image asset prompt template covers asset subtypes"
require_pattern "02_共享资产库/01_模板库/图片模板/模板_AI图片提示词_资产型通用结构.md" "正面 / 半正面.*电影级艺术照|光源来自|真人写实风格|禁止做成白底三视图" "image asset prompt template covers character image asset"
require_pattern "02_共享资产库/01_模板库/图片模板/模板_AI图片提示词_资产型通用结构.md" "人物资产双提示词规则|人物形象资产.*人物设计资产|同一个人物资产编号|禁止写成.*A1-1.*A1-2" "image asset prompt template enforces two prompts under one asset id"
require_pattern "02_共享资产库/01_模板库/图片模板/模板_AI图片提示词_资产型通用结构.md" "可复制图片提示词|代码块里只放模型投喂正文|代码块外" "image asset prompt template enforces copyable prompt blocks"
require_pattern "02_共享资产库/01_模板库/图片模板/模板_AI图片提示词_资产型通用结构.md" "参考图 \\+ 服装图拆分写法|人物资产分区版式|主视觉区.*补充信息区.*局部细节区.*比例照" "image asset prompt template covers character reference sheet layout"
require_pattern "02_共享资产库/01_模板库/图片模板/模板_AI图片提示词_资产型通用结构.md" "左手特写.*右手特写|音色文字说明|音色说明：|【形象参考@xx】.*【音色参考@xx】" "image asset prompt template covers hand closeups and voice text"
require_pattern "02_共享资产库/00_核心规则手册.md" "主角色人物设计资产默认只固定中性常见表情|不默认做七宫格、九宫格|情绪表演.*视频提示词" "core manual avoids default multi-expression character assets"
require_pattern "02_共享资产库/05_工具流程/剧本到AI视觉资产转换规则.md" "主角色人物设计资产不要默认做多格情绪表情|中性常见表情|表情测试参考图" "asset conversion avoids default multi-expression character assets"
require_pattern "02_共享资产库/00_核心规则手册.md" "衣服如何适配身体|肩颈.*胸腰比例.*腰线|修身但不紧绷" "core manual enforces body-fit clothing adaptation"
require_pattern "02_共享资产库/01_模板库/图片模板/模板_AI图片提示词_资产型通用结构.md" "身体适配|肩线.*胸前.*腰侧.*高腰线|修身但不紧绷" "image asset prompt template enforces body-fit clothing adaptation"
require_pattern "02_共享资产库/05_工具流程/助手执行失败经验与防复发规则.md" "人物定装必须写身体适配和版型机制|肩线、胸口、腰侧、高腰线|松垮无形、直筒麻袋、胸前塌陷、腰线消失" "failure rules record body-fit clothing adaptation"
require_pattern "02_共享资产库/00_核心规则手册.md" "代表性基准体态.*不是统一套.*挺拔|左手.*右手.*拇指" "core manual preserves identity-specific posture and correct left-right hands"
require_pattern "02_共享资产库/01_模板库/图片模板/模板_AI图片提示词_资产型通用结构.md" "代表性基准体态.*不是统一套挺拔站姿|左手.*右手.*拇指" "image asset prompt template preserves identity-specific posture and correct left-right hands"
require_pattern "02_共享资产库/05_工具流程/助手执行失败经验与防复发规则.md" "人物设计资产必须锁代表性基准体态和左右手解剖方向|左手拇指.*画面右侧.*右手拇指.*画面左侧|同一只手" "failure rules record identity-specific posture and correct left-right hands"
require_pattern "02_共享资产库/01_模板库/图片模板/模板_AI图片提示词_资产型通用结构.md" "人物设计资产表情规则|中性常见表情|不要把心动、雀跃、怀疑、愤怒、落泪.*七宫格" "image asset template avoids default multi-expression character assets"
require_pattern "02_共享资产库/01_模板库/图片模板/模板_AI图片提示词_资产型通用结构.md" "POV 主体人物资产|身高.*头身比.*上下身比例|手部.*鞋.*书包.*低视线" "image asset prompt template covers full character assets for POV subjects"
require_pattern "02_共享资产库/01_模板库/图片模板/模板_AI图片提示词_资产型通用结构.md" "场景四视图设定图|正面视角|左侧视角|右侧视角|正面反打图|物体空间逻辑" "image asset prompt template covers scene four-view setting sheets"
require_pattern "02_共享资产库/00_核心规则手册.md" "资产.*唯一性|一个图片资产只能固定一个确定对象|分镜图|桌面.*案板.*操作台.*先判断.*空间.*物" "core manual enforces asset uniqueness and local operation splitting"
require_pattern "skills/laohu_visual_assets/SKILL.md" "资产唯一性原则|一个图片资产只能固定一个确定对象|分镜图|局部操作空间.*先拆资产" "visual assets skill enforces asset uniqueness and local operation splitting"
require_pattern "02_共享资产库/05_工具流程/剧本到AI视觉资产转换规则.md" "资产唯一性先于资产数量控制|一个图片资产只能固定一个确定对象|分镜图|局部场景资产不能把可移动道具和动作混在一起" "asset conversion rules enforce asset uniqueness and local operation splitting"
require_pattern "02_共享资产库/01_模板库/图片模板/模板_AI图片提示词_资产型通用结构.md" "资产唯一性原则|一个图片资产只能固定一个确定对象|分镜图|局部操作空间拆分" "image asset template enforces asset uniqueness and local operation splitting"
require_pattern "skills/laohu_visual_assets/SKILL.md" "POV 主体.*正常人物资产|年龄.*身高.*头身比.*上下身比例|手部.*鞋.*书包.*视线高度" "visual assets skill enforces full character assets for POV subjects"
require_pattern "02_共享资产库/00_核心规则手册.md" "POV 主体.*正常人物资产|年龄.*身高.*头身比.*上下身比例|手部.*鞋.*书包.*视线高度" "core manual enforces full character assets for POV subjects"
require_pattern "01_作品项目/进行中/2026-06-18_不想长大/03_视觉资产/文本/2026-06-18_图片提示词_不想长大.md" "A1 小安儿童人物资产（POV 主体）|身高约 115-125cm|儿童头身比|完整儿童身体来源" "current project image prompts use full child asset for POV protagonist"
require_pattern "01_作品项目/进行中/2026-06-18_不想长大/03_视觉资产/文本/2026-06-18_图片提示词_不想长大.md" "A1 小安人物形象资产提示词|A1 小安人物设计资产提示词|A2 父亲人物形象资产提示词|A2 父亲人物设计资产提示词|最终只登记一个 A1" "current project image prompts split character image/design prompts under one asset id"
require_pattern "01_作品项目/进行中/2026-06-18_不想长大/03_视觉资产/文本/2026-06-18_图片提示词_不想长大.md" "资产唯一性修正|P3 包汤圆旧木案桌|P4 元宵完整白汤圆|P10 元宵小面值硬币|S2 堂屋 / 灶房|S2 \\+ P3 \\+ P4 \\+ P10 \\+ A4" "current project splits tangyuan scene into single-object assets"
require_pattern "02_共享资产库/01_模板库/图片模板/模板_角色一致性网格图.md" "人物素体资产|人物定装资产|16:9 横幅|全身三视图" "character grid template supports body and styled character assets"
require_pattern "02_共享资产库/01_模板库/视频模板/模板_视频提示词_基础设定氛围画面内容.md" "每条正式视频提示词本体必须单独放进.*text.*代码块|代码块里只放可投喂模型的三段正文|代码块外" "video prompt template enforces copyable code blocks"

if python3 - <<'PY'
from pathlib import Path
path = Path("01_作品项目/进行中/2026-06-18_不想长大/03_视觉资产/文本/2026-06-18_图片提示词_不想长大.md")
lines = path.read_text().splitlines()
ok = True
in_block = False
for i, line in enumerate(lines):
    if line.startswith("```"):
        if in_block:
            in_block = False
            continue
        in_block = True
        prev = ""
        for j in range(i - 1, -1, -1):
            if lines[j].strip():
                prev = lines[j].strip()
                break
        if prev != "可复制图片提示词：":
            print(f"{path}:{i+1}: code block is not introduced by 可复制图片提示词： (previous: {prev})")
            ok = False
if not ok:
    raise SystemExit(1)
PY
then
  pass "current image prompt code blocks are only copyable prompt bodies"
else
  fail "current image prompt code blocks are only copyable prompt bodies"
fi

if python3 - <<'PY'
from pathlib import Path
files = [
    Path("01_作品项目/进行中/2026-06-18_不想长大/04_分镜/文本/2026-06-19_分镜表_不想长大.md"),
    Path("01_作品项目/进行中/2026-06-18_不想长大/05_视频/文本/2026-06-19_视频提示词_全分镜_不想长大.md"),
]
bad = []
for path in files:
    text = path.read_text()
    start = text.find("E1-S8-C1")
    if start == -1:
        start = text.find("VID-25")
    end_candidates = [i for marker in ("E1-S8-C2", "## VID-26", "| E1-S8-C2", "| VID-26") if (i := text.find(marker, start + 1)) != -1]
    end = min(end_candidates) if end_candidates else min(len(text), start + 3000)
    block = text[start:end]
    if "P6" in block or "输液瓶" in block or "输液管" in block:
        bad.append(str(path))
if bad:
    print("E1-S8-C1 / VID-25 must not reference P6 or infusion props:")
    for item in bad:
        print(item)
    raise SystemExit(1)
PY
then
  pass "current E1-S8-C1 / VID-25 does not reference unused P6 infusion asset"
else
  fail "current E1-S8-C1 / VID-25 references unused P6 infusion asset"
fi

if python3 - <<'PY'
from pathlib import Path
path = Path("01_作品项目/进行中/2026-06-18_不想长大/03_视觉资产/文本/2026-06-18_图片提示词_不想长大.md")
text = path.read_text()
required = [
    "A1 小安人物形象资产提示词", "A1 小安人物设计资产提示词",
    "A2 父亲人物形象资产提示词", "A2 父亲人物设计资产提示词",
    "A3 爷爷人物形象资产提示词", "A3 爷爷人物设计资产提示词",
    "A4 奶奶人物形象资产提示词", "A4 奶奶人物设计资产提示词",
    "A5 姐姐人物形象资产提示词", "A5 姐姐人物设计资产提示词",
]
missing = [item for item in required if item not in text]
if missing:
    for item in missing:
        print(f"{path}: missing character image/design asset heading: {item}")
    raise SystemExit(1)
import re
bad = sorted(set(re.findall(r"\bA[1-5]-[12]\b", text)))
if bad:
    print(f"{path}: character prompt types must not become sub asset ids: {', '.join(bad)}")
    raise SystemExit(1)
PY
then
  pass "current project has image/design prompt pairs under stable asset ids for every main character"
else
  fail "current project has image/design prompt pairs under stable asset ids for every main character"
fi

require_pattern "skills/laohu_ai_visual/SKILL.md" "所有可复制给模型的正文.*图片资产.*视频提示词.*封面.*首帧.*生图.*分镜参考|代码块里不能用排除句" "entry skill enforces positive prompts for all model-facing bodies"
require_pattern "skills/laohu_visual_assets/SKILL.md" "所有图片资产、封面、首帧和生图提示词.*出现什么描述什么|混用风险.*代码块外" "visual assets enforces positive prompts across image-facing bodies"
require_pattern "02_共享资产库/01_模板库/图片模板/模板_AI图片提示词_资产型通用结构.md" "质量边界|具体跑偏对象和混用风险写在代码块外|出现什么描述什么" "image prompt template uses positive bodies and externalized risks"
require_pattern "02_共享资产库/00_核心规则手册.md" "特写进.*注意力开关|局部证据特写.*空间揭示" "core manual enforces close-up-in attention control"
require_pattern "skills/laohu_video_prompt/SKILL.md" "特写进.*高张力短视频|局部证据特写.*空间揭示" "video prompt skill enforces close-up-in attention control"
require_pattern "02_共享资产库/01_模板库/视频模板/模板_视频提示词_基础设定氛围画面内容.md" "高张力镜头必须做特写进判断|特写蒙太奇连接器" "video prompt template enforces close-up-in and close-up montage"
require_pattern "02_共享资产库/02_视觉语言资产/镜头语言库/镜头语言词典.md" "特写进与注意力控制|特写作为蒙太奇连接器" "shot language dictionary defines close-up-in and close-up montage"
require_pattern "02_共享资产库/05_工具流程/助手执行失败经验与防复发规则.md" "高张力场面不能默认全景开场|特写进是注意力开关" "failure rules record close-up-in attention lesson"
require_pattern "02_共享资产库/00_核心规则手册.md" "泛化弱词.*小、轻、低|语义适配" "core manual enforces generic weak-word review"
require_pattern "skills/laohu_script_writer/SKILL.md" "泛化弱词审稿|安全宽词替代人物真实口气" "script writer enforces generic weak-word review"
require_pattern "skills/laohu_video_prompt/SKILL.md" "泛化弱词审稿|可生成维度" "video prompt skill enforces generic weak-word review"
require_pattern "02_共享资产库/01_模板库/视频模板/模板_视频提示词_基础设定氛围画面内容.md" "泛化弱词必须过审|动作幅度 / 速度 / 力道" "video prompt template enforces generic weak-word review"
require_pattern "02_共享资产库/05_工具流程/助手执行失败经验与防复发规则.md" "泛化弱词不能代替精准判断|语义相似度" "failure rules record generic weak-word lesson"
require_pattern "输入输出索引.md" "AI 用词泛化|泛化弱词审稿" "index records generic weak-word lesson"
require_pattern "02_共享资产库/00_核心规则手册.md" "空间留白和信息留白|局部遮蔽让观众参与想象" "core manual distinguishes spatial and information negative space"
require_pattern "skills/laohu_visual_assets/SKILL.md" "信息留白强化第一眼吸引力|不能替代完整人物设计资产" "visual assets supports information negative space in character image assets"
require_pattern "skills/laohu_video_prompt/SKILL.md" "空间留白让画面呼吸，信息留白让观众补完|局部遮蔽制造期待" "video prompt skill enforces information negative space boundary"
require_pattern "02_共享资产库/01_模板库/图片模板/模板_AI图片提示词_资产型通用结构.md" "信息留白|遮住哪里、露出哪里" "image prompt template supports information negative space"
require_pattern "02_共享资产库/01_模板库/视频模板/模板_视频提示词_基础设定氛围画面内容.md" "空间留白和信息留白|观众靠哪个局部补完人物" "video prompt template supports information negative space"
require_pattern "02_共享资产库/02_视觉语言资产/镜头语言库/镜头语言词典.md" "信息留白、局部遮蔽与观众补完|空间留白是画面里空出来" "shot language dictionary defines information negative space"
require_pattern "02_共享资产库/05_工具流程/助手执行失败经验与防复发规则.md" "留白要区分空间呼吸和信息缺口|完整展示解决的是确认" "failure rules record information negative space lesson"
require_pattern "输入输出索引.md" "留白、局部遮蔽和观众补完|空间留白负责画面呼吸" "index records information negative space lesson"
require_pattern "02_共享资产库/00_核心规则手册.md" "给观众眼睛找一个家|视觉落点|视觉导引线|空间块面" "core manual enforces point-line-plane subject emphasis"
require_pattern "skills/laohu_video_prompt/SKILL.md" "点线面.*视觉落点|先定视觉落点.*导引线.*块面" "video prompt skill enforces point-line-plane composition"
require_pattern "skills/laohu_generation_review/SKILL.md" "构图逻辑.*视觉落点|三分法、黄金分割、引导线和留白只是候选" "generation review checks contribution-based composition"
require_pattern "02_共享资产库/02_视觉语言资产/镜头语言库/镜头语言词典.md" "点线面与主体突出|视觉落点|视觉导引|空间块面" "shot language dictionary defines point-line-plane composition"
require_pattern "02_共享资产库/01_模板库/视频模板/模板_视频生成质量检查清单.md" "观众第一眼是否有明确视觉落点" "video quality checklist checks visual landing point"
require_pattern "02_共享资产库/05_工具流程/助手执行失败经验与防复发规则.md" "先解决视觉落点，点线面只在承重时使用|先确定主注意力目标|点、线、面是候选构图机制，不是三项必填" "failure rules record contribution-based point-line-plane lesson"
require_pattern "输入输出索引.md" "点、线、面、主体突出|给观众眼睛找一个家" "index records point-line-plane composition lesson"
require_pattern "AGENTS.md" "色卡 / 色彩风格资产|导演级调色资产|正式视频提示词里不能只写.*调用色卡" "top-level rules define color palette style assets"
require_pattern "02_共享资产库/00_核心规则手册.md" "色彩风格资产.*主色.*辅助色.*点缀色|母色卡不变，阶段变体受控变化|色彩与影调" "core manual defines color palette style assets"
require_pattern "skills/laohu_visual_assets/SKILL.md" "色卡可以升级为色彩风格资产|C1 全片母色卡|C1-A 心动期色卡变体" "visual assets skill supports color palette assets"
require_pattern "skills/laohu_video_prompt/SKILL.md" "【@C1 色卡名】|不能只写.*调用色卡|颜色映射.*连续画面段落|切换到新空间" "video prompt skill maps palette colors inside continuous shot passages"
require_pattern "02_共享资产库/01_模板库/图片模板/模板_AI图片提示词_资产型通用结构.md" "色彩风格资产 / 色卡资产|十六进制 RGB|阶段变体" "image prompt template supports color palette assets"
require_pattern "02_共享资产库/01_模板库/视频模板/模板_视频提示词_基础设定氛围画面内容.md" "【@C1 色卡】|主色彩锚定|逐对象.*颜色映射|HEX" "video prompt template supports palette reference and shot-level mapping"
require_pattern "AGENTS.md" "人物组.*道具组.*场景组.*氛围与过渡组|主色彩锚定|颜色映射" "top-level rules define four-group color palette mapping"
require_pattern "02_共享资产库/00_核心规则手册.md" "人物组：肤色.*道具组：关键道具.*场景组：墙面.*氛围与过渡组：整体光线|主色彩锚定|颜色映射" "core manual enforces four-group color palette mapping"
require_pattern "skills/laohu_visual_assets/SKILL.md" "人物组、道具组、场景组、氛围与过渡组|色卡图片提示词|视频调用句|颜色映射模板" "visual assets skill outputs four-group color palette assets"
require_pattern "skills/laohu_video_prompt/SKILL.md" "主色彩锚定|颜色映射|整体光线.*主角服装.*肤色.*发色.*场景结构.*关键道具.*氛围与过渡" "video prompt skill enforces color-card anchor and shot-level mapping"
require_pattern "02_共享资产库/01_模板库/图片模板/模板_AI图片提示词_资产型通用结构.md" "人物组、道具组、场景组、氛围与过渡组|视频调用句|颜色映射模板" "image prompt template supports four-group color palette assets"
require_pattern "02_共享资产库/01_模板库/视频模板/模板_视频提示词_基础设定氛围画面内容.md" "主色彩锚定|逐对象.*颜色映射|整体光线.*主角服装.*肤色.*发色.*场景结构.*关键道具.*氛围过渡" "video prompt template includes shot-level color-card mapping"
require_pattern "02_共享资产库/05_工具流程/助手执行失败经验与防复发规则.md" "色卡必须四组化|人物组、道具组、场景组、氛围与过渡组|主色彩锚定|颜色映射" "failure rules record four-group color palette mapping lesson"
require_pattern "输入输出索引.md" "正式提示词镜头承接|连续镜头叙事|分镜表和预演板仍可保留编号|VID-01 至 VID-09" "index records continuous shot narrative upgrade"
require_pattern "02_共享资产库/02_视觉语言资产/画面风格库/画面氛围与画质规范.md" "色卡是色彩体系的资产化版本|母色卡 \\+ 阶段变体|同一片美景变得不美了" "style guide defines color palette assets"
require_pattern "02_共享资产库/05_工具流程/剧本到AI视觉资产转换规则.md" "色彩风格资产.*色卡图片 \\+ 文本规则|C.*系列色彩风格资产|人物设计资产里的紧凑色值卡" "asset conversion supports color palette assets"
require_pattern "02_共享资产库/05_工具流程/助手执行失败经验与防复发规则.md" "色卡要升级为色彩风格资产|母色卡不变，阶段变体受控变化|不能只当几个色号" "failure rules record color palette asset lesson"
require_pattern "输入输出索引.md" "AI 视频色卡|C.*系列色彩风格资产|母色卡不变，阶段变体受控变化" "index records color palette asset lesson"
require_pattern "AGENTS.md" "主体明确.*场景承托.*时间定光.*风格定情绪|图片四锚点" "top-level rules define the four image anchors"
require_pattern "02_共享资产库/00_核心规则手册.md" "主体明确.*场景承托.*时间定光.*风格定情绪|时间.*太阳高度.*色温.*阴影" "core manual defines time-led image reasoning"
require_pattern "02_共享资产库/02_视觉语言资产/高质量创作特征资产库/高质量AI图片开发计划.md" "开放属性空间|示例.*不是.*封闭|不得.*穷举" "image quality plan keeps examples open-ended"
require_pattern "02_共享资产库/02_视觉语言资产/高质量创作特征资产库/高质量AI图片开发计划.md" "年代.*季节.*时刻|太阳高度.*色温.*阴影长度.*空气" "image quality plan defines the time-to-light causal chain"
require_pattern "skills/laohu_visual_assets/SKILL.md" "抽象词具象化|裁切边界.*焦点落点|导演级自动补全" "visual assets skill translates abstractions into visible evidence"
require_pattern "02_共享资产库/01_模板库/图片模板/模板_AI图片提示词_资产型通用结构.md" "主体锚点|场景锚点|时间锚点|风格锚点" "image prompt template exposes the four image anchors"
require_pattern "02_共享资产库/02_视觉语言资产/画面风格库/画面氛围与画质规范.md" "参考作品.*风格母体|片名.*构图.*色彩.*光影.*材质" "style guide decomposes reference works into visible traits"
require_pattern "02_共享资产库/05_工具流程/助手执行失败经验与防复发规则.md" "四锚点不是四个词槽|示例.*开放.*推导|抽象词.*可见证据" "failure rules record open-ended four-anchor reasoning"
require_pattern "输入输出索引.md" "生图四锚点|主体.*场景.*时间.*风格|抽象词具象化" "index records the four-anchor image prompt upgrade"
require_pattern "AGENTS.md" "主情绪唯一性|第一情绪.*只能有一个|视觉焦点.*情绪重心" "top-level rules enforce one dominant image emotion"
require_pattern "02_共享资产库/00_核心规则手册.md" "主情绪命题|气质标签.*不是.*主情绪|所有视觉证据.*同一个情绪方向" "core manual distinguishes temperament labels from dominant emotion"
require_pattern "02_共享资产库/02_视觉语言资产/高质量创作特征资产库/高质量AI图片开发计划.md" "主情绪唯一性|情绪命题.*情绪证据.*情绪退让|复杂余味.*第一情绪" "image quality plan defines dominant-emotion hierarchy"
require_pattern "skills/laohu_visual_assets/SKILL.md" "主情绪唯一性|情绪命题.*视觉证据|英姿飒爽.*人物气质" "visual assets skill enforces dominant-emotion reasoning"
require_pattern "02_共享资产库/01_模板库/图片模板/模板_AI图片提示词_资产型通用结构.md" "主情绪命题|辅助余味|冲突情绪信号" "image prompt template checks emotional hierarchy"
require_pattern "skills/laohu_generation_review/SKILL.md" "情绪重心|视觉焦点清楚.*情绪.*发散|主情绪命题" "generation review diagnoses emotionally unfocused images"
require_pattern "02_共享资产库/05_工具流程/助手执行失败经验与防复发规则.md" "^### 111\\. 视觉焦点清楚不等于情绪重心清楚" "failure rules record dominant-emotion lesson"
require_pattern "输入输出索引.md" "图片主情绪唯一性|临敌不退的镇定|视觉焦点.*情绪重心" "index records the dominant-emotion image upgrade"
require_pattern "AGENTS.md" "全片情绪命题.*场次情绪功能.*镜头主情绪|一个镜头一个主情绪目标|情绪转折镜头.*起点情绪.*触发.*终点情绪" "top-level rules define emotional hierarchy from film to beat"
require_pattern "02_共享资产库/00_核心规则手册.md" "情绪目标层级|全片.*场次.*镜头.*情绪节拍|主注意力目标.*主观看任务.*主情绪目标.*三种不同判断" "core manual separates attention, task and emotion targets"
require_pattern "02_共享资产库/05_工具流程/导演级影视创作总控流程.md" "情绪总控门|全片主情绪.*场次情绪.*镜头主情绪|多个镜头.*情绪曲线" "director flow controls emotional hierarchy"
require_pattern "skills/laohu_script_writer/SKILL.md" "全片情绪命题|场次情绪功能|镜头情绪节拍|转折镜头.*起点.*触发.*终点" "script writer designs emotional hierarchy before shots"
require_pattern "02_共享资产库/02_视觉语言资产/高质量创作特征资产库/高质量AI视频提示词开发计划.md" "单镜头主情绪|注意力目标.*观看任务.*情绪目标|情绪变化.*同时并列" "video quality plan defines one dominant emotion per beat"
require_pattern "skills/laohu_video_prompt/SKILL.md" "一个镜头一个主情绪目标|主注意力目标.*主观看任务.*主情绪目标|情绪转折.*起点情绪.*触发.*终点情绪" "video prompt skill enforces one dominant emotion per beat"
require_pattern "02_共享资产库/01_模板库/视频模板/模板_视频提示词_基础设定氛围画面内容.md" "本镜主情绪|情绪命题|起点情绪.*触发.*终点情绪" "video prompt template exposes emotional target reasoning"
require_pattern "02_共享资产库/01_模板库/视频模板/模板_视频生成质量检查清单.md" "主情绪目标|注意力目标.*观看任务.*情绪目标|多个情绪.*同等权重" "video QA checks emotional hierarchy"
require_pattern "skills/laohu_generation_review/SKILL.md" "情绪目标混乱|注意力集中.*任务完成.*情绪仍然杂乱|镜头主情绪" "generation review diagnoses emotional target conflicts"
require_pattern "02_共享资产库/05_工具流程/助手执行失败经验与防复发规则.md" "^### 112\\. 一个镜头一个重点必须包含一个主情绪目标" "failure rules record one-emotion-per-beat lesson"
require_pattern "输入输出索引.md" "影视情绪目标层级|全片情绪命题.*场次情绪功能.*镜头主情绪|注意力.*任务.*情绪" "index records emotional hierarchy upgrade"
require_pattern "02_共享资产库/00_核心规则手册.md" "情绪拥有否决权|加强主情绪.*保留|削弱.*删除|专业完整度" "core manual gives emotion veto power over technical detail"
require_pattern "skills/laohu_visual_assets/SKILL.md" "专业字段.*不是必填|不能加强主情绪.*省略|削弱主情绪.*否决" "visual assets skill subordinates technical detail to emotion"
require_pattern "skills/laohu_video_prompt/SKILL.md" "构图、光影、时间、姿态、场景.*服务.*主情绪|加强.*保留.*削弱.*删除" "video prompt skill subordinates craft to emotional purpose"
require_pattern "02_共享资产库/01_模板库/视频模板/模板_视频生成质量检查清单.md" "每个专业字段.*增强主情绪|无关字段.*删除|削弱.*改写" "video QA checks emotional contribution of every craft choice"
require_pattern "AGENTS.md" "受众体验目标|叙事 / 审美成品.*主情绪|制作资产.*功能目标|功能型内容.*理解 / 信任 / 行动" "top-level rules scope emotion-first decisions by output type"
require_pattern "02_共享资产库/00_核心规则手册.md" "先定目的，再选手段|情绪承重项|生成必需项|专业展示项|删除专业展示项" "core manual classifies craft fields by contribution"
require_pattern "skills/laohu_script_writer/SKILL.md" "节奏网格.*诊断尺|不能为了反转.*破坏.*情绪|场景可以.*情绪压力" "script rules subordinate structure and pacing to emotional purpose"
require_pattern "skills/laohu_visual_assets/SKILL.md" "观众成品图.*情绪优先|制作参考资产.*功能优先|中性基准" "visual assets skill scopes emotion-first vs function-first assets"
require_pattern "skills/laohu_video_prompt/SKILL.md" "承重字段选择|生成必需信息|不要求每镜.*全部|审美停点.*情绪停点" "video prompt skill removes mandatory field packing"
require_pattern "02_共享资产库/01_模板库/视频模板/模板_视频提示词_基础设定氛围画面内容.md" "按镜头目的选择承重字段|不要求每个镜头同时写满|审美停点 / 情绪停点" "video prompt template removes mandatory field packing"
require_pattern "02_共享资产库/03_模型适配/Seedance2/Seedance2视频提示词书写规范.md" "承重项|不要求每镜.*景别.*机位.*运镜.*光影.*色彩.*声音" "Seedance profile uses contribution-based detail"
require_pattern "02_共享资产库/01_模板库/视频模板/模板_视频生成质量检查清单.md" "承重字段|生成必需|功能型镜头|不强制壁纸帧" "video QA scopes technical completeness"
require_pattern "02_共享资产库/05_工具流程/助手执行失败经验与防复发规则.md" "^### 113\\. 专业字段不是必填清单，旧规则必须服从情绪目的" "failure rules record system-wide field-packing correction"
require_pattern "02_共享资产库/00_核心规则手册.md" "演员临场感.*具体事件压力.*生理反应.*行为选择.*环境反馈|具体事件压力.*可见生理反应.*带态度的行为选择" "core rules distinguish acted event response from posed character mood"
require_pattern "skills/laohu_visual_assets/SKILL.md" "演员临场感 = 具体事件压力 \+ 可见生理反应 \+ 带态度的行为选择 \+ 对手 / 环境反馈" "visual assets skill enforces event-response acting evidence"
require_pattern "02_共享资产库/01_模板库/图片模板/模板_AI图片提示词_资产型通用结构.md" "演员临场感：|静止要写成面对压力后的主动不动" "image prompt template includes actor-in-event evidence"
require_pattern "skills/laohu_generation_review/SKILL.md" "演员临场感.*摆拍|事件压力、生理反应、行为选择、对手 / 环境反馈" "generation review scores acting presence versus posing"
require_pattern "02_共享资产库/05_工具流程/助手执行失败经验与防复发规则.md" "^### 114\\. 人物有主情绪不等于像演员" "failure rules record actor-presence lesson"
require_pattern "输入输出索引.md" "演员临场感|事件压力.*行为选择.*环境反馈" "index records actor-presence image upgrade"
require_pattern "02_共享资产库/00_核心规则手册.md" "导演镜头构思|剧情意图.*可拍事件节拍.*决定性瞬间.*摄影机观看位置.*画内证据" "core rules require shot invention between script and prompts"
require_pattern "02_共享资产库/05_工具流程/导演级影视创作总控流程.md" "第一次：导演镜头构思|模糊需求.*3-5 个镜头构思候选" "director visual gate separates shot invention from execution"
require_pattern "skills/laohu_script_writer/SKILL.md" "剧本不承担完整摄影设计|待导演构思|不需要继续写.*俯拍" "script skill preserves narrative detail without camera overloading"
require_pattern "skills/laohu_visual_assets/SKILL.md" "具体事件压力 / 关系状态.*决定性瞬间.*摄影机观看位置|黑白剪影.*镜头骨架" "visual assets skill invents and tests shot concepts for vague requests"
require_pattern "02_共享资产库/02_视觉语言资产/镜头语言库/短剧短片分镜生成字段规范.md" "导演镜头构思|事件节拍.*决定性瞬间.*动作与调度几何.*摄影机观看位置" "shot specification requires concept competition before fields"
require_pattern "skills/laohu_video_prompt/SKILL.md" "视频提示词不能承担第一次发明镜头|退回分镜层生成 3-5 个镜头构思候选" "video prompt skill rejects detailed execution of weak shot concepts"
require_pattern "skills/laohu_generation_review/SKILL.md" "镜头构思强度|黑白剪影.*镜头力量" "generation review diagnoses shot concept separately from prompt execution"
require_pattern "02_共享资产库/05_工具流程/助手执行失败经验与防复发规则.md" "^### 115\\. 模糊剧本不能直接扩写提示词" "failure rules record shot-invention pipeline lesson"
require_pattern "输入输出索引.md" "导演镜头构思层|决定性瞬间.*摄影机关系.*画内证据" "index records shot-invention pipeline upgrade"
require_pattern "AGENTS.md" "已明确事实.*创意留白|授权创意空间.*主动补全" "top-level rules grant creative autonomy while preserving explicit facts"
require_pattern "AGENTS.md" "情绪识别.*情绪代入|目标与代价.*信息对齐.*空间对齐.*身体对齐.*时间对齐.*选择对齐" "top-level rules distinguish emotional recognition from audience embodiment"
require_pattern "AGENTS.md" "六个核心 skill.*不能只是转发上游|继承硬约束.*诊断上游缺口.*主动升级" "top-level rules require independent module improvement"
require_pattern "02_共享资产库/00_核心规则手册.md" "情绪传递与观众代入.*两层结果|进入处境.*共同经历.*拉开.*余波" "core manual defines audience embodiment path"
require_pattern "02_共享资产库/05_工具流程/导演级影视创作总控流程.md" "目标与代价：观众是否知道人物为什么在乎|信息对齐：观众与人物同时知道|空间对齐：危险、出口、遮挡|身体对齐：呼吸、重心、受力|时间对齐：等待、逼近、触发|选择对齐：观众是否跟随人物" "director flow controls audience embodiment dimensions"
require_pattern "02_共享资产库/05_工具流程/laohu_skills核心合约.md" "每个 skill 都执行独立升级循环|本模块新增创意决定|下游必须继承" "core skill contract enforces creative enhancement handoffs"
require_pattern "skills/laohu_script_writer/SKILL.md" "编剧模块本身也必须独立升级|目标与代价.*信息差.*选择.*因果" "script writer actively improves vague upstream input"
require_pattern "skills/laohu_visual_assets/SKILL.md" "视觉资产模块不能只继承剧本名词|世界的触感和人物生活痕迹" "visual assets independently improve embodied world evidence"
require_pattern "skills/laohu_video_prompt/SKILL.md" "观众看懂情绪.*观众经历情绪|目标与代价.*危险方向.*触感.*声场" "video prompt skill designs embodied audience experience"
require_pattern "skills/laohu_vibe_creating_prompt/SKILL.md" "独立提升观众代入|体验连续性与呼吸" "VC optimization improves embodiment instead of only compressing"
require_pattern "skills/laohu_generation_review/SKILL.md" "观众代入强度.*主情绪可读性分开评分" "generation review scores embodiment separately from emotion recognition"
require_pattern "02_共享资产库/02_视觉语言资产/高质量创作特征资产库/高质量AI视频提示词开发计划.md" "情绪识别与观众代入|目标与代价.*信息对齐.*空间对齐.*身体对齐.*时间对齐.*选择对齐" "video quality plan defines embodiment design"
require_pattern "02_共享资产库/01_模板库/视频模板/模板_视频生成质量检查清单.md" "观众代入强度|全程 POV.*唯一代入方法" "video QA evaluates embodiment without forcing POV"
require_pattern "02_共享资产库/05_工具流程/助手执行失败经验与防复发规则.md" "^### 116\\. 看懂人物情绪不等于进入人物" "failure rules record creative-autonomy and embodiment lesson"
require_pattern "输入输出索引.md" "创意授权、模块独立升级和观众代入规则" "index records creative-autonomy and embodiment upgrade"
require_pattern "输入输出索引.md" "情绪目的优先全项目审计|强制字段堆砌|固定情绪映射|制作资产.*功能优先" "index records project-wide emotion-first audit"
require_pattern "02_共享资产库/00_核心规则手册.md" "角色自己的肤色、气色、妆效|冷白偏中性.*只是林栀案例|暖肤、深肤、晒痕" "core manual avoids one-size-fits-all beauty skin"
require_pattern "skills/laohu_visual_assets/SKILL.md" "代表性基准体态|不是统一套挺拔站姿|冷白偏中性.*只是林栀案例" "visual assets preserve character-specific body and skin identity"
require_pattern "02_共享资产库/01_模板库/图片模板/模板_AI图片提示词_资产型通用结构.md" "角色自己的肤色、气色、妆效|冷白偏中性.*只作为林栀案例|不是美女角色默认值" "image template avoids one-size-fits-all beauty skin"
require_pattern "AGENTS.md" "视频画面内容四核|主体与注意力目标.*动作与表演.*效果系统.*节奏" "top-level rules define the four video-content cores"

emotion_conflict_pattern='逐镜头写景别、机位、运镜路径、主体动作、表演、动作结果、本镜光影、HEX 色彩落点、材质、环境运动、同期声、切换触发和停止画面|每个镜头必须包含景别、机位、运镜起点 / 路径 / 速度 / 落点|壁纸帧必须有光影体系|壁纸帧必须有色彩美学体系|壁纸帧必须有景深与空间层次体系|壁纸帧必须有画质与材质质感体系|壁纸帧必须有氛围环境元素体系|短视频极简镜头至少包含景别、机位、运镜、主体画面、光影氛围和画质规格|每条镜头都要写可定格停留|每个动态镜头都要有可定格停留|关键动作后.*停住 1-2 秒|治愈日常写轻微自然手持微抖|平视适合日常、真实和温暖家庭生活|人物设计资产的三视图必须展示角色的高光体态|每个审美停点优先控制在|严格 POV 必须套用专项公式|严格 POV 使用专项公式|时间关系链至少包含|峰值停点必须可剪辑、可截图|每镜写景别、机位|摄影指导层 =|武戏 / 动作视频必须按|爆点在哪一秒停成可截图帧|每条执行稿都要写清楚主体动作.*片内转场|每条执行稿都要写出动作链和因果链|每场戏至少有一个微型戏剧动作|每个正式故事必须有对立面|每场戏至少有一个画面停点|每条视觉执行稿至少判断|每条可复制图片提示词至少要落实这些|正常对话.*默认使用.*68%-72%|音乐卡点.*也要写清.*前中后景|表情主任务镜头不能用低位身体|只有手部证据.*才允许'
if rg -n "$emotion_conflict_pattern" \
  AGENTS.md \
  "02_共享资产库/00_核心规则手册.md" \
  skills/laohu_script_writer/SKILL.md \
  skills/laohu_visual_assets/SKILL.md \
  skills/laohu_video_prompt/SKILL.md \
  "02_共享资产库/01_模板库/图片模板/模板_AI图片提示词_资产型通用结构.md" \
  "02_共享资产库/01_模板库/视频模板/模板_视频提示词_基础设定氛围画面内容.md" \
  "02_共享资产库/01_模板库/视频模板/模板_视频生成质量检查清单.md" \
  "02_共享资产库/02_视觉语言资产/画面风格库/画面氛围与画质规范.md" \
  "02_共享资产库/02_视觉语言资产/镜头语言库/镜头语言词典.md" \
  "02_共享资产库/03_模型适配/Seedance2/Seedance2视频提示词书写规范.md" \
  "02_共享资产库/05_工具流程/助手执行失败经验与防复发规则.md" \
  输入输出索引.md; then
  fail "active rules still force every shot to fill non-contributing craft fields"
else
  pass "active rules do not force every shot to fill non-contributing craft fields"
fi
require_pattern "02_共享资产库/00_核心规则手册.md" "主体与注意力目标.*动作与表演.*效果系统.*节奏与时长|运镜.*情绪倾向.*固定含义" "core manual defines video prompt causal writing"
require_pattern "02_共享资产库/02_视觉语言资产/高质量创作特征资产库/高质量AI视频提示词开发计划.md" "主体.*动作.*效果.*节奏|观看意图.*物理路径.*屏幕变化.*情绪倾向.*停点" "video quality plan defines open four-core reasoning"
require_pattern "skills/laohu_video_prompt/SKILL.md" "视频画面内容四核|观看意图.*摄影机物理路径.*屏幕变化.*情绪倾向.*停点" "video prompt skill turns camera terms into visible change"
require_pattern "skills/laohu_video_prompt/SKILL.md" "图生视频.*文生视频|描述预算|资产.*重复" "video prompt skill distinguishes image-to-video and text-to-video budgets"
require_pattern "02_共享资产库/01_模板库/视频模板/模板_视频提示词_基础设定氛围画面内容.md" "注意力目标.*动作与表演.*效果系统.*节奏与时长|焦点.*环境.*光色.*速度.*声音" "video prompt template exposes the four-core shot logic"
require_pattern "02_共享资产库/02_视觉语言资产/镜头语言库/镜头语言词典.md" "运镜情绪.*固定字典|情绪倾向.*上下文|物理路径.*可见结果" "shot dictionary treats camera emotion as contextual"
require_pattern "02_共享资产库/02_视觉语言资产/声音与同期声库/声音提示词规范.md" "画外声音.*不可见空间|声源.*镜头之外|默认.*BGM" "sound guide defines offscreen space and no-BGM default"
require_pattern "02_共享资产库/03_模型适配/Seedance2/Seedance2视频提示词书写规范.md" "图生视频.*资产输入|文生视频.*必要外观|主体.*动作.*效果.*节奏" "Seedance profile adapts prompt detail to input assets"
require_pattern "02_共享资产库/05_工具流程/助手执行失败经验与防复发规则.md" "四核不是四个词槽|镜头术语.*可见变化|情绪建立时间" "failure rules record video four-core reasoning"
require_pattern "输入输出索引.md" "视频提示词四核|主体.*动作.*效果.*节奏|运镜具象化" "index records the video prompt four-core upgrade"
require_pattern "skills/laohu_generation_review/SKILL.md" "主注意力目标.*动作与表演.*效果系统.*节奏与时长|四核" "generation review diagnoses the four video-content cores"
require_pattern "02_共享资产库/01_模板库/视频模板/模板_视频生成质量检查清单.md" "主体与注意力目标.*动作与表演.*效果系统.*节奏与时长|运镜具象化" "video QA checks the four video-content cores"
require_pattern "skills/laohu_vibe_creating_prompt/SKILL.md" "摄影机物理路径.*屏幕变化|不能.*技术噪声.*运镜" "VC optimization preserves executable camera paths"
require_pattern "AGENTS.md" "首尾帧双端锚定|首帧状态.*触发机制.*中间状态链.*尾帧召回.*精确收束" "top-level rules define first-last-frame dual-anchor generation"
require_pattern "02_共享资产库/00_核心规则手册.md" "首尾帧生成模式.*不同于.*尾帧.*首帧|不变量.*变化量.*共同桥梁.*最大断裂点" "core manual distinguishes dual-anchor generation from clip stitching"
require_pattern "02_共享资产库/02_视觉语言资产/高质量创作特征资产库/高质量AI视频提示词开发计划.md" "首尾帧变换链|端点兼容性分析|尾帧元素提前召回|精确落入尾帧" "video quality plan defines an open dual-anchor transition chain"
require_pattern "skills/laohu_video_prompt/SKILL.md" "首尾帧双端锚定模式|必须保持什么.*必须改变什么.*共同桥梁.*最大断裂点|尾帧召回.*减速收束" "video prompt skill implements first-last-frame transition reasoning"
require_pattern "02_共享资产库/01_模板库/视频模板/模板_视频提示词_基础设定氛围画面内容.md" "【首帧参考@图1】|【尾帧参考@图2】|首帧状态.*触发.*中间状态.*尾帧召回.*收束" "video prompt template supports dual-anchor references and transition chain"
require_pattern "02_共享资产库/03_模型适配/Seedance2/Seedance2视频提示词书写规范.md" "首尾帧生成模式|双端参考|端点兼容性|模型能力和版本" "Seedance profile documents dual-anchor generation without freezing version limits"
require_pattern "02_共享资产库/01_模板库/视频模板/模板_视频生成质量检查清单.md" "首尾帧双端锚定|端点兼容性|尾帧召回|落帧" "video QA checks dual-anchor transition quality"
require_pattern "skills/laohu_generation_review/SKILL.md" "首尾帧模式|端点.*中间变换链.*尾帧收束|首帧漂移.*尾帧未落准" "generation review diagnoses dual-anchor transition failures"
require_pattern "skills/laohu_vibe_creating_prompt/SKILL.md" "首尾帧双端锚定|不变量.*变化量|尾帧召回.*收束" "VC optimization preserves dual-anchor transition constraints"
require_pattern "02_共享资产库/05_工具流程/助手执行失败经验与防复发规则.md" "^### 110\\. 首尾帧生成不是两个画面之间随便加特效" "failure rules record the reusable dual-anchor lesson"
require_pattern "输入输出索引.md" "首尾帧双端锚定|端点兼容性.*中间状态链.*尾帧收束" "index records the dual-anchor prompt upgrade"

if python3 - <<'PY'
from pathlib import Path
project = Path("01_作品项目/已发布/2026-06-28_30秒钟带你体验谈恋爱")
paths = [
    project / "00_阶段确认记录.md",
    project / "01_世界观故事/文本/00_故事确认.md",
    project / "01_世界观故事/文本/2026-06-28_情绪节奏设计_30秒钟带你体验谈恋爱.md",
    project / "02_剧本/文本/2026-06-28_剧本_30秒钟带你体验谈恋爱.md",
    project / "03_视觉资产/文本/2026-06-28_图片提示词_30秒钟带你体验谈恋爱.md",
    Path("输入输出索引.md"),
]
bad = []
for path in paths:
    if not path.exists():
        continue
    text = path.read_text()
    if "A1-E 林栀表情一致性参考图" in text or "A1-E_林栀表情一致性参考" in text:
        bad.append(str(path))
if bad:
    print("current romance project should not keep A1-E as an executable expression asset:")
    for item in bad:
        print(item)
    raise SystemExit(1)
PY
then
  pass "current romance project has no executable A1-E expression asset"
else
  fail "current romance project still references executable A1-E expression asset"
fi

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
