---
name: laohu-image-creation
description: 用于图片描述补全、单张图片与编辑、人物服装妆造场景道具设计、稳定视觉资产以及封面创作。按用途整合美术、摄影、构图、材质和可复制提示词，保护已确认画面，不把普通成品图强制做成资产板。
---

# 老胡图片创作

## 包级任务路由与独立执行

先分单图、设计、资产与封面。设计不足走人物/服装/场景等专业，复现不稳走资产，单张观看问题走人像或图像编译，封面以可信承诺和缩略可读性验收。

先读[独立使用与交接](references/独立使用与交接.md)，明确本次输入、结果和跨阶段边界。含自然语言沟通或创作正文时使用本包[语言表达](references/语言表达.md)，不依赖另一个包。

- [老胡美术风格设计](skills/laohu-art-direction/SKILL.md)：人物、服装、空间缺少共同视觉方向时进入；建立形态、色彩、材料与光影体系及相邻题材边界。
- [老胡人物设计](skills/laohu-character-design/SKILL.md)：人物外形、选角、身体动作或群像差异尚未成立时进入；交付可见、可表演的人物母版。
- [老胡服装设计](skills/laohu-costume-design/SKILL.md)：人物为什么这样穿、轮廓结构或世界衣橱未定时进入；完成情境判断、设计候选、定案正文及资产交接。
- [老胡妆发设计](skills/laohu-makeup-design/SKILL.md)：妆面、发型、毛发、特效妆或阶段连续性不清时进入；交付人物可整合、资产可继承的妆造补充正文。
- [老胡场景与布景设计](skills/laohu-set-design/SKILL.md)：地点、空间关系、行动条件或陈设未定时进入；交付可供场景资产复现的空间与布景设计。
- [老胡道具设计](skills/laohu-prop-design/SKILL.md)：道具本体、功能、操作结构或界面未定时进入；先确定结构与使用条件，再交道具资产编译。
- [老胡视觉资产](skills/laohu-visual-assets/SKILL.md)：设计已成立但人物、服装或空间需要跨镜复用时进入；选择必要资产，确定依赖、固定项与验收，不把单张成品强制改成资产板。
- [老胡封面与海报](skills/laohu-cover-design/SKILL.md)：需要封面、海报或缩略图时进入；把正片真实价值转成一眼可读的视觉与标题，承诺不得超过内容。

## 灵魂：一张图只承重一个值得停留的结果

图片的统一性来自观看结果，不来自把所有题材都套成写真。人像要有人的现场关系，产品要有可见价值，知识图要有准确解释，制作资产要有可复现结构。

## 筋骨：按最终用途调度

先识别成品图、F人工定调、故事板、局部编辑或稳定资产。稳定B/W/M/S/A/G由视觉资产负责，图片专业按需会商；F生成定调与B/W/M资格不同，F仍由资产依赖表登记为共同源。

读取当前权威内容、使用者、已确认设计、图像参考职责、画幅与可变范围。只补当前缺口：缺新意请求创意开发，缺统一风格请求美术；对象未设计定案回到人物、服装、妆发、场景或道具。专业返回后整合单一时刻，交图片提示词编译，再完成本任务验收。

## 血肉：让专项共同证明同一结果

人像、静物与分镜决定当前对象怎样被看见；构图、摄影、光影、色材、版式和字体提供需要的专业决定。它们不需每次全部调用。共享理论的唯一负责人在美术专业树，图片只决定其静态应用。现有图编辑先判权限再修画面，不能一边修光一边更换身份。

## 表皮：交付与资格

默认交付可复制图片提示词；生成工具调用依用户授权。成品图沿用既有工作卡与正文外壳，F沿用既有人工定调与资产交接合同，故事板沿用源镜号，不创建第二份剧本。真实结果未出现时不登记已生成、不冒充像素验收通过。

## 整合验收

所有实际生图与编辑均继承图片提示词编译Skill的「全部图片的细节质量要求」，提交前核对正文及真实材质保护项；不能绕过编译直接调用工具。

单一观看任务是否清楚；锁定文字、身份、设计与状态是否保护；各专业是否支持同一承重证据；格式是否适合成品图或制作板；Reference是否实际改变了可指认的决定。未通过返回最早能改变原因的负责人。

## 专业路由

由下表按缺口读取入口，入口再选择Reference。每次CONSULT只返回本专业决定，不重复接管整张图。


## 专业能力路由

| 当前缺口 | 专业能力 | 独立返回 |
|---|---|---|
| 人像摄影需要独立判断 | [laohu-portrait](skills/laohu-portrait/SKILL.md) | 该专业的方案、边界与可执行描述；返回当前负责人整合 |
| 静物摄影需要独立判断 | [laohu-still-life-photography](skills/laohu-still-life-photography/SKILL.md) | 该专业的方案、边界与可执行描述；返回当前负责人整合 |
| 分镜设计需要独立判断 | [laohu-storyboard](skills/laohu-storyboard/SKILL.md) | 该专业的方案、边界与可执行描述；返回当前负责人整合 |
| 图像编辑需要独立判断 | [laohu-image-editing](skills/laohu-image-editing/SKILL.md) | 该专业的方案、边界与可执行描述；返回当前负责人整合 |
| 图片提示词编译需要独立判断 | [laohu-image-prompt](skills/laohu-image-prompt/SKILL.md) | 该专业的方案、边界与可执行描述；返回当前负责人整合 |

共享专业按缺口会商，不按目录顺序全部读取。图片负责静态关系，视频负责时间变化；专业判断不能覆盖已确认故事和对象事实。

### 成品与F合同

- [图片与资产生产合同](references/图片与资产生产合同.md)：单张成品图或F定调时读取，继承完整工作卡、正文和交接。
- [图片验收与封面交接](references/图片验收与封面交接.md)：已有结果或需要封面交接时读取。


## 专业合同补充

- [F人物主视觉编译](references/F人物主视觉编译.md)：涉及该对象或生产合同就读取，保持固定项与例外。


## 跨专业会商

- 创意开发尚有未决问题时，CONSULT [laohu-creative-development](references/内置方法/laohu-ai-visual/skills/laohu-creative-development/专业方法.md)；已有有效结论直接继承，不重跑父流程。
- 美术指导尚有未决问题时，CONSULT [laohu-art-direction](skills/laohu-art-direction/SKILL.md)；已有有效结论直接继承，不重跑父流程。
- 视觉资产尚有未决问题时，CONSULT [laohu-visual-assets](skills/laohu-visual-assets/SKILL.md)；已有有效结论直接继承，不重跑父流程。
- 构图尚有未决问题时，CONSULT [laohu-composition](skills/laohu-art-direction/skills/laohu-composition/SKILL.md)；已有有效结论直接继承，不重跑父流程。
- 摄影尚有未决问题时，CONSULT [laohu-photography](skills/laohu-art-direction/skills/laohu-photography/SKILL.md)；已有有效结论直接继承，不重跑父流程。
- 光影设计尚有未决问题时，CONSULT [laohu-light-shadow](skills/laohu-art-direction/skills/laohu-light-shadow/SKILL.md)；已有有效结论直接继承，不重跑父流程。

## 按当前缺口读取的补充方法

- [高质量AI图片开发计划](references/高质量AI图片开发计划.md)：当前任务涉及0. 特征资产的描述粒度、1. 不变骨架资产、2. 主体突出审美特征资产时读取相应章节，形成可指认的专业选择；不把整份候选清单机械填入正文。
