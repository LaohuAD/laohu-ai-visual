# 老胡 Skills 目录与使用说明

当前结构已实施。五个文件夹都是真实技能内容；`.agents/skills/`是唯一技能实体目录，旧根目录`skills/`已迁入，不再使用符号链接或快捷方式。本文同时说明上传选择、职责边界、灵感双份保存与实际文件树，后续结构调整继续更新本文件。

## 直接上传哪一个文件夹

在本项目`.agents/skills/`下面，选择本次需要的**一个完整文件夹**上传。不要只上传SKILL.md，也不需要连同整个共享资产库上传。以下链接可以查看各包入口，文件夹名就是上传时要选择的名称。

| 文件夹 | 用途 | 典型请求 |
|---|---|---|
| [laohu-ai-visual](../../SKILL.md) | 项目总控 | 把一首歌做成MV；确定作品方向；判断已有成片哪里先出了问题 |
| laohu-script-writer（按本包任务交接，非必需外部文件） | 故事与剧本 | 记录灵感；用故事原子开发剧情；编写完整剧本；定稿后分段讲戏 |
| laohu-image-creation（按本包任务交接，非必需外部文件） | 图片与视觉资产 | 补全图片描述；设计人物服装场景；制作可复用资产；设计封面 |
| laohu-video-prompt（按本包任务交接，非必需外部文件） | 视频制作与提示词 | 段内分镜；视频提示词及提纯；音色、对白、音效、环境音、音乐 |
| laohu-language-mode（按本包任务交接，非必需外部文件） | 语言模式 | 判断不同文本应该怎样表达；改进沟通、创作和模型指令的语言方式 |

每包根目录都有SKILL.md，入口会指向本包内的专业方法、Reference、模板与必要脚本。没有脚本运行能力时，文本创作仍可读取Markdown方法和故事原子；需要执行校验或写入工具时，如实说明当前环境能力。这里已经完成文件层面的独立性验证，未在RunningHub内实际上传或运行。

独立完整指本包职责内的方法齐全。例如视频仍需要你提供已确认内容和必要资产，这属于作品输入。它不能因为没有剧本就伪造上游确认，也不能因为只安装一个包就声称已调用另一个包。

## 项目大顶层与五个小顶层

```text
老胡AI视觉/
├── AGENTS.md                       大顶层：按任务选择五包，约束阶段与权威边界
├── 输入输出索引.md                 本地入口与内容去向
├── .agents/
│   ├── README.md                   本地发现与维护说明
│   └── skills/
│       ├── README.md               当前说明
│       ├── laohu-ai-visual/         项目总控
│       ├── laohu-script-writer/     故事与剧本
│       ├── laohu-image-creation/    图片与视觉资产
│       ├── laohu-video-prompt/      视频制作与提示词
│       └── laohu-language-mode/    语言模式
├── 00_输入原料/                    尚未归属作品的需求与研究原料
├── 01_作品项目/                    每部作品的完整生产链与真实结果
├── 02_共享资产库/                  可选的本地积累与完整素材来源
│   ├── README.md                  共享内容的职责
│   ├── 故事素材库/                完整原话、故事原子、使用记录与检索数据
│   └── 02_视觉语言资产/画面风格库/ 已有创作样例
├── 03_发布与课程化/                教程、课程与发布内容
├── 04_诊断与系统日志/              历史证据、迁移记录与能力进化台账
├── scripts/                       本地维护与机械校验
└── tests/                         有意义的行为与历史保真检查
```

包内保留114个内部专业入口，与5个包入口合计119个Skill。专业职责没有为了减少顶层目录而删除；日常只需按当前任务选择一个包，再按缺口进入内部专业。某些本地宿主可能递归显示内部Skill，这与磁盘只有五个小顶层文件夹是两件事。

## 这些专业为什么这样归类

- **分段讲戏归故事与剧本。** 它确定这次演哪段原文、段落目的、估时与接续，交出P级内容执行卡；视频包才负责P内C镜头、摄影和提示词。分类依据是交付结果，不只是“是否处理文本”。
- **MV导演归项目总控。** 它负责歌曲怎样转成观众经历，保留音乐时间证据、声画关系与表演策略，不强制把歌曲改成叙事剧本。
- **音频设计归视频制作与提示词。** 音色、声音表演、环境声、动作声、音乐、剪辑和混音保留专业方法；独立音色请求可直接做，不必先设计整段分镜。
- **封面归图片与视觉资产。** 封面以真实承诺和缩略后可读性验收；稳定资产以身份、结构和复用验收，两种用途分别处理。
- **语言模式独立维护，同时内置于四个业务包。** 各业务包的references/语言表达.md负责领域使用，references/语言模式/带有完整方法；单独上传图片或视频包后仍能判断怎么沟通、怎么写专业正文，不需要另外安装语言包。

## 灵感在本地保存两份，分别用于溯源和应用

后续每次明确要求“记录灵感、保存素材”，都完成下面这条流程：

```text
完整原话 → 共享目录sources/保存来源
         → 提炼独立价值核心，保存共享目录atoms/故事原子
         → 自动同步到故事技能包references/故事原子/
         → 核验同一编号、内容与可用状态，两处成功后回执
```

共享目录里的完整库负责保留原话、语境、来源、原子分析与使用证据。故事包保存同一原子的应用内容：结论、人性机制、可见证据、延展方式、适用边界、置信度与source_id。它有真实正文，不是只放一个指向共享目录的索引。原话不重复塞进应用文件；需要溯源时，本地可以按source_id找到来源。

本地收录工具的add-source、add-atoms、log-usage、migrate-legacy会自动同步应用内容。原子修订回到共享权威库，再同步；暂停或重新启用也会改变包内可用状态。同步失败会明确报告“来源已保存”，修复后只重试同步，避免重复新增。不能只更新共享目录，把补应用副本拖到上传前。

[故事原子应用目录](laohu-script-writer/references/故事原子/README.md)可以直接浏览和按需读取。包内scripts/story_atoms.py支持分页搜索、详情读取与本地同步；云端没有Python时也可按目录读原子Markdown。没有匹配素材允许零采用，原子提供创作机制，不是可以拼接或照搬的剧情答案。

截至2026-09-13本轮迁移，已有完整来源3条、应用原子12条。两处均属于本地创作内容，不进入Git；选择上传故事包时，应用原子随文件夹一起带走。云端持有上传时的内容，本地新增不会自动推送云端，后续上传更新后的同一文件夹即可。云端产生的来源或使用证据需回流本地后再同步，不能声称已自动写回本地。

## Reference、共享目录与维护方式

包内文件链接使用**相对于当前文件的路径**，可使用`../`到达本包内的其他专业，但不能越出该包寻找必需方法。没有绑定某台电脑的绝对路径。项目AGENTS、共享来源库、历史审计和其他包只承担本地协作、可选增强或追溯，不能成为独立创作的必读前置。

原共享目录里的专业规则已经按负责人迁入对应Reference；历史工具设想和初始化记录进入系统日志。视频注意力与时间编译从图片/通用编译资料中拆出，归视频编译专业，保留完整判断条件。共享目录继续保存完整素材来源和真实创作积累，有这些材料时可更深入复用、溯源，没有时五包仍能执行通用专业方法。

跨包真正需要的专业方法，以真实文件保存在消费包references/内置方法/中，来源专业负责维护。语言方法与交付渲染脚本同样有完整副本；这是为了独立上传而保留必要内容，不是快捷方式，也不是执行时远程取文件。维护者改动公共方法后，在同一轮更新所有受影响副本并校验。**使用者上传前不用导出或拼包。**

维护命令从项目根目录执行：

```bash
python3 scripts/sync_skill_packages.py
python3 scripts/sync_skill_packages.py --check
python3 scripts/validate_skill_packages.py
```

现有吸收后的专业方法、案例与条件保留在本地Reference；外部网址只作为出处信息，不代替本地方法或要求日常执行时重新读网页。外部原文保留来路与已有证据，来源未知则如实标记，不冒充项目原创。

入口优化重点是“识别任务—保护已确认内容—选择必要方法—整合结果—验收”。Reference长并不是问题；入口能选对它、用好它才是关键。仅补全图片描述时，应保留原构图、动作、光影等已确认内容，只补影响理解或执行的不足，不擅自换画面。

## 五包实际文件树

下面按当前磁盘列出正式方法文件。目录后的说明标明用途，Skill名称后的中文名称来自实际入口。隐藏缓存和私有原子逐条数据不列入方法清单；应用原子请看上方专门目录。内置方法也是随包上传的正文。

<details>
<summary>项目总控：laohu-ai-visual（含11个Skill入口）</summary>

目的、导演、MV、创意、真实结果复盘与能力更新。

```text
laohu-ai-visual/
├── agents/  宿主识别元数据
│   └── openai.yaml
├── references/  按需读取的专业方法、案例与合同
│   ├── 内置方法/  本包实际保存的跨专业方法，维护时同步
│   │   ├── laohu-image-creation/
│   │   │   ├── references/  按需读取的专业方法、案例与合同
│   │   │   │   ├── 语言表达.md  图片与视觉资产的语言表达
│   │   │   │   └── 高质量AI图片开发计划.md  高质量 AI 图片开发计划
│   │   │   └── skills/  内部专业，每项有自己的入口与验收
│   │   │       ├── laohu-art-direction/
│   │   │       │   ├── references/  按需读取的专业方法、案例与合同
│   │   │       │   │   ├── 01_题材视觉证据与相邻类型边界.md  题材视觉证据与相邻类型边界
│   │   │       │   │   └── 画面氛围与画质规范.md  画面风格与画质规范
│   │   │       │   └── skills/  内部专业，每项有自己的入口与验收
│   │   │       │       ├── laohu-layout-design/
│   │   │       │       │   └── references/  按需读取的专业方法、案例与合同
│   │   │       │       │       └── 02_日本版面与文字空间机制.md  日本版面与文字空间机制
│   │   │       │       └── laohu-photography/
│   │   │       │           └── references/  按需读取的专业方法、案例与合同
│   │   │       │               └── 镜头语言词典.md
│   │   │       ├── laohu-character-design/
│   │   │       │   ├── skills/  内部专业，每项有自己的入口与验收
│   │   │       │   │   ├── laohu-ensemble-design/
│   │   │       │   │   │   ├── references/  按需读取的专业方法、案例与合同
│   │   │       │   │   │   │   └── 专业方法.md  群像设计专业方法
│   │   │       │   │   │   └── 专业方法.md  老胡群像设计
│   │   │       │   │   └── laohu-face-design/
│   │   │       │   │       ├── references/  按需读取的专业方法、案例与合同
│   │   │       │   │       │   ├── 专业方法.md  面部设计专业方法
│   │   │       │   │       │   ├── 结构与妆容候选词表.md
│   │   │       │   │       │   └── 结构兼容与阵容方法.md  结构选择、兼容与阵容
│   │   │       │   │       └── 专业方法.md  老胡面部设计
│   │   │       │   └── 专业方法.md  老胡人物设计
│   │   │       ├── laohu-costume-design/
│   │   │       │   └── skills/  内部专业，每项有自己的入口与验收
│   │   │       │       ├── laohu-costume-research/
│   │   │       │       │   └── references/  按需读取的专业方法、案例与合同
│   │   │       │       │       └── 专业方法.md  服饰考据专业方法
│   │   │       │       └── laohu-costume-silhouette/
│   │   │       │           └── references/  按需读取的专业方法、案例与合同
│   │   │       │               └── 专业方法.md  服装造型专业方法
│   │   │       ├── laohu-cover-design/
│   │   │       │   ├── agents/  宿主识别元数据
│   │   │       │   │   └── openai.yaml
│   │   │       │   ├── references/  按需读取的专业方法、案例与合同
│   │   │       │   │   └── 模板_封面海报创作执行单.md  封面海报创作执行单
│   │   │       │   ├── skills/  内部专业，每项有自己的入口与验收
│   │   │       │   │   └── laohu-cover-concept/
│   │   │       │   │       └── references/  按需读取的专业方法、案例与合同
│   │   │       │   │           └── 01_文化素材事实与视觉基因转译.md  文化素材事实与视觉基因转译
│   │   │       │   └── 专业方法.md  老胡封面与海报
│   │   │       ├── laohu-image-prompt/
│   │   │       │   └── references/  按需读取的专业方法、案例与合同
│   │   │       │       ├── 模板_通用负面提示词.md  模板：通用质量边界
│   │   │       │       └── 视觉生成模型注意力与提示词编译参考.md
│   │   │       ├── laohu-makeup-design/
│   │   │       │   ├── skills/  内部专业，每项有自己的入口与验收
│   │   │       │   │   └── laohu-makeup/
│   │   │       │   │       ├── references/  按需读取的专业方法、案例与合同
│   │   │       │   │       │   ├── 专业方法.md  妆容设计专业方法
│   │   │       │   │       │   └── 妆容条件适配.md  妆容与人物适配
│   │   │       │   │       └── 专业方法.md  老胡妆容设计
│   │   │       │   └── 专业方法.md  老胡妆发设计
│   │   │       ├── laohu-portrait/
│   │   │       │   └── references/  按需读取的专业方法、案例与合同
│   │   │       │       └── 06_人物生命感与现场摄影关系.md  人物生命感与现场摄影关系
│   │   │       ├── laohu-prop-design/
│   │   │       │   └── 专业方法.md  老胡道具设计
│   │   │       ├── laohu-set-design/
│   │   │       │   ├── skills/  内部专业，每项有自己的入口与验收
│   │   │       │   │   ├── laohu-environment-research/
│   │   │       │   │   │   └── references/  按需读取的专业方法、案例与合同
│   │   │       │   │   │       └── 专业方法.md  场景考据专业方法
│   │   │       │   │   └── laohu-spatial-layout/
│   │   │       │   │       └── references/  按需读取的专业方法、案例与合同
│   │   │       │   │           └── 专业方法.md  空间布局专业方法
│   │   │       │   └── 专业方法.md  老胡场景与布景设计
│   │   │       └── laohu-visual-assets/
│   │   │           ├── references/  按需读取的专业方法、案例与合同
│   │   │           │   ├── 00_资料来源与专业校准.md  资料来源与专业校准
│   │   │           │   ├── 剧本到AI视觉资产转换规则.md  剧本到 AI 视觉资产转换规则
│   │   │           │   ├── 模板_AI图片提示词_资产型通用结构.md
│   │   │           │   ├── 模板_角色一致性网格图.md
│   │   │           │   ├── 状态帧与下游运动.md  资产状态与接续参考
│   │   │           │   └── 身份状态与最小资产.md  资产规格与编译
│   │   │           └── 专业方法.md  老胡视觉资产
│   │   ├── laohu-language-mode/
│   │   │   └── references/  按需读取的专业方法、案例与合同
│   │   │       ├── 01_模式判定与块级切换.md  模式判定与块级切换
│   │   │       ├── 02_用户沟通与制作说明.md  用户沟通与制作说明
│   │   │       ├── 03_剧本文本块语言.md  剧本文本块语言
│   │   │       ├── 04_资产图片视频与声音提示词桥接.md  资产、图片、视频与声音提示词桥接
│   │   │       └── 05_有效信息与冗余裁决.md  有效信息与冗余裁决
│   │   ├── laohu-script-writer/
│   │   │   ├── references/  按需读取的专业方法、案例与合同
│   │   │   │   ├── 故事原子/  完整应用原子与检索目录，逐条内容见专门目录
│   │   │   │   ├── 04_叙事视角命名与故事因果.md  叙事视角、命名与故事因果
│   │   │   │   ├── 05_剧本语言诊断与反向审稿.md  剧本语言诊断与反向审稿
│   │   │   │   ├── 06_故事构件拆解与组合语法.md  故事构件拆解与组合语法
│   │   │   │   ├── 07_故事构件库.jsonl
│   │   │   │   ├── 外部编剧工作流.md  编剧工作流的本地适配
│   │   │   │   ├── 外部编剧工作流案例.md  story-bible.md 模板与各阶段工作单
│   │   │   │   ├── 模板_AI电影级剧本开发工作流.md
│   │   │   │   ├── 模板_阶段门控剧本开发.md
│   │   │   │   └── 语言表达.md  故事与剧本的语言表达
│   │   │   ├── scripts/  执行、检索或校验工具
│   │   │   │   ├── story_atoms.py
│   │   │   │   └── story_component_library.py
│   │   │   └── skills/  内部专业，每项有自己的入口与验收
│   │   │       ├── laohu-american-case-studies/
│   │   │       │   ├── reference.md  美国电影剧作案例：补充范例与分析表
│   │   │       │   └── 专业方法.md  老胡美国电影剧作案例
│   │   │       ├── laohu-character-conflict/
│   │   │       │   ├── references/  按需读取的专业方法、案例与合同
│   │   │       │   │   └── 人物行动与连续性.md
│   │   │       │   ├── reference.md  人物与冲突：原型表、心理学检查清单与分析模板
│   │   │       │   └── 专业方法.md  老胡人物与冲突
│   │   │       ├── laohu-chekhov-dramaturgy/
│   │   │       │   ├── reference.md  契诃夫七部多幕剧：逐幕结构表与原文范例
│   │   │       │   └── 专业方法.md  老胡契诃夫戏剧法
│   │   │       ├── laohu-chinese-series-practice/
│   │   │       │   ├── reference-cases.md  国产剧实务（三）：张巍六个改编案例对照
│   │   │       │   ├── reference-rules.md  国产剧实务（四）：片段索引与内容红线
│   │   │       │   ├── reference-samples.md  国产剧实务（二）：格式样本、策划样本、场面表与境遇清单
│   │   │       │   ├── reference.md  国产剧实务：格式样本、改编案例表、术语字典与制片链文件
│   │   │       │   └── 专业方法.md  老胡国产剧创作与生产衔接
│   │   │       ├── laohu-dialogue/
│   │   │       │   ├── references/  按需读取的专业方法、案例与合同
│   │   │       │   │   ├── 喜剧场面与传播.md
│   │   │       │   │   └── 本地对白与表演补充.md  对白与表演方法
│   │   │       │   ├── reference.md  对白：七个场景节拍分析范例、改写对照与唱词范例
│   │   │       │   └── 专业方法.md  老胡对白创作
│   │   │       ├── laohu-format-adaptation/
│   │   │       │   ├── references/  按需读取的专业方法、案例与合同
│   │   │       │   │   └── 镜头化剧本与连续性.md  体量、形态、编号与连续性
│   │   │       │   ├── reference.md  格式·流程·改编：模板、符号表与范例
│   │   │       │   └── 专业方法.md  老胡格式、流程与改编
│   │   │       ├── laohu-industry-business/
│   │   │       │   ├── reference.md  行业与生意经：清单、样本与术语
│   │   │       │   └── 专业方法.md  老胡编剧行业与生意经
│   │   │       ├── laohu-japanese-screenwriting/
│   │   │       │   ├── reference.md  日本编剧方法：情节构想范例与工作单
│   │   │       │   └── 专业方法.md  老胡日本编剧方法
│   │   │       ├── laohu-korean-french-screenwriting/
│   │   │       │   └── 专业方法.md  老胡韩国与法国编剧方法
│   │   │       ├── laohu-ozu-screenplay-style/
│   │   │       │   ├── reference.md  小津六部剧本：逐场结构表与原文范例
│   │   │       │   └── 专业方法.md  老胡小津剧本写法
│   │   │       ├── laohu-premise-theme/
│   │   │       │   ├── references/  按需读取的专业方法、案例与合同
│   │   │       │   │   └── 创意开发与主题检验.md
│   │   │       │   ├── reference.md  前提·主题：工作单与范例库
│   │   │       │   └── 专业方法.md  老胡前提与主题
│   │   │       ├── laohu-scene-craft/
│   │   │       │   ├── references/  按需读取的专业方法、案例与合同
│   │   │       │   │   └── 场面推进与苦难叙事.md
│   │   │       │   ├── reference.md  场景与段落：分析范例与工具表
│   │   │       │   └── 专业方法.md  老胡场景与段落
│   │   │       ├── laohu-series-case-studies/
│   │   │       │   ├── reference-asia.md  剧集案例库（三）：坂元裕二与卢熙京
│   │   │       │   ├── reference-pilots.md  剧集案例库（二）：方法书里的 pilot 节拍表与 beat sheet 实物
│   │   │       │   ├── reference.md  剧集案例库：逐集结构表、节拍表与原文范例
│   │   │       │   └── 专业方法.md  老胡剧集案例研究
│   │   │       ├── laohu-series-engine-bible/
│   │   │       │   ├── reference-documents.md  剧集引擎与 bible（二）：文档模板字段表
│   │   │       │   ├── reference-samples.md  剧集引擎与 bible（三）：填好的样例
│   │   │       │   ├── reference.md  剧集引擎与 bible（一）：引擎拆解、剧集类型与人物网
│   │   │       │   └── 专业方法.md  老胡剧集引擎与开发文档
│   │   │       ├── laohu-series-structure/
│   │   │       │   ├── reference.md  剧集单集与季结构：完整节拍表、页码表与逐集数据
│   │   │       │   └── 专业方法.md  老胡剧集单集与季结构
│   │   │       ├── laohu-sitcom-comedy/
│   │   │       │   ├── reference.md  半小时喜剧：格式规范、笑点技法目录与结构模板
│   │   │       │   └── 专业方法.md  老胡情景喜剧与半小时喜剧
│   │   │       ├── laohu-story-material/
│   │   │       │   ├── references/  按需读取的专业方法、案例与合同
│   │   │       │   │   └── 01_原子记录与渐进检索合同.md  原子记录与渐进检索合同
│   │   │       │   └── scripts/  执行、检索或校验工具
│   │   │       │       ├── story_material_db.py
│   │   │       │       └── story_material_store.py
│   │   │       ├── laohu-story-structure/
│   │   │       │   ├── references/  按需读取的专业方法、案例与合同
│   │   │       │   │   └── 结构尺度与高潮设计.md
│   │   │       │   ├── reference.md  故事结构：对照表、范例与逐片情节点
│   │   │       │   └── 专业方法.md  老胡故事结构
│   │   │       ├── laohu-succession-series-writing/
│   │   │       │   ├── reference.md  《继承之战》四季 39 集：逐集结构表、季弧表、set piece 对照表与原文范例
│   │   │       │   └── 专业方法.md  老胡权力群像剧写法
│   │   │       ├── laohu-video-segmentation/
│   │   │       │   └── references/  按需读取的专业方法、案例与合同
│   │   │       │       └── 短剧剧本到视频提示词编号与时长规则.md  剧本、分段与视频编号交接
│   │   │       └── laohu-writers-room/
│   │   │           ├── reference.md  编剧室：日程表、文档实物与一手访谈材料
│   │   │           └── 专业方法.md  老胡编剧室与制作修订
│   │   ├── laohu-video-prompt/
│   │   │   ├── references/  按需读取的专业方法、案例与合同
│   │   │   │   ├── 交接与验收.md  视频提示词：交接与验收合同
│   │   │   │   ├── 基础运动与专项路由.md  视频基础必读与专项按需调用
│   │   │   │   ├── 模板_视频生成质量检查清单.md
│   │   │   │   ├── 独立使用与交接.md  视频制作与提示词的独立使用与交接
│   │   │   │   ├── 短剧短片分镜生成字段规范.md
│   │   │   │   ├── 语言表达.md  视频制作与提示词的语言表达
│   │   │   │   ├── 镜头空间与连续性.md  段内摄影与空间连续性
│   │   │   │   └── 高质量AI视频提示词开发计划.md  高质量 AI 视频提示词开发计划
│   │   │   ├── scripts/  执行、检索或校验工具
│   │   │   │   └── count_video_prompt_chars.sh
│   │   │   ├── skills/  内部专业，每项有自己的入口与验收
│   │   │   │   ├── laohu-action-design/
│   │   │   │   │   ├── references/  按需读取的专业方法、案例与合同
│   │   │   │   │   │   └── 专业方法与案例.md  动作设计：专业方法与案例
│   │   │   │   │   └── 专业方法.md  老胡动作设计
│   │   │   │   ├── laohu-animation/
│   │   │   │   │   ├── references/  按需读取的专业方法、案例与合同
│   │   │   │   │   │   └── 专业方法与案例.md  动画：专业方法与案例
│   │   │   │   │   └── 专业方法.md  老胡动画
│   │   │   │   ├── laohu-audio-design/
│   │   │   │   │   ├── references/  按需读取的专业方法、案例与合同
│   │   │   │   │   │   └── 声音提示词规范.md
│   │   │   │   │   └── skills/  内部专业，每项有自己的入口与验收
│   │   │   │   │       ├── laohu-audio-editing/
│   │   │   │   │       │   ├── references/  按需读取的专业方法、案例与合同
│   │   │   │   │       │   │   └── 专业方法与案例.md  音频剪辑：专业方法与案例
│   │   │   │   │       │   └── 专业方法.md  老胡音频剪辑
│   │   │   │   │       ├── laohu-audio-mixing/
│   │   │   │   │       │   ├── references/  按需读取的专业方法、案例与合同
│   │   │   │   │       │   │   └── 专业方法与案例.md  混音：专业方法与案例
│   │   │   │   │       │   └── 专业方法.md  老胡混音
│   │   │   │   │       └── laohu-audio-prompt/
│   │   │   │   │           ├── references/  按需读取的专业方法、案例与合同
│   │   │   │   │           │   └── 专业方法与案例.md  音频提示词编译：专业方法与案例
│   │   │   │   │           └── 专业方法.md  老胡音频提示词编译
│   │   │   │   ├── laohu-audiovisual/
│   │   │   │   │   ├── references/  按需读取的专业方法、案例与合同
│   │   │   │   │   │   └── 专业方法与案例.md  声画关系：专业方法与案例
│   │   │   │   │   └── 专业方法.md  老胡声画关系
│   │   │   │   ├── laohu-camera-movement/
│   │   │   │   │   ├── references/  按需读取的专业方法、案例与合同
│   │   │   │   │   │   └── 专业方法与案例.md  运镜：专业方法与案例
│   │   │   │   │   └── 专业方法.md  老胡运镜
│   │   │   │   ├── laohu-choreography/
│   │   │   │   │   ├── references/  按需读取的专业方法、案例与合同
│   │   │   │   │   │   └── 专业方法与案例.md  舞蹈编排：专业方法与案例
│   │   │   │   │   └── 专业方法.md  老胡舞蹈编排
│   │   │   │   ├── laohu-editing/
│   │   │   │   │   ├── references/  按需读取的专业方法、案例与合同
│   │   │   │   │   │   ├── 专业方法与案例.md  剪辑：专业方法与案例
│   │   │   │   │   │   └── 模板_多镜头后期拼接.md  模板：多镜头后期拼接
│   │   │   │   │   └── 专业方法.md  老胡剪辑
│   │   │   │   ├── laohu-motion-design/
│   │   │   │   │   ├── references/  按需读取的专业方法、案例与合同
│   │   │   │   │   │   └── 专业方法与案例.md  动态图形设计：专业方法与案例
│   │   │   │   │   ├── skills/  内部专业，每项有自己的入口与验收
│   │   │   │   │   │   ├── laohu-editorial-explainer/
│   │   │   │   │   │   │   ├── references/  按需读取的专业方法、案例与合同
│   │   │   │   │   │   │   │   └── 证据编排与动态解释.md  编辑型知识讲解的证据编排
│   │   │   │   │   │   │   └── 专业方法.md  老胡编辑型知识动画
│   │   │   │   │   │   └── laohu-stickman-explainer/
│   │   │   │   │   │       ├── references/  按需读取的专业方法、案例与合同
│   │   │   │   │   │       │   ├── upstream/
│   │   │   │   │   │       │   │   ├── references/  按需读取的专业方法、案例与合同
│   │   │   │   │   │       │   │   │   ├── examples.md  Complete Example
│   │   │   │   │   │       │   │   │   ├── omni-flash-prompt-contract.md  Omni Flash Production Prompt Contract
│   │   │   │   │   │       │   │   │   └── storyboard-template.md  Director's Proposal Contract
│   │   │   │   │   │       │   │   └── 原始方法.md  Directing Stickman Videos
│   │   │   │   │   │       │   └── 专项方法与适配.md  火柴人讲解：专业方法与本地适配
│   │   │   │   │   │       └── 专业方法.md  老胡火柴人知识动画
│   │   │   │   │   └── 专业方法.md  老胡动态图形设计
│   │   │   │   ├── laohu-performance/
│   │   │   │   │   ├── references/  按需读取的专业方法、案例与合同
│   │   │   │   │   │   ├── 专业方法与案例.md  表演：专业方法与案例
│   │   │   │   │   │   ├── 人物表情与肢体动作词典.md
│   │   │   │   │   │   ├── 人物表演提示词规范.md
│   │   │   │   │   │   └── 模板_人物表演_情绪时间轴.md  模板：人物表演_情绪时间轴
│   │   │   │   │   └── 专业方法.md  老胡表演
│   │   │   │   ├── laohu-vfx/
│   │   │   │   │   └── references/  按需读取的专业方法、案例与合同
│   │   │   │   │       └── 专业方法与案例.md  视觉特效 VFX：专业方法与案例
│   │   │   │   ├── laohu-vibe-creating-prompt/
│   │   │   │   │   ├── references/  按需读取的专业方法、案例与合同
│   │   │   │   │   │   └── 01_外部Vibe_Creating原文.md  Vibe Creating Prompt Skill
│   │   │   │   │   └── 专业方法.md  老胡视频提示词提纯
│   │   │   │   ├── laohu-video-compilation/
│   │   │   │   │   ├── references/  按需读取的专业方法、案例与合同
│   │   │   │   │   │   ├── Seedance2视频提示词书写规范.md  Seedance 2 视频提示词书写规范
│   │   │   │   │   │   ├── 专业方法与案例.md  视频提示词编译：专业方法与案例
│   │   │   │   │   │   ├── 多模型AI视频提示词通用规范.md  多模型 AI 视频提示词通用规范
│   │   │   │   │   │   └── 模板_视频提示词_基础设定氛围画面内容.md  模板：视频提示词_基础设定氛围画面内容
│   │   │   │   │   └── 专业方法.md  老胡视频提示词编译
│   │   │   │   └── laohu-video-references/
│   │   │   │       ├── references/  按需读取的专业方法、案例与合同
│   │   │   │       │   └── 专业方法与案例.md  视频参考与资产绑定：专业方法与案例
│   │   │   │       └── 专业方法.md  老胡视频参考与资产绑定
│   │   │   └── 视频注意力与时间编译.md
│   │   ├── scripts/  执行、检索或校验工具
│   │   │   ├── render_delivery_html.py
│   │   │   ├── validate_delivery_dependencies.py
│   │   │   └── validate_semantic_migration.py
│   │   ├── LICENSE.md  分层授权
│   │   └── README.md  老胡 Skills 目录与使用说明
│   ├── 语言模式/  随包携带的完整语言方法
│   │   ├── 01_模式判定与块级切换.md  模式判定与块级切换
│   │   ├── 02_用户沟通与制作说明.md  用户沟通与制作说明
│   │   ├── 03_剧本文本块语言.md  剧本文本块语言
│   │   ├── 04_资产图片视频与声音提示词桥接.md  资产、图片、视频与声音提示词桥接
│   │   └── 05_有效信息与冗余裁决.md  有效信息与冗余裁决
│   ├── 00_核心规则手册.md  老胡 AI 视觉能力地图
│   ├── laohu_skills核心合约.md  laohu Skills 核心合约
│   ├── 外部能力依赖清单.md
│   ├── 新作品创建与归位流程.md
│   ├── 模板_作品项目启动包.md
│   ├── 模板_作品项目目录结构.md
│   ├── 独立使用与交接.md  项目总控的独立使用与交接
│   ├── 能力协作图谱.md  老胡 AI 视觉能力协作图谱
│   ├── 能力注册表.json
│   └── 语言表达.md  项目总控的语言表达
├── scripts/  执行、检索或校验工具
│   ├── check_laohu_skills.sh
│   ├── create_work_project.sh
│   └── render_delivery_html.py
├── skills/  内部专业，每项有自己的入口与验收
│   ├── laohu-capability-evolution/  老胡 AI 视觉能力进化
│   │   ├── agents/  宿主识别元数据
│   │   │   └── openai.yaml
│   │   ├── references/  按需读取的专业方法、案例与合同
│   │   │   ├── 01_证据吸收与根因判断.md  证据吸收与根因判断
│   │   │   ├── 02_四层能力重编译.md  四层能力重编译
│   │   │   ├── 03_保真迁移回归与回退.md  保真迁移、回归与回退
│   │   │   ├── 04_进化记忆与能力生长.md  进化记忆与能力生长
│   │   │   ├── laohu_skills能力加厚规范.md  laohu Skills 能力生长规范（兼容入口）
│   │   │   ├── 助手执行失败经验与防复发规则.md
│   │   │   └── 经验材料吸收与本地资产更新闭环.md
│   │   └── SKILL.md  触发、主责、流程与方法路由
│   ├── laohu-creative-development/  老胡创意开发
│   │   ├── agents/  宿主识别元数据
│   │   │   └── openai.yaml
│   │   ├── references/  按需读取的专业方法、案例与合同
│   │   │   └── 创意机制与候选裁决.md
│   │   └── SKILL.md  触发、主责、流程与方法路由
│   ├── laohu-director/  老胡总导演
│   │   ├── agents/  宿主识别元数据
│   │   │   └── openai.yaml
│   │   ├── references/  按需读取的专业方法、案例与合同
│   │   │   ├── 01_导演判断与协作网络.md  导演判断与协作网络
│   │   │   └── 导演级影视创作总控流程.md
│   │   └── SKILL.md  触发、主责、流程与方法路由
│   ├── laohu-generation-review/  老胡生成与发布复盘
│   │   ├── agents/  宿主识别元数据
│   │   │   └── openai.yaml
│   │   ├── references/  按需读取的专业方法、案例与合同
│   │   │   ├── 交接与验收.md  生成与发布复盘：交接与验收合同
│   │   │   ├── 失败案例记录模板.md
│   │   │   ├── 成功案例记录模板.md
│   │   │   ├── 案例拆解与入库规则.md
│   │   │   ├── 模板_真实作品首轮验证看板.md
│   │   │   ├── 真实作品首轮验证计划.md
│   │   │   └── 真实生产验证回传包.md
│   │   ├── skills/  内部专业，每项有自己的入口与验收
│   │   │   ├── laohu-audio-review/  老胡音频评审
│   │   │   │   ├── references/  按需读取的专业方法、案例与合同
│   │   │   │   │   └── 专业方法与案例.md  音频评审：专业方法与案例
│   │   │   │   └── SKILL.md  触发、主责、流程与方法路由
│   │   │   ├── laohu-edit-review/  老胡成片评审
│   │   │   │   ├── references/  按需读取的专业方法、案例与合同
│   │   │   │   │   └── 专业方法与案例.md  成片评审：专业方法与案例
│   │   │   │   └── SKILL.md  触发、主责、流程与方法路由
│   │   │   ├── laohu-image-review/  老胡图片评审
│   │   │   │   ├── references/  按需读取的专业方法、案例与合同
│   │   │   │   │   └── 专业方法与案例.md  图片评审：专业方法与案例
│   │   │   │   └── SKILL.md  触发、主责、流程与方法路由
│   │   │   ├── laohu-release-review/  老胡发布复盘
│   │   │   │   ├── references/  按需读取的专业方法、案例与合同
│   │   │   │   │   └── 专业方法与案例.md  发布复盘：专业方法与案例
│   │   │   │   └── SKILL.md  触发、主责、流程与方法路由
│   │   │   └── laohu-video-review/  老胡视频评审
│   │   │       ├── references/  按需读取的专业方法、案例与合同
│   │   │       │   └── 专业方法与案例.md  视频评审：专业方法与案例
│   │   │       └── SKILL.md  触发、主责、流程与方法路由
│   │   └── SKILL.md  触发、主责、流程与方法路由
│   └── laohu-mv-director/  老胡 MV 导演
│       ├── agents/  宿主识别元数据
│       │   └── openai.yaml
│       ├── references/  按需读取的专业方法、案例与合同
│       │   ├── 01_歌曲事实歌词与时间证据.md  歌曲事实、歌词与时间证据
│       │   ├── 02_MV引擎声画表演与分段.md  MV 引擎、声画、表演与分段
│       │   └── 03_MV导演交接与文本验收.md  MV 导演交接与文本验收
│       └── SKILL.md  触发、主责、流程与方法路由
└── SKILL.md  触发、主责、流程与方法路由
```

</details>

<details>
<summary>故事与剧本：laohu-script-writer（含22个Skill入口）</summary>

灵感记录、故事原子、故事开发、完整剧本与分段讲戏。

```text
laohu-script-writer/
├── agents/  宿主识别元数据
│   └── openai.yaml
├── references/  按需读取的专业方法、案例与合同
│   ├── 内置方法/  本包实际保存的跨专业方法，维护时同步
│   │   ├── laohu-ai-visual/
│   │   │   ├── references/  按需读取的专业方法、案例与合同
│   │   │   │   └── 独立使用与交接.md  项目总控的独立使用与交接
│   │   │   └── skills/  内部专业，每项有自己的入口与验收
│   │   │       ├── laohu-capability-evolution/
│   │   │       │   └── references/  按需读取的专业方法、案例与合同
│   │   │       │       ├── 01_证据吸收与根因判断.md  证据吸收与根因判断
│   │   │       │       ├── 02_四层能力重编译.md  四层能力重编译
│   │   │       │       ├── 03_保真迁移回归与回退.md  保真迁移、回归与回退
│   │   │       │       ├── 04_进化记忆与能力生长.md  进化记忆与能力生长
│   │   │       │       └── laohu_skills能力加厚规范.md  laohu Skills 能力生长规范（兼容入口）
│   │   │       └── laohu-director/
│   │   │           └── references/  按需读取的专业方法、案例与合同
│   │   │               └── 导演级影视创作总控流程.md
│   │   ├── laohu-image-creation/
│   │   │   └── skills/  内部专业，每项有自己的入口与验收
│   │   │       ├── laohu-art-direction/
│   │   │       │   ├── references/  按需读取的专业方法、案例与合同
│   │   │       │   │   └── 画面氛围与画质规范.md  画面风格与画质规范
│   │   │       │   └── skills/  内部专业，每项有自己的入口与验收
│   │   │       │       └── laohu-photography/
│   │   │       │           └── references/  按需读取的专业方法、案例与合同
│   │   │       │               └── 镜头语言词典.md
│   │   │       ├── laohu-image-prompt/
│   │   │       │   └── references/  按需读取的专业方法、案例与合同
│   │   │       │       └── 视觉生成模型注意力与提示词编译参考.md
│   │   │       ├── laohu-portrait/
│   │   │       │   └── references/  按需读取的专业方法、案例与合同
│   │   │       │       └── 06_人物生命感与现场摄影关系.md  人物生命感与现场摄影关系
│   │   │       └── laohu-visual-assets/
│   │   │           └── references/  按需读取的专业方法、案例与合同
│   │   │               ├── 剧本到AI视觉资产转换规则.md  剧本到 AI 视觉资产转换规则
│   │   │               └── 状态帧与下游运动.md  资产状态与接续参考
│   │   ├── laohu-language-mode/
│   │   │   └── references/  按需读取的专业方法、案例与合同
│   │   │       └── 05_有效信息与冗余裁决.md  有效信息与冗余裁决
│   │   ├── laohu-video-prompt/
│   │   │   ├── references/  按需读取的专业方法、案例与合同
│   │   │   │   ├── 交接与验收.md  视频提示词：交接与验收合同
│   │   │   │   └── 镜头空间与连续性.md  段内摄影与空间连续性
│   │   │   ├── scripts/  执行、检索或校验工具
│   │   │   │   └── count_video_prompt_chars.sh
│   │   │   └── skills/  内部专业，每项有自己的入口与验收
│   │   │       ├── laohu-action-design/
│   │   │       │   └── references/  按需读取的专业方法、案例与合同
│   │   │       │       └── 专业方法与案例.md  动作设计：专业方法与案例
│   │   │       ├── laohu-audio-design/
│   │   │       │   └── references/  按需读取的专业方法、案例与合同
│   │   │       │       └── 声音提示词规范.md
│   │   │       ├── laohu-audiovisual/
│   │   │       │   └── references/  按需读取的专业方法、案例与合同
│   │   │       │       └── 专业方法与案例.md  声画关系：专业方法与案例
│   │   │       ├── laohu-camera-movement/
│   │   │       │   └── references/  按需读取的专业方法、案例与合同
│   │   │       │       └── 专业方法与案例.md  运镜：专业方法与案例
│   │   │       ├── laohu-motion-design/
│   │   │       │   └── references/  按需读取的专业方法、案例与合同
│   │   │       │       └── 专业方法与案例.md  动态图形设计：专业方法与案例
│   │   │       ├── laohu-performance/
│   │   │       │   └── references/  按需读取的专业方法、案例与合同
│   │   │       │       ├── 专业方法与案例.md  表演：专业方法与案例
│   │   │       │       └── 人物表演提示词规范.md
│   │   │       ├── laohu-vfx/
│   │   │       │   └── references/  按需读取的专业方法、案例与合同
│   │   │       │       └── 专业方法与案例.md  视觉特效 VFX：专业方法与案例
│   │   │       └── laohu-video-compilation/
│   │   │           └── references/  按需读取的专业方法、案例与合同
│   │   │               ├── 专业方法与案例.md  视频提示词编译：专业方法与案例
│   │   │               ├── 多模型AI视频提示词通用规范.md  多模型 AI 视频提示词通用规范
│   │   │               └── 模板_视频提示词_基础设定氛围画面内容.md  模板：视频提示词_基础设定氛围画面内容
│   │   └── scripts/  执行、检索或校验工具
│   │       └── validate_delivery_dependencies.py
│   ├── 故事原子/  完整应用原子与检索目录，逐条内容见专门目录
│   ├── 语言模式/  随包携带的完整语言方法
│   │   ├── 01_模式判定与块级切换.md  模式判定与块级切换
│   │   ├── 02_用户沟通与制作说明.md  用户沟通与制作说明
│   │   ├── 03_剧本文本块语言.md  剧本文本块语言
│   │   ├── 04_资产图片视频与声音提示词桥接.md  资产、图片、视频与声音提示词桥接
│   │   └── 05_有效信息与冗余裁决.md  有效信息与冗余裁决
│   ├── 00_资料来源与专业校准.md  资料来源与专业校准
│   ├── 01_口述故事补全.md  口述故事补全
│   ├── 04_叙事视角命名与故事因果.md  叙事视角、命名与故事因果
│   ├── 05_剧本语言诊断与反向审稿.md  剧本语言诊断与反向审稿
│   ├── 06_故事构件拆解与组合语法.md  故事构件拆解与组合语法
│   ├── 07_故事构件库.jsonl
│   ├── 世界观基础设定规范.md
│   ├── 外部编剧工作流.md  编剧工作流的本地适配
│   ├── 外部编剧工作流案例.md  story-bible.md 模板与各阶段工作单
│   ├── 模板_AI电影级剧本开发工作流.md
│   ├── 模板_阶段门控剧本开发.md
│   ├── 独立使用与交接.md  故事与剧本的独立使用与交接
│   ├── 语言表达.md  故事与剧本的语言表达
│   └── 高质量AI剧本开发计划.md  高质量 AI 剧本开发计划
├── scripts/  执行、检索或校验工具
│   ├── render_delivery_html.py
│   ├── story_atoms.py
│   └── story_component_library.py
├── skills/  内部专业，每项有自己的入口与验收
│   ├── laohu-american-case-studies/  老胡美国电影剧作案例
│   │   ├── agents/  宿主识别元数据
│   │   │   └── openai.yaml
│   │   ├── SKILL.md  触发、主责、流程与方法路由
│   │   └── reference.md  美国电影剧作案例：补充范例与分析表
│   ├── laohu-character-conflict/  老胡人物与冲突
│   │   ├── agents/  宿主识别元数据
│   │   │   └── openai.yaml
│   │   ├── references/  按需读取的专业方法、案例与合同
│   │   │   └── 人物行动与连续性.md
│   │   ├── SKILL.md  触发、主责、流程与方法路由
│   │   └── reference.md  人物与冲突：原型表、心理学检查清单与分析模板
│   ├── laohu-chekhov-dramaturgy/  老胡契诃夫戏剧法
│   │   ├── agents/  宿主识别元数据
│   │   │   └── openai.yaml
│   │   ├── SKILL.md  触发、主责、流程与方法路由
│   │   └── reference.md  契诃夫七部多幕剧：逐幕结构表与原文范例
│   ├── laohu-chinese-series-practice/  老胡国产剧创作与生产衔接
│   │   ├── SKILL.md  触发、主责、流程与方法路由
│   │   ├── reference-cases.md  国产剧实务（三）：张巍六个改编案例对照
│   │   ├── reference-rules.md  国产剧实务（四）：片段索引与内容红线
│   │   ├── reference-samples.md  国产剧实务（二）：格式样本、策划样本、场面表与境遇清单
│   │   └── reference.md  国产剧实务：格式样本、改编案例表、术语字典与制片链文件
│   ├── laohu-dialogue/  老胡对白创作
│   │   ├── agents/  宿主识别元数据
│   │   │   └── openai.yaml
│   │   ├── references/  按需读取的专业方法、案例与合同
│   │   │   ├── 喜剧场面与传播.md
│   │   │   └── 本地对白与表演补充.md  对白与表演方法
│   │   ├── SKILL.md  触发、主责、流程与方法路由
│   │   └── reference.md  对白：七个场景节拍分析范例、改写对照与唱词范例
│   ├── laohu-format-adaptation/  老胡格式、流程与改编
│   │   ├── agents/  宿主识别元数据
│   │   │   └── openai.yaml
│   │   ├── references/  按需读取的专业方法、案例与合同
│   │   │   └── 镜头化剧本与连续性.md  体量、形态、编号与连续性
│   │   ├── SKILL.md  触发、主责、流程与方法路由
│   │   └── reference.md  格式·流程·改编：模板、符号表与范例
│   ├── laohu-industry-business/  老胡编剧行业与生意经
│   │   ├── agents/  宿主识别元数据
│   │   │   └── openai.yaml
│   │   ├── SKILL.md  触发、主责、流程与方法路由
│   │   └── reference.md  行业与生意经：清单、样本与术语
│   ├── laohu-japanese-screenwriting/  老胡日本编剧方法
│   │   ├── agents/  宿主识别元数据
│   │   │   └── openai.yaml
│   │   ├── SKILL.md  触发、主责、流程与方法路由
│   │   └── reference.md  日本编剧方法：情节构想范例与工作单
│   ├── laohu-korean-french-screenwriting/  老胡韩国与法国编剧方法
│   │   ├── agents/  宿主识别元数据
│   │   │   └── openai.yaml
│   │   └── SKILL.md  触发、主责、流程与方法路由
│   ├── laohu-ozu-screenplay-style/  老胡小津剧本写法
│   │   ├── agents/  宿主识别元数据
│   │   │   └── openai.yaml
│   │   ├── SKILL.md  触发、主责、流程与方法路由
│   │   └── reference.md  小津六部剧本：逐场结构表与原文范例
│   ├── laohu-premise-theme/  老胡前提与主题
│   │   ├── agents/  宿主识别元数据
│   │   │   └── openai.yaml
│   │   ├── references/  按需读取的专业方法、案例与合同
│   │   │   └── 创意开发与主题检验.md
│   │   ├── SKILL.md  触发、主责、流程与方法路由
│   │   └── reference.md  前提·主题：工作单与范例库
│   ├── laohu-scene-craft/  老胡场景与段落
│   │   ├── agents/  宿主识别元数据
│   │   │   └── openai.yaml
│   │   ├── references/  按需读取的专业方法、案例与合同
│   │   │   └── 场面推进与苦难叙事.md
│   │   ├── SKILL.md  触发、主责、流程与方法路由
│   │   └── reference.md  场景与段落：分析范例与工具表
│   ├── laohu-series-case-studies/  老胡剧集案例研究
│   │   ├── SKILL.md  触发、主责、流程与方法路由
│   │   ├── reference-asia.md  剧集案例库（三）：坂元裕二与卢熙京
│   │   ├── reference-pilots.md  剧集案例库（二）：方法书里的 pilot 节拍表与 beat sheet 实物
│   │   └── reference.md  剧集案例库：逐集结构表、节拍表与原文范例
│   ├── laohu-series-engine-bible/  老胡剧集引擎与开发文档
│   │   ├── SKILL.md  触发、主责、流程与方法路由
│   │   ├── reference-documents.md  剧集引擎与 bible（二）：文档模板字段表
│   │   ├── reference-samples.md  剧集引擎与 bible（三）：填好的样例
│   │   └── reference.md  剧集引擎与 bible（一）：引擎拆解、剧集类型与人物网
│   ├── laohu-series-structure/  老胡剧集单集与季结构
│   │   ├── SKILL.md  触发、主责、流程与方法路由
│   │   └── reference.md  剧集单集与季结构：完整节拍表、页码表与逐集数据
│   ├── laohu-sitcom-comedy/  老胡情景喜剧与半小时喜剧
│   │   ├── SKILL.md  触发、主责、流程与方法路由
│   │   └── reference.md  半小时喜剧：格式规范、笑点技法目录与结构模板
│   ├── laohu-story-material/  老胡故事素材库
│   │   ├── agents/  宿主识别元数据
│   │   │   └── openai.yaml
│   │   ├── references/  按需读取的专业方法、案例与合同
│   │   │   └── 01_原子记录与渐进检索合同.md  原子记录与渐进检索合同
│   │   ├── scripts/  执行、检索或校验工具
│   │   │   ├── story_material_db.py
│   │   │   └── story_material_store.py
│   │   └── SKILL.md  触发、主责、流程与方法路由
│   ├── laohu-story-structure/  老胡故事结构
│   │   ├── agents/  宿主识别元数据
│   │   │   └── openai.yaml
│   │   ├── references/  按需读取的专业方法、案例与合同
│   │   │   └── 结构尺度与高潮设计.md
│   │   ├── SKILL.md  触发、主责、流程与方法路由
│   │   └── reference.md  故事结构：对照表、范例与逐片情节点
│   ├── laohu-succession-series-writing/  老胡权力群像剧写法
│   │   ├── SKILL.md  触发、主责、流程与方法路由
│   │   └── reference.md  《继承之战》四季 39 集：逐集结构表、季弧表、set piece 对照表与原文范例
│   ├── laohu-video-segmentation/  视频分段规划
│   │   ├── references/  按需读取的专业方法、案例与合同
│   │   │   ├── 执行卡与行为校验.md  分段执行卡：填写样例与边界比较
│   │   │   └── 短剧剧本到视频提示词编号与时长规则.md  剧本、分段与视频编号交接
│   │   ├── scripts/  执行、检索或校验工具
│   │   │   └── validate_plan.py
│   │   └── SKILL.md  触发、主责、流程与方法路由
│   └── laohu-writers-room/  老胡编剧室与制作修订
│       ├── SKILL.md  触发、主责、流程与方法路由
│       └── reference.md  编剧室：日程表、文档实物与一手访谈材料
└── SKILL.md  触发、主责、流程与方法路由
```

</details>

<details>
<summary>图片与视觉资产：laohu-image-creation（含61个Skill入口）</summary>

图片、人物、服装、妆造、场景、道具、稳定资产与封面。

```text
laohu-image-creation/
├── agents/  宿主识别元数据
│   └── openai.yaml
├── references/  按需读取的专业方法、案例与合同
│   ├── 内置方法/  本包实际保存的跨专业方法，维护时同步
│   │   ├── laohu-ai-visual/
│   │   │   ├── references/  按需读取的专业方法、案例与合同
│   │   │   │   ├── 00_核心规则手册.md  老胡 AI 视觉能力地图
│   │   │   │   ├── 模板_作品项目启动包.md
│   │   │   │   ├── 独立使用与交接.md  项目总控的独立使用与交接
│   │   │   │   └── 语言表达.md  项目总控的语言表达
│   │   │   ├── scripts/  执行、检索或校验工具
│   │   │   │   ├── check_laohu_skills.sh
│   │   │   │   └── create_work_project.sh
│   │   │   └── skills/  内部专业，每项有自己的入口与验收
│   │   │       ├── laohu-capability-evolution/
│   │   │       │   └── references/  按需读取的专业方法、案例与合同
│   │   │       │       ├── 01_证据吸收与根因判断.md  证据吸收与根因判断
│   │   │       │       ├── 02_四层能力重编译.md  四层能力重编译
│   │   │       │       ├── 03_保真迁移回归与回退.md  保真迁移、回归与回退
│   │   │       │       ├── 04_进化记忆与能力生长.md  进化记忆与能力生长
│   │   │       │       ├── laohu_skills能力加厚规范.md  laohu Skills 能力生长规范（兼容入口）
│   │   │       │       └── 助手执行失败经验与防复发规则.md
│   │   │       ├── laohu-creative-development/
│   │   │       │   ├── references/  按需读取的专业方法、案例与合同
│   │   │       │   │   └── 创意机制与候选裁决.md
│   │   │       │   └── 专业方法.md  老胡创意开发
│   │   │       └── laohu-director/
│   │   │           └── references/  按需读取的专业方法、案例与合同
│   │   │               └── 导演级影视创作总控流程.md
│   │   ├── laohu-language-mode/
│   │   │   └── references/  按需读取的专业方法、案例与合同
│   │   │       ├── 01_模式判定与块级切换.md  模式判定与块级切换
│   │   │       ├── 02_用户沟通与制作说明.md  用户沟通与制作说明
│   │   │       ├── 03_剧本文本块语言.md  剧本文本块语言
│   │   │       ├── 04_资产图片视频与声音提示词桥接.md  资产、图片、视频与声音提示词桥接
│   │   │       └── 05_有效信息与冗余裁决.md  有效信息与冗余裁决
│   │   ├── laohu-script-writer/
│   │   │   ├── references/  按需读取的专业方法、案例与合同
│   │   │   │   ├── 故事原子/  完整应用原子与检索目录，逐条内容见专门目录
│   │   │   │   ├── 06_故事构件拆解与组合语法.md  故事构件拆解与组合语法
│   │   │   │   ├── 07_故事构件库.jsonl
│   │   │   │   ├── 模板_AI电影级剧本开发工作流.md
│   │   │   │   ├── 模板_阶段门控剧本开发.md
│   │   │   │   └── 语言表达.md  故事与剧本的语言表达
│   │   │   ├── scripts/  执行、检索或校验工具
│   │   │   │   ├── story_atoms.py
│   │   │   │   └── story_component_library.py
│   │   │   └── skills/  内部专业，每项有自己的入口与验收
│   │   │       ├── laohu-story-material/
│   │   │       │   ├── references/  按需读取的专业方法、案例与合同
│   │   │       │   │   └── 01_原子记录与渐进检索合同.md  原子记录与渐进检索合同
│   │   │       │   └── scripts/  执行、检索或校验工具
│   │   │       │       ├── story_material_db.py
│   │   │       │       └── story_material_store.py
│   │   │       └── laohu-video-segmentation/
│   │   │           ├── references/  按需读取的专业方法、案例与合同
│   │   │           │   ├── 执行卡与行为校验.md  分段执行卡：填写样例与边界比较
│   │   │           │   └── 短剧剧本到视频提示词编号与时长规则.md  剧本、分段与视频编号交接
│   │   │           ├── scripts/  执行、检索或校验工具
│   │   │           │   └── validate_plan.py
│   │   │           └── 专业方法.md  视频分段规划
│   │   ├── laohu-video-prompt/
│   │   │   ├── references/  按需读取的专业方法、案例与合同
│   │   │   │   ├── 交接与验收.md  视频提示词：交接与验收合同
│   │   │   │   ├── 基础运动与专项路由.md  视频基础必读与专项按需调用
│   │   │   │   ├── 模板_视频生成质量检查清单.md
│   │   │   │   ├── 短剧短片分镜生成字段规范.md
│   │   │   │   ├── 语言表达.md  视频制作与提示词的语言表达
│   │   │   │   ├── 镜头空间与连续性.md  段内摄影与空间连续性
│   │   │   │   └── 高质量AI视频提示词开发计划.md  高质量 AI 视频提示词开发计划
│   │   │   ├── scripts/  执行、检索或校验工具
│   │   │   │   └── count_video_prompt_chars.sh
│   │   │   └── skills/  内部专业，每项有自己的入口与验收
│   │   │       ├── laohu-action-design/
│   │   │       │   └── references/  按需读取的专业方法、案例与合同
│   │   │       │       └── 专业方法与案例.md  动作设计：专业方法与案例
│   │   │       ├── laohu-audio-design/
│   │   │       │   └── references/  按需读取的专业方法、案例与合同
│   │   │       │       └── 声音提示词规范.md
│   │   │       ├── laohu-audiovisual/
│   │   │       │   └── references/  按需读取的专业方法、案例与合同
│   │   │       │       └── 专业方法与案例.md  声画关系：专业方法与案例
│   │   │       ├── laohu-camera-movement/
│   │   │       │   └── references/  按需读取的专业方法、案例与合同
│   │   │       │       └── 专业方法与案例.md  运镜：专业方法与案例
│   │   │       ├── laohu-editing/
│   │   │       │   └── references/  按需读取的专业方法、案例与合同
│   │   │       │       └── 模板_多镜头后期拼接.md  模板：多镜头后期拼接
│   │   │       ├── laohu-motion-design/
│   │   │       │   ├── references/  按需读取的专业方法、案例与合同
│   │   │       │   │   └── 专业方法与案例.md  动态图形设计：专业方法与案例
│   │   │       │   └── skills/  内部专业，每项有自己的入口与验收
│   │   │       │       ├── laohu-editorial-explainer/
│   │   │       │       │   ├── references/  按需读取的专业方法、案例与合同
│   │   │       │       │   │   └── 证据编排与动态解释.md  编辑型知识讲解的证据编排
│   │   │       │       │   └── 专业方法.md  老胡编辑型知识动画
│   │   │       │       └── laohu-stickman-explainer/
│   │   │       │           ├── references/  按需读取的专业方法、案例与合同
│   │   │       │           │   ├── upstream/
│   │   │       │           │   │   ├── references/  按需读取的专业方法、案例与合同
│   │   │       │           │   │   │   ├── examples.md  Complete Example
│   │   │       │           │   │   │   ├── omni-flash-prompt-contract.md  Omni Flash Production Prompt Contract
│   │   │       │           │   │   │   └── storyboard-template.md  Director's Proposal Contract
│   │   │       │           │   │   └── 原始方法.md  Directing Stickman Videos
│   │   │       │           │   └── 专项方法与适配.md  火柴人讲解：专业方法与本地适配
│   │   │       │           └── 专业方法.md  老胡火柴人知识动画
│   │   │       ├── laohu-performance/
│   │   │       │   └── references/  按需读取的专业方法、案例与合同
│   │   │       │       ├── 专业方法与案例.md  表演：专业方法与案例
│   │   │       │       ├── 人物表情与肢体动作词典.md
│   │   │       │       ├── 人物表演提示词规范.md
│   │   │       │       └── 模板_人物表演_情绪时间轴.md  模板：人物表演_情绪时间轴
│   │   │       ├── laohu-vfx/
│   │   │       │   └── references/  按需读取的专业方法、案例与合同
│   │   │       │       └── 专业方法与案例.md  视觉特效 VFX：专业方法与案例
│   │   │       └── laohu-video-compilation/
│   │   │           └── references/  按需读取的专业方法、案例与合同
│   │   │               ├── Seedance2视频提示词书写规范.md  Seedance 2 视频提示词书写规范
│   │   │               ├── 专业方法与案例.md  视频提示词编译：专业方法与案例
│   │   │               ├── 多模型AI视频提示词通用规范.md  多模型 AI 视频提示词通用规范
│   │   │               └── 模板_视频提示词_基础设定氛围画面内容.md  模板：视频提示词_基础设定氛围画面内容
│   │   ├── scripts/  执行、检索或校验工具
│   │   │   └── validate_delivery_dependencies.py
│   │   ├── LICENSE.md  分层授权
│   │   └── README.md  老胡 Skills 目录与使用说明
│   ├── 语言模式/  随包携带的完整语言方法
│   │   ├── 01_模式判定与块级切换.md  模式判定与块级切换
│   │   ├── 02_用户沟通与制作说明.md  用户沟通与制作说明
│   │   ├── 03_剧本文本块语言.md  剧本文本块语言
│   │   ├── 04_资产图片视频与声音提示词桥接.md  资产、图片、视频与声音提示词桥接
│   │   └── 05_有效信息与冗余裁决.md  有效信息与冗余裁决
│   ├── F人物主视觉编译.md  资产规格与编译
│   ├── 图片与资产生产合同.md
│   ├── 图片验收与封面交接.md  图片生成验收与封面资产交接
│   ├── 独立使用与交接.md  图片与视觉资产的独立使用与交接
│   ├── 语言表达.md  图片与视觉资产的语言表达
│   └── 高质量AI图片开发计划.md  高质量 AI 图片开发计划
├── scripts/  执行、检索或校验工具
│   └── render_delivery_html.py
├── skills/  内部专业，每项有自己的入口与验收
│   ├── laohu-art-direction/  老胡美术风格设计
│   │   ├── agents/  宿主识别元数据
│   │   │   └── openai.yaml
│   │   ├── references/  按需读取的专业方法、案例与合同
│   │   │   ├── 01_题材视觉证据与相邻类型边界.md  题材视觉证据与相邻类型边界
│   │   │   ├── 02_风格先验与结果图美术锚点.md  风格先验与结果图美术锚点
│   │   │   ├── 03_参考图证据与视觉形式转译.md  参考图证据与视觉形式转译
│   │   │   └── 画面氛围与画质规范.md  画面风格与画质规范
│   │   ├── skills/  内部专业，每项有自己的入口与验收
│   │   │   ├── laohu-color-design/  老胡色彩设计
│   │   │   │   ├── agents/  宿主识别元数据
│   │   │   │   │   └── openai.yaml
│   │   │   │   ├── references/  按需读取的专业方法、案例与合同
│   │   │   │   │   └── 专业判断与编译.md  色彩设计的判断与编译
│   │   │   │   └── SKILL.md  触发、主责、流程与方法路由
│   │   │   ├── laohu-compositing/  老胡合成
│   │   │   │   ├── agents/  宿主识别元数据
│   │   │   │   │   └── openai.yaml
│   │   │   │   ├── references/  按需读取的专业方法、案例与合同
│   │   │   │   │   └── 专业判断与编译.md  合成的判断与编译
│   │   │   │   └── SKILL.md  触发、主责、流程与方法路由
│   │   │   ├── laohu-composition/  老胡构图
│   │   │   │   ├── agents/  宿主识别元数据
│   │   │   │   │   └── openai.yaml
│   │   │   │   ├── references/  按需读取的专业方法、案例与合同
│   │   │   │   │   └── 专业判断与编译.md  构图的判断与编译
│   │   │   │   └── SKILL.md  触发、主责、流程与方法路由
│   │   │   ├── laohu-illustration/  老胡插画
│   │   │   │   ├── agents/  宿主识别元数据
│   │   │   │   │   └── openai.yaml
│   │   │   │   ├── references/  按需读取的专业方法、案例与合同
│   │   │   │   │   └── 专业判断与编译.md  插画的判断与编译
│   │   │   │   └── SKILL.md  触发、主责、流程与方法路由
│   │   │   ├── laohu-information-design/  老胡信息设计
│   │   │   │   ├── agents/  宿主识别元数据
│   │   │   │   │   └── openai.yaml
│   │   │   │   ├── references/  按需读取的专业方法、案例与合同
│   │   │   │   │   └── 专业判断与编译.md  信息设计的判断与编译
│   │   │   │   └── SKILL.md  触发、主责、流程与方法路由
│   │   │   ├── laohu-layout-design/  老胡版式设计
│   │   │   │   ├── agents/  宿主识别元数据
│   │   │   │   │   └── openai.yaml
│   │   │   │   ├── references/  按需读取的专业方法、案例与合同
│   │   │   │   │   ├── 02_日本版面与文字空间机制.md  日本版面与文字空间机制
│   │   │   │   │   └── 专业判断与编译.md  版式设计的判断与编译
│   │   │   │   └── SKILL.md  触发、主责、流程与方法路由
│   │   │   ├── laohu-light-shadow/  老胡光影设计
│   │   │   │   ├── agents/  宿主识别元数据
│   │   │   │   │   └── openai.yaml
│   │   │   │   ├── references/  按需读取的专业方法、案例与合同
│   │   │   │   │   ├── 04_叙事灯光与光源因果.md  叙事灯光与光源因果
│   │   │   │   │   ├── 专业判断与编译.md  光影设计的判断与编译
│   │   │   │   │   └── 作品级光影判断.md
│   │   │   │   └── SKILL.md  触发、主责、流程与方法路由
│   │   │   ├── laohu-material-design/  老胡材质设计
│   │   │   │   ├── agents/  宿主识别元数据
│   │   │   │   │   └── openai.yaml
│   │   │   │   ├── references/  按需读取的专业方法、案例与合同
│   │   │   │   │   └── 专业判断与编译.md  材质设计的判断与编译
│   │   │   │   └── SKILL.md  触发、主责、流程与方法路由
│   │   │   ├── laohu-photography/  老胡摄影
│   │   │   │   ├── agents/  宿主识别元数据
│   │   │   │   │   └── openai.yaml
│   │   │   │   ├── references/  按需读取的专业方法、案例与合同
│   │   │   │   │   ├── 专业判断与编译.md  摄影的判断与编译
│   │   │   │   │   └── 镜头语言词典.md
│   │   │   │   └── SKILL.md  触发、主责、流程与方法路由
│   │   │   └── laohu-typography/  老胡字体与文字排印
│   │   │       ├── agents/  宿主识别元数据
│   │   │       │   └── openai.yaml
│   │   │       ├── references/  按需读取的专业方法、案例与合同
│   │   │       │   └── 专业判断与编译.md  字体与文字排印的判断与编译
│   │   │       └── SKILL.md  触发、主责、流程与方法路由
│   │   └── SKILL.md  触发、主责、流程与方法路由
│   ├── laohu-character-design/  老胡人物设计
│   │   ├── agents/  宿主识别元数据
│   │   │   └── openai.yaml
│   │   ├── skills/  内部专业，每项有自己的入口与验收
│   │   │   ├── laohu-body-design/  老胡人体与体态设计
│   │   │   │   ├── agents/  宿主识别元数据
│   │   │   │   │   └── openai.yaml
│   │   │   │   ├── references/  按需读取的专业方法、案例与合同
│   │   │   │   │   └── 专业方法.md  人体与体态设计专业方法
│   │   │   │   └── SKILL.md  触发、主责、流程与方法路由
│   │   │   ├── laohu-casting/  老胡选角
│   │   │   │   ├── agents/  宿主识别元数据
│   │   │   │   │   └── openai.yaml
│   │   │   │   ├── references/  按需读取的专业方法、案例与合同
│   │   │   │   │   └── 专业方法.md  选角专业方法
│   │   │   │   └── SKILL.md  触发、主责、流程与方法路由
│   │   │   ├── laohu-creature-design/  老胡生物设计
│   │   │   │   ├── agents/  宿主识别元数据
│   │   │   │   │   └── openai.yaml
│   │   │   │   ├── references/  按需读取的专业方法、案例与合同
│   │   │   │   │   └── 专业方法.md  生物设计专业方法
│   │   │   │   └── SKILL.md  触发、主责、流程与方法路由
│   │   │   ├── laohu-ensemble-design/  老胡群像设计
│   │   │   │   ├── agents/  宿主识别元数据
│   │   │   │   │   └── openai.yaml
│   │   │   │   ├── references/  按需读取的专业方法、案例与合同
│   │   │   │   │   └── 专业方法.md  群像设计专业方法
│   │   │   │   └── SKILL.md  触发、主责、流程与方法路由
│   │   │   └── laohu-face-design/  老胡面部设计
│   │   │       ├── agents/  宿主识别元数据
│   │   │       │   └── openai.yaml
│   │   │       ├── references/  按需读取的专业方法、案例与合同
│   │   │       │   ├── NUYOAH_LICENSE
│   │   │       │   ├── 专业方法.md  面部设计专业方法
│   │   │       │   ├── 结构与妆容候选词表.md
│   │   │       │   └── 结构兼容与阵容方法.md  结构选择、兼容与阵容
│   │   │       └── SKILL.md  触发、主责、流程与方法路由
│   │   └── SKILL.md  触发、主责、流程与方法路由
│   ├── laohu-costume-design/  老胡服装设计
│   │   ├── agents/  宿主识别元数据
│   │   │   └── openai.yaml
│   │   ├── skills/  内部专业，每项有自己的入口与验收
│   │   │   ├── laohu-accessory-design/  老胡配饰设计
│   │   │   │   ├── agents/  宿主识别元数据
│   │   │   │   │   └── openai.yaml
│   │   │   │   ├── references/  按需读取的专业方法、案例与合同
│   │   │   │   │   └── 专业方法.md  配饰设计专业方法
│   │   │   │   └── SKILL.md  触发、主责、流程与方法路由
│   │   │   ├── laohu-costume-continuity/  老胡戏服连续性
│   │   │   │   ├── agents/  宿主识别元数据
│   │   │   │   │   └── openai.yaml
│   │   │   │   ├── references/  按需读取的专业方法、案例与合同
│   │   │   │   │   └── 专业方法.md  戏服连续性专业方法
│   │   │   │   └── SKILL.md  触发、主责、流程与方法路由
│   │   │   ├── laohu-costume-ornament/  老胡纹样与装饰
│   │   │   │   ├── agents/  宿主识别元数据
│   │   │   │   │   └── openai.yaml
│   │   │   │   ├── references/  按需读取的专业方法、案例与合同
│   │   │   │   │   └── 专业方法.md  纹样与装饰专业方法
│   │   │   │   └── SKILL.md  触发、主责、流程与方法路由
│   │   │   ├── laohu-costume-research/  老胡服饰考据
│   │   │   │   ├── agents/  宿主识别元数据
│   │   │   │   │   └── openai.yaml
│   │   │   │   ├── references/  按需读取的专业方法、案例与合同
│   │   │   │   │   └── 专业方法.md  服饰考据专业方法
│   │   │   │   └── SKILL.md  触发、主责、流程与方法路由
│   │   │   ├── laohu-costume-silhouette/  老胡服装造型
│   │   │   │   ├── agents/  宿主识别元数据
│   │   │   │   │   └── openai.yaml
│   │   │   │   ├── references/  按需读取的专业方法、案例与合同
│   │   │   │   │   └── 专业方法.md  服装造型专业方法
│   │   │   │   └── SKILL.md  触发、主责、流程与方法路由
│   │   │   ├── laohu-garment-structure/  老胡服装结构
│   │   │   │   ├── agents/  宿主识别元数据
│   │   │   │   │   └── openai.yaml
│   │   │   │   ├── references/  按需读取的专业方法、案例与合同
│   │   │   │   │   └── 专业方法.md  服装结构专业方法
│   │   │   │   └── SKILL.md  触发、主责、流程与方法路由
│   │   │   └── laohu-textile-design/  老胡面料设计
│   │   │       ├── agents/  宿主识别元数据
│   │   │       │   └── openai.yaml
│   │   │       ├── references/  按需读取的专业方法、案例与合同
│   │   │       │   └── 专业方法.md  面料设计专业方法
│   │   │       └── SKILL.md  触发、主责、流程与方法路由
│   │   └── SKILL.md  触发、主责、流程与方法路由
│   ├── laohu-cover-design/  老胡封面与海报
│   │   ├── agents/  宿主识别元数据
│   │   │   └── openai.yaml
│   │   ├── references/  按需读取的专业方法、案例与合同
│   │   │   └── 模板_封面海报创作执行单.md  封面海报创作执行单
│   │   ├── skills/  内部专业，每项有自己的入口与验收
│   │   │   ├── laohu-cover-concept/  老胡封面概念
│   │   │   │   ├── agents/  宿主识别元数据
│   │   │   │   │   └── openai.yaml
│   │   │   │   ├── references/  按需读取的专业方法、案例与合同
│   │   │   │   │   ├── 01_文化素材事实与视觉基因转译.md  文化素材事实与视觉基因转译
│   │   │   │   │   ├── 专业判断与编译.md  封面概念的判断与编译
│   │   │   │   │   └── 封面专业合同.md
│   │   │   │   └── SKILL.md  触发、主责、流程与方法路由
│   │   │   ├── laohu-cover-copy/  老胡封面文案
│   │   │   │   ├── agents/  宿主识别元数据
│   │   │   │   │   └── openai.yaml
│   │   │   │   ├── references/  按需读取的专业方法、案例与合同
│   │   │   │   │   ├── 专业判断与编译.md  封面文案的判断与编译
│   │   │   │   │   └── 封面专业合同.md
│   │   │   │   └── SKILL.md  触发、主责、流程与方法路由
│   │   │   ├── laohu-cover-layout/  老胡封面版式
│   │   │   │   ├── agents/  宿主识别元数据
│   │   │   │   │   └── openai.yaml
│   │   │   │   ├── references/  按需读取的专业方法、案例与合同
│   │   │   │   │   ├── 专业判断与编译.md  封面版式的判断与编译
│   │   │   │   │   └── 封面专业合同.md
│   │   │   │   └── SKILL.md  触发、主责、流程与方法路由
│   │   │   └── laohu-thumbnail/  老胡缩略图适配
│   │   │       ├── agents/  宿主识别元数据
│   │   │       │   └── openai.yaml
│   │   │       ├── references/  按需读取的专业方法、案例与合同
│   │   │       │   ├── 专业判断与编译.md  缩略图适配的判断与编译
│   │   │       │   └── 封面专业合同.md
│   │   │       └── SKILL.md  触发、主责、流程与方法路由
│   │   └── SKILL.md  触发、主责、流程与方法路由
│   ├── laohu-image-editing/  老胡图片编辑
│   │   ├── agents/  宿主识别元数据
│   │   │   └── openai.yaml
│   │   ├── references/  按需读取的专业方法、案例与合同
│   │   │   ├── 专业判断与编译.md  图片编辑的判断与编译
│   │   │   ├── 图片与资产生产合同.md
│   │   │   └── 局部编辑三权分离.md
│   │   └── SKILL.md  触发、主责、流程与方法路由
│   ├── laohu-image-prompt/  老胡图片提示词编译
│   │   ├── agents/  宿主识别元数据
│   │   │   └── openai.yaml
│   │   ├── references/  按需读取的专业方法、案例与合同
│   │   │   ├── 专业判断与编译.md  图片提示词编译的判断与编译
│   │   │   ├── 图片与资产生产合同.md
│   │   │   ├── 模板_通用负面提示词.md  模板：通用质量边界
│   │   │   ├── 视觉生成模型注意力与提示词编译参考.md
│   │   │   └── 风格继承与图片编译.md  风格决策与图片提示词
│   │   └── SKILL.md  触发、主责、流程与方法路由
│   ├── laohu-makeup-design/  老胡妆发设计
│   │   ├── agents/  宿主识别元数据
│   │   │   └── openai.yaml
│   │   ├── skills/  内部专业，每项有自己的入口与验收
│   │   │   ├── laohu-groom-design/  老胡毛发设计
│   │   │   │   ├── agents/  宿主识别元数据
│   │   │   │   │   └── openai.yaml
│   │   │   │   ├── references/  按需读取的专业方法、案例与合同
│   │   │   │   │   └── 专业方法.md  毛发设计专业方法
│   │   │   │   └── SKILL.md  触发、主责、流程与方法路由
│   │   │   ├── laohu-hair-design/  老胡发型设计
│   │   │   │   ├── agents/  宿主识别元数据
│   │   │   │   │   └── openai.yaml
│   │   │   │   ├── references/  按需读取的专业方法、案例与合同
│   │   │   │   │   └── 专业方法.md  发型设计专业方法
│   │   │   │   └── SKILL.md  触发、主责、流程与方法路由
│   │   │   ├── laohu-makeup/  老胡妆容设计
│   │   │   │   ├── agents/  宿主识别元数据
│   │   │   │   │   └── openai.yaml
│   │   │   │   ├── references/  按需读取的专业方法、案例与合同
│   │   │   │   │   ├── 专业方法.md  妆容设计专业方法
│   │   │   │   │   └── 妆容条件适配.md  妆容与人物适配
│   │   │   │   └── SKILL.md  触发、主责、流程与方法路由
│   │   │   └── laohu-prosthetic-makeup/  老胡特效化妆
│   │   │       ├── agents/  宿主识别元数据
│   │   │       │   └── openai.yaml
│   │   │       ├── references/  按需读取的专业方法、案例与合同
│   │   │       │   └── 专业方法.md  特效化妆专业方法
│   │   │       └── SKILL.md  触发、主责、流程与方法路由
│   │   └── SKILL.md  触发、主责、流程与方法路由
│   ├── laohu-portrait/  老胡人像摄影
│   │   ├── agents/  宿主识别元数据
│   │   │   └── openai.yaml
│   │   ├── references/  按需读取的专业方法、案例与合同
│   │   │   ├── 06_人物生命感与现场摄影关系.md  人物生命感与现场摄影关系
│   │   │   └── 专业判断与编译.md  人像摄影的判断与编译
│   │   └── SKILL.md  触发、主责、流程与方法路由
│   ├── laohu-prop-design/  老胡道具设计
│   │   ├── agents/  宿主识别元数据
│   │   │   └── openai.yaml
│   │   ├── skills/  内部专业，每项有自己的入口与验收
│   │   │   ├── laohu-hand-props/  老胡手持道具设计
│   │   │   │   ├── agents/  宿主识别元数据
│   │   │   │   │   └── openai.yaml
│   │   │   │   ├── references/  按需读取的专业方法、案例与合同
│   │   │   │   │   └── 专业方法.md  手持道具设计专业方法
│   │   │   │   └── SKILL.md  触发、主责、流程与方法路由
│   │   │   ├── laohu-mechanical-design/  老胡机械设计
│   │   │   │   ├── agents/  宿主识别元数据
│   │   │   │   │   └── openai.yaml
│   │   │   │   ├── references/  按需读取的专业方法、案例与合同
│   │   │   │   │   └── 专业方法.md  机械设计专业方法
│   │   │   │   └── SKILL.md  触发、主责、流程与方法路由
│   │   │   ├── laohu-product-design/  老胡产品设计
│   │   │   │   ├── agents/  宿主识别元数据
│   │   │   │   │   └── openai.yaml
│   │   │   │   ├── references/  按需读取的专业方法、案例与合同
│   │   │   │   │   └── 专业方法.md  产品设计专业方法
│   │   │   │   └── SKILL.md  触发、主责、流程与方法路由
│   │   │   └── laohu-vehicle-design/  老胡载具设计
│   │   │       ├── agents/  宿主识别元数据
│   │   │       │   └── openai.yaml
│   │   │       ├── references/  按需读取的专业方法、案例与合同
│   │   │       │   └── 专业方法.md  载具设计专业方法
│   │   │       └── SKILL.md  触发、主责、流程与方法路由
│   │   └── SKILL.md  触发、主责、流程与方法路由
│   ├── laohu-set-design/  老胡场景与布景设计
│   │   ├── agents/  宿主识别元数据
│   │   │   └── openai.yaml
│   │   ├── skills/  内部专业，每项有自己的入口与验收
│   │   │   ├── laohu-architecture-design/  老胡建筑设计
│   │   │   │   ├── agents/  宿主识别元数据
│   │   │   │   │   └── openai.yaml
│   │   │   │   ├── references/  按需读取的专业方法、案例与合同
│   │   │   │   │   └── 专业方法.md  建筑设计专业方法
│   │   │   │   └── SKILL.md  触发、主责、流程与方法路由
│   │   │   ├── laohu-environment-research/  老胡场景考据
│   │   │   │   ├── agents/  宿主识别元数据
│   │   │   │   │   └── openai.yaml
│   │   │   │   ├── references/  按需读取的专业方法、案例与合同
│   │   │   │   │   └── 专业方法.md  场景考据专业方法
│   │   │   │   └── SKILL.md  触发、主责、流程与方法路由
│   │   │   ├── laohu-interior-design/  老胡室内设计
│   │   │   │   ├── agents/  宿主识别元数据
│   │   │   │   │   └── openai.yaml
│   │   │   │   ├── references/  按需读取的专业方法、案例与合同
│   │   │   │   │   └── 专业方法.md  室内设计专业方法
│   │   │   │   └── SKILL.md  触发、主责、流程与方法路由
│   │   │   ├── laohu-landscape-design/  老胡景观设计
│   │   │   │   ├── agents/  宿主识别元数据
│   │   │   │   │   └── openai.yaml
│   │   │   │   ├── references/  按需读取的专业方法、案例与合同
│   │   │   │   │   └── 专业方法.md  景观设计专业方法
│   │   │   │   └── SKILL.md  触发、主责、流程与方法路由
│   │   │   ├── laohu-set-decoration/  老胡布景陈设
│   │   │   │   ├── agents/  宿主识别元数据
│   │   │   │   │   └── openai.yaml
│   │   │   │   ├── references/  按需读取的专业方法、案例与合同
│   │   │   │   │   └── 专业方法.md  布景陈设专业方法
│   │   │   │   └── SKILL.md  触发、主责、流程与方法路由
│   │   │   └── laohu-spatial-layout/  老胡空间布局
│   │   │       ├── agents/  宿主识别元数据
│   │   │       │   └── openai.yaml
│   │   │       ├── references/  按需读取的专业方法、案例与合同
│   │   │       │   └── 专业方法.md  空间布局专业方法
│   │   │       └── SKILL.md  触发、主责、流程与方法路由
│   │   └── SKILL.md  触发、主责、流程与方法路由
│   ├── laohu-still-life-photography/  老胡静物摄影
│   │   ├── agents/  宿主识别元数据
│   │   │   └── openai.yaml
│   │   ├── references/  按需读取的专业方法、案例与合同
│   │   │   └── 专业判断与编译.md  静物摄影的判断与编译
│   │   └── SKILL.md  触发、主责、流程与方法路由
│   ├── laohu-storyboard/  老胡故事板
│   │   ├── agents/  宿主识别元数据
│   │   │   └── openai.yaml
│   │   ├── references/  按需读取的专业方法、案例与合同
│   │   │   ├── 专业判断与编译.md  故事板的判断与编译
│   │   │   └── 镜头任务拆解.md
│   │   └── SKILL.md  触发、主责、流程与方法路由
│   └── laohu-visual-assets/  老胡视觉资产
│       ├── agents/  宿主识别元数据
│       │   └── openai.yaml
│       ├── references/  按需读取的专业方法、案例与合同
│       │   ├── 00_资料来源与专业校准.md  资料来源与专业校准
│       │   ├── 剧本到AI视觉资产转换规则.md  剧本到 AI 视觉资产转换规则
│       │   ├── 模板_AI图片提示词_资产型通用结构.md
│       │   ├── 模板_角色一致性网格图.md
│       │   ├── 状态帧与下游运动.md  资产状态与接续参考
│       │   └── 身份状态与最小资产.md  资产规格与编译
│       ├── scripts/  执行、检索或校验工具
│       │   ├── test_validate_character_asset_structure.sh
│       │   └── validate_character_asset_structure.py
│       ├── skills/  内部专业，每项有自己的入口与验收
│       │   ├── laohu-body-assets/  老胡素体与阶段资产
│       │   │   ├── agents/  宿主识别元数据
│       │   │   │   └── openai.yaml
│       │   │   ├── references/  按需读取的专业方法、案例与合同
│       │   │   │   ├── 专业判断与编译.md  素体与阶段资产的判断与编译
│       │   │   │   ├── 人物身份与阶段连续性.md  人物、群像、角色状态与所属物
│       │   │   │   └── 资产规格与编译.md
│       │   │   └── SKILL.md  触发、主责、流程与方法路由
│       │   ├── laohu-costume-assets/  老胡服装资产
│       │   │   ├── agents/  宿主识别元数据
│       │   │   │   └── openai.yaml
│       │   │   ├── references/  按需读取的专业方法、案例与合同
│       │   │   │   ├── 专业判断与编译.md  服装资产的判断与编译
│       │   │   │   ├── 服装设计包与资产编译.md  服装设计包到W/M资产编译
│       │   │   │   └── 资产规格与编译.md
│       │   │   └── SKILL.md  触发、主责、流程与方法路由
│       │   ├── laohu-environment-assets/  老胡场景资产
│       │   │   ├── agents/  宿主识别元数据
│       │   │   │   └── openai.yaml
│       │   │   ├── references/  按需读取的专业方法、案例与合同
│       │   │   │   ├── 专业判断与编译.md  场景资产的判断与编译
│       │   │   │   ├── 场景空间与尺度证明.md  场景、道具、空间与镜头任务
│       │   │   │   └── 资产规格与编译.md
│       │   │   └── SKILL.md  触发、主责、流程与方法路由
│       │   ├── laohu-group-assets/  老胡群像资产
│       │   │   ├── agents/  宿主识别元数据
│       │   │   │   └── openai.yaml
│       │   │   ├── references/  按需读取的专业方法、案例与合同
│       │   │   │   ├── 专业判断与编译.md  群像资产的判断与编译
│       │   │   │   └── 群像身份与调度分权.md
│       │   │   └── SKILL.md  触发、主责、流程与方法路由
│       │   ├── laohu-makeup-assets/  老胡妆造资产
│       │   │   ├── agents/  宿主识别元数据
│       │   │   │   └── openai.yaml
│       │   │   ├── references/  按需读取的专业方法、案例与合同
│       │   │   │   ├── 专业判断与编译.md  妆造资产的判断与编译
│       │   │   │   ├── 妆造资产编译.md
│       │   │   │   └── 资产规格与编译.md
│       │   │   └── SKILL.md  触发、主责、流程与方法路由
│       │   ├── laohu-prop-assets/  老胡道具资产
│       │   │   ├── agents/  宿主识别元数据
│       │   │   │   └── openai.yaml
│       │   │   ├── references/  按需读取的专业方法、案例与合同
│       │   │   │   ├── 专业判断与编译.md  道具资产的判断与编译
│       │   │   │   ├── 角色所属物.md
│       │   │   │   ├── 资产规格与编译.md
│       │   │   │   └── 道具与操作结构.md
│       │   │   └── SKILL.md  触发、主责、流程与方法路由
│       │   └── laohu-style-reference/  老胡风格定调资产
│       │       ├── agents/  宿主识别元数据
│       │       │   └── openai.yaml
│       │       ├── references/  按需读取的专业方法、案例与合同
│       │       │   ├── 专业判断与编译.md  风格定调资产的判断与编译
│       │       │   └── 图片与资产生产合同.md
│       │       └── SKILL.md  触发、主责、流程与方法路由
│       └── SKILL.md  触发、主责、流程与方法路由
└── SKILL.md  触发、主责、流程与方法路由
```

</details>

<details>
<summary>视频制作与提示词：laohu-video-prompt（含24个Skill入口）</summary>

段内分镜、表演、声音、剪辑、视频编译与VC提纯。

```text
laohu-video-prompt/
├── agents/  宿主识别元数据
│   └── openai.yaml
├── references/  按需读取的专业方法、案例与合同
│   ├── 内置方法/  本包实际保存的跨专业方法，维护时同步
│   │   ├── laohu-ai-visual/
│   │   │   ├── references/  按需读取的专业方法、案例与合同
│   │   │   │   └── 语言表达.md  项目总控的语言表达
│   │   │   └── skills/  内部专业，每项有自己的入口与验收
│   │   │       └── laohu-generation-review/
│   │   │           └── skills/  内部专业，每项有自己的入口与验收
│   │   │               ├── laohu-audio-review/
│   │   │               │   ├── references/  按需读取的专业方法、案例与合同
│   │   │               │   │   └── 专业方法与案例.md  音频评审：专业方法与案例
│   │   │               │   └── 专业方法.md  老胡音频评审
│   │   │               ├── laohu-edit-review/
│   │   │               │   ├── references/  按需读取的专业方法、案例与合同
│   │   │               │   │   └── 专业方法与案例.md  成片评审：专业方法与案例
│   │   │               │   └── 专业方法.md  老胡成片评审
│   │   │               └── laohu-video-review/
│   │   │                   ├── references/  按需读取的专业方法、案例与合同
│   │   │                   │   └── 专业方法与案例.md  视频评审：专业方法与案例
│   │   │                   └── 专业方法.md  老胡视频评审
│   │   ├── laohu-image-creation/
│   │   │   ├── references/  按需读取的专业方法、案例与合同
│   │   │   │   └── 语言表达.md  图片与视觉资产的语言表达
│   │   │   └── skills/  内部专业，每项有自己的入口与验收
│   │   │       ├── laohu-art-direction/
│   │   │       │   ├── references/  按需读取的专业方法、案例与合同
│   │   │       │   │   ├── 01_题材视觉证据与相邻类型边界.md  题材视觉证据与相邻类型边界
│   │   │       │   │   ├── 02_风格先验与结果图美术锚点.md  风格先验与结果图美术锚点
│   │   │       │   │   ├── 03_参考图证据与视觉形式转译.md  参考图证据与视觉形式转译
│   │   │       │   │   └── 画面氛围与画质规范.md  画面风格与画质规范
│   │   │       │   ├── skills/  内部专业，每项有自己的入口与验收
│   │   │       │   │   ├── laohu-light-shadow/
│   │   │       │   │   │   └── references/  按需读取的专业方法、案例与合同
│   │   │       │   │   │       └── 04_叙事灯光与光源因果.md  叙事灯光与光源因果
│   │   │       │   │   └── laohu-photography/
│   │   │       │   │       └── references/  按需读取的专业方法、案例与合同
│   │   │       │   │           └── 镜头语言词典.md
│   │   │       │   └── 专业方法.md  老胡美术风格设计
│   │   │       ├── laohu-image-prompt/
│   │   │       │   └── references/  按需读取的专业方法、案例与合同
│   │   │       │       └── 视觉生成模型注意力与提示词编译参考.md
│   │   │       ├── laohu-portrait/
│   │   │       │   └── references/  按需读取的专业方法、案例与合同
│   │   │       │       └── 06_人物生命感与现场摄影关系.md  人物生命感与现场摄影关系
│   │   │       └── laohu-visual-assets/
│   │   │           └── references/  按需读取的专业方法、案例与合同
│   │   │               └── 状态帧与下游运动.md  资产状态与接续参考
│   │   ├── laohu-language-mode/
│   │   │   └── references/  按需读取的专业方法、案例与合同
│   │   │       └── 05_有效信息与冗余裁决.md  有效信息与冗余裁决
│   │   └── scripts/  执行、检索或校验工具
│   │       └── validate_delivery_dependencies.py
│   ├── 语言模式/  随包携带的完整语言方法
│   │   ├── 01_模式判定与块级切换.md  模式判定与块级切换
│   │   ├── 02_用户沟通与制作说明.md  用户沟通与制作说明
│   │   ├── 03_剧本文本块语言.md  剧本文本块语言
│   │   ├── 04_资产图片视频与声音提示词桥接.md  资产、图片、视频与声音提示词桥接
│   │   └── 05_有效信息与冗余裁决.md  有效信息与冗余裁决
│   ├── 交接与验收.md  视频提示词：交接与验收合同
│   ├── 分镜提示词字段说明.md
│   ├── 基础运动与专项路由.md  视频基础必读与专项按需调用
│   ├── 模板_分镜到生成任务清单.md
│   ├── 模板_视频生成质量检查清单.md
│   ├── 独立使用与交接.md  视频制作与提示词的独立使用与交接
│   ├── 短剧短片分镜生成字段规范.md
│   ├── 语言表达.md  视频制作与提示词的语言表达
│   ├── 镜头空间与连续性.md  段内摄影与空间连续性
│   └── 高质量AI视频提示词开发计划.md  高质量 AI 视频提示词开发计划
├── scripts/  执行、检索或校验工具
│   ├── count_video_prompt_chars.sh
│   ├── render_delivery_html.py
│   ├── test_count_video_prompt_chars.sh
│   ├── test_validate_video_prompt_structure.sh
│   └── validate_video_prompt_structure.sh
├── skills/  内部专业，每项有自己的入口与验收
│   ├── laohu-action-design/  老胡动作设计
│   │   ├── references/  按需读取的专业方法、案例与合同
│   │   │   └── 专业方法与案例.md  动作设计：专业方法与案例
│   │   └── SKILL.md  触发、主责、流程与方法路由
│   ├── laohu-animation/  老胡动画
│   │   ├── references/  按需读取的专业方法、案例与合同
│   │   │   └── 专业方法与案例.md  动画：专业方法与案例
│   │   └── SKILL.md  触发、主责、流程与方法路由
│   ├── laohu-audio-design/  老胡音频设计
│   │   ├── agents/  宿主识别元数据
│   │   │   └── openai.yaml
│   │   ├── references/  按需读取的专业方法、案例与合同
│   │   │   ├── 交接与验收.md  音频设计：交接与验收合同
│   │   │   └── 声音提示词规范.md
│   │   ├── skills/  内部专业，每项有自己的入口与验收
│   │   │   ├── laohu-ambience/  老胡环境声设计
│   │   │   │   ├── references/  按需读取的专业方法、案例与合同
│   │   │   │   │   └── 专业方法与案例.md  环境声设计：专业方法与案例
│   │   │   │   └── SKILL.md  触发、主责、流程与方法路由
│   │   │   ├── laohu-audio-editing/  老胡音频剪辑
│   │   │   │   ├── references/  按需读取的专业方法、案例与合同
│   │   │   │   │   └── 专业方法与案例.md  音频剪辑：专业方法与案例
│   │   │   │   └── SKILL.md  触发、主责、流程与方法路由
│   │   │   ├── laohu-audio-mixing/  老胡混音
│   │   │   │   ├── references/  按需读取的专业方法、案例与合同
│   │   │   │   │   └── 专业方法与案例.md  混音：专业方法与案例
│   │   │   │   └── SKILL.md  触发、主责、流程与方法路由
│   │   │   ├── laohu-audio-prompt/  老胡音频提示词编译
│   │   │   │   ├── references/  按需读取的专业方法、案例与合同
│   │   │   │   │   └── 专业方法与案例.md  音频提示词编译：专业方法与案例
│   │   │   │   └── SKILL.md  触发、主责、流程与方法路由
│   │   │   ├── laohu-music-design/  老胡配乐设计
│   │   │   │   ├── references/  按需读取的专业方法、案例与合同
│   │   │   │   │   └── 专业方法与案例.md  配乐设计：专业方法与案例
│   │   │   │   └── SKILL.md  触发、主责、流程与方法路由
│   │   │   ├── laohu-sound-effects/  老胡音效设计
│   │   │   │   ├── references/  按需读取的专业方法、案例与合同
│   │   │   │   │   └── 专业方法与案例.md  音效设计：专业方法与案例
│   │   │   │   └── SKILL.md  触发、主责、流程与方法路由
│   │   │   ├── laohu-voice-design/  老胡音色设计
│   │   │   │   ├── references/  按需读取的专业方法、案例与合同
│   │   │   │   │   └── 专业方法与案例.md  音色设计：专业方法与案例
│   │   │   │   └── SKILL.md  触发、主责、流程与方法路由
│   │   │   └── laohu-voice-performance/  老胡配音
│   │   │       ├── references/  按需读取的专业方法、案例与合同
│   │   │       │   └── 专业方法与案例.md  配音：专业方法与案例
│   │   │       └── SKILL.md  触发、主责、流程与方法路由
│   │   └── SKILL.md  触发、主责、流程与方法路由
│   ├── laohu-audiovisual/  老胡声画关系
│   │   ├── references/  按需读取的专业方法、案例与合同
│   │   │   └── 专业方法与案例.md  声画关系：专业方法与案例
│   │   └── SKILL.md  触发、主责、流程与方法路由
│   ├── laohu-camera-movement/  老胡运镜
│   │   ├── references/  按需读取的专业方法、案例与合同
│   │   │   └── 专业方法与案例.md  运镜：专业方法与案例
│   │   └── SKILL.md  触发、主责、流程与方法路由
│   ├── laohu-choreography/  老胡舞蹈编排
│   │   ├── references/  按需读取的专业方法、案例与合同
│   │   │   └── 专业方法与案例.md  舞蹈编排：专业方法与案例
│   │   └── SKILL.md  触发、主责、流程与方法路由
│   ├── laohu-editing/  老胡剪辑
│   │   ├── references/  按需读取的专业方法、案例与合同
│   │   │   ├── 专业方法与案例.md  剪辑：专业方法与案例
│   │   │   └── 模板_多镜头后期拼接.md  模板：多镜头后期拼接
│   │   └── SKILL.md  触发、主责、流程与方法路由
│   ├── laohu-motion-design/  老胡动态图形设计
│   │   ├── references/  按需读取的专业方法、案例与合同
│   │   │   └── 专业方法与案例.md  动态图形设计：专业方法与案例
│   │   ├── skills/  内部专业，每项有自己的入口与验收
│   │   │   ├── laohu-editorial-explainer/  老胡编辑型知识动画
│   │   │   │   ├── references/  按需读取的专业方法、案例与合同
│   │   │   │   │   └── 证据编排与动态解释.md  编辑型知识讲解的证据编排
│   │   │   │   └── SKILL.md  触发、主责、流程与方法路由
│   │   │   └── laohu-stickman-explainer/  老胡火柴人知识动画
│   │   │       ├── references/  按需读取的专业方法、案例与合同
│   │   │       │   ├── upstream/
│   │   │       │   │   ├── references/  按需读取的专业方法、案例与合同
│   │   │       │   │   │   ├── examples.md  Complete Example
│   │   │       │   │   │   ├── omni-flash-prompt-contract.md  Omni Flash Production Prompt Contract
│   │   │       │   │   │   └── storyboard-template.md  Director's Proposal Contract
│   │   │       │   │   ├── LICENSE
│   │   │       │   │   └── 原始方法.md  Directing Stickman Videos
│   │   │       │   └── 专项方法与适配.md  火柴人讲解：专业方法与本地适配
│   │   │       └── SKILL.md  触发、主责、流程与方法路由
│   │   └── SKILL.md  触发、主责、流程与方法路由
│   ├── laohu-performance/  老胡表演
│   │   ├── references/  按需读取的专业方法、案例与合同
│   │   │   ├── 专业方法与案例.md  表演：专业方法与案例
│   │   │   ├── 人物表情与肢体动作词典.md
│   │   │   ├── 人物表演提示词规范.md
│   │   │   └── 模板_人物表演_情绪时间轴.md  模板：人物表演_情绪时间轴
│   │   └── SKILL.md  触发、主责、流程与方法路由
│   ├── laohu-vfx/  老胡视觉特效 VFX
│   │   ├── references/  按需读取的专业方法、案例与合同
│   │   │   └── 专业方法与案例.md  视觉特效 VFX：专业方法与案例
│   │   └── SKILL.md  触发、主责、流程与方法路由
│   ├── laohu-vibe-creating-prompt/  老胡视频提示词提纯
│   │   ├── agents/  宿主识别元数据
│   │   │   └── openai.yaml
│   │   ├── references/  按需读取的专业方法、案例与合同
│   │   │   └── 01_外部Vibe_Creating原文.md  Vibe Creating Prompt Skill
│   │   └── SKILL.md  触发、主责、流程与方法路由
│   ├── laohu-video-compilation/  老胡视频提示词编译
│   │   ├── references/  按需读取的专业方法、案例与合同
│   │   │   ├── Seedance2视频提示词书写规范.md  Seedance 2 视频提示词书写规范
│   │   │   ├── 专业方法与案例.md  视频提示词编译：专业方法与案例
│   │   │   ├── 多模型AI视频提示词通用规范.md  多模型 AI 视频提示词通用规范
│   │   │   ├── 模板_视频提示词_基础设定氛围画面内容.md  模板：视频提示词_基础设定氛围画面内容
│   │   │   └── 视频注意力与时间编译.md
│   │   └── SKILL.md  触发、主责、流程与方法路由
│   └── laohu-video-references/  老胡视频参考与资产绑定
│       ├── references/  按需读取的专业方法、案例与合同
│       │   └── 专业方法与案例.md  视频参考与资产绑定：专业方法与案例
│       └── SKILL.md  触发、主责、流程与方法路由
└── SKILL.md  触发、主责、流程与方法路由
```

</details>

<details>
<summary>语言模式：laohu-language-mode（含1个Skill入口）</summary>

跨领域表达判断与共同语言规则的维护。

```text
laohu-language-mode/
├── agents/  宿主识别元数据
│   └── openai.yaml
├── references/  按需读取的专业方法、案例与合同
│   ├── 01_模式判定与块级切换.md  模式判定与块级切换
│   ├── 02_用户沟通与制作说明.md  用户沟通与制作说明
│   ├── 03_剧本文本块语言.md  剧本文本块语言
│   ├── 04_资产图片视频与声音提示词桥接.md  资产、图片、视频与声音提示词桥接
│   ├── 05_有效信息与冗余裁决.md  有效信息与冗余裁决
│   └── 独立使用与交接.md  语言模式的独立使用与交接
├── scripts/  执行、检索或校验工具
│   └── render_delivery_html.py
└── SKILL.md  触发、主责、流程与方法路由
```

</details>

迁移路径、共享文件去向、受控副本与可逆历史证据保存在项目系统日志的五包迁移清单中；该清单服务维护审计，不是技能运行入口。
