#!/usr/bin/env python3
"""Validate F/B/P-stage/W/M character production references and boards."""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass
class PromptBlock:
    heading: str
    body: str
    line: int
    context: str


def read_blocks(text: str) -> list[PromptBlock]:
    blocks: list[PromptBlock] = []
    heading = ""
    heading_line = -1
    lines = text.splitlines()
    index = 0
    while index < len(lines):
        line = lines[index]
        if line.startswith("### "):
            heading = line[4:].strip()
            heading_line = index
        if line.strip() == "```text":
            start = index + 2
            body_lines: list[str] = []
            index += 1
            while index < len(lines) and lines[index].strip() != "```":
                body_lines.append(lines[index])
                index += 1
            context = "\n".join(lines[heading_line + 1 : start - 1]) if heading_line >= 0 else ""
            blocks.append(PromptBlock(heading, "\n".join(body_lines), start, context))
        index += 1
    return blocks


def contains_all(body: str, terms: list[str]) -> list[str]:
    return [term for term in terms if term not in body]


def uses_disallowed_parameter_panel(body: str) -> bool:
    pattern = r"(?:横跨(?:整幅|画面)?底部|底部横栏|底部参数栏|左下)[^。；\n]{0,60}(?:参数|信息)"
    for sentence in re.split(r"[。；\n]", body):
        if re.search(pattern, sentence) and not re.search(r"(?:不允许|不得|不能|禁止|不生成|不新增|不建立|不改成)", sentence):
            return True
    return False


def validate_f(block: PromptBlock) -> list[str]:
    required_groups = {
        "人物主视觉图": r"人物主视觉|角色主视觉|人物瞬间|正片人物",
        "脸部设计": r"脸部|脸型|面型|面部|鹅蛋脸|窄长面|宽额",
        "身体与动作状态": r"身体比例|身材|体态|身高|重心|肩膀|肩线|腰胯|前进",
        "服装": r"服装|穿搭|外穿|下穿|穿着|穿的是|身着",
        "妆容": r"妆容|妆面|底妆|无妆",
        "发型": r"发型|发髻|长发|短发|发束|半束|低束|高束|低髻|双环髻",
        "人物气质": r"人物气质|气质|人物身份|第一眼|灵动|亲近|沉稳|冷冽|温和",
        "光影": r"光影|主光|轮廓光|侧逆光|逆光|柔光|日光|天光|环境光|暖光",
        "摄影位置": r"摄影机|镜头|机位|前景",
        "关系对象": r"看向|朝向|面向|对方|师兄|师妹|关系对象",
        "未完成状态": r"刚|正|即将|尚未|还没|未完成|下一刻",
    }
    failures = [
        f"缺少：{label}"
        for label, pattern in required_groups.items()
        if not re.search(pattern, block.body)
    ]
    if not (
        re.search(r"眼|眼裂|眼睑", block.body)
        and re.search(r"鼻|鼻梁", block.body)
        and re.search(r"唇|嘴角|嘴唇", block.body)
    ):
        failures.append("缺少：可执行的眼鼻唇面部关系")
    if not re.search(r"(?:\d+岁|表观\d+岁|年龄感)", block.body):
        failures.append("缺少：年龄感")
    if not re.search(r"(?:肤色|皮肤|肤质)[^。；\n]{0,100}(?:毛孔|纹理|细纹|细绒毛)", block.body):
        failures.append("缺少：自然肤质证据")

    # 机械校验只负责拦住“字段齐全但所有元素同权”的明显低强度稿。
    # 真正的审美强度仍由 Skill 的视觉主导合同和人工审稿判断，不能由正则冒充。
    hierarchy_floor = {
        "明确第一视觉落点": r"第一(?:视觉)?落点|第一眼|主焦点|主要焦点",
        "承重焦点清晰度": r"(?:双眼|眼睛|面部|脸部|人物)[^。；\n]{0,80}(?:最清楚|最清晰|焦平面|最高局部反差)",
        "视线引导机制": r"引导线|框景|对角线|视线[^。；\n]{0,60}(?:送回|落到|集中|指向)|(?:栏杆|柱线|门框|剑身|手臂)[^。；\n]{0,60}(?:引导|指向)",
        "竞争元素退让": r"低对比|柔焦|降低清晰度|降低饱和度|退入背景|压入暗部|只保留[^。；\n]{0,30}轮廓",
        "阅读层级": r"第二眼[^。；\n]{0,120}第三眼|主焦点[^。；\n]{0,120}(?:次要|辅助|背景)",
    }
    failures.extend(
        f"视觉层级底线缺少：{label}"
        for label, pattern in hierarchy_floor.items()
        if not re.search(pattern, block.body)
    )

    if re.search(r"挥剑|格挡|劈砍|劈山|推(?:动|住|向)?(?:石柱|巨柱|山门)|撞击|爆炸|托举巨物|近身交手", block.body):
        action_floor = {
            "力量来源或支撑点": r"力量来源|发力|承重脚|支撑脚|支点|肩背|腰胯|蹬地|重心",
            "单一运动或力量路径": r"力量线|运动路径|发力路径|沿[^。；\n]{0,60}(?:劈|推|压|送|传|撞)|从[^。；\n]{0,40}传到",
            "接触点": r"接触点|抵住|撞上|劈中|压在|贴住|卡住|剑刃[^。；\n]{0,30}(?:相接|碰撞)",
            "受影响对象与结果": r"受力|被推|被劈|裂开|后退|位移|倾斜|震动|碎裂|结果|余势|回弹|水花|石屑",
        }
        failures.extend(
            f"动态人物图底线缺少：{label}"
            for label, pattern in action_floor.items()
            if not re.search(pattern, block.body)
        )
    if not (
        re.search(r"发际线|发根|美人尖|头发|黑发|长发|乌黑", block.body)
        and re.search(r"发质|细软|中粗|粗硬|顺直|长发|低束|高束|低髻|双环髻", block.body)
    ):
        failures.append("缺少：发际线与发质关系")
    if not re.search(r"B\d+[^。；\n]{0,30}W\d+[^。；\n]{0,30}M\d+", block.context):
        failures.append("缺少：F必须声明为同编号B/W/M共同上游")
    f_match = re.match(r"F(\d+)", block.heading)
    if f_match:
        referenced = re.findall(r"[BWM](\d+)", block.context)
        wrong_refs = sorted({ref for ref in referenced if ref != f_match.group(1)})
        if wrong_refs:
            failures.append(f"F{f_match.group(1)}只能服务同编号B/W/M，不得错绑：" + "、".join(wrong_refs))
    if not re.search(r"不直接进入视频|不进入视频|只服务资产", block.context + block.body):
        failures.append("缺少：F不直接进入视频")
    if re.search(r"必须[^。；\n]{0,40}(?:完整全身|鞋底入画|直视镜头|正面站立)", block.body):
        failures.append("F不得为后续拆解强制站桩式完整展示")
    if re.search(
        r"(?:改成|改为|变成|重塑|替换|重新选择|重新选角)[^。；\n]{0,40}(?:更年轻|更年长|新骨相|骨相|年龄|身份|另一张脸)",
        block.body,
    ):
        failures.append("F不得重新选角或改变已确认年龄骨相")
    return failures


def validate_b(block: PromptBlock) -> list[str]:
    required = [
        "16:9",
        "固定三列网格",
        "左栏约36%",
        "中栏约45%",
        "右栏约19%",
        "整高",
        "三等分",
        "正面头部大特写",
        "唯一清晰人脸",
        "左前方45度身体",
        "正面身体",
        "背面身体",
        "无五官校准头模",
        "完全无头发",
        "哑光校准头模表面",
        "纯白",
        "不透明",
        "中等克重校准服",
        "立领前拉链长袖校准上衣",
        "全长校准裤",
        "白袜",
        "肩缝",
        "袖口",
        "腰头",
        "侧缝",
        "裤脚",
        "2—4cm活动松量",
        "除头颈与双手外不露出皮肤",
        "衣料与肤色有清楚色差",
        "标题固定右上",
        "说明固定右下",
        "固定纵坐标",
        "水平细白引线",
        "除头身比短标外",
        "身高",
        "体重",
        "头身比",
        "肩宽",
        "胸围",
        "腰围",
        "臀围",
    ]
    failures = [f"缺少：{term}" for term in contains_all(block.body, required)]
    if re.search(
        r"(?:右侧|三张|每张)[^。\n]{0,120}(?:完整显示|清楚显示|保留)(?:人物)?(?:真实)?五官",
        block.body,
    ):
        failures.append("右侧身体视图重新生成了真实或清晰五官")
    if re.search(
        r"(?:中栏|右侧|三张|头模)[^。\n]{0,160}(?:保留|生成|带有|具有)(?:人物)?(?:真实)?(?:头发|发型|发际线)",
        block.body,
    ):
        failures.append("中栏身体人台保留了头发或真实发型")
    if uses_disallowed_parameter_panel(block.body):
        failures.append("参数区位置偏离固定右栏")
    if re.search(r"(?:肤色|肉色)(?:贴体|紧身|连体)?(?:衣|服|裤)|半透明(?:校准)?(?:衣|服)|无缝表皮|第二层皮肤|裸体|裸模|裸感", block.body):
        failures.append("B包含裸体误读或肤色第二层皮肤指令")
    if not re.search(r"【写真(?:母图)?参考@F\d+】", block.body):
        failures.append("缺少：B必须引用写真母图F")
    b_match = re.match(r"B(\d+)", block.heading)
    if b_match:
        referenced_f_ids = set(re.findall(r"(?<![A-Za-z0-9])F(\d+)(?!\d)", block.body))
        wrong_refs = sorted(ref_id for ref_id in referenced_f_ids if ref_id != b_match.group(1))
        if wrong_refs:
            failures.append(
                f"B{b_match.group(1)}只能引用同编号F{b_match.group(1)}，不得引用："
                + "、".join(f"F{ref_id}" for ref_id in wrong_refs)
            )
    return failures


def validate_m(block: PromptBlock) -> list[str]:
    required_groups = {
        "16:9": r"16:9",
        "三列纵向组合": r"三列纵向组合|三组纵向组合",
        "左前45度": r"左前(?:方)?45度",
        "正面": r"正面",
        "背面": r"背面",
        "上部头部特写": r"上(?:排|部)[^。；\n]{0,80}头部",
        "下部无头穿着身体": r"下(?:排|部)[^。；\n]{0,120}无头[^。；\n]{0,60}(?:身体|躯体)",
        "鞋底": r"鞋底",
        "妆造补充正文": r"妆造补充",
    }
    failures = [
        f"缺少：{label}"
        for label, pattern in required_groups.items()
        if not re.search(pattern, block.body)
    ]
    if not re.search(r"上(?:排|部)[^。；\n]{0,80}(?:约)?三分之一", block.body):
        failures.append("缺少：上部约三分之一")
    if not re.search(r"下(?:排|部)[^。；\n]{0,80}(?:约)?三分之二", block.body):
        failures.append("缺少：下部约三分之二")
    if not re.search(r"颈(?:部)?根|肩线以下", block.body):
        failures.append("缺少：下部从颈根或肩线以下开始")
    if not re.search(r"同角度|一一对应|严格对应|角度对应", block.body):
        failures.append("缺少：上下同列角度对应")
    if not re.search(r"三列纵向(?:组合|复合)|三组纵向(?:组合|复合)", block.body):
        failures.append("缺少：M必须组织为三列纵向复合，而非六张独立照片")
    if not re.search(r"下(?:排|部)[^。；\n]{0,120}无头[^。；\n]{0,60}(?:身体|躯体)", block.body):
        failures.append("缺少：下部必须是无头穿着身体")
    if not re.search(
        r"上(?:排|部)[^。；\n]{0,120}覆盖[^。；\n]{0,120}下(?:排|部)[^。；\n]{0,80}(?:头颅|头部)[^。；\n]{0,30}位置",
        block.body,
    ):
        failures.append("缺少：上部头部特写覆盖下部原头部位置")
    if not re.search(r"唯一对应头部|同列只保留一个头部", block.body):
        failures.append("缺少：上部特写是同列身体唯一对应头部")
    if not re.search(r"从颈(?:部)?根到鞋底|画框最高可见点[^。；\n]{0,100}(?:锁骨|肩峰|后领)", block.body):
        failures.append("缺少：下部画框从颈肩结构开始")
    if not re.search(r"无头穿着身体|头颅完整位于下(?:排|部)画框之外", block.body):
        failures.append("缺少：下部头颅必须完整位于画框之外")
    if not re.search(r"(?:覆盖)?接缝[^。；\n]{0,80}(?:颈肩交界|服装领口|领口)", block.body):
        failures.append("缺少：上下覆盖接缝必须藏在颈肩或领口附近")
    if re.search(r"四视图|左侧(?:斜视)?90度|严格左侧90度", block.body):
        failures.append("仍在使用旧四视图或左侧90度版式")
    if re.search(r"(?<!不是)六张独立|每一格各自独立", block.body):
        failures.append("M被错误拆成六张独立人物照片")
    if re.search(
        r"下(?:排|部)[^。；\n]{0,180}(?:完整人物全身|全身肖像|从头顶到鞋底|再次[^。；\n]{0,30}(?:显示|出现|保留)[^。；\n]{0,20}(?:头部|头发|脸))",
        block.body,
    ):
        failures.append("下排重复生成了人物头部或完整全身肖像")
    if not re.search(r"【服装参考@W\d+", block.body):
        failures.append("缺少：M必须引用服装资产W")
    if not re.search(r"【(?:人物主视觉|写真母图|写真)参考@F\d+", block.body):
        failures.append("缺少：M必须引用人物主视觉图F")
    if not re.search(r"【(?:素体|阶段素体)参考@(?:B|P|LZ)\d+", block.body):
        failures.append("缺少：M必须引用B或阶段素体")
    return failures


def validate_stage(block: PromptBlock) -> list[str]:
    required = [
        "16:9",
        "固定三列网格",
        "左栏约36%",
        "中栏约45%",
        "右栏约19%",
        "整高",
        "三等分",
        "阶段素体",
        "阶段人脸",
        "受控变化",
        "永久身份锚点",
        "阶段可变区",
        "绝对目标",
        "剪影级差",
        "正面头部大特写",
        "左前方45度身体",
        "正面身体",
        "背面身体",
        "无五官校准头模",
        "完全无头发",
        "哑光校准头模表面",
        "纯白",
        "不透明",
        "中等克重校准服",
        "立领前拉链长袖校准上衣",
        "全长校准裤",
        "白袜",
        "2—4cm活动松量",
        "标题固定右上",
        "说明固定右下",
        "固定纵坐标",
        "水平细白引线",
        "除头身比短标外",
        "当前完整参数",
        "相对上一阶段",
        "可见形体变化",
        "身高",
        "体重",
        "头身比",
        "肩宽",
        "胸围",
        "腰围",
        "臀围",
    ]
    failures = [f"缺少：{term}" for term in contains_all(block.body, required)]
    if not re.search(r"五官(?:比例|位置)[^。；\n]{0,120}(?:不变|保持)", block.body):
        failures.append("缺少：阶段脸永久身份保持")
    if re.search(r"全阶段最饱满|进一步饱满|自然皮肤张力|形成[^。；\n]{0,40}阶段脸受控变化", block.body):
        failures.append("阶段脸仍使用悬空比较、抽象质量词或作者解释")
    if not re.search(r"剪影级差[^。；\n]{0,160}(?:遮住五官|遮蔽五官|只看外轮廓)", block.body):
        failures.append("缺少：阶段脸外轮廓盲验")
    if uses_disallowed_parameter_panel(block.body):
        failures.append("阶段参数区位置偏离固定右栏")
    return failures


def validate_w(block: PromptBlock) -> list[str]:
    common_required = {
        "16:9": r"16:9",
        "服装资产": r"服装资产",
        "人物主视觉参考": r"(?:人物主视觉|写真母图|写真)参考",
        "服装设计描述": r"服装设计描述",
        "材料": r"材料|主料|面料|丝麻|细麻|粗麻|软革|里布",
        "严格正背": r"严格正背|严格正面[^。；\n]{0,80}严格背面",
        "平铺": r"平铺",
        "活动余量": r"活动余量|动作余量|奔跑|盘坐|拔剑|举剑|深蹲|托举",
        "鞋履": r"鞋履|鞋底|短靴|长靴|软底鞋|窄靴|软靴",
    }
    failures = [
        f"缺少：{label}"
        for label, pattern in common_required.items()
        if not re.search(pattern, block.body)
    ]

    if "可拆套装分件拆解板" in block.body or "2行×2列" in block.body:
        component_required = {
            "固定2行×2列": r"固定2行×2列",
            "上装区": r"左上[^。；\n]{0,60}(?:展示|上装)",
            "下装区": r"右上[^。；\n]{0,60}(?:展示|下装)",
            "配件与鞋履区": r"左下[^。；\n]{0,80}(?:陈列|展示)[^。；\n]{0,100}(?:鞋|靴)",
            "材质与活动结构区": r"右下[^。；\n]{0,100}(?:材料|主料|丝麻|细麻|粗麻|软革|里布)",
            "平铺": r"平铺",
            "材料微距": r"微距",
        }
        failures.extend(
            f"可拆套装缺少：{label}"
            for label, pattern in component_required.items()
            if not re.search(pattern, block.body)
        )
    elif "连续主件完整展示板" in block.body:
        integrated_required = {
            "连续主件": r"连续主件|长袍",
            "左侧约三分之一": r"左侧约三分之一",
            "右侧约三分之二": r"右侧约三分之二",
            "无五官全身承托人台": r"无五官全身承托人台",
            "严格正背": r"严格正面[^。；\n]{0,80}严格背面|严格正背",
            "4列×3行细节矩阵": r"4列×3行[^。；\n]{0,40}(?:细节矩阵|十二格|12)",
            "内里": r"内里",
            "平铺": r"平铺",
            "材料微距": r"微距",
        }
        failures.extend(
            f"连续主件缺少：{label}"
            for label, pattern in integrated_required.items()
            if not re.search(pattern, block.body)
        )
    else:
        failures.append("缺少：根据服装主件结构选择可拆套装分件拆解板或连续主件完整展示板")

    forbidden = ["必要时补左前方45度", "全身人物三视图"]
    failures.extend(f"禁止：{term}" for term in forbidden if term in block.body)
    if re.search(
        r"(?:人物|角色|身体)(?:的)?(?:身高|体重|头身比|肩宽|胸围|腰围|臀围|颈围|上臂围|大腿围|小腿围)"
        r"\s*(?:约|为|：|:)?\s*\d"
        r"|(?:^|[，。；：\s])(?:身高|体重|头身比)\s*(?:约|为|：|:)?\s*\d",
        block.body,
    ):
        failures.append("人物身体参数不得进入W")
    if not re.search(r"【(?:人物主视觉|写真母图|写真)参考@F\d+", block.body):
        failures.append("缺少：W必须引用人物主视觉图F")
    unresolved_meta = ["身份场景活动推导", "当前阶段适配", "材料必须清楚", "平均答案回避"]
    failures.extend(f"W仍含未完成元要求：{term}" for term in unresolved_meta if term in block.body)
    return failures


def classify(block: PromptBlock) -> str | None:
    if re.match(r"F\d+", block.heading):
        return "F"
    if re.match(r"M\d+", block.heading):
        return "M"
    if re.match(r"B\d+", block.heading):
        return "B"
    if re.match(r"(?:P\d+|LZ\d+)", block.heading):
        return "P"
    if re.match(r"W\d+", block.heading):
        return "W"
    first_line = block.body.splitlines()[0] if block.body.splitlines() else ""
    if re.match(r"F\d+[^。\n]*写真(?:参考|母图)", first_line):
        return "F"
    if re.match(r"B\d+[^。\n]*素体", first_line):
        return "B"
    if re.match(r"(?:P\d+|LZ\d+)[^。\n]*(?:阶段|素体)", first_line):
        return "P"
    if re.match(r"W\d+[^。\n]*服装", first_line):
        return "W"
    if re.search(r"(?<![A-Za-z0-9])M\d+(?!\d)", first_line):
        return "M"
    return None


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: validate_character_asset_structure.py <asset.md>", file=sys.stderr)
        return 2

    path = Path(sys.argv[1])
    if not path.is_file():
        print(f"missing file: {path}", file=sys.stderr)
        return 2

    typed = [(classify(block), block) for block in read_blocks(path.read_text(encoding="utf-8"))]
    typed = [(kind, block) for kind, block in typed if kind is not None]
    if not typed:
        print("FAIL: no F/B/P-stage/W/M prompt blocks found", file=sys.stderr)
        return 1

    failures = 0
    for kind, block in typed:
        assert kind is not None
        validators = {"F": validate_f, "B": validate_b, "P": validate_stage, "W": validate_w, "M": validate_m}
        issues = validators[kind](block)
        id_pattern = r"(?:P\d+|LZ\d+)" if kind == "P" else rf"{kind}\d+"
        # Prefer the asset's own heading. Stage prompts often reference the
        # previous phase first, which would otherwise mislabel LZ70 as LZ60.
        label_match = re.match(id_pattern, block.heading) or re.search(
            rf"(?<![A-Za-z0-9]){id_pattern}(?!\d)", block.body
        )
        label = label_match.group(0) if label_match else f"{kind}@{block.line}"
        if issues:
            failures += 1
            print(f"FAIL: {label} line={block.line}: " + "；".join(issues))
        else:
            print(f"PASS: {label} line={block.line}")

    f_ids = {re.match(r"F\d+", block.heading).group(0) for kind, block in typed if kind == "F" and re.match(r"F\d+", block.heading)}
    b_ids = {re.match(r"B\d+", block.heading).group(0) for kind, block in typed if kind == "B" and re.match(r"B\d+", block.heading)}
    w_ids = {re.match(r"W\d+", block.heading).group(0) for kind, block in typed if kind == "W" and re.match(r"W\d+", block.heading)}
    m_ids = {re.match(r"M\d+", block.heading).group(0) for kind, block in typed if kind == "M" and re.match(r"M\d+", block.heading)}
    for f_id in sorted(f_ids):
        suffix = f_id[1:]
        expected_assets = [f"B{suffix}", f"W{suffix}", f"M{suffix}"]
        missing_assets = [asset for asset in expected_assets if asset not in b_ids | w_ids | m_ids]
        if missing_assets:
            failures += 1
            print(f"FAIL: {f_id}: 缺少同编号反向拆解资产：" + "、".join(missing_assets))
    for kind, block in typed:
        if kind != "B":
            continue
        b_match = re.match(r"B(\d+)", block.heading)
        if not b_match:
            continue
        expected_f = f"F{b_match.group(1)}"
        if expected_f in f_ids and not re.search(rf"【(?:人物主视觉|写真母图|写真)参考@{expected_f}】", block.body):
            failures += 1
            print(f"FAIL: {b_match.group(0)} line={block.line}: 缺少对应人物主视觉参考@{expected_f}")
    for kind, block in typed:
        if kind not in {"W", "M"}:
            continue
        match = re.match(rf"{kind}(\d+)", block.heading)
        if not match:
            continue
        expected_f = f"F{match.group(1)}"
        if expected_f in f_ids and not re.search(rf"【(?:人物主视觉|写真母图|写真)参考@{expected_f}】", block.body):
            failures += 1
            print(f"FAIL: {match.group(0)} line={block.line}: 缺少对应人物主视觉参考@{expected_f}")

    if failures:
        print(f"character asset validation failed: {failures} block(s)", file=sys.stderr)
        return 1
    print(f"character asset validation passed: {len(typed)} block(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
