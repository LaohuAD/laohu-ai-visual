---
name: laohu-image-creation
description: 用于图片描述补全、单张图片与编辑、人物服装妆造场景道具设计、稳定视觉资产以及封面创作。按用途整合美术、摄影、构图、材质和可复制提示词，保护已确认画面，不把普通成品图强制做成资产板。
---

# 老胡图片创作

## 包级任务路由与独立执行

先分单图、设计、资产与封面。设计不足走人物/服装/场景等专业，复现不稳走资产，单张观看问题走人像或图像编译，封面以可信承诺和缩略可读性验收。

先读[独立使用与交接](references/独立使用与交接.md)，明确本次输入、结果和跨阶段边界。含自然语言沟通或创作正文时先读本包[语言表达](references/语言表达.md)取得领域写法；完整通用规则按 `../laohu-language-mode/references/01_模式判定与块级切换.md` 等唯一正文读取，本包不再另存一套副本。

### 意图理解与父级继承

先写清本领域要改变的结果：这张图、这套设计或这份资产被谁在什么场景使用，哪些事实、画面与设计已经锁定，哪些只是候选解释或创意留白，当前材料能支持到什么程度。助手推断与用户已确认的事实分开记录，不把候选解释写成需求。

本包继承项目顶层规则 `AGENTS.md` 的目的、路由、边界、路径与隐私要求，在本层形成自己的专业判断；不要求用户先给专业简报，也不重复整套上游工作。能由现有材料与专业方法合理补全的开放选择直接提出或完成；只有互斥方向、无法同时成立的事实、用户明确要求共创，或会显著改变成本、权利、公开声称与外部动作时，才提少量能区分方向的问题或具体候选，并说明差异与后果。讨论本身可以是本轮交付。

按本层判断选择下一层：命中哪条分支就读取哪条，读取范围以命中行为界，不遍历全部专业；命中的行必须读完再产出本阶段结果。直接点名深层专业技能时，先沿其父级链接补齐所属链，再继续当前子任务；补依赖只建立上下文继承，不重新发起同一个任务。子专业结果返回本入口整合，核对它们是否使用同一组已确认事实与设计，冲突定位到最早作出该决定的负责人；已读且仍有效的父级与共同方法不重复通读，缺失、变更或新会话时补读。

### 强制读取路由

本层是路由层，专业方法在下层。下表每行是一条读取义务：情形出现，就在产出本阶段结果之前读取右列文件；命中多行就读完多行。读取为了取得「必须得到的决定」；决定没拿到时继续读该文件，直到拿到为止。右列指向第二层或第三层时，先读它的 `SKILL.md`，需要更细判断时按它自己的强制读取路由继续下沉；每层 CONSULT 只返回本专业决定，不重复接管整张图。

**第一层 Reference**

| 出现的情形 | 必须读取 | 必须得到的决定 |
|---|---|---|
| 本次任务的输入、结果或跨阶段边界尚未写清 | [独立使用与交接](references/独立使用与交接.md) | 本次交付身份、输入来源与上下游边界 |
| 正文含人物台词、旁白、导演说明、平台文案或面向老胡的沟通 | [语言表达](references/语言表达.md) | 当前文本块的语言身份与领域写法 |
| 需要判断这次要的是稳定资产、F人工定调还是面向观众的成品图 | [图片与资产生产合同](references/图片与资产生产合同.md) | 结果身份、完整工作卡、正文外壳与对应验收门 |
| 要产出可复制图片提示词，或把结果交封面阶段 | [图片生成执行与封面交接](references/图片生成执行与封面交接.md) | 正文格式、参考绑定、生成顺序与交接清单 |
| 要做F人物主视觉并登记为B/W/M共同上游源 | [F人物主视觉编译](references/F人物主视觉编译.md) | F的编译方式、固定项、例外与依赖登记 |

**第二层专业**

| 出现的情形 | 必须读取 | 必须得到的决定 |
|---|---|---|
| 人物、服装、空间缺少共同视觉方向，或结果只有表面元素却落入相邻题材 | [laohu-art-direction](skills/laohu-art-direction/SKILL.md) | 形态、色彩、材料与光影体系及相邻题材边界 |
| 人物外形、选角、身体动作或群像差异尚未成立，或人物同脸同体型同气质 | [laohu-character-design](skills/laohu-character-design/SKILL.md) | 可见、可表演的人物母版 |
| 人物为什么这样穿、轮廓结构或世界衣橱未定，或服装合理但平庸、彼此同质 | [laohu-costume-design](skills/laohu-costume-design/SKILL.md) | 情境判断、设计候选、定案正文及资产交接 |
| 已有图片需要局部替换、修复、扩图或摄影升级 | [laohu-image-editing](skills/laohu-image-editing/SKILL.md) | 三权划分、编辑与保护清单、边缘过渡、改前改后差异 |
| 专业判断已完成，需要可复制的图片生成正文 | [laohu-image-prompt](skills/laohu-image-prompt/SKILL.md) | 独立可复制正文、参考绑定、画幅与必要保护项 |
| 妆发需要原创、需要整合，或既有设计在结构状态上返修 | [laohu-makeup-design](skills/laohu-makeup-design/SKILL.md) | 同一人物身份上的妆发设计正文，交视觉资产编译 |
| 写真、F人物主视觉、人物结果图或已有照片需要可信现场 | [laohu-portrait](skills/laohu-portrait/SKILL.md) | 单帧因果、人物—摄影机—环境关系、身份保护与静态提示词 |
| 道具需要原创、需要整合功能结构与材料状态，或既有设计返修 | [laohu-prop-design](skills/laohu-prop-design/SKILL.md) | 功能结构一致、材料与状态可追踪的道具设计正文，交视觉资产编译 |
| 固定场景、世界地点系统、空间关系、布景陈设或数字环境未定 | [laohu-set-design](skills/laohu-set-design/SKILL.md) | 可供场景资产复现的空间与布景设计 |
| 产品、食物、器物或非人物主体需要静物画面 | [laohu-still-life-photography](skills/laohu-still-life-photography/SKILL.md) | 对象锁定表、角度与摆置、材料证据、背景与尺度关系 |
| 已确认剧本需要关键帧、故事板或预视化 | [laohu-storyboard](skills/laohu-storyboard/SKILL.md) | 源镜号、格间状态、画面投影、动作关键帧与下游引用范围 |
| 设计已成立但人物、服装或空间需要跨镜复用 | [laohu-visual-assets](skills/laohu-visual-assets/SKILL.md) | 资产选择、依赖顺序、固定项与验收 |
| 需要封面、海报或缩略图 | [laohu-cover-design](skills/laohu-cover-design/SKILL.md) | 把正片真实价值转成一眼可读的承诺、主视觉与标题 |

**第三层专项**

情形已经精确到下表某一项时直接读取该文件；读完仍要沿它写明的父级链接补齐尚未读取的上层决定。

| 出现的情形 | 必须读取 |
|---|---|
| 颜色承担分组、身份识别、情绪转折或肤色产品色保护 | [laohu-color-design](skills/laohu-art-direction/skills/laohu-color-design/SKILL.md) |
| 多来源图层出现透视、光色、边缘或遮挡不一致 | [laohu-compositing](skills/laohu-art-direction/skills/laohu-compositing/SKILL.md) |
| 主体关系、景别、视觉中心、遮挡或画面空间不清 | [laohu-composition](skills/laohu-art-direction/skills/laohu-composition/SKILL.md) |
| 需要手绘、版画、拼贴、图形化或跨媒介转译 | [laohu-illustration](skills/laohu-art-direction/skills/laohu-illustration/SKILL.md) |
| 比较、数据、流程、层级或知识可视化需要编码 | [laohu-information-design](skills/laohu-art-direction/skills/laohu-information-design/SKILL.md) |
| 图文分组、网格、对齐、留白或多比例重排需要设计 | [laohu-layout-design](skills/laohu-art-direction/skills/laohu-layout-design/SKILL.md) |
| 光源、阴影、体积光、反射、轮廓或动态受光需要专业判断 | [laohu-light-shadow](skills/laohu-art-direction/skills/laohu-light-shadow/SKILL.md) |
| 表面看似同一种塑料，或材料与使用、光照不相容 | [laohu-material-design](skills/laohu-art-direction/skills/laohu-material-design/SKILL.md) |
| 透视、景深、曝光、镜头质感或成像逻辑不成立 | [laohu-photography](skills/laohu-art-direction/skills/laohu-photography/SKILL.md) |
| 字体、字重、字距、行距、中西文混排或文字可读性不足 | [laohu-typography](skills/laohu-art-direction/skills/laohu-typography/SKILL.md) |
| 人物的重量、活动能力和日常习惯互不相干，或身体只靠外观描述承担不了动作 | [laohu-body-design](skills/laohu-character-design/skills/laohu-body-design/SKILL.md) |
| 只按美貌或名气选人、候选人之间没有关系差异、选出的身体撑不住剧本里的行动 | [laohu-casting](skills/laohu-character-design/skills/laohu-casting/SKILL.md) |
| 虚构生物只有拼出来的形状、看不出它怎样在环境里活下来 | [laohu-creature-design](skills/laohu-character-design/skills/laohu-creature-design/SKILL.md) |
| 多个角色单看都成立、放在一起却读不出关系，或群像只剩一份名单 | [laohu-ensemble-design](skills/laohu-character-design/skills/laohu-ensemble-design/SKILL.md) |
| 同一张脸在侧转、换表情或换光后被认成别人，或五官各自好看却不构成一张脸 | [laohu-face-design](skills/laohu-character-design/skills/laohu-face-design/SKILL.md) |
| 配饰只是挂在身上、看不出怎样佩戴取用，或与进入剧情的道具混为一谈 | [laohu-accessory-design](skills/laohu-costume-design/skills/laohu-accessory-design/SKILL.md) |
| 换装、湿痕、破口或卷袖在不同镜次里对不上故事时间 | [laohu-costume-continuity](skills/laohu-costume-design/skills/laohu-costume-continuity/SKILL.md) |
| 纹样只是贴上去的花，或装饰盖过服装本体、远景让看不见的小纹承担等级 | [laohu-costume-ornament](skills/laohu-costume-design/skills/laohu-costume-ornament/SKILL.md) |
| 服装的年代、制度、材料或资源来路说不清，或拿一张漂亮参考代替考据 | [laohu-costume-research](skills/laohu-costume-design/skills/laohu-costume-research/SKILL.md) |
| 穿衣在远景看不出身份变化，或几套衣服只靠颜色和饰物区分 | [laohu-costume-silhouette](skills/laohu-costume-design/skills/laohu-costume-silhouette/SKILL.md) |
| 衣服穿不上、动不了，或转身换角度后不像同一件 | [laohu-garment-structure](skills/laohu-costume-design/skills/laohu-garment-structure/SKILL.md) |
| 不同面料在同一光下没有区别，或材料的重量与垂坠对不上它该承担的功能与资源 | [laohu-textile-design](skills/laohu-costume-design/skills/laohu-textile-design/SKILL.md) |
| 作品事实成立，需要点击主张与主视觉候选 | [laohu-cover-concept](skills/laohu-cover-design/skills/laohu-cover-concept/SKILL.md) |
| 封面文字需生成、优化或逐字排版 | [laohu-cover-copy](skills/laohu-cover-design/skills/laohu-cover-copy/SKILL.md) |
| 封面主体、标题、轴线或语义保护区需要组合 | [laohu-cover-layout](skills/laohu-cover-design/skills/laohu-cover-layout/SKILL.md) |
| 主视觉需要手机缩略图、裁切或多画幅适配 | [laohu-thumbnail](skills/laohu-cover-design/skills/laohu-thumbnail/SKILL.md) |
| 毛发的方向、密度与束感不服从皮肤结构和尺度，或概念稿冒充已经执行了梳理 | [laohu-groom-design](skills/laohu-makeup-design/skills/laohu-groom-design/SKILL.md) |
| 发型正侧背对不上、固定方式不可信，或动作一开始头发就散掉 | [laohu-hair-design](skills/laohu-makeup-design/skills/laohu-hair-design/SKILL.md) |
| 妆面换了却让人觉得换了人，或妆效只在某一个光位下成立 | [laohu-makeup](skills/laohu-makeup-design/skills/laohu-makeup/SKILL.md) |
| 外加形态与伤痕只有平面颜色、缺少体积和边缘，或换一个故事状态就对不上 | [laohu-prosthetic-makeup](skills/laohu-makeup-design/skills/laohu-prosthetic-makeup/SKILL.md) |
| 道具在手里做不成动作、状态交不到下一镜，或与配饰职责混在一起 | [laohu-hand-props](skills/laohu-prop-design/skills/laohu-hand-props/SKILL.md) |
| 机械只有齿轮纹样、看不出输入怎样传到输出 | [laohu-mechanical-design](skills/laohu-prop-design/skills/laohu-mechanical-design/SKILL.md) |
| 产品形态与它声称的功能对不上，或参数与认证没有证据 | [laohu-product-design](skills/laohu-prop-design/skills/laohu-product-design/SKILL.md) |
| 载具装不下乘员货物、看不出怎样接地推进，或尺度随镜次变化 | [laohu-vehicle-design](skills/laohu-prop-design/skills/laohu-vehicle-design/SKILL.md) |
| 建筑只有外观体量、看不出怎样站住和进入，或尺度靠后景遮藏糊弄 | [laohu-architecture-design](skills/laohu-set-design/skills/laohu-architecture-design/SKILL.md) |
| 地点先有漂亮参考、却说不清时代功能与环境条件 | [laohu-environment-research](skills/laohu-set-design/skills/laohu-environment-research/SKILL.md) |
| 房间先定了装修风格、却放不下人物的实际使用，或家具为每次反打随意迁位 | [laohu-interior-design](skills/laohu-set-design/skills/laohu-interior-design/SKILL.md) |
| 地形、水、植被与路径互不相干，或景观没有时间厚度、只剩一块布景板 | [laohu-landscape-design](skills/laohu-set-design/skills/laohu-landscape-design/SKILL.md) |
| 陈设只是摆满好看、看不出谁用过这里，或线索提前泄底 | [laohu-set-decoration](skills/laohu-set-design/skills/laohu-set-decoration/SKILL.md) |
| 入口、距离或遮挡在戏里说不通，只能到下游临时换房间 | [laohu-spatial-layout](skills/laohu-set-design/skills/laohu-spatial-layout/SKILL.md) |
| 角色需要B素体、阶段身体或局部身份校准 | [laohu-body-assets](skills/laohu-visual-assets/skills/laohu-body-assets/SKILL.md) |
| 已确认服装需要W制作板与可复用引用 | [laohu-costume-assets](skills/laohu-visual-assets/skills/laohu-costume-assets/SKILL.md) |
| 已确认场景需要S空间资产、巨构或多视图 | [laohu-environment-assets](skills/laohu-visual-assets/skills/laohu-environment-assets/SKILL.md) |
| 背景群体或多角色需要复用身份分布 | [laohu-group-assets](skills/laohu-visual-assets/skills/laohu-group-assets/SKILL.md) |
| F/B/W与妆发正文齐备，需要M穿着结果 | [laohu-makeup-assets](skills/laohu-visual-assets/skills/laohu-makeup-assets/SKILL.md) |
| 已确认道具需要A形态、功能或操作引用 | [laohu-prop-assets](skills/laohu-visual-assets/skills/laohu-prop-assets/SKILL.md) |
| 美术方向需要可视候选定调，或已定案风格需要STY母板、系列参考与跨主体校准 | [laohu-style-reference](skills/laohu-visual-assets/skills/laohu-style-reference/SKILL.md) |

共享专业按缺口会商，不按目录顺序全部读取。图片负责静态关系，视频负责时间变化；专业判断不能覆盖已确认故事和对象事实。

**机械检查**

下表的脚本地址相对于本文件；在仓库根执行时按 `.agents/skills/laohu-image-creation/` 前缀展开。

| 出现的情形 | 必须运行 | 必须得到的结论 |
|---|---|---|
| 正式资产文件写好，需要核对 B 素体、阶段身体与 M 穿着结果的结构 | [validate_character_asset_structure.py](skills/laohu-visual-assets/scripts/validate_character_asset_structure.py) 加资产文件路径 | 结构门通过或具体违约项 |
| 修改过该结构校验脚本本身 | [test_validate_character_asset_structure.sh](skills/laohu-visual-assets/scripts/test_validate_character_asset_structure.sh) | `validate_character_asset_structure tests passed` |

## 灵魂：一张图只承重一个值得停留的结果

图片的统一性来自观看结果，不来自把所有题材都套成写真。人像要有人的现场关系，产品要有可见价值，知识图要有准确解释，制作资产要有可复现结构。

## 筋骨：按最终用途调度

先识别成品图、F人工定调、故事板、局部编辑或稳定资产。稳定B/W/M/S/A/G由视觉资产负责，图片专业按命中行会商；F生成定调与B/W/M资格不同，F仍由资产依赖表登记为共同源。

读取当前权威内容、使用者、已确认设计、图像参考职责、画幅与可变范围。只补当前缺口：缺新意请求创意开发，缺统一风格请求美术；对象未设计定案回到人物、服装、妆发、场景或道具。专业返回后整合单一时刻，交图片提示词编译，再完成本任务验收。

## 血肉：让专项共同证明同一结果

人像、静物与分镜决定当前对象怎样被看见；构图、摄影、光影、色材、版式和字体提供需要的专业决定。它们不需每次全部调用。共享理论的唯一负责人在美术专业树，图片只决定其静态应用。现有图编辑先判权限再修画面，不能一边修光一边更换身份。

## 表皮：交付与资格

默认交付可复制图片提示词；生成工具调用依用户授权。成品图沿用既有工作卡与正文外壳，F沿用既有人工定调与资产交接合同，故事板沿用源镜号，不创建第二份剧本。真实结果未出现时不登记已生成、不冒充像素验收通过。

## 整合验收

所有实际生图与编辑均继承图片提示词编译Skill的「全部图片的细节质量要求」，提交前核对正文及真实材质保护项；不能绕过编译直接调用工具。

单一观看任务是否清楚；锁定文字、身份、设计与状态是否保护；各专业是否支持同一承重证据；格式是否适合成品图或制作板；Reference是否实际改变了可指认的决定。未通过返回最早能改变原因的负责人。

## 专业返回与整合

每个第二层专业返回本专业的方案、边界与可执行描述，交当前负责人整合；每次 CONSULT 只返回本专业决定，不重复接管整张图。


## 跨专业会商

- 创意开发尚有未决问题时，CONSULT [laohu-creative-development](../laohu-ai-visual/skills/laohu-creative-development/SKILL.md)；已有有效结论直接继承，不重跑父流程。
- 美术指导尚有未决问题时，CONSULT [laohu-art-direction](skills/laohu-art-direction/SKILL.md)；已有有效结论直接继承，不重跑父流程。
- 视觉资产尚有未决问题时，CONSULT [laohu-visual-assets](skills/laohu-visual-assets/SKILL.md)；已有有效结论直接继承，不重跑父流程。
- 构图尚有未决问题时，CONSULT [laohu-composition](skills/laohu-art-direction/skills/laohu-composition/SKILL.md)；已有有效结论直接继承，不重跑父流程。
- 摄影尚有未决问题时，CONSULT [laohu-photography](skills/laohu-art-direction/skills/laohu-photography/SKILL.md)；已有有效结论直接继承，不重跑父流程。
- 光影设计尚有未决问题时，CONSULT [laohu-light-shadow](skills/laohu-art-direction/skills/laohu-light-shadow/SKILL.md)；已有有效结论直接继承，不重跑父流程。

## 按当前缺口读取的补充方法

上表之外的缺口按当前未决问题补读，读一条就写清要读的精确相对文件与章节、应形成的决定；读完要能指出它确认或改变了哪一个具体判断，只记录“已读取”不算激活。

