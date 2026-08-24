#!/usr/bin/env python3
"""Validate B/P-stage/W/M character production boards."""

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


def read_blocks(text: str) -> list[PromptBlock]:
    blocks: list[PromptBlock] = []
    heading = ""
    lines = text.splitlines()
    index = 0
    while index < len(lines):
        line = lines[index]
        if line.startswith("### "):
            heading = line[4:].strip()
        if line.strip() == "```text":
            start = index + 2
            body_lines: list[str] = []
            index += 1
            while index < len(lines) and lines[index].strip() != "```":
                body_lines.append(lines[index])
                index += 1
            blocks.append(PromptBlock(heading, "\n".join(body_lines), start))
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
        "无五官假人头模",
        "完全无头发",
        "哑光人台表面",
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
    return failures


def validate_m(block: PromptBlock) -> list[str]:
    required = [
        "16:9",
        "2行×3列",
        "左前方45度",
        "正面",
        "背面",
        "上排",
        "头部",
        "下排",
        "鞋底",
        "妆造记忆锚点",
        "穿着方式",
        "阶段变化",
        "克制边界",
    ]
    failures = [f"缺少：{term}" for term in contains_all(block.body, required)]
    if not re.search(r"上排约(?:占(?:画面)?高度)?(?:的)?三分之一|上排约三分之一", block.body):
        failures.append("缺少：上排约三分之一")
    if not re.search(r"下排约(?:占(?:画面)?高度)?(?:的)?三分之二|下排约三分之二", block.body):
        failures.append("缺少：下排约三分之二")
    if not re.search(r"颈部根部|肩线以下", block.body):
        failures.append("缺少：下排从颈部根部或肩线以下开始")
    if "角度" not in block.body or not re.search(r"一一对应|严格对应|角度对应", block.body):
        failures.append("缺少：上下同列角度一一对应")
    if not re.search(r"三列纵向(?:组合|复合)|三组纵向(?:组合|复合)", block.body):
        failures.append("缺少：M必须组织为三列纵向复合，而非六张独立照片")
    if not re.search(r"下(?:排|部)[^。；\n]{0,100}无头[^。；\n]{0,60}(?:身体|躯体)", block.body):
        failures.append("缺少：下排必须是无头穿着身体")
    if not re.search(
        r"上(?:排|部)[^。；\n]{0,120}覆盖[^。；\n]{0,100}下(?:排|部)[^。；\n]{0,80}(?:头颅|头部)[^。；\n]{0,20}位置",
        block.body,
    ):
        failures.append("缺少：上部头部特写覆盖下部原头部位置")
    if not re.search(r"唯一对应头部", block.body):
        failures.append("缺少：上部特写是同列身体唯一对应头部")
    if not re.search(r"画框最高可见点[^。；\n]{0,100}(?:锁骨|肩峰|后领)", block.body):
        failures.append("缺少：下排画框最高可见点必须落在颈肩结构")
    if not re.search(r"头颅完整位于下(?:排|部)画框之外", block.body):
        failures.append("缺少：下排头颅必须完整位于画框之外")
    if not re.search(r"覆盖接缝[^。；\n]{0,80}(?:颈肩交界|服装领口)", block.body):
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
        "无五官假人头模",
        "完全无头发",
        "哑光人台表面",
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
    common_required = [
        "16:9",
        "人物服装资产",
        "身份场景活动推导",
        "服装主件结构判断",
        "服装轮廓",
        "当前阶段适配",
        "材料",
        "配色",
        "工艺",
        "固定服装视觉规格板",
        "图片信息为主",
        "名词性标题",
        "服装规格",
        "活动余量",
        "鞋履",
        "季节阶段",
        "人物化设计锚点",
        "连续继承",
        "阶段替换",
        "平均答案",
    ]
    failures = [f"缺少：{term}" for term in contains_all(block.body, common_required)]

    if "可拆套装分件拆解板" in block.body:
        component_required = [
            "固定2行×2列四象限",
            "上装拆解",
            "下装拆解",
            "配件与鞋履",
            "材质与活动余量",
            "上半身服装承托架",
            "下半身服装承托架",
            "无头无脸",
            "严格正面",
            "严格背面",
            "局部摄影",
            "展开平铺",
            "技术线稿",
            "材质微距",
        ]
        failures.extend(f"可拆套装缺少：{term}" for term in contains_all(block.body, component_required))
        if "全身服装承托人台" in block.body:
            failures.append("可拆套装不得继续用全身成套人台代替上下装独立承托架")
    elif "连续主件完整展示板" in block.body:
        integrated_required = [
            "单一连续主件",
            "不可拆分",
            "连续轮廓",
            "左侧约三分之一",
            "右侧约三分之二",
            "无五官全身服装承托人台",
            "完全无头发",
            "严格正面",
            "严格背面",
            "正面成套展示",
            "背面成套展示",
            "4列×3行",
            "12个",
            "近似正方形",
            "整件正面",
            "整件背面",
            "内里",
            "局部摄影",
            "展开平铺",
            "技术线稿",
            "材质微距",
        ]
        failures.extend(f"连续主件缺少：{term}" for term in contains_all(block.body, integrated_required))
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
    return failures


def classify(block: PromptBlock) -> str | None:
    if re.match(r"M\d+", block.heading):
        return "M"
    if re.match(r"B\d+", block.heading):
        return "B"
    if re.match(r"(?:P\d+|LZ\d+)", block.heading):
        return "P"
    if re.match(r"W\d+", block.heading):
        return "W"
    first_line = block.body.splitlines()[0] if block.body.splitlines() else ""
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
        print("FAIL: no B/P-stage/W/M prompt blocks found", file=sys.stderr)
        return 1

    failures = 0
    for kind, block in typed:
        assert kind is not None
        validators = {"B": validate_b, "P": validate_stage, "W": validate_w, "M": validate_m}
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

    if failures:
        print(f"character asset validation failed: {failures} block(s)", file=sys.stderr)
        return 1
    print(f"character asset validation passed: {len(typed)} block(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
