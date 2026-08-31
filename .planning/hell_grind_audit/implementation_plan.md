# Higgsfield 三项方法本地化 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在不新增平行 Skill、不接入外部生成 API 的前提下，把 LIRA、ACTING、CINEDANCE 中经审计成立的机制编译进现有“老胡 AI 视觉”生产链，并建立动态模型能力合同、连续性把手、条件化摄影控制和真实生成回流。

**Architecture:** 现有十四个 Skill 的职责不变。LIRA 进入视觉资产的图片任务路由和单变量编辑；ACTING 由编剧、人物设计、视频和复盘分权承担；CINEDANCE 进入视频主 Skill、镜头叙事 Reference 和 Seedance 适配。四层能力只用于内部设计，业务文件使用“接续合同、运行时切片、任务路由、行为签名、入口能力合同”等领域语言，不暴露机械的四层标题。

**Tech Stack:** Markdown Skill / Reference、JSON 能力场景、Bash + Perl 校验脚本、Python 3 架构验证器、`rg`、Git。

---

## 文件结构与唯一职责

### 主要修改

- `tests/capability_scenarios.json`：先定义新能力必须可达的行为场景，移除旧固定字符数字作为能力锚点。
- `skills/laohu-video-prompt/SKILL.md`：连续性把手、当前镜头封闭编译、动态入口预算、相对时长和最终视频交付的唯一负责人。
- `skills/laohu-video-prompt/references/10_画面内容镜头叙事语法.md`：跨题材镜头连接、长镜头、焦段/FOV和成像召回锚点的通用机制。
- `skills/laohu-video-prompt/references/08_提示词压缩质检与失败修复.md`：只按真实入口能力合同压缩，保护承重控制。
- `skills/laohu-video-prompt/references/01_文戏对白与人物表演.md`：把角色稳定行为编译成当前场景表演。
- `02_共享资产库/03_模型适配/Seedance2/Seedance2视频提示词书写规范.md`：Seedance 当前入口的条件化适配，不再争夺通用规则权威。
- `02_共享资产库/03_模型适配/通用规范/多模型AI视频提示词通用规范.md`：目标入口能力合同的统一记录格式。
- `02_共享资产库/05_工具流程/laohu_skills核心合约.md`：剧本、人物、场景、资产、视频、复盘之间的新交接字段。
- `skills/laohu-visual-assets/SKILL.md` 与 `references/04_风格决策与图片提示词.md`：LIRA 图片任务路由、局部单变量编辑和参数/参考/正文分权。
- `skills/laohu-script-writer/SKILL.md`、`skills/laohu-character-design/SKILL.md`：ACTING 的写作声音、可听声纹、条件化行为签名分权。
- `skills/laohu-set-design/SKILL.md`：场景母版向视频输出 GEO 运行时切片所需事实。
- `skills/laohu-generation-review/SKILL.md` 与 `references/01_图片与视频生成诊断.md`：连续性把手质量门、单变量实验账和停止改词条件。

### 脚本与测试

- `skills/laohu-video-prompt/scripts/validate_video_prompt_structure.sh`：结构校验与入口长度校验解耦；未提供上限时不伪造默认值。
- `skills/laohu-video-prompt/scripts/test_validate_video_prompt_structure.sh`：验证局部相对时长通过、完整绝对时间轴失败、无入口上限时只做结构检查。
- `skills/laohu-video-prompt/scripts/test_count_video_prompt_chars.sh`：保留显式 `--limit` 行为，补无上限信息模式回归。
- `scripts/validate_capability_architecture.py`：不改算法，只消费新增后的能力场景。
- `04_诊断与系统日志/能力进化台账.md`：记录本次外部方法研究、旧行为、新行为和重新唤醒条件。

### 不创建

- 不创建 `laohu-acting`、`laohu-cinedance` 或 `laohu-lira` 平行 Skill。
- 不创建第二套视频提示词模板。
- 不把本次研究正文复制进业务 Reference。
- 不修改 `AGENTS.md`；顶层边界已经足够，专业细节归现有负责人。

---

### Task 1: 用失败场景锁定新能力边界

**Files:**
- Modify: `tests/capability_scenarios.json`
- Test: `scripts/validate_capability_architecture.py`

- [ ] **Step 1: 运行当前基线**

Run:

```bash
python3 scripts/validate_capability_architecture.py
```

Expected: 当前工作树基线 `exit 0`。若存在用户已有失败，记录具体失败但不顺手修复范围外内容。

- [ ] **Step 2: 把视频 Skill 的旧数字锚点替换为能力锚点**

在 `skill_contracts.laohu-video-prompt.anchors` 中删除：

```json
"Seedance 2.5",
"10000"
```

加入：

```json
"目标入口能力合同",
"当前镜头封闭编译",
"连续性把手",
"接续类型",
"GEO 运行时切片",
"激活参考职责",
"首帧阻挡",
"局部相对时长",
"入口长度兼容性未验证"
```

- [ ] **Step 3: 增加四个运行时可达场景**

向 `runtime_reachability_scenarios` 加入以下完整对象：

```json
{
  "name": "同场景复杂站位使用空间连续性把手",
  "owner": "laohu-video-prompt",
  "request": "VID-A和VID-B直接连续，场景内有三个人、固定入口、桌子和受损窗户；希望B继承A真实站位而不是重新排列。",
  "required_references": [
    "skills/laohu-video-prompt/references/10_画面内容镜头叙事语法.md"
  ],
  "required_intermediate": [
    "接续类型",
    "连续性把手",
    "GEO 运行时切片",
    "A 真实结束状态",
    "B 第一项新变化"
  ],
  "observable_change": "先验收A最后一个有效机位；空间风险高时优先保留能读清人物、入口、桌子和破窗关系的约1—3秒尾部视频，或按入口能力退化为终帧加稳定资产。B只继承已声明的站位、观看侧、破坏状态和运动余势，从下一相位开始；剪辑可裁掉把手。",
  "forbidden_shortcut": "所有镜头机械拉成大全景；把计划尾帧当真实结果；引用包含两个硬切机位的尾部；让B复演A已完成动作。"
},
{
  "name": "承重文戏选择表演把手而不强拉广角",
  "owner": "laohu-video-prompt",
  "request": "一段母女近景对白拆成两个VID，A结束在母亲压住哭腔的停顿，B从孩子的迟疑反应继续。",
  "required_references": [
    "skills/laohu-video-prompt/references/01_文戏对白与人物表演.md",
    "skills/laohu-video-prompt/references/10_画面内容镜头叙事语法.md"
  ],
  "required_intermediate": [
    "表演连续",
    "连续性把手",
    "条件化行为签名",
    "下一相位"
  ],
  "observable_change": "保留母亲呼吸、眼线、肩颈、手中物、与孩子的屏幕方向和声音余韵作为表演把手；B从孩子听见重词后的迟疑开始，不为了空间完整强迫A后拉到大全景。",
  "forbidden_shortcut": "把所有接续统一成广角；用悲伤、克制等抽象词替代身体与发声证据；B重复母亲整句台词。"
},
{
  "name": "MV或广告按作品目标选择艺术转场",
  "owner": "laohu-video-prompt",
  "request": "两个空间不连续的MV段落需要通过相似动作和光线完成转场，不要求物理空间连续。",
  "required_references": [
    "skills/laohu-video-prompt/references/04_MV概念PV与动态图形蒙太奇.md",
    "skills/laohu-video-prompt/references/10_画面内容镜头叙事语法.md"
  ],
  "required_intermediate": [
    "艺术转场",
    "共同载体",
    "预计裁剪区",
    "B 第一项新变化"
  ],
  "observable_change": "接续合同明确动作相位、轮廓、光线或声音中的共同载体；A种下线索，B从同一线索下一相位接收并新增意义，不引用错误的上一场景空间状态。",
  "forbidden_shortcut": "为了连续而继承不该继承的地点；只写炫酷转场、无缝衔接；把所有转场改成遮挡。"
},
{
  "name": "未知入口长度不触发伪造字符硬门",
  "owner": "laohu-video-prompt",
  "request": "复杂多人视频提示词已经闭合空间、表演、物理和声音，但目标平台入口尚未确认字符限制。",
  "required_references": [
    "skills/laohu-video-prompt/references/08_提示词压缩质检与失败修复.md"
  ],
  "required_intermediate": [
    "目标入口能力合同",
    "高密度导演母稿",
    "入口长度兼容性未验证",
    "最低充分控制密度"
  ],
  "observable_change": "保留结构完整的导演母稿，长度状态标记为未验证；只有官方限制、真实入口报错或可复现实测才能形成硬上限，不回退到跨模型4000或默认10000字符。",
  "forbidden_shortcut": "把未知模型按4000字符裁切；把HELL GRIND样本长度改成新目标；因没有硬上限而保留重复解释和装饰词。"
}
```

- [ ] **Step 4: 更新已有相对时长场景**

在名为`正式视频提示词保留逐镜方头并只用相对时长`的场景中，把：

```json
["镜头编号只标顺序", "相对时长约束", "绝对起止区间", "Seedance 2.5", "10000"]
```

替换为：

```json
["镜头编号只标顺序", "局部相对时长", "绝对起止区间", "目标入口能力合同", "入口长度兼容性未验证"]
```

- [ ] **Step 5: 运行架构验证并确认测试先失败**

Run:

```bash
python3 scripts/validate_capability_architecture.py
```

Expected: `exit 1`，失败只指向尚未进入业务文件的新锚点或新运行时中间结果，例如`连续性把手`、`GEO 运行时切片`和`入口长度兼容性未验证`。

- [ ] **Step 6: 提交测试合同**

```bash
git add tests/capability_scenarios.json
git commit -m "test: define cinematic continuity capability contracts"
```

---

### Task 2: 让长度校验读取真实入口能力合同

**Files:**
- Modify: `02_共享资产库/03_模型适配/通用规范/多模型AI视频提示词通用规范.md:106`
- Modify: `skills/laohu-video-prompt/scripts/validate_video_prompt_structure.sh`
- Modify: `skills/laohu-video-prompt/scripts/test_validate_video_prompt_structure.sh`
- Modify: `skills/laohu-video-prompt/scripts/test_count_video_prompt_chars.sh`
- Test: `skills/laohu-video-prompt/scripts/test_validate_video_prompt_structure.sh`
- Test: `skills/laohu-video-prompt/scripts/test_count_video_prompt_chars.sh`

- [ ] **Step 1: 先为结构校验器补失败测试**

在 `test_validate_video_prompt_structure.sh` 中新增局部时长有效样本：

```bash
fixture_relative_time="$(mktemp)"
```

把它加入 `trap`，并写入：

```bash
write_prompt "$fixture_relative_time" \
  '【镜头01｜中远景｜平视侧面｜缓慢后撤后固定】' \
  '中远景先看见两人分立桌子两侧，后门与破窗同时可见；听见门外脚步后约0.4秒，两人先后转向门口，镜头在两人、桌子和入口关系稳定可读后停住，结尾约1—2秒保持这一站位。'
```

增加显式断言：

```bash
no_limit_output="$($VALIDATOR "$fixture_valid")"
printf '%s\n' "$no_limit_output" | rg -q 'limit=none'
"$VALIDATOR" "$fixture_relative_time" >/dev/null
```

保留 `fixture_timeline` 失败，证明完整绝对起止区间仍被拦截。

- [ ] **Step 2: 运行测试确认默认10000行为仍存在**

Run:

```bash
bash skills/laohu-video-prompt/scripts/test_validate_video_prompt_structure.sh
```

Expected: 新增用例可能通过，但直接运行校验器输出仍显示`limit=10000`，证明默认值尚未移除。

- [ ] **Step 3: 移除结构校验器的伪造默认上限**

在 `validate_video_prompt_structure.sh` 把：

```bash
limit="10000"
```

改为：

```bash
limit=""
```

Perl 校验段把字符判断改为：

```perl
my $shown_limit = defined $limit && length $limit ? $limit : 'none';
push @errors, "chars=$chars exceeds limit=$limit"
  if defined $limit && length $limit && $chars > $limit;
```

输出改为：

```perl
printf "block=%d chars=%d limit=%s shots=%d status=%s",
  $index + 1, $chars, $shown_limit, scalar @shots, $status;
```

结构错误仍然失败；未提供 `--limit` 时只把长度标记为`limit=none`，不把它算作通过某个入口限制。

- [ ] **Step 4: 补字符计数器的信息模式回归**

在 `test_count_video_prompt_chars.sh` 增加：

```bash
info_output="$($COUNTER "$fixture" --block 1)"
printf '%s\n' "$info_output" | rg -q '^block=1 chars=33 limit=none status=INFO$'
```

显式`--limit 33`继续PASS，`--limit 32`继续FAIL。

- [ ] **Step 5: 扩展目标入口能力合同格式**

把通用模型适配记录替换为以下字段，不保留一个模糊的`模型限制`空格：

```text
平台 / 具体入口：
模型 / 版本日期：
任务模式：T2V / I2V / 首尾帧 / 多参考 / 音频 / 视频参考
目标时长 / 画幅 / 分辨率：
可绑定输入及各自职责：
由 UI 或 API 结构化承担的参数：
提示词语言与计数方法：
官方公开硬限制及来源：有 / 无 / 未找到
本地实测最大可提交长度：
超过后的行为：拒绝 / 截断 / 可提交但遵循衰减 / 未验证
后半段遵循与长程漂移：
原提示词 / 改写提示词：
样本量、测试日期与证据位置：
生成结果与逐项遵循：
模型优势 / 限制 / 副作用：
下次写法调整：
是否更新模板：
```

- [ ] **Step 6: 运行脚本测试**

Run:

```bash
bash skills/laohu-video-prompt/scripts/test_validate_video_prompt_structure.sh
bash skills/laohu-video-prompt/scripts/test_count_video_prompt_chars.sh
```

Expected:

```text
validate_video_prompt_structure tests passed
count_video_prompt_chars tests passed
```

- [ ] **Step 7: 提交入口合同和脚本**

```bash
git add '02_共享资产库/03_模型适配/通用规范/多模型AI视频提示词通用规范.md' \
  skills/laohu-video-prompt/scripts/validate_video_prompt_structure.sh \
  skills/laohu-video-prompt/scripts/test_validate_video_prompt_structure.sh \
  skills/laohu-video-prompt/scripts/test_count_video_prompt_chars.sh
git commit -m "fix: decouple prompt structure from unverified length caps"
```

---

### Task 3: 把 CINEDANCE 机制编译进视频主负责人

**Files:**
- Modify: `skills/laohu-video-prompt/SKILL.md:174-345`
- Modify: `skills/laohu-video-prompt/SKILL.md:429-508`
- Modify: `skills/laohu-video-prompt/references/10_画面内容镜头叙事语法.md`
- Modify: `skills/laohu-video-prompt/references/08_提示词压缩质检与失败修复.md:67-92`
- Test: `tests/capability_scenarios.json`

- [ ] **Step 1: 在视频主 Skill 增加当前镜头封闭编译**

在`先定生成单元，再在单元内分镜`之后加入领域化规则：

```text
当前镜头封闭编译：每条VID只保留当前激活的人物、场景、道具、状态与参考。正式成稿前清除旧镜头标签、旧场景措辞、未出现人物、已完成动作和未上传资产；相同名称若版本或状态不同，必须重新绑定。封闭不是丢掉连续性，而是让连续性只通过相邻单元合同和实际参考进入，不能靠上一版正文残留碰运气。

激活参考职责：逐项登记当前真实输入、唯一职责和不得继承。身份参考不自动拥有构图权，场景参考不自动拥有临时破坏状态，尾部视频不自动拥有稳定身份权。

GEO 运行时切片：从场景母版切出当前VID需要的世界坐标、主锚点、摄影机侧与180度轴、人物/道具起点、允许路径、屏幕投影和参考构图非继承项。完整场景说明书不直接粘贴进正文。

首帧阻挡：复杂镜头在写时间变化前，先验收精确人数、世界位置、屏幕位置、朝向、遮挡、手中物、主锚点和摄影机观看侧；简单镜头可合并表达，但不能让模型猜起点。
```

- [ ] **Step 2: 把相邻单元改成六类接续合同**

扩展现有相邻单元表为：

```text
接续类型：空间连续 / 动作连续 / 表演连续 / 状态连续 / 艺术转场 / 场景重置
A 已完成结果：
A 真实结束状态：
连续性把手：尾部视频 / 终帧 / 稳定资产 / 双参考 / 无需继承
把手有效机位与建议长度：
必须继承 / 允许重建 / 不得继承：
B 第一项新变化：
下一相位：
共同载体 / 主匹配属性：
预计裁剪区：
```

增加裁决句：

```text
所有相邻VID都必须选择接续类型；同场景且空间风险高时优先空间连续性把手，但不强制所有结尾拉成大全景。文戏可以保留表演把手，动作戏保留运动余势，MV/广告/文艺片可按作品命题使用艺术转场，场景关系重置时不继承错误空间。1—3秒只是当前视频参考经验，最终长度来自入口能力合同和运动信息需要。
```

- [ ] **Step 3: 固化相对时长而非完整绝对时间轴**

把现有`时长反推与相对时长约束`中的核心术语统一为：

```text
总时长是入口参数；镜头编号只标顺序。模型正文不建立从0排到总时长的完整绝对时间轴，只在动作速度、触发后延迟、反应窗口、连续性把手或结果保持需要时写局部相对时长。
```

允许示例：

```text
听到重词后约0.4秒移开目光；两秒内完成转身；结尾约1—2秒稳定展示两人与入口的相对位置。
```

拒绝示例：

```text
0—2秒建立空间；2—5秒转身；5—8秒后退。
```

- [ ] **Step 4: 把固定硬规格改为入口兼容状态**

删除主 Skill 中：

```text
Seedance 2.0 单条不超过4000字符。
Seedance 2.5单条不超过10000字符。
模型未明确或跨模型共用按4000字符。
```

替换为：

```text
字符数只受当前目标入口能力合同约束。合同有官方硬限制或可复现实测时，运行字符脚本并把该值显式传给--limit；入口未知时保留高密度导演母稿，标记“入口长度兼容性未验证”，不得回退到模型名或跨模型默认数字。长度不是扩写目标；即使无硬上限，也必须删除作者解释、同义重复、无来源装饰和未激活常量。
```

命令示例改成：

```bash
bash skills/laohu-video-prompt/scripts/count_video_prompt_chars.sh "提示词文件.md"
bash skills/laohu-video-prompt/scripts/count_video_prompt_chars.sh "提示词文件.md" --limit "能力合同中的实测值"
```

- [ ] **Step 5: 在镜头叙事 Reference 增加四个领域分支**

不要写`灵魂/筋骨/血肉/表皮`标题。新增：

```markdown
## 跨VID连续性把手
```

内容必须覆盖六类接续、空间把手不是强制大全景、尾部质量门、B不复演A、裁剪区和退化顺序。

新增：

```markdown
## 连续长镜头与切镜路线
```

写清长镜头保护真实时间/空间/身法/压力，通过调度、前景、焦点和重新构图形成内部段落；任务过载、局部失败拖垮整条、需多视角证据或长程漂移时拆镜。

新增：

```markdown
## FOV、焦段与可见结果
```

写清焦段从观看距离、空间覆盖、透视、主体占比和背景压缩倒推；数字只作适配候选，正文仍要写可见结果。

新增：

```markdown
## 成像召回锚点
```

把8K、IMAX等定义为可能召回大画幅/材质/宽动态先验的入口词；只有成像合同需要时使用，展开可见后果，记录A/B与副作用，不能覆盖DV、手机、监控、低保真或胶片合同。

- [ ] **Step 6: 重写压缩 Reference 的长度与连续性段**

`references/08`删除4000/10000固定数字，写入：

```text
压缩前先读取目标入口能力合同。没有真实上限时只做信息密度审稿，不做限长裁切；有硬限制时先删作者解释、重复、未激活常量和参考已充分承担的静态信息，保护激活参考职责、GEO切片、首帧阻挡、人物触发、动作物理、局部相对时长、连续性把手和结束状态。仍装不下时降低镜头任务或拆VID，不删承重因果。
```

- [ ] **Step 7: 运行架构测试**

Run:

```bash
python3 scripts/validate_capability_architecture.py
```

Expected: Task 1中由视频主负责人承担的新场景通过；LIRA、ACTING和跨Skill接口仍可能因后续任务尚未完成而失败。

- [ ] **Step 8: 提交 CINEDANCE 编译能力**

```bash
git add skills/laohu-video-prompt/SKILL.md \
  skills/laohu-video-prompt/references/10_画面内容镜头叙事语法.md \
  skills/laohu-video-prompt/references/08_提示词压缩质检与失败修复.md
git commit -m "feat: compile cinematic continuity into video prompts"
```

---

### Task 4: 重构 Seedance 适配而不丢失有效经验

**Files:**
- Modify: `02_共享资产库/03_模型适配/Seedance2/Seedance2视频提示词书写规范.md`
- Test: `skills/laohu-video-prompt/scripts/test_validate_video_prompt_structure.sh`
- Test: `scripts/validate_capability_architecture.py`

- [ ] **Step 1: 清除旧适配与主 Skill 的台词冲突**

删除模板里的独立：

```text
【台词】角色名……
[台词：角色名……]
```

改为：

```text
冻结台词直接嵌入说话人物所在的镜头正文，与开口前动作、发声变化、听者反应和说完后的停点连续书写；环境音、动作音和音乐校准轨只能补来源与时点，不能替代正文事件。
```

- [ ] **Step 2: 移除未经证实的固定字符路由**

删除第8节的4000/10000/跨版本4000规则，替换为：

```text
正式提示词的长度兼容性读取当前Seedance平台与入口能力合同。没有官方限制、真实报错或可复现实测时标记“入口长度兼容性未验证”；先保留高密度母稿，再按已验证入口编译运行稿。简单镜头允许短，复杂镜头允许长；长度由控制覆盖自然产生，不以HELL GRIND样本或历史数字为目标。
```

- [ ] **Step 3: 扩展跨VID连续性参考**

在现有第129行分支上增加：

```text
空间连续性把手：同场景多人、复杂站位、固定入口/锚点或破坏状态需要继承时，A最后一个有效机位优先停在能同时读清高风险关系的广角或中远景；“能读清”优先于“越广越好”。文戏若情绪近景承重，使用表演把手；动作戏使用可读的动作相位与运动余势；场景重置不引用A空间状态。
```

保留现有`最后一个有效机位约1—3秒`、双参考、真实尾帧质量门和入口数量不写死规则。

- [ ] **Step 4: 为长镜头、FOV和8K/IMAX建立条件路由**

加入：

```text
连续长镜头不是默认质量等级。它在真实时间、空间探索、完整身法、压迫或情绪累积承重时优先；内部仍用调度、遮挡、焦点、距离和重新构图形成段落。任务过载、后半段遗忘、局部失败拖垮整条或需要多视角证据时拆镜。

FOV/焦段数值是Seedance入口候选，不替代可见结果。每次先写需要同时看见什么、人物占比、透视强弱、背景压缩、边缘变形和停点，再按当前入口验证过的焦段/FOV词补充。

8K、IMAX等词属于成像召回锚点。作品成像合同需要大画幅尺度、材质密度或商业电影先验时才启用，并展开亮部衰减、暗部色彩、肤色、远近层次和构图后果；与DV、监控、手机UGC、低保真或胶片介质冲突时停用。每次A/B记录真实增益和副作用。
```

- [ ] **Step 5: 保留相对时长项目默认**

第4节继续拒绝完整逐秒时间轴，并补充：

```text
允许局部相对时长控制动作完成速度、触发延迟、反应窗口、连续性把手和结果保持；它们不从0排到总时长。
```

- [ ] **Step 6: 运行冲突扫描与回归**

Run:

```bash
! rg -n 'Seedance 2\.0 单条不超过|单条不超过 `4000`|单条不超过 `10000`|\【台词\】|\[台词：' \
  '02_共享资产库/03_模型适配/Seedance2/Seedance2视频提示词书写规范.md'
bash skills/laohu-video-prompt/scripts/test_validate_video_prompt_structure.sh
python3 scripts/validate_capability_architecture.py
```

Expected: 冲突扫描无输出；脚本测试通过；架构测试不再要求旧数字。

- [ ] **Step 7: 提交 Seedance 适配**

```bash
git add '02_共享资产库/03_模型适配/Seedance2/Seedance2视频提示词书写规范.md'
git commit -m "refactor: make Seedance controls evidence based"
```

---

### Task 5: 把 LIRA 拆入现有视觉资产能力

**Files:**
- Modify: `skills/laohu-visual-assets/SKILL.md`
- Modify: `skills/laohu-visual-assets/references/04_风格决策与图片提示词.md`
- Modify: `tests/capability_scenarios.json`
- Test: `scripts/validate_capability_architecture.py`

- [ ] **Step 1: 先在视觉资产能力锚点加入任务分流**

向 `skill_contracts.laohu-visual-assets.anchors` 加入：

```json
"图片任务路由",
"身份创建 / 地点创建 / 道具创建 / 局部编辑 / 叙事首帧",
"单变量编辑合同",
"变化区 / 保护区",
"UI参数 / 参考绑定 / 模型正文"
```

- [ ] **Step 2: 在视觉资产主 Skill 增加图片任务路由**

在美术与提示词工作流入口加入：

```text
图片任务路由：身份创建、地点创建、道具创建、局部编辑、叙事首帧是五种不同任务。先确定当前唯一生成任务和下游用途，再选择资产规格、参考职责和提示词密度；不能让同一请求同时承担中性身份校准、电影叙事、服装拆解、场景拓扑和局部修复。

参数分权：UI或入口已经稳定承担的画幅、分辨率、参考权重和生成模式进入参数清单；实际上传对象进入参考绑定；模型正文只写当前可见结果和变化。三者冲突时不得交付。
```

- [ ] **Step 3: 在图片 Reference 增加单变量编辑合同**

加入：

```text
单变量编辑合同：每次局部编辑只指定一个主变化变量，登记变化区、保护区、允许联动和禁止漂移。变化区写最终可见绝对目标；保护区写身份、结构、比例、材质、光线、构图或文字中必须保持的部分。若一次请求必须同时改脸、服装、姿态、背景和光线，先拆成顺序明确的多个编辑任务，并在每轮使用上一轮真实结果复验。
```

同时明确LIRA的80—150英文词或1500—2000字符只作为图片软经验，不进入视频上限。

- [ ] **Step 4: 增加运行时可达场景**

向 `runtime_reachability_scenarios` 增加：

```json
{
  "name": "局部图片编辑只改变一个主变量",
  "owner": "laohu-visual-assets",
  "request": "人物身份、服装、姿态和背景已经确认，只需要把右袖口的金属扣改为磨旧木扣。",
  "required_references": [
    "skills/laohu-visual-assets/references/04_风格决策与图片提示词.md"
  ],
  "required_intermediate": [
    "图片任务路由",
    "单变量编辑合同",
    "变化区 / 保护区",
    "UI参数 / 参考绑定 / 模型正文"
  ],
  "observable_change": "任务被路由为局部编辑；变化区只描述右袖口扣件的材料、形状、磨损和连接结果，保护区锁人物身份、服装其余结构、姿态、背景、光线和构图；入口参数与正文分开。",
  "forbidden_shortcut": "重写整套人物资产；同时改妆容、服装、姿势和环境；把图片字符软目标变成视频上限。"
}
```

- [ ] **Step 5: 运行架构验证**

Run:

```bash
python3 scripts/validate_capability_architecture.py
```

Expected: LIRA相关锚点和局部编辑场景通过。

- [ ] **Step 6: 提交视觉资产路由**

```bash
git add skills/laohu-visual-assets/SKILL.md \
  skills/laohu-visual-assets/references/04_风格决策与图片提示词.md \
  tests/capability_scenarios.json
git commit -m "feat: route image asset and local edit tasks"
```

---

### Task 6: 把 ACTING 编译为四项现有职责

**Files:**
- Modify: `skills/laohu-script-writer/SKILL.md`
- Modify: `skills/laohu-character-design/SKILL.md`
- Modify: `skills/laohu-video-prompt/SKILL.md`
- Modify: `skills/laohu-video-prompt/references/01_文戏对白与人物表演.md`
- Modify: `02_共享资产库/05_工具流程/laohu_skills核心合约.md`
- Modify: `tests/capability_scenarios.json`
- Test: `scripts/validate_capability_architecture.py`

- [ ] **Step 1: 为人物和视频能力增加分权锚点**

向人物设计能力锚点加入：

```json
"可听声音身份",
"条件化行为签名",
"控制 / 被逼 / 撒谎 / 失去优势"
```

向视频能力锚点加入：

```json
"当前场景表演",
"策略变化",
"表演连续"
```

编剧继续保留既有`人物声音合同`，不复制声纹参数。

- [ ] **Step 2: 在编剧中明确写作声音边界**

在人物声音合同末尾加入：

```text
本合同负责人物怎样选择证据、解释处境、回避什么和为什么说这句话，属于写作声音；它不决定可听声纹参数，也不替视频阶段写当前呼吸、语速、口型和身体表演。
```

- [ ] **Step 3: 在人物设计中增加稳定声音与条件化行为**

人物设计交接包增加：

```text
【可听声音身份】稳定音色、音高范围、基础语速、口音/咬字、呼吸支持、共鸣位置和不可漂移辨识点；当前场景的情绪、音量、气口和节奏由表演改写。
【条件化行为签名】人物在控制局面、被逼迫、撒谎、失去优势、保护他人和独处时，重心、眼线、呼吸、步态、手部任务、空间距离和稳定动作语言怎样出现裂缝；只写跨场景可复用差异。
```

- [ ] **Step 4: 在文戏 Reference 增加场景级表演编译**

加入：

```text
当前场景表演只展开本镜被触发的行为，不粘贴整份人物母档。先读人物目标、障碍/风险、当前策略和潜台词，再写开口前判断、重词触发、2—4个承重身体/声音通道、听者反应、策略变化和结束状态。相邻VID按表演连续合同继承呼吸、眼线、姿态、关系距离和声音余韵；人物有意延迟、误解或冻结时，可以不在台词结束前反应，但必须是当前策略的可见结果。
```

- [ ] **Step 5: 让视频主 Skill 显式消费四项分权**

在视频主 Skill 的输入与人物表演段加入：

```text
人物表演输入必须先分权：写作声音由剧本提供，决定人物怎样选择、解释和回避事实；可听声音身份与条件化行为签名由人物设计提供，分别保护稳定发声辨识和不同压力下的跨场景行为差异；当前场景表演由本Skill负责，只展开本镜目标、触发、策略变化、身体/声音通道、听者反应和停点。四者不得互相替代，也不得把整份人物母档粘贴进正式正文。
```

相邻单元段显式使用：

```text
表演连续：继承A真实结束时的呼吸、眼线、姿态、关系距离、手中物和声音余韵；B从下一项策略或听者反应开始，不复演A台词与表演结果。
```

这一步必须让`写作声音`、`可听声音身份`、`条件化行为签名`、`当前场景表演`、`策略变化`和`表演连续`六个中间结果出现在视频主 Skill，而不是只存在于Reference。

- [ ] **Step 6: 更新核心合约的四项分权**

在人物/剧本/视频交接处写入：

```text
写作声音：编剧负责人物怎样选择、解释和回避事实。
可听声音身份：人物设计负责稳定音色与发声辨识，不冻结当前情绪。
条件化行为签名：人物设计负责不同压力条件下的稳定身体与行为差异。
当前场景表演：视频负责本镜目标、触发、策略、身体/声音变化、听者反应和停点。
```

- [ ] **Step 7: 增加ACTING运行时场景**

向 `runtime_reachability_scenarios` 增加：

```json
{
  "name": "稳定人物母档选择性进入当前文戏表演",
  "owner": "laohu-video-prompt",
  "request": "一个平时控制欲很强的父亲正在撒谎，想让孩子相信家里没出事；需要生成父子对话。",
  "required_references": [
    "skills/laohu-video-prompt/references/01_文戏对白与人物表演.md"
  ],
  "required_intermediate": [
    "写作声音",
    "可听声音身份",
    "条件化行为签名",
    "当前场景表演",
    "策略变化"
  ],
  "observable_change": "台词由父亲选择和回避事实的写作声音决定；稳定声纹只保护辨识；当前镜头从撒谎条件下的行为签名选择眼线、呼吸、手边任务和距离裂缝，并在孩子追问后改变策略。",
  "forbidden_shortcut": "把人物小传和整份表演母档粘进正文；只写心虚、克制；用口头禅代替人格；把声纹和当前情绪混成一个永久参数。"
}
```

- [ ] **Step 8: 运行架构验证**

Run:

```bash
python3 scripts/validate_capability_architecture.py
```

Expected: ACTING四项分权场景通过，原有编剧人物声音和视频表演场景继续通过。

- [ ] **Step 9: 提交表演接口**

```bash
git add skills/laohu-script-writer/SKILL.md \
  skills/laohu-character-design/SKILL.md \
  skills/laohu-video-prompt/SKILL.md \
  skills/laohu-video-prompt/references/01_文戏对白与人物表演.md \
  '02_共享资产库/05_工具流程/laohu_skills核心合约.md' \
  tests/capability_scenarios.json
git commit -m "feat: separate character voice and scene acting contracts"
```

---

### Task 7: 打通场景母版、资产参考与视频运行时切片

**Files:**
- Modify: `skills/laohu-set-design/SKILL.md`
- Modify: `skills/laohu-visual-assets/SKILL.md`
- Modify: `02_共享资产库/05_工具流程/laohu_skills核心合约.md`
- Modify: `tests/capability_scenarios.json`
- Test: `scripts/validate_capability_architecture.py`

- [ ] **Step 1: 在场景交接包增加运行时可切片事实**

在`【人物调度与摄影接口】`之后增加：

```text
【GEO切片源】统一世界原点和前方；主次锚点世界坐标/方向距离；入口出口；180度轴和可选观看侧；人物/道具允许起点区、路径和停留区；固定家具不可移动项；当前媒介可用机位；反打后不改变的世界关系。它是视频运行时切片的事实源，不是一条完整视频提示词。
```

- [ ] **Step 2: 在视觉资产交接增加激活参考合同**

加入：

```text
【激活参考候选】参考编号、真实存在状态、可控制属性、不得继承属性、适用VID/状态、与其他参考的冲突优先级。稳定资产负责身份/结构/材质/拓扑；真实状态帧只负责通过质量门的临时站位、破坏、光影、观看侧和结束相位。
```

保持“没有实际上传或本地不存在的素材不能冒充已绑定”。

- [ ] **Step 3: 更新核心合约的场景/资产→视频字段**

加入：

```text
GEO 运行时切片：当前世界坐标、摄影机侧/轴线、人物道具起点、允许路径、屏幕投影和固定锚点。
激活参考职责：每张真实输入的唯一职责、不得继承、状态版本与冲突优先级。
首帧阻挡：精确人数、位置、朝向、遮挡、手中物、主锚点和观看侧。
连续性把手：接续类型、真实尾部/终帧、必须继承、允许重建、不得继承、预计裁剪区。
```

- [ ] **Step 4: 增加跨Skill空间运行时场景**

向 `runtime_reachability_scenarios` 增加：

```json
{
  "name": "完整场景母版被切成当前VID的GEO运行时信息",
  "owner": "laohu-video-prompt",
  "request": "固定诊室已有完整场景母版和多机位资产，当前只拍医生从操作台走到门口拦住病人。",
  "required_references": [
    "skills/laohu-video-prompt/references/10_画面内容镜头叙事语法.md"
  ],
  "required_intermediate": [
    "GEO 运行时切片",
    "激活参考职责",
    "首帧阻挡",
    "当前镜头封闭编译"
  ],
  "observable_change": "只从场景母版提取操作台、门口、医生起点、病人位置、允许路径、观看侧和屏幕投影；只绑定当前人物/场景参考并声明非继承构图，不把整份场景说明书、未出现家具和其他机位全部粘贴进正文。",
  "forbidden_shortcut": "视频阶段移动固定入口或家具；用房间左边等机位相关词代替世界坐标；把完整设计库当投喂清单。"
}
```

- [ ] **Step 5: 运行架构验证**

Run:

```bash
python3 scripts/validate_capability_architecture.py
```

Expected: GEO、激活参考、首帧阻挡和连续性把手跨Skill可达。

- [ ] **Step 6: 提交运行时接口**

```bash
git add skills/laohu-set-design/SKILL.md \
  skills/laohu-visual-assets/SKILL.md \
  '02_共享资产库/05_工具流程/laohu_skills核心合约.md' \
  tests/capability_scenarios.json
git commit -m "feat: compile scene and asset state into runtime shots"
```

---

### Task 8: 建立真实生成实验和停止改词闭环

**Files:**
- Modify: `skills/laohu-generation-review/SKILL.md`
- Modify: `skills/laohu-generation-review/references/01_图片与视频生成诊断.md`
- Modify: `02_共享资产库/05_工具流程/laohu_skills核心合约.md`
- Modify: `tests/capability_scenarios.json`
- Test: `scripts/validate_capability_architecture.py`

- [ ] **Step 1: 在复盘负责人增加实验账**

加入：

```text
【单变量生成实验账】实验ID；模型/平台/入口/版本/日期；模式与参数；参考输入；母稿与运行稿；本轮唯一改动；预期影响；样本数量；逐项遵循；首断点；成本；KEEP/OBSERVE/REVERT；下一轮唯一动作。
```

逐项遵循至少检查：首帧人数位置、身份状态、GEO/轴线/路径、动作接触与物理、人物策略与听者反应、摄影机与注意力、声源台词、结束状态、连续性把手和提示词后半段。

- [ ] **Step 2: 增加停止同义改词条件**

加入：

```text
若连续失败仍落在同一个首断点，且两轮以上只是在替换同义词、加强警告或重复约束，立即停止改词。根据证据返回：降低单节拍任务、拆VID、换观看侧、修首帧/资产、改变参考组合或重做动作调度。失败次数不写死为10—15；由单次成本、镜头价值、问题稳定性和可替代路线共同裁决。
```

- [ ] **Step 3: 增加连续性把手质量门**

写入：

```text
把手只有在人物/服装/道具/场景无新增错误、最后有效机位无硬切、世界位置/屏幕方向/观看侧/锚点可读、临时状态与A真实结尾一致时才可绑定B。广角损害人脸、情绪或预算时，依次退化为中远景、动作/表演把手、终帧+稳定资产、单独空间参考或B重新建立场景。
```

- [ ] **Step 4: 增加实验回流场景**

向 `runtime_reachability_scenarios` 增加：

```json
{
  "name": "重复失败从提示词改写返回镜头或资产设计",
  "owner": "laohu-generation-review",
  "request": "同一多人动作镜头已经生成多轮，人物仍交换位置；最近两轮只增加了保持位置、绝对不要换位等警告。",
  "required_references": [
    "skills/laohu-generation-review/references/01_图片与视频生成诊断.md"
  ],
  "required_intermediate": [
    "单变量生成实验账",
    "本轮唯一改动",
    "逐项遵循",
    "停止同义改词",
    "最早负责人"
  ],
  "observable_change": "复盘确认首断点仍是首帧/GEO或镜头负载，不再增加否定警告；按证据返回空间把手、参考组合、调度、观看侧或拆VID中的最早负责人，并保留一次只改一个变量的下一轮实验。",
  "forbidden_shortcut": "继续堆保持一致和绝对不要；用失败次数机械决定；同时改提示词、参考图、时长、机位和人物动作后宣称某一项有效。"
}
```

- [ ] **Step 5: 更新视频→复盘核心交接**

增加：

```text
实验ID与目标入口能力合同；母稿/运行稿；当前激活参考；连续性把手；本轮唯一改动；预期遵循；实际样本与首断点；返回负责人。
```

- [ ] **Step 6: 运行架构验证**

Run:

```bash
python3 scripts/validate_capability_architecture.py
```

Expected: 单变量实验、停止改词和连续性把手回流场景通过。

- [ ] **Step 7: 提交真实结果闭环**

```bash
git add skills/laohu-generation-review/SKILL.md \
  skills/laohu-generation-review/references/01_图片与视频生成诊断.md \
  '02_共享资产库/05_工具流程/laohu_skills核心合约.md' \
  tests/capability_scenarios.json
git commit -m "feat: add generation experiments and redesign stops"
```

---

### Task 9: 能力进化记录与全链回归

**Files:**
- Modify: `04_诊断与系统日志/能力进化台账.md`
- Verify: all files modified in Tasks 1-8

- [ ] **Step 1: 写入能力进化记录**

按台账现有格式增加一条记录，内容必须包括：

```text
证据：HELL GRIND官方Project Brief、CINEDANCE/ACTING/LIRA、真实提示词样本，以及老胡对广角连续性把手的生产解释。
旧行为：固定4000/10000字符门；把广角、长镜头、FOV和8K/IMAX主要列为不吸收项；连续性只有状态相等，没有把手构图与裁剪合同。
新行为：目标入口能力合同；所有相邻VID选择接续类型；条件化连续性把手；LIRA图片任务路由；ACTING四项分权；CINEDANCE封闭镜头/GEO/首帧；单变量实验与停止改词。
保护项：三段式、高密度母稿、选择性编译、相对时长、现有资产分类、首断点归因、只输出文本。
重新唤醒条件：真实入口报错；长文本后半段持续不遵循；广角把手损害身份/情绪/成本；FOV或8K/IMAX A/B出现稳定增益或副作用；不同模型支持视频参考发生变化。
决定：OBSERVE，待四类真实生成回归后决定KEEP或局部REVERT。
```

- [ ] **Step 2: 运行视频脚本回归**

```bash
bash skills/laohu-video-prompt/scripts/test_count_video_prompt_chars.sh
bash skills/laohu-video-prompt/scripts/test_validate_video_prompt_structure.sh
```

Expected: 两个脚本均输出`tests passed`。

- [ ] **Step 3: 运行全项目架构回归**

```bash
python3 scripts/validate_capability_architecture.py
```

Expected: `exit 0`，所有Skill职责、Reference路由、迁移合同和运行时场景通过。

- [ ] **Step 4: 运行相关Python测试**

```bash
python3 -m unittest \
  tests.test_script_writer_architecture \
  tests.test_mv_architecture \
  tests.test_story_material_architecture
```

Expected: `OK`。本次不改故事素材数据库，但需要证明核心合约没有破坏上游路由。

- [ ] **Step 5: 扫描旧规则残留与四层泄漏**

```bash
! rg -n 'Seedance 2\.0 单条不超过|单条 `≤4000`|单条 `≤10000`|跨模型共用.*4000' \
  skills/laohu-video-prompt \
  '02_共享资产库/03_模型适配/Seedance2'
! rg -n '^## (灵魂|筋骨|血肉|表皮)(层)?$' \
  skills/laohu-video-prompt \
  skills/laohu-visual-assets \
  skills/laohu-character-design \
  skills/laohu-generation-review
```

Expected: 两次扫描均无输出。

- [ ] **Step 6: 检查格式与范围**

```bash
git diff --check
git status --short
```

Expected: `git diff --check`无输出；`git status`只显示本轮计划列明的文件和用户原有的无关改动，没有临时测试文件。

- [ ] **Step 7: 反向审稿四个失败场景**

逐项人工核对：

```text
简单建立镜头：允许短提示词，不为动态预算强行扩写。
承重文戏：选择表演把手，不因连续性强制大全景。
复杂多人动作：允许高密度长稿，GEO/首帧/物理/声音不过载到同一节拍。
MV/广告艺术转场：共同载体成立，不继承错误空间，也不被同期声默认删除音乐关系。
```

Expected: 四个场景都能从总控路由到唯一负责人、产生可检查中间结果并进入下游，不依赖作者口头补充。

- [ ] **Step 8: 提交能力进化记录和最终回归**

```bash
git add '04_诊断与系统日志/能力进化台账.md'
git commit -m "docs: record Higgsfield capability integration evidence"
```

---

## 完成条件

- 项目中不再把4000/10000写成Seedance或跨模型普适硬门。
- 未知入口得到`入口长度兼容性未验证`，不是默认裁切或虚假通过。
- 所有相邻VID必须选择六类接续之一，但没有“所有结尾必须广角”。
- 空间连续性把手、表演把手、动作把手、状态把手、艺术转场和场景重置都有可达路径。
- 长镜头、FOV/焦段、8K/IMAX保留底层机制、条件入口和退出机制，不成为全局模板。
- LIRA没有变成新Skill，而是图片任务路由和单变量编辑。
- ACTING没有变成新Skill，而是写作声音、可听声纹、条件化行为签名、当前场景表演四项分权。
- CINEDANCE没有覆盖本地三段式，而是补充当前镜头封闭编译、激活参考、GEO运行时切片、首帧阻挡和风险加权密度。
- 模型正文继续使用局部相对时长，不建立完整绝对时间轴。
- 单变量实验账能够阻止无尽同义改词，并把失败返回最早负责人。
- 脚本测试、架构验证和相关Python测试全部通过。
