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
require_pattern "skills/laohu_visual_assets/SKILL.md" "风格|图片生成执行单|A/B/C/D|封面|laohu_video_prompt" "visual assets covers merged image and cover work"
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
require_pattern "skills/laohu_visual_assets/SKILL.md" "高光体态|胸腔舒展.*肩背打开.*站姿自信|左手.*右手.*拇指" "visual assets enforces highlight posture and correct left-right hands"
require_pattern "skills/laohu_visual_assets/SKILL.md" "信息优先级.*三视图.*脸部.*比例图|手模级|十六进制 RGB|厘米测量线" "visual assets enforces character asset layout information priority"
require_pattern "skills/laohu_visual_assets/SKILL.md" "人物设计资产本身会反向影响后续视频肤色|冷白偏中性的白皙肤色|白皙通透|柔雾奶油肌|参考图.*偏黄.*偏油" "visual assets enforces asset-level complexion before video reference"
require_pattern "02_共享资产库/00_核心规则手册.md" "人物设计资产本身会反向影响后续视频肤色|资产图里的肤色.*强锚点|冷白偏中性的白皙肤色|白皙通透|柔雾奶油肌" "core manual enforces asset-level complexion before video reference"
require_pattern "02_共享资产库/01_模板库/图片模板/模板_AI图片提示词_资产型通用结构.md" "人物设计资产会作为视频参考图|先锁住肤色妆效|冷白偏中性的白皙肤色|白皙通透|柔雾奶油肌" "image asset template enforces asset-level complexion before video reference"
require_pattern "02_共享资产库/05_工具流程/助手执行失败经验与防复发规则.md" "人物资产肤色会反向污染视频生成|视频参考图.*强锚点|冷白偏中性|白皙通透|柔雾奶油肌" "failure rules record asset-level complexion contamination"
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
require_pattern "skills/laohu_video_prompt/SKILL.md" "冷白偏中性的白皙肤色|肤色通透匀净|清透裸妆|轻薄服帖底妆|柔雾奶油肌|柔雾哑光带内透光肤感|自然漫反射|柔和次表面透光" "video prompt skill enforces Chinese positive complexion and makeup finish system"
require_pattern "skills/laohu_video_prompt/SKILL.md" "风格交集.*主风格母体.*辅助风格.*胶片 / 滤镜分级.*明度对比.*光影方式.*肤色妆效.*场景环境色.*情绪阶段边界|日系清新治愈青春电影色彩.*海边低饱和胶片写真" "video prompt skill enforces style-intersection mood and quality system"
require_pattern "skills/laohu_video_prompt/SKILL.md" "摄影指导层.*光影分离.*动态光源 / 光影运动.*光源色温.*主体细节束.*空间层次.*时间天气空气.*镜头参数 / 景深.*画面类型自动选型.*情绪反差点" "video prompt skill enforces cinematography direction layer"
require_pattern "skills/laohu_video_prompt/SKILL.md" "主体细节束.*颜色 \\+ 材质 \\+ 纹理 \\+ 状态 \\+ 反光 \\+ 破损 / 湿度 / 瑕疵 \\+ 边缘细节" "video prompt skill enforces subject detail bundle"
require_pattern "skills/laohu_video_prompt/SKILL.md" "动态光源.*风吹树叶形成移动树影|柔金侧逆光.*动态树影|镜头参数.*85mm.*50mm.*35mm.*135mm" "video prompt skill enforces motivated dynamic light and focal-length selection"
require_pattern "02_共享资产库/00_核心规则手册.md" "风格交集.*主风格母体.*辅助风格.*胶片 / 滤镜分级.*明度对比.*光影方式.*肤色妆效.*场景环境色.*情绪阶段边界|真人写实海边情绪短片.*日系清新治愈青春电影色彩" "core manual enforces style-intersection mood and quality system"
require_pattern "02_共享资产库/00_核心规则手册.md" "摄影指导层.*光影分离.*动态光源 / 光影运动.*光源色温.*主体细节束.*空间层次.*时间天气空气.*镜头参数 / 景深.*画面类型自动选型.*情绪反差点" "core manual enforces cinematography direction layer"
require_pattern "02_共享资产库/01_模板库/视频模板/模板_视频提示词_基础设定氛围画面内容.md" "风格交集.*主风格母体.*辅助风格.*胶片 / 滤镜分级.*明度对比.*光影方式.*肤色妆效.*场景环境色.*情绪阶段边界|富士胶片清透蓝绿倾向.*柯达 Portra" "video prompt template enforces style-intersection mood and quality system"
require_pattern "02_共享资产库/01_模板库/视频模板/模板_视频提示词_基础设定氛围画面内容.md" "摄影指导层.*光影分离.*动态光源 / 光影运动.*光源色温.*主体细节束.*空间层次.*时间天气空气.*镜头参数 / 景深.*画面类型自动选型.*情绪反差点" "video prompt template enforces cinematography direction layer"
require_pattern "02_共享资产库/05_工具流程/助手执行失败经验与防复发规则.md" "情绪短片的氛围画质必须建立风格交集|清新透亮.*日系治愈系风格色彩|富士胶片清透蓝绿倾向.*柯达 Portra" "failure rules record style-intersection mood and quality lesson"
require_pattern "02_共享资产库/05_工具流程/助手执行失败经验与防复发规则.md" "视频提示词必须有摄影指导层|光影分离.*动态光源.*光源色温.*主体细节束.*镜头参数.*情绪反差点" "failure rules record cinematography direction layer lesson"
require_pattern "skills/laohu_video_prompt/SKILL.md" "正式视频提示词代码块里禁止写作者意图|让观众懂|表现孩子不冷漠|避免误读|模型不知道上下文|屏幕证据" "video prompt blocks author-intent and process explanations in formal prompts"
require_pattern "skills/laohu_video_prompt/SKILL.md" "风格核心|视觉基调|色彩与影调|Photirealism|IMAX|Panavision|光影.*嵌入.*自然段" "video prompt enforces benchmark vibe fields and embedded lighting prose"
require_pattern "skills/laohu_video_prompt/SKILL.md" "基础设定.*世界观.*固定资产行.*声音设定|进入基础设定.*固定资产支撑|没有固定资产.*画面内容" "video prompt enforces fixed assets in basic setting"
require_pattern "skills/laohu_video_prompt/SKILL.md" "【形象参考@xx】|【音色参考@xx】|双参考占位|不要在每条视频提示词里重复长篇基础声线" "video prompt enforces character image and voice reference placeholders"
require_pattern "skills/laohu_video_prompt/SKILL.md" "正向收束|目标画面|排除句|抽象质量边界|代码块外" "video prompt enforces positive model-facing prompt convergence"
require_pattern "skills/laohu_video_prompt/SKILL.md" "提示词资产.*基础设定.*氛围与画质|图片资产 / 固定资产.*画面内容.*交互|未资产化元素.*画面内容.*详细描述" "video prompt enforces asset-aware画面内容 description budget"
require_pattern "skills/laohu_video_prompt/SKILL.md" "【@资产名】|资产占位|固定实体|资产图片引用" "video prompt supports explicit asset placeholders"
require_pattern "skills/laohu_video_prompt/SKILL.md" "动作链|因果链|冲击结果|连锁反应|动作段落" "video prompt enforces benchmark-level action choreography"
require_pattern "skills/laohu_video_prompt/SKILL.md" "丁达尔效应|轮廓光|侧逆光|体积光|明暗交错" "video prompt includes concrete lighting vocabulary"
require_pattern "skills/laohu_video_prompt/SKILL.md" "2000 字以内|分镜编号.*所属场次.*镜头任务|基础设定.*全片统一层|画面内容不默认逐秒拆死" "video prompt enforces concise model-facing prompts"
require_pattern "skills/laohu_video_prompt/SKILL.md" "剧本.*语气 / 神态.*视频提示词|表情来源|表情占用时长|眼神.*眉头.*嘴角.*呼吸|POV.*手部.*呼吸.*声音" "video prompt inherits script demeanor annotations into visible performance"
require_pattern "skills/laohu_video_prompt/SKILL.md" "视频提示词不得擅自改剧本台词|台词原文.*旁白原文.*VO 原文.*字幕原文|不能改句子.*删关键词.*加新句|VID-27" "video prompt locks confirmed script dialogue"
require_pattern "skills/laohu_video_prompt/SKILL.md" "单点反馈.*全局扫描同类问题|指出某一个镜头.*默认.*通用失败模式|抽取剧本全部对白.*全分镜视频提示词" "video prompt enforces global scan after single-shot feedback"
require_pattern "02_共享资产库/01_模板库/视频模板/模板_视频提示词_基础设定氛围画面内容.md" "单点反馈必须触发全局同类扫描|台词问题扫所有对白.*VO.*OS.*画外音|POV 问题扫所有主观镜头|VID-27" "video prompt template enforces global scan after single-shot feedback"
require_pattern "skills/laohu_video_prompt/SKILL.md" "分镜表格输出文件|第一个分镜的视频提示词展示文件|所有分镜视频提示词结果输出文件|对话里不要贴长篇" "video prompt enforces staged file outputs"
require_pattern "skills/laohu_video_prompt/SKILL.md" "视频提示词交付必须方便老胡直接复制|代码块里只放可直接投喂视频模型|代码块外" "video prompt enforces copyable video prompt code blocks"
require_pattern "skills/laohu_video_prompt/SKILL.md" "每个最终视频单元.*VID.*【故事板图片提示词】.*【视频生成提示词】|表情驱动.*故事板.*胸部以上|人物.*65%-80%" "video prompt enforces paired close-framed storyboard prompts"
require_pattern "skills/laohu_video_prompt/SKILL.md" "首帧参考@VID-A尾帧|【画面内容】.*第一句.*第 0 秒使用.*首帧参考|同一景别.*人物比例.*光源方向.*背景锚点.*表情余韵" "video prompt enforces one-shot tail-frame to head-frame continuity"
require_pattern "skills/laohu_video_prompt/SKILL.md" "对镜头情绪表演|声音方向|镜头前方.*脑海|眼线.*镜头|风景只做留白" "video prompt enforces direct-to-camera emotional performance"
require_pattern "skills/laohu_video_prompt/SKILL.md" "默认在同一个阶段文件上迭代更新|不自动新建 v1/v2/v3" "video prompt enforces single-file iteration"
require_pattern "skills/laohu_generation_review/SKILL.md" "生成诊断|剪辑验收|发布复盘|最多 3 个返修动作|下一版修正提示词" "generation review covers merged review work"
require_pattern "skills/laohu_generation_review/SKILL.md" "归档、复盘、生成结果诊断和发布复盘必须写入文件|生成复盘文件|发布复盘文件" "generation review enforces file output"
require_pattern "skills/laohu_generation_review/SKILL.md" "默认在同一个当前文件上更新|不自动新建 v1/v2/v3" "generation review enforces single-file iteration"
require_pattern "skills/laohu_generation_review/SKILL.md" "人物皮肤油|脸部油亮|正向肤色妆效缺失|肤色冷暖与明度|清透裸妆|柔雾奶油肌|自然漫反射" "generation review diagnoses oily skin as missing Chinese positive complexion and makeup system"
require_pattern "02_共享资产库/00_核心规则手册.md" "正式视频提示词必须严格使用.*模板_视频提示词_基础设定氛围画面内容|不能混进正式视频提示词正文" "core manual enforces strict video prompt template"
require_pattern "02_共享资产库/00_核心规则手册.md" "每个最终视频单元.*VID.*【故事板图片提示词】.*【视频生成提示词】|表情驱动.*故事板.*胸部以上|人物.*65%-80%" "core manual enforces paired close-framed storyboard prompts"
require_pattern "02_共享资产库/00_核心规则手册.md" "冷白偏中性的白皙肤色|肤色通透匀净|清透裸妆|轻薄服帖底妆|柔雾奶油肌|提示词资产" "core manual enforces Chinese positive complexion and makeup prompt asset"
require_pattern "02_共享资产库/01_模板库/视频模板/模板_视频提示词_基础设定氛围画面内容.md" "清透裸妆|轻薄服帖底妆|柔雾奶油肌|柔雾哑光带内透光肤感|缎光柔雾肤感|提示词资产" "video prompt template enforces Chinese positive complexion and makeup prompt asset"
require_pattern "02_共享资产库/05_工具流程/助手执行失败经验与防复发规则.md" "情绪人像必须先写肤色妆效|冷白偏中性的白皙肤色|肤色通透匀净|清透裸妆|P-SKIN 林栀皮肤妆效提示词资产" "failure rules record Chinese positive complexion and makeup system"
require_pattern "02_共享资产库/00_核心规则手册.md" "首帧参考@VID-A尾帧|【画面内容】.*第一句.*第 0 秒使用.*首帧参考|同一景别.*人物比例.*光源方向.*背景锚点.*表情余韵" "core manual enforces one-shot tail-frame to head-frame continuity"
require_pattern "02_共享资产库/00_核心规则手册.md" "对镜头情绪表演|镜头.*对话对象|声音方向|视线箭头指向镜头|风景.*不能成为主要表演对象" "core manual enforces direct-to-camera emotional performance"
require_pattern "02_共享资产库/00_核心规则手册.md" "每条正式视频提示词 = 一次独立投喂|不能写.*沿用全片|图片资产|15 秒内同场合并规则" "core manual enforces independent prompt and merge rules"
require_pattern "02_共享资产库/00_核心规则手册.md" "laohu_vibe_creating_prompt|视频提示词生成结果在输出呈现前|外部原文 skill|重新落回" "core manual enforces VC optimization pass"
require_pattern "02_共享资产库/00_核心规则手册.md" "转场不是.*后期备注|遮挡转场|明暗转场|运镜转场|匹配转场" "core manual enforces in-frame transitions"
require_pattern "02_共享资产库/00_核心规则手册.md" "画面内容.*主体动作.*环境运动.*镜头路径.*构图层次" "core manual enforces detailed画面内容"
require_pattern "02_共享资产库/00_核心规则手册.md" "关键发声镜头不能只依赖.*【音色参考@xx】|短视频开场钩子.*本镜声线|冷感磁性女中音.*近麦干声" "core manual enforces key-voice shot timbre restatement"
require_pattern "02_共享资产库/00_核心规则手册.md" "台词、旁白、画外音和脑内 VO.*声音参数|音高 / 音区.*响度 / 音量.*语速 / 节奏.*停顿 / 气口.*重音位置.*气息状态.*咬字 / 吐字.*混响和衰减" "core manual enforces parameterized voice performance"
require_pattern "02_共享资产库/00_核心规则手册.md" "VO 是推动人物表情变化的主要触发器|按情绪阶段设计声音曲线|初识.*热恋.*平淡.*猜忌.*争吵.*决裂" "core manual enforces staged VO emotional curve"
require_pattern "02_共享资产库/00_核心规则手册.md" "人物情绪开场.*肌肉路径|单侧嘴角.*呼吸.*停顿|皮肤.*曝光.*雾面底妆.*真实毛孔|服装.*耳坠.*海风" "core manual enforces emotional portrait expression, skin and environment interaction"
require_pattern "02_共享资产库/00_核心规则手册.md" "正式视频提示词正文不能写作者意图|让观众懂|表现孩子不冷漠|防误读说明|生成流程解释|可见 / 可听证据" "core manual blocks author-intent and process explanations in formal prompts"
require_pattern "02_共享资产库/00_核心规则手册.md" "风格核心|视觉基调|色彩与影调|Photirealism|IMAX|Panavision|光影.*嵌入.*自然段" "core manual enforces benchmark vibe fields and embedded lighting prose"
require_pattern "02_共享资产库/00_核心规则手册.md" "基础设定.*世界观.*资产行.*声音设定|进入.*基础设定.*固定资产支撑|没有固定资产.*画面内容" "core manual enforces fixed assets in basic setting"
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
require_pattern "02_共享资产库/01_模板库/视频模板/模板_视频提示词_基础设定氛围画面内容.md" "关键发声镜头.*音色例外|短视频开场钩子.*【音色参考@xx】|冷感磁性女中音.*近麦干声|情绪人像.*雾面底妆.*真实毛孔" "video prompt template enforces key voice and emotional portrait detail"
require_pattern "02_共享资产库/01_模板库/视频模板/模板_视频提示词_基础设定氛围画面内容.md" "台词、旁白、画外音和脑内 VO.*参数化|音高 / 音区.*响度 / 音量.*语速 / 节奏.*停顿 / 气口.*重音位置.*气息状态.*咬字 / 吐字.*混响和衰减" "video prompt template enforces parameterized voice performance"
require_pattern "02_共享资产库/02_视觉语言资产/声音与同期声库/声音提示词规范.md" "台词与 VO 表演参数|音高 / 音区.*响度 / 音量.*语速 / 节奏.*停顿 / 气口.*重音 / 强调.*气息 / 发声状态.*咬字 / 吐字.*距离 / 空间.*混响 / 衰减" "sound guide defines voice performance parameters"
require_pattern "02_共享资产库/01_模板库/视频模板/模板_视频提示词_基础设定氛围画面内容.md" "首帧参考@VID-A尾帧|【画面内容】.*第一句.*第 0 秒使用.*首帧参考|同一景别.*人物比例.*光源方向.*背景锚点" "video prompt template enforces one-shot tail-frame to head-frame continuity"
require_pattern "02_共享资产库/01_模板库/视频模板/模板_视频提示词_基础设定氛围画面内容.md" "对镜头情绪表演规则|眼线箭头指向镜头中心|声音方向|看向海面|看向天空" "video prompt template enforces direct-to-camera storyboard and prompt checks"
require_pattern "02_共享资产库/05_工具流程/助手执行失败经验与防复发规则.md" "画面内容必须先建立场景关系图|人物和物品.*物品和物品.*人物和人物|交互方式 \\+ 接触点 \\+ 作用力大小轻重 \\+ 受力方向 \\+ 可见结果|光源位置 \\+ 光线方向 \\+ 光线类型" "failure rules record scene relationship, interaction force, motion and lighting causality"
require_pattern "02_共享资产库/05_工具流程/助手执行失败经验与防复发规则.md" "多段视频拼成一镜到底必须写首尾帧复用|【画面内容】.*第一句.*第 0 秒使用.*首帧参考|同一景别.*人物比例.*光源方向.*背景锚点" "failure rules record one-shot tail-frame to head-frame continuity"
require_pattern "02_共享资产库/05_工具流程/助手执行失败经验与防复发规则.md" "关键发声和情绪开场不能只格式正确|冷感磁性女中音.*近麦干声|表情肌肉路径|雾面底妆.*真实毛孔|服装、首饰和环境必须参与情绪" "failure rules record key voice and emotional portrait detail"
require_pattern "02_共享资产库/05_工具流程/助手执行失败经验与防复发规则.md" "关键 VO 不能只写抽象情绪词|音高 / 音区.*响度 / 音量.*语速 / 节奏.*停顿 / 气口.*重音位置.*气息状态.*咬字 / 吐字.*距离感.*混响和衰减|男声温柔深情，带压迫感" "failure rules record parameterized VO performance regression"
require_pattern "02_共享资产库/05_工具流程/助手执行失败经验与防复发规则.md" "对镜头情绪表演不能写成看向风景或声音方向|镜头就是对话对象|从镜头位置进入她脑海|视线箭头指向镜头" "failure rules record direct-to-camera emotional performance regression"
require_pattern "skills/laohu_video_prompt/SKILL.md" "壁纸帧 / 审美停点|暂停后仍然成立|主体轮廓.*前景 / 中景 / 背景.*视觉中心.*留白.*主次色彩.*方向性光影.*材质细节.*镜头停稳点" "video prompt skill enforces wallpaper-frame aesthetic stopping point"
require_pattern "02_共享资产库/00_核心规则手册.md" "壁纸帧 / 审美停点|封面候选、壁纸、海报局部或段落记忆点|主体轮廓.*前景 / 中景 / 背景.*视觉中心.*留白.*色彩.*光影" "core manual enforces wallpaper-frame aesthetic stopping point"
require_pattern "02_共享资产库/01_模板库/视频模板/模板_视频提示词_基础设定氛围画面内容.md" "壁纸帧 / 审美停点|暂停后仍然成立|主体轮廓.*前景 / 中景 / 背景.*视觉中心.*留白.*主次色彩.*方向性光影.*材质细节.*镜头停稳点" "video prompt template enforces wallpaper-frame aesthetic stopping point"
require_pattern "skills/laohu_generation_review/SKILL.md" "壁纸帧 / 审美停点|没有值得截图|主体轮廓.*层次.*留白.*光影记忆点|暂停后仍然成立" "generation review scores wallpaper-frame aesthetic stopping point"
require_pattern "02_共享资产库/01_模板库/视频模板/模板_视频生成质量检查清单.md" "壁纸帧 / 审美停点|值得截图|封面候选、壁纸或段落记忆点|主体轮廓.*前景 / 中景 / 背景.*视觉中心.*留白" "video generation QA checks wallpaper-frame aesthetic stopping point"
require_pattern "02_共享资产库/02_视觉语言资产/画面风格库/画面氛围与画质规范.md" "壁纸帧 / 审美停点|抽帧可用|主体轮廓 \\+ 前中后景层次 \\+ 视觉中心 \\+ 留白 \\+ 主次色彩 \\+ 方向性光影 \\+ 材质细节 \\+ 情绪张力 \\+ 镜头停稳点" "visual style guide defines wallpaper-frame aesthetic stopping point"
require_pattern "02_共享资产库/05_工具流程/助手执行失败经验与防复发规则.md" "视频提示词必须设计壁纸帧 / 审美停点|几乎找不到一个可以作为壁纸的画面|主体轮廓、前中后景层次、视觉中心、留白、主次色彩、方向性光影、材质细节、情绪张力和镜头停稳点" "failure rules record missing wallpaper-frame aesthetic stopping point"
require_pattern "skills/laohu_video_prompt/SKILL.md" "构图逻辑|三分构图.*黄金分割构图.*中心对称构图.*框架式构图.*引导线构图.*对角线构图.*留白构图.*前景框构图.*三角稳定构图" "video prompt skill enforces wallpaper-frame composition structures"
require_pattern "skills/laohu_video_prompt/SKILL.md" "大面积干净留白.*上方留白.*侧边留白.*极简留白.*负空间|视觉重心.*稳定.*主体.*1/3.*边角.*干净|21:9.*3:4.*16:9.*方形文艺画幅" "video prompt skill enforces negative space, balance, clean corners and frame ratios"
require_pattern "02_共享资产库/00_核心规则手册.md" "构图逻辑|三分构图.*黄金分割构图.*中心对称构图.*框架式构图.*引导线构图.*对角线构图.*留白构图.*前景框构图.*三角稳定构图" "core manual enforces wallpaper-frame composition structures"
require_pattern "02_共享资产库/00_核心规则手册.md" "大面积干净留白.*上方留白.*侧边留白.*负空间|视觉重心.*稳定.*边角.*干净|21:9.*3:4.*16:9.*方形文艺画幅" "core manual enforces negative space, balance, clean corners and frame ratios"
require_pattern "02_共享资产库/01_模板库/视频模板/模板_视频提示词_基础设定氛围画面内容.md" "构图逻辑|三分构图.*黄金分割构图.*中心对称构图.*框架式构图.*引导线构图.*对角线构图.*留白构图.*前景框构图.*三角稳定构图" "video prompt template enforces composition structures"
require_pattern "02_共享资产库/01_模板库/视频模板/模板_视频生成质量检查清单.md" "构图逻辑|主体落点|大面积干净留白.*上方留白.*侧边留白.*负空间|16:9.*21:9.*3:4.*方形文艺画幅" "video QA checklist checks composition logic and ratios"
require_pattern "skills/laohu_generation_review/SKILL.md" "构图逻辑|主体落点|大面积干净留白.*上方留白.*侧边留白.*负空间|16:9.*21:9.*3:4.*方形文艺画幅" "generation review diagnoses composition logic"
require_pattern "02_共享资产库/02_视觉语言资产/画面风格库/画面氛围与画质规范.md" "构图逻辑 = 画幅比例 \\+ 构图结构 \\+ 主体落点 \\+ 留白方向 \\+ 引导线 / 框架 \\+ 边角清洁 \\+ 镜头停稳点|三分构图.*黄金分割构图.*中心对称构图" "visual style guide defines composition logic formula"
require_pattern "02_共享资产库/05_工具流程/助手执行失败经验与防复发规则.md" "壁纸帧必须有构图逻辑|不能只堆画面元素|构图结构、主体落点、留白方向、视觉重心、边角清洁、画幅比例和镜头停稳点" "failure rules record missing composition logic"
require_pattern "skills/laohu_video_prompt/SKILL.md" "光影体系 = 时段光线 \\+ 主光方向 \\+ 弱辅光 \\+ 轮廓光 / 反光 \\+ 阴影层次 \\+ 材质反应 \\+ 动态稳定|黄金一小时逆光.*日出柔光.*蓝调时刻冷光.*傍晚漫射光.*雨后柔和天光" "video prompt skill enforces structured lighting system"
require_pattern "skills/laohu_video_prompt/SKILL.md" "单侧轮廓逆光.*侧顺柔光.*层次主光 \\+ 弱辅光.*包裹柔光.*柔和窗光|柔和虚化阴影.*低对比度阴影.*细腻层次阴影.*长投影.*镜面反光.*水面反光" "video prompt skill enforces light layers, shadow and reflections"
require_pattern "02_共享资产库/00_核心规则手册.md" "光影体系 = 时段光线 \\+ 主光方向 \\+ 弱辅光 \\+ 轮廓光 / 反光 \\+ 阴影层次 \\+ 材质反应 \\+ 动态稳定|黄金一小时逆光.*日出柔光.*蓝调时刻冷光.*傍晚漫射光.*雨后柔和天光" "core manual enforces structured lighting system"
require_pattern "02_共享资产库/00_核心规则手册.md" "单侧轮廓逆光.*侧顺柔光.*层次主光 \\+ 弱辅光.*包裹柔光.*柔和窗光|柔和虚化阴影.*低对比度阴影.*细腻层次阴影.*长投影.*镜面反光.*水面反光" "core manual enforces light layers, shadow and reflections"
require_pattern "02_共享资产库/01_模板库/视频模板/模板_视频提示词_基础设定氛围画面内容.md" "壁纸帧必须有光影体系|时段光线 \\+ 主光方向 \\+ 弱辅光 \\+ 轮廓光 / 反光 \\+ 阴影层次 \\+ 材质反应 \\+ 动态稳定|黄金一小时逆光.*日出柔光.*蓝调时刻冷光" "video prompt template enforces structured lighting system"
require_pattern "02_共享资产库/01_模板库/视频模板/模板_视频生成质量检查清单.md" "光影体系|时段光线.*主光方向.*弱辅光.*轮廓光 / 反光.*阴影层次.*材质反应.*动态稳定|生硬死黑阴影.*动态光源乱闪" "video QA checklist checks structured lighting system"
require_pattern "skills/laohu_generation_review/SKILL.md" "光影体系|画面平、灰、没有层次|时段定向光线、主光、弱辅光、轮廓光 / 反光、柔和阴影或长投影|光源方向稳定" "generation review diagnoses lighting system"
require_pattern "02_共享资产库/02_视觉语言资产/画面风格库/画面氛围与画质规范.md" "光影体系 = 时段光线 \\+ 主光方向 \\+ 弱辅光 \\+ 轮廓光 / 反光 \\+ 阴影层次 \\+ 材质反应 \\+ 动态稳定|黄金一小时逆光.*日出柔光.*蓝调时刻冷光" "visual style guide defines structured lighting formula"
require_pattern "02_共享资产库/05_工具流程/助手执行失败经验与防复发规则.md" "光影体系不能只写自然光|时段光线 \\+ 主光方向 \\+ 弱辅光 \\+ 轮廓光 / 反光 \\+ 阴影层次 \\+ 材质反应 \\+ 动态稳定|画面平灰 / 光影潦草 / 没有高级质感 / 光源乱闪" "failure rules record missing lighting system"
require_pattern "skills/laohu_video_prompt/SKILL.md" "构图、光影、色彩以及后续所有审美模块.*不能被当成封闭词表|启发样例.*不是固定菜单|不要机械照抄用户列举词" "video prompt skill treats aesthetic examples as open frameworks"
require_pattern "02_共享资产库/00_核心规则手册.md" "构图、光影、色彩以及后续所有审美模块.*不能被当成封闭词表|启发样例.*不是固定菜单|不要机械照抄用户列举词" "core manual treats aesthetic examples as open frameworks"
require_pattern "02_共享资产库/01_模板库/视频模板/模板_视频提示词_基础设定氛围画面内容.md" "构图、光影、色彩以及后续审美模块都不是封闭词表|启发样例.*不是固定菜单|未列出的有效方案也可以使用" "video prompt template treats aesthetic examples as open frameworks"
require_pattern "skills/laohu_video_prompt/SKILL.md" "色彩体系 = 主色调 \\+ 辅助色 \\+ 点缀色 \\+ 饱和度策略 \\+ 明度 / 对比 \\+ 环境色反光 \\+ 色彩过渡 \\+ 统一滤镜 / 分级|莫兰迪低饱和.*青橙电影色调.*冷调蓝灰.*复古胶片棕调" "video prompt skill enforces color aesthetic system"
require_pattern "skills/laohu_video_prompt/SKILL.md" "1 个主色 \\+ 1 个辅助色 \\+ 1 个小面积点缀色|通常不超过 2 种主色|统一环境色.*柔和色彩渐变|富士胶片色调.*柯达金 200.*电影 LUT.*轻微暗角" "video prompt skill enforces color hierarchy and grading"
require_pattern "02_共享资产库/00_核心规则手册.md" "色彩体系 = 主色调 \\+ 辅助色 \\+ 点缀色 \\+ 饱和度策略 \\+ 明度 / 对比 \\+ 环境色反光 \\+ 色彩过渡 \\+ 统一滤镜 / 分级|莫兰迪低饱和.*青橙电影色调.*冷调蓝灰.*复古胶片棕调" "core manual enforces color aesthetic system"
require_pattern "02_共享资产库/01_模板库/视频模板/模板_视频提示词_基础设定氛围画面内容.md" "壁纸帧必须有色彩美学体系|主色调 \\+ 辅助色 \\+ 点缀色 \\+ 饱和度策略 \\+ 明度 / 对比 \\+ 环境色反光 \\+ 色彩过渡 \\+ 统一滤镜 / 分级|富士胶片色调.*柯达金 200.*电影 LUT" "video prompt template enforces color aesthetic system"
require_pattern "02_共享资产库/01_模板库/视频模板/模板_视频生成质量检查清单.md" "色彩体系|主色调.*辅助色.*点缀色.*饱和度策略.*明度 / 对比.*环境色反光.*色彩过渡.*统一滤镜 / 分级|高饱和.*同时抢画面" "video QA checklist checks color aesthetic system"
require_pattern "skills/laohu_generation_review/SKILL.md" "色彩体系|廉价撞色|主色调、辅助色、小面积点缀色、饱和度策略、明度 / 对比、环境色反光、柔和色彩过渡和统一滤镜 / 分级" "generation review diagnoses color aesthetic system"
require_pattern "02_共享资产库/02_视觉语言资产/画面风格库/画面氛围与画质规范.md" "色彩体系 = 主色调 \\+ 辅助色 \\+ 点缀色 \\+ 饱和度策略 \\+ 明度 / 对比 \\+ 环境色反光 \\+ 色彩过渡 \\+ 统一滤镜 / 分级|莫兰迪低饱和色系.*青橙电影色调.*冷调蓝灰" "visual style guide defines color aesthetic system"
require_pattern "02_共享资产库/05_工具流程/助手执行失败经验与防复发规则.md" "审美模块不是封闭词表，色彩体系必须有主次、过渡和统一分级|色彩体系 = 主色调 \\+ 辅助色 \\+ 点缀色 \\+ 饱和度策略 \\+ 明度 / 对比 \\+ 环境色反光 \\+ 色彩过渡 \\+ 统一滤镜 / 分级|色彩杂乱 / 廉价撞色 / 没有统一调性" "failure rules record missing color aesthetic system"
require_pattern "skills/laohu_video_prompt/SKILL.md" "空间层次体系 = 前景虚化遮挡 \\+ 中景清晰主体 \\+ 远景朦胧环境 \\+ 焦段选择 \\+ 焦点落点 \\+ 虚实过渡 \\+ 空气透视 / 散景|85mm.*50mm.*35mm.*135mm|动态镜头.*焦点.*稳定" "video prompt skill enforces depth and spatial layering"
require_pattern "02_共享资产库/00_核心规则手册.md" "空间层次体系 = 前景虚化遮挡 \\+ 中景清晰主体 \\+ 远景朦胧环境 \\+ 焦段选择 \\+ 焦点落点 \\+ 虚实过渡 \\+ 空气透视 / 散景|85mm.*50mm.*35mm.*135mm|动态镜头.*焦点.*稳定" "core manual enforces depth and spatial layering"
require_pattern "02_共享资产库/01_模板库/视频模板/模板_视频提示词_基础设定氛围画面内容.md" "壁纸帧必须有景深与空间层次体系|前景虚化遮挡 \\+ 中景清晰主体 \\+ 远景朦胧环境 \\+ 焦段选择 \\+ 焦点落点 \\+ 虚实过渡 \\+ 空气透视 / 散景|85mm.*50mm.*35mm.*135mm" "video prompt template enforces depth and spatial layering"
require_pattern "02_共享资产库/01_模板库/视频模板/模板_视频生成质量检查清单.md" "景深与空间层次|前景虚化遮挡.*中景清晰主体.*远景朦胧环境.*焦段选择.*焦点落点|动态镜头焦点是否稳定|85mm.*50mm.*35mm.*135mm" "video QA checklist checks depth and spatial layering"
require_pattern "skills/laohu_generation_review/SKILL.md" "景深与空间层次|空间扁平 / 没有纵深 / 景深失效 / 焦点乱|前景虚化遮挡、中景清晰主体、远景朦胧环境、焦段选择、焦点落点、虚实过渡和空气透视 / 散景|85mm、50mm、35mm、135mm" "generation review diagnoses depth and spatial layering"
require_pattern "02_共享资产库/02_视觉语言资产/画面风格库/画面氛围与画质规范.md" "空间层次体系 = 前景虚化遮挡 \\+ 中景清晰主体 \\+ 远景朦胧环境 \\+ 焦段选择 \\+ 焦点落点 \\+ 虚实过渡 \\+ 空气透视 / 散景|85mm 人像定焦.*50mm 标准人文镜头.*35mm 人文广角.*135mm 长焦|动态镜头.*焦点" "visual style guide defines depth and spatial layering"
require_pattern "02_共享资产库/05_工具流程/助手执行失败经验与防复发规则.md" "景深与空间层次不能平铺|空间层次体系 = 前景虚化遮挡 \\+ 中景清晰主体 \\+ 远景朦胧环境 \\+ 焦段选择 \\+ 焦点落点 \\+ 虚实过渡 \\+ 空气透视 / 散景|空间扁平 / 没有纵深 / 景深失效 / 焦点乱" "failure rules record missing depth and spatial layering"
require_pattern "skills/laohu_video_prompt/SKILL.md" "画质材质体系 = 分辨率清晰度 \\+ 主体边缘锐度 \\+ 材质质感细分 \\+ 微细节锚点 \\+ 运动模糊控制 \\+ 画面洁净度 \\+ 介质颗粒边界|哑光柔和质感.*磨砂低反光.*丝绒柔和肌理.*金属细腻拉丝.*水雾朦胧质感|极低运动模糊.*边缘.*清晰" "video prompt skill enforces image quality and material texture"
require_pattern "02_共享资产库/00_核心规则手册.md" "画质材质体系 = 分辨率清晰度 \\+ 主体边缘锐度 \\+ 材质质感细分 \\+ 微细节锚点 \\+ 运动模糊控制 \\+ 画面洁净度 \\+ 介质颗粒边界|哑光柔和质感.*磨砂低反光.*丝绒柔和肌理.*金属细腻拉丝.*水雾朦胧质感|极低运动模糊|介质颗粒边界" "core manual enforces image quality and material texture"
require_pattern "02_共享资产库/01_模板库/视频模板/模板_视频提示词_基础设定氛围画面内容.md" "壁纸帧必须有画质与材质质感体系|分辨率清晰度 \\+ 主体边缘锐度 \\+ 材质质感细分 \\+ 微细节锚点 \\+ 运动模糊控制 \\+ 画面洁净度 \\+ 介质颗粒边界|8K 高清|极低运动模糊" "video prompt template enforces image quality and material texture"
require_pattern "02_共享资产库/01_模板库/视频模板/模板_视频生成质量检查清单.md" "画质与材质质感|分辨率清晰度.*主体边缘锐度.*材质质感细分.*微细节锚点.*运动模糊控制.*画面洁净度.*介质颗粒边界|截图停点.*极低运动模糊" "video QA checklist checks image quality and material texture"
require_pattern "skills/laohu_generation_review/SKILL.md" "画质与材质质感|截图发糊 / 质感假 / 材质糊 / 放大不能看 / 画面脏|分辨率清晰度、主体边缘锐度、材质质感细分、微细节锚点、运动模糊控制、画面洁净度和介质颗粒边界" "generation review diagnoses image quality and material texture"
require_pattern "02_共享资产库/02_视觉语言资产/画面风格库/画面氛围与画质规范.md" "画质材质体系 = 分辨率清晰度 \\+ 主体边缘锐度 \\+ 材质质感细分 \\+ 微细节锚点 \\+ 运动模糊控制 \\+ 画面洁净度 \\+ 介质颗粒边界|哑光柔和质感.*磨砂低反光.*丝绒柔和肌理.*金属细腻拉丝.*水雾朦胧质感|动态模糊.*管理" "visual style guide defines image quality and material texture"
require_pattern "02_共享资产库/05_工具流程/助手执行失败经验与防复发规则.md" "画质与材质质感不能只写 8K|画质材质体系 = 分辨率清晰度 \\+ 主体边缘锐度 \\+ 材质质感细分 \\+ 微细节锚点 \\+ 运动模糊控制 \\+ 画面洁净度 \\+ 介质颗粒边界|截图发糊 / 质感假 / 材质糊 / 放大不能看 / 画面脏" "failure rules record missing image quality and material texture"
require_pattern "skills/laohu_video_prompt/SKILL.md" "氛围环境体系 = 天气 / 时间基底 \\+ 空气媒介 \\+ 漂浮微粒 \\+ 光学点缀 \\+ 环境运动 \\+ 密度控制 \\+ 题材适配|清晨薄雾.*雨后水汽.*黄昏薄雾.*灶房水汽.*火盆烟气.*窗边落尘微光|氛围元素.*来源.*密度.*方向" "video prompt skill enforces atmosphere environment elements"
require_pattern "02_共享资产库/00_核心规则手册.md" "氛围环境体系 = 天气 / 时间基底 \\+ 空气媒介 \\+ 漂浮微粒 \\+ 光学点缀 \\+ 环境运动 \\+ 密度控制 \\+ 题材适配|清晨薄雾.*雨后水汽.*黄昏薄雾.*灶房水汽.*火盆烟气.*窗边落尘微光|氛围元素.*来源和方向" "core manual enforces atmosphere environment elements"
require_pattern "02_共享资产库/01_模板库/视频模板/模板_视频提示词_基础设定氛围画面内容.md" "壁纸帧必须有氛围环境元素体系|天气 / 时间基底 \\+ 空气媒介 \\+ 漂浮微粒 \\+ 光学点缀 \\+ 环境运动 \\+ 密度控制 \\+ 题材适配|画面有雾和光斑，很有氛围" "video prompt template enforces atmosphere environment elements"
require_pattern "02_共享资产库/01_模板库/视频模板/模板_视频生成质量检查清单.md" "氛围环境元素|天气 / 时间基底.*空气媒介.*漂浮微粒.*光学点缀.*环境运动.*密度控制.*题材适配|无来源花瓣.*过浓雾.*舞台特效感" "video QA checklist checks atmosphere environment elements"
require_pattern "skills/laohu_generation_review/SKILL.md" "氛围环境元素|画面死板 / 没氛围 / 氛围元素乱 / 雾太假|天气 / 时间基底、空气媒介、漂浮微粒、光学点缀、环境运动、密度控制和题材适配" "generation review diagnoses atmosphere environment elements"
require_pattern "02_共享资产库/02_视觉语言资产/画面风格库/画面氛围与画质规范.md" "氛围环境体系 = 天气 / 时间基底 \\+ 空气媒介 \\+ 漂浮微粒 \\+ 光学点缀 \\+ 环境运动 \\+ 密度控制 \\+ 题材适配|清晨薄雾.*雨后水汽.*黄昏薄雾.*灶房水汽.*火盆烟气|氛围元素要有来源、位置、方向和密度" "visual style guide defines atmosphere environment elements"
require_pattern "02_共享资产库/05_工具流程/助手执行失败经验与防复发规则.md" "氛围环境元素不能空白，也不能无来源乱加|氛围环境体系 = 天气 / 时间基底 \\+ 空气媒介 \\+ 漂浮微粒 \\+ 光学点缀 \\+ 环境运动 \\+ 密度控制 \\+ 题材适配|画面死板 / 没氛围 / 氛围元素乱 / 雾太假" "failure rules record missing atmosphere environment elements"
require_pattern "skills/laohu_video_prompt/SKILL.md" "运动稳定体系 = 机位稳定策略 \\+ 运镜速度 \\+ 抖动强度 \\+ 变焦 / 旋转控制 \\+ 构图保持 \\+ 可定格停留 \\+ 运动模糊边界|固定机位长镜头.*极缓慢微动.*轻微呼吸手持|关键动作后停住 1-2 秒" "video prompt skill enforces camera motion constraints for wallpaper frames"
require_pattern "02_共享资产库/00_核心规则手册.md" "运动稳定体系 = 机位稳定策略 \\+ 运镜速度 \\+ 抖动强度 \\+ 变焦 / 旋转控制 \\+ 构图保持 \\+ 可定格停留 \\+ 运动模糊边界|固定机位长镜头.*极缓慢微动运镜.*轻微呼吸手持|抽帧全糊.*主体漂移" "core manual enforces camera motion constraints for wallpaper frames"
require_pattern "02_共享资产库/01_模板库/视频模板/模板_视频提示词_基础设定氛围画面内容.md" "壁纸帧必须有镜头运动约束|机位稳定策略 \\+ 运镜速度 \\+ 抖动强度 \\+ 变焦 / 旋转控制 \\+ 构图保持 \\+ 可定格停留 \\+ 运动模糊边界|镜头快速推进旋转，很有动感" "video prompt template enforces camera motion constraints"
require_pattern "02_共享资产库/01_模板库/视频模板/模板_视频生成质量检查清单.md" "镜头运动约束|机位稳定策略.*运镜速度.*抖动强度.*变焦 / 旋转控制.*构图保持.*可定格停留.*运动模糊边界|全程快速推拉.*连续旋转.*快速变焦" "video QA checklist checks camera motion constraints"
require_pattern "skills/laohu_generation_review/SKILL.md" "镜头运动约束|没有一帧能当壁纸 / 抽帧全糊 / 镜头一直晃 / 主体一直漂 / 运镜破坏美感|机位稳定策略、运镜速度、抖动强度、变焦 / 旋转控制、构图保持、可定格停留和运动模糊边界" "generation review diagnoses camera motion constraints"
require_pattern "02_共享资产库/02_视觉语言资产/画面风格库/画面氛围与画质规范.md" "运动稳定体系 = 机位稳定策略 \\+ 运镜速度 \\+ 抖动强度 \\+ 变焦 / 旋转控制 \\+ 构图保持 \\+ 可定格停留 \\+ 运动模糊边界|固定机位长镜头.*极缓慢微动运镜.*轻微呼吸手持|每个动态镜头都要有可定格停留" "visual style guide defines camera motion constraints"
require_pattern "02_共享资产库/05_工具流程/助手执行失败经验与防复发规则.md" "镜头运动不能破坏静态美感|运动稳定体系 = 机位稳定策略 \\+ 运镜速度 \\+ 抖动强度 \\+ 变焦 / 旋转控制 \\+ 构图保持 \\+ 可定格停留 \\+ 运动模糊边界|没有一帧能当壁纸 / 抽帧全糊 / 镜头一直晃 / 主体一直漂 / 运镜破坏美感" "failure rules record missing camera motion constraints"
require_pattern "02_共享资产库/00_核心规则手册.md" "2000 字以内|分镜编号.*所属场次.*镜头任务|基础设定.*全片统一层|画面内容不默认逐秒拆死" "core manual enforces concise model-facing video prompts"
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
require_pattern "AGENTS.md" "口述故事逐项追问|一次只追问一个最关键问题|有冲突、有转折、有高潮" "top-level rules enforce oral story clarification"
require_pattern "02_共享资产库/00_核心规则手册.md" "口述故事阶段只允许一次追问一个最关键问题|重大疑问未解决前，不得进入正式剧本" "core manual enforces oral story clarification"
require_pattern "skills/laohu_script_writer/SKILL.md" "口述故事逐项追问|一次只追问一个最关键问题|故事完整、冲突清楚、转折成立、高潮明确" "script writer enforces oral story clarification"
require_pattern "02_共享资产库/05_工具流程/助手执行失败经验与防复发规则.md" "口述故事不能直接跳到剧本|逐项追问补完|重大疑问未解决前，不得进入正式剧本" "failure rules record oral story clarification"
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
require_pattern "02_共享资产库/02_视觉语言资产/镜头语言库/镜头语言词典.md" "镜头语言四件套|景别.*机位.*运镜.*光学质感|景别选择|机位角度选择|运镜运动选择|光学质感选择" "shot language dictionary defines four-part shot language system"
require_pattern "skills/laohu_video_prompt/SKILL.md" "镜头语言四件套|景别、机位、运镜、光学质感|景别选择.*镜头任务倒推|运镜必须写路径、方向、速度和停点|光学质感必须和故事介质统一" "video prompt skill enforces four-part shot language system"
require_pattern "02_共享资产库/00_核心规则手册.md" "镜头语言四件套判断|景别：画面需要容纳多少信息|机位：观众站在什么高度|运镜：镜头是否移动|光学质感：景深" "core manual enforces four-part shot language system"
require_pattern "02_共享资产库/01_模板库/视频模板/模板_视频提示词_基础设定氛围画面内容.md" "镜头语言四件套判断|景别、机位、运镜、光学质感|运镜必须写路径、方向、速度和停点|光学质感必须和故事介质统一" "video prompt template enforces four-part shot language system"
require_pattern "02_共享资产库/05_工具流程/助手执行失败经验与防复发规则.md" "镜头语言不能只堆术语|景别、机位、运镜、光学质感四件套|如果提示词只写.*氛围感环绕.*浅景深.*大全景.*低角度" "failure rules record four-part shot language system"
require_pattern "输入输出索引.md" "镜头语言四件套判断|景别、机位、运镜、光学质感|老式 DV 质感.*暖黄配色.*轻微频闪噪点.*自然光" "index records four-part shot language system"
require_pattern "02_共享资产库/02_视觉语言资产/镜头语言库/镜头语言词典.md" "视频提示词分层公式|镜头语言层 → 主体叙事层 → 环境布景层 → 光影色彩层 → 镜头光学质感 → 画幅帧率画质|四套梯度公式|高级氛围感极简公式" "shot language dictionary records universal video layered formula and gradient formulas"
require_pattern "skills/laohu_video_prompt/SKILL.md" "通用 AI 视频公式.*内部分层写作顺序|镜头语言层 → 主体叙事层 → 环境布景层 → 光影色彩层 → 镜头光学质感 → 画幅帧率画质|四套梯度公式|高级氛围感极简公式" "video prompt skill enforces universal video layered formula and gradient formulas"
require_pattern "02_共享资产库/00_核心规则手册.md" "通用 AI 视频公式.*内部分层写作顺序|镜头语言层 → 主体叙事层 → 环境布景层 → 光影色彩层 → 镜头光学质感 → 画幅帧率画质|四套梯度公式|高级氛围感极简公式" "core manual enforces universal video layered formula and gradient formulas"
require_pattern "02_共享资产库/01_模板库/视频模板/模板_视频提示词_基础设定氛围画面内容.md" "通用 AI 视频公式.*内部分层写作顺序|镜头语言层 → 主体叙事层 → 环境布景层 → 光影色彩层 → 镜头光学质感 → 画幅帧率画质|四套梯度公式|高级氛围感极简公式" "video prompt template enforces universal video layered formula and gradient formulas"
require_pattern "02_共享资产库/05_工具流程/助手执行失败经验与防复发规则.md" "通用视频公式要变成分层写作顺序|镜头语言层 → 主体叙事层 → 环境布景层 → 光影色彩层 → 镜头光学质感 → 画幅帧率画质|四套梯度公式|高级氛围感极简公式" "failure rules record universal video layered formula and gradient formulas"
require_pattern "输入输出索引.md" "通用 AI 视频公式.*内部分层写作顺序|镜头语言层.*主体叙事层.*环境布景层.*光影色彩层.*镜头光学质感.*画幅帧率画质|四套梯度公式|高级氛围感极简公式" "index records universal video layered formula and gradient formulas"
require_pattern "02_共享资产库/02_视觉语言资产/镜头语言库/镜头语言词典.md" "专业运镜术语扩展|Dolly / Track.*机身整体移动|Pan / Tilt.*原地转动|希区柯克.*机身向前推进.*光学变焦拉远.*主体大小基本保持不变.*背景空间拉伸畸变" "shot language dictionary records professional camera movement mechanics"
require_pattern "skills/laohu_video_prompt/SKILL.md" "专业运镜术语必须先区分物理机制|Dolly / Track.*机身整体移动|Pan / Tilt.*原地转动|希区柯克变焦.*机身向前推进.*光学变焦拉远" "video prompt skill enforces professional camera movement mechanics"
require_pattern "02_共享资产库/00_核心规则手册.md" "专业运镜术语必须先区分物理机制|Dolly / Track.*机身整体移动|Pan / Tilt.*原地转动|希区柯克变焦.*机身向前推进.*光学变焦拉远" "core manual enforces professional camera movement mechanics"
require_pattern "02_共享资产库/01_模板库/视频模板/模板_视频提示词_基础设定氛围画面内容.md" "专业运镜术语必须先区分物理机制|Dolly / Track.*机身整体移动|Pan / Tilt.*原地转动|希区柯克变焦.*机身向前推进.*光学变焦拉远" "video prompt template enforces professional camera movement mechanics"
require_pattern "02_共享资产库/05_工具流程/助手执行失败经验与防复发规则.md" "专业运镜术语必须先区分物理机制|Dolly / Track / Tracking Dolly 是机身整体移动|希区柯克变焦 / Vertigo Shot 必须同时写.*机身向前推进.*光学变焦拉远" "failure rules record professional camera movement mechanics"
require_pattern "输入输出索引.md" "专业运镜术语.*Dolly / Track.*机身整体移动|Pan / Tilt.*原地转动|希区柯克变焦必须同时写机身向前推进.*光学变焦拉远.*主体大小基本保持不变.*背景空间拉伸畸变" "index records professional camera movement mechanics"
require_pattern "02_共享资产库/00_核心规则手册.md" "低保真故事板不是资产|2.5D 线框|时间点 / 微分镜编号|2.5D 线框构图图|引导线 / 动线路径|参考强度" "core manual defines low-fidelity storyboard workflow and table columns"
require_pattern "skills/laohu_visual_assets/SKILL.md" "低保真故事板不属于图片资产|不调用具体资产图|火柴人或简化剪影|几何块|04_分镜/文本" "visual assets skill separates low-fidelity storyboard from image assets"
require_pattern "skills/laohu_video_prompt/SKILL.md" "故事板提示词和视频提示词是同源并行关系|同一组微分镜|【故事板图片提示词】|【视频生成提示词】|锚点重叠" "video prompt skill outputs separate storyboard and video prompts with shared micro-shots"
require_pattern "02_共享资产库/01_模板库/视频模板/模板_视频提示词_基础设定氛围画面内容.md" "配套低保真故事板提示词模板|生成一张用于 AI 视频生成参考的低保真 2.5D 线框分镜故事板表格图|强锁构图.*弱锁人物外观|同一组微分镜编号" "video prompt template enforces separate low-fidelity storyboard prompt"
require_pattern "02_共享资产库/01_模板库/视频模板/模板_视频生成质量检查清单.md" "低保真故事板|故事板提示词单独存在.*04_分镜/文本|视频提示词单独存在.*05_视频/文本|2.5D 线框表格图|参考强度" "video QA checklist checks storyboard separation, lineframe style and reference strength"
require_pattern "02_共享资产库/05_工具流程/laohu_skills核心合约.md" "低保真故事板交接包|VID 编号|使用微分镜|强锁内容.*构图 / 景别 / 机位|弱锁内容.*人物外观|对应视频提示词文件" "core skill contract defines low-fidelity storyboard handoff"
require_pattern "02_共享资产库/05_工具流程/剧本到AI视觉资产转换规则.md" "低保真故事板也不进入资产表|04_分镜/文本|2.5D 线框故事板表格图|同源同编号|时间点 / 微分镜编号" "asset conversion rules define storyboard as non-asset parallel output"
require_pattern "02_共享资产库/05_工具流程/助手执行失败经验与防复发规则.md" "低保真故事板必须承接文字提示词最弱的空间关系|不是图片资产|同一组微分镜编号|强锁构图.*弱锁人物外观|动态强、打斗强" "failure rules record low-fidelity storyboard workflow"
require_pattern "02_共享资产库/02_视觉语言资产/镜头语言库/镜头语言词典.md" "POV 专项公式|具体人物第一人称 POV|前景身体或道具锚点|手持质感|35mm 或 50mm 人眼等效" "shot language dictionary defines dedicated POV formula"
require_pattern "skills/laohu_video_prompt/SKILL.md" "严格 POV 使用专项公式|具体人物第一人称 POV|前景身体或道具锚点|POV 手持质感|35mm 或 50mm 人眼等效" "video prompt skill enforces dedicated POV formula"
require_pattern "02_共享资产库/00_核心规则手册.md" "严格 POV 必须套用专项公式|具体人物第一人称 POV|POV 前景锚点|POV 手持质感|35mm 或 50mm 人眼等效" "core manual enforces dedicated POV formula"
require_pattern "02_共享资产库/01_模板库/视频模板/模板_视频提示词_基础设定氛围画面内容.md" "严格 POV 必须套用专项公式|具体人物第一人称 POV|POV 前景锚点|POV 手持质感|35mm 或 50mm 人眼等效" "video prompt template enforces dedicated POV formula"
require_pattern "02_共享资产库/05_工具流程/助手执行失败经验与防复发规则.md" "POV 不是标签|前景锚点、身体感、视线运动和人眼光学|具体人物第一人称 POV|小安床上 POV" "failure rules record dedicated POV formula"
require_pattern "输入输出索引.md" "严格 POV 不能只写标签|具体人物第一人称 POV|前景身体或道具锚点|人眼等效焦段和景深" "index records dedicated POV formula"
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
require_pattern "02_共享资产库/01_模板库/视频模板/模板_视频提示词_基础设定氛围画面内容.md" "风格核心|视觉基调|色彩与影调|Photirealism|IMAX|Panavision|禁止" "video prompt template uses benchmark vibe fields"
require_pattern "02_共享资产库/01_模板库/视频模板/模板_视频提示词_基础设定氛围画面内容.md" "资产名.*【@资产名】|世界观：|声音设定：" "video prompt template uses benchmark asset lines"
require_pattern "02_共享资产库/01_模板库/视频模板/模板_视频提示词_基础设定氛围画面内容.md" "4-15 秒|情绪|动作因果|奇观|展示时间" "video prompt template enforces 4-15 second duration strategy"
require_pattern "02_共享资产库/01_模板库/视频模板/模板_视频提示词_基础设定氛围画面内容.md" "时长预演|动作单元|估算|装不下|加时长|删内容|拆镜头" "video prompt template enforces duration previsualization"
require_pattern "02_共享资产库/01_模板库/视频模板/模板_视频提示词_基础设定氛围画面内容.md" "【@资产名】|资产占位|固定实体|动作链|冲击结果" "video prompt template includes asset placeholders and action-density rules"
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
require_pattern "02_共享资产库/00_核心规则手册.md" "高光体态|胸腔舒展.*肩背打开.*站姿自信|左手.*右手.*拇指" "core manual enforces highlight posture and correct left-right hands"
require_pattern "02_共享资产库/01_模板库/图片模板/模板_AI图片提示词_资产型通用结构.md" "高光体态|胸腔舒展.*肩背打开.*站姿自信|左手.*右手.*拇指" "image asset prompt template enforces highlight posture and correct left-right hands"
require_pattern "02_共享资产库/05_工具流程/助手执行失败经验与防复发规则.md" "人物设计资产必须锁高光体态和左右手解剖方向|左手拇指.*画面右侧.*右手拇指.*画面左侧|同一只手" "failure rules record highlight posture and correct left-right hands"
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
require_pattern "AGENTS.md" "色卡 / 色彩风格资产|导演级调色资产|正式视频提示词里不能只写.*调用色卡" "top-level rules define color palette style assets"
require_pattern "02_共享资产库/00_核心规则手册.md" "色彩风格资产.*主色.*辅助色.*点缀色|母色卡不变，阶段变体受控变化|色彩与影调" "core manual defines color palette style assets"
require_pattern "skills/laohu_visual_assets/SKILL.md" "色卡可以升级为色彩风格资产|C1 全片母色卡|C1-A 心动期色卡变体" "visual assets skill supports color palette assets"
require_pattern "skills/laohu_video_prompt/SKILL.md" "色彩风格资产：【@C1 色卡名】|不能只写.*调用色卡|母色卡不变，阶段变体受控变化" "video prompt skill expands color palette assets"
require_pattern "02_共享资产库/01_模板库/图片模板/模板_AI图片提示词_资产型通用结构.md" "色彩风格资产 / 色卡资产|十六进制 RGB|阶段变体" "image prompt template supports color palette assets"
require_pattern "02_共享资产库/01_模板库/视频模板/模板_视频提示词_基础设定氛围画面内容.md" "色彩风格资产：【@C1 色卡名】|母色卡不变，阶段变体受控变化|文字规则是执行" "video prompt template supports color palette assets"
require_pattern "02_共享资产库/02_视觉语言资产/画面风格库/画面氛围与画质规范.md" "色卡是色彩体系的资产化版本|母色卡 \\+ 阶段变体|同一片美景变得不美了" "style guide defines color palette assets"
require_pattern "02_共享资产库/05_工具流程/剧本到AI视觉资产转换规则.md" "色彩风格资产.*色卡图片 \\+ 文本规则|C.*系列色彩风格资产|人物设计资产里的紧凑色值卡" "asset conversion supports color palette assets"
require_pattern "02_共享资产库/05_工具流程/助手执行失败经验与防复发规则.md" "色卡要升级为色彩风格资产|母色卡不变，阶段变体受控变化|不能只当几个色号" "failure rules record color palette asset lesson"
require_pattern "输入输出索引.md" "AI 视频色卡|C.*系列色彩风格资产|母色卡不变，阶段变体受控变化" "index records color palette asset lesson"

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
