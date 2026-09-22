#!/usr/bin/env bash
# 三段式视频提示词结构校验：参数与文件边界由本外壳处理，分区、分标签检查交给
# 同目录的词法辅助 video_prompt_lexing.py（唯一围栏/载荷实现），本文件不复制第二份。
set -euo pipefail

usage() {
  printf 'Usage: %s <markdown-file> [--limit N] [--profile seedance|h3|kling] [--block N]...\n' "$(basename "$0")" >&2
}

if [[ $# -lt 1 ]]; then
  usage
  exit 2
fi

file="$1"
shift
limit=""
profile="seedance"
blocks=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --limit)
      [[ $# -ge 2 && "$2" =~ ^[1-9][0-9]*$ ]] || { usage; exit 2; }
      limit="$2"
      shift 2
      ;;
    --profile)
      [[ $# -ge 2 ]] || { usage; exit 2; }
      case "$2" in
        seedance|h3|kling) profile="$2" ;;
        *) printf 'Unknown profile: %s\n' "$2" >&2; usage; exit 2 ;;
      esac
      shift 2
      ;;
    --block)
      [[ $# -ge 2 && "$2" =~ ^[1-9][0-9]*$ ]] || { usage; exit 2; }
      blocks="${blocks:+$blocks,}$2"
      shift 2
      ;;
    *)
      usage
      exit 2
      ;;
  esac
done

[[ -f "$file" ]] || { printf 'File not found: %s\n' "$file" >&2; exit 2; }

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LEXING="$ROOT/video_prompt_lexing.py"
[[ -f "$LEXING" ]] || { printf 'Missing lexical helper: %s\n' "$LEXING" >&2; exit 2; }

status=0
python3 - "$LEXING" "$file" "$profile" "$limit" "$blocks" <<'PY' || status=$?
"""Partition-aware structural checks for one raw three-section video prompt.

Selection rules (U22):
  * explicit --block N refers to the Nth fence of the whole Markdown file;
  * a production document (a heading that names an E-S-P card or a prompt section)
    contributes the fences inside that scope which really carry three-section
    headings, so an execution card's internal note block is not read as a prompt
    and a second, incomplete pending block is still reported;
  * any other file is a plain prompt test file and uses the shared auto-selection
    (text/prompt fences or fences with a real three-section heading).
"""
import re
import sys
from importlib import util as importlib_util
from pathlib import Path

HEADINGS = ("【基础设定】", "【场景状态与氛围画质】", "【画面内容】")
HEADING_LINE = re.compile(r"^(【[^\n】]+】)[ \t]*$", re.M)
HEADING_ANY = re.compile(r"^(#{1,6})[ \t]+(.+?)[ \t]*$", re.M)
ESP_CARD_ID = re.compile(r"E\d{2}-S\d{2}-P\d{2,}")
SHOT_HEADER = re.compile(r"【(?:C|镜头)(\d{2,})｜([^\n】]+)】")
FULL_SHOT_HEADER = re.compile(r"【(?:C|镜头)(\d{2,})｜[^｜】\n]+｜[^｜】\n]+｜[^】\n]+】")
COMPOUND_SETUP = re.compile(r"(?:硬切|软切|切(?:到|至|回|换|车内|车外|主观|客观))")
INTRASHOT_CUT = re.compile(
    r"(?:画面|镜头|摄影机)?(?:随即|随后|立即|然后|再|又)?\s*(?:硬切|软切|切到|切至|切回|切换到)"
)
VISIBLE_EVIDENCE = re.compile(
    r"(?:先看见|画面|镜头|前景|中景|后景|焦平面|构图|主体|人物|孩子|男人|女人|女生|男生|师兄|师妹)"
)
CHANGE_EVIDENCE = re.compile(
    r"(?:听到|说完|随后|然后|同时|当[^，。；\n]{0,30}时|开始|触发|才|转为|移向|抬起|落下|停住|变化)"
)
# 镜尾保留 is an audible landing point in the canonical H3/Kling samples.
ENDPOINT_EVIDENCE = re.compile(
    r"(?:最后|最终|停在|停住|锁住|保持|保留|结束|交给|定格|余响|余韵|落回|退入|出画|切入)"
)
AUTHOR_EXPLANATION = re.compile(
    r"(?:让观众|观众(?:看见|看到|感到|理解|知道|得到)|为了表现|为了说明|戏剧任务|表演任务|"
    r"人物调度目标|这一镜(?:证明|表达|说明)|形成[^。；\n]{0,40}受控变化)"
)
CONTRASTIVE = re.compile(r"不是[^。；\n]{0,48}而是")
AMBIGUOUS_FOCUS = re.compile(r"(?:焦点[^。；\n]{0,24}抬到|抬焦|跟焦到(?:情绪|眼神)|焦点扫向)")
DETACHED_DIALOGUE = re.compile(r"【(?:台词|对白)(?:-[^】]+)?】")
ABSOLUTE_TIME = re.compile(r"(?:片内\s*)?\d+(?:\.\d+)?\s*[—–-]\s*\d+(?:\.\d+)?\s*秒")
NEGATIVE_INSTRUCTION = re.compile(r"(?:不生成|不使用|不新增|不要出现|避免出现|禁止生成)")
# 有范围的音乐/声音政策：无配乐与不生成BGM是生产约束，只在基础设定内放行。
MUSIC_POLICY = re.compile(
    r"(?:不生成|不使用|不新增|不要出现|避免出现|禁止生成)\s*(?:BGM|bgm|Bgm|配乐|背景音乐|音乐)"
    r"|无(?:配乐|BGM|bgm|背景音乐)"
)
F_REFERENCE = re.compile(r"(?<![A-Za-z0-9])F(\d+)(?![\d.])")
F_CONTEXT = re.compile(r"(?:参考|引用|资产|写真|人物|身份|图片|素材|沿用|锁定|替代|代替|作为|绑定|@|【)")
TIMING_POLICY_LINE = re.compile(r"^[ \t]*timing_policy[ \t]*[:：][ \t]*(\S+)[ \t]*$", re.M)
TIMING_EVIDENCE_LINE = re.compile(r"^[ \t]*timing_evidence[ \t]*[:：][ \t]*(\S.*?)[ \t]*$", re.M)
TIMING_POLICIES = ("locked_audio", "real_timecode", "fixed_broadcast")
N04_ERROR_TEXT = (
    (re.compile(r"^HEADING_COUNT:(.+):(\d+)$"), r"\1 count=\2"),
    (re.compile(r"^SHOT_SEQUENCE:(\d+):(\d+)$"), r"shot sequence expected=\1 actual=\2"),
    (re.compile(r"^MISSING_SHOT_HEADER$"), "missing numbered shot header"),
    (re.compile(r"^CHARACTER_LIMIT:(\d+):(\d+)$"), r"chars=\1 exceeds limit=\2"),
)


def load_lexing(path: str):
    spec = importlib_util.spec_from_file_location("laohu_video_prompt_lexing", path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load lexical helper: {path}")
    module = importlib_util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def mask_of(lex, text: str, profile: str) -> str:
    spans, _ = lex.payload_spans(text, profile)
    return lex.mask_spans(text, spans)


def outside_fences(source: str, lex) -> str:
    """The document contract around the prompts; a block cannot grant itself an exception."""
    lines = source.splitlines()
    fenced = set()
    for block in lex.scan_fences(source):
        fenced.update(range(block.opening_line, block.closing_line + 1))
    return "\n".join("" if number in fenced else line for number, line in enumerate(lines, 1))


def has_heading(masked: str) -> bool:
    return any(re.search(r"^" + re.escape(h) + r"\s*$", masked, re.M) for h in HEADINGS)


def prompt_scopes(source: str, lex):
    """Return the 1-based heading scopes that declare a prompt (E-S-P card or 提示词)."""
    lines = source.splitlines()
    fenced = set()
    for block in lex.scan_fences(source):
        fenced.update(range(block.opening_line, block.closing_line + 1))
    heading_rows = []
    for number, line in enumerate(lines, 1):
        if number in fenced:
            continue
        match = HEADING_ANY.match(line)
        if match:
            heading_rows.append((number, len(match.group(1)), match.group(2).strip()))
    scopes = []
    for position, (number, level, text) in enumerate(heading_rows):
        if not (ESP_CARD_ID.search(text) or "提示词" in text):
            continue
        last = len(lines)
        for later_number, later_level, _ in heading_rows[position + 1:]:
            if later_level <= level:
                last = later_number - 1
                break
        scopes.append((text, number, last))
    return scopes


def card_selection(source: str, lex, profile: str):
    """Return (selected fence indices, cards that declared a prompt without a block)."""
    scopes = prompt_scopes(source, lex)
    if not scopes:
        return None, []
    blocks = lex.scan_fences(source)
    selected = []
    failures = []
    for name, first, last in scopes:
        picked = [
            index
            for index, block in enumerate(blocks, 1)
            if first <= block.opening_line <= last and has_heading(mask_of(lex, block.text, profile))
        ]
        if not picked:
            failures.append(name)
        for index in picked:
            if index not in selected:
                selected.append(index)
    return selected, failures


def sections(view: str):
    found = []
    for match in HEADING_LINE.finditer(view):
        if match.group(1) in HEADINGS and all(item[0] != match.group(1) for item in found):
            found.append((match.group(1), match.start(), match.end()))
    found.sort(key=lambda item: item[1])
    if [item[0] for item in found] != list(HEADINGS):
        return None
    spans = {}
    for position, (name, _, end) in enumerate(found):
        stop = found[position + 1][1] if position + 1 < len(found) else len(view)
        spans[name] = view[end:stop]
    return spans


def timing_policy(contract: str):
    declared = TIMING_POLICY_LINE.search(contract)
    if not declared:
        return None, []
    policy = declared.group(1)
    evidence = TIMING_EVIDENCE_LINE.search(contract)
    if policy not in TIMING_POLICIES:
        return None, [f"unknown timing_policy={policy}"]
    if not evidence or not evidence.group(1).strip():
        return None, [f"timing_policy={policy} declared without evidence"]
    return policy, []


def semantic_errors(view: str, policy):
    errors = []
    spans = sections(view)
    if spans:
        basic, atmosphere, picture = spans[HEADINGS[0]], spans[HEADINGS[1]], spans[HEADINGS[2]]
        negative_view = MUSIC_POLICY.sub(" ", basic) + atmosphere + picture
    else:
        picture = view
        negative_view = view

    headers = list(SHOT_HEADER.finditer(picture))
    if not headers:
        errors.append("missing numbered shot header")
    else:
        for expected, match in enumerate(headers, 1):
            if int(match.group(1)) != expected:
                errors.append(f"shot sequence expected={expected:02d} actual={match.group(1)}")
            fields = match.group(2).split("｜")
            if any(COMPOUND_SETUP.search(field) for field in fields[:2]):
                errors.append(
                    f"{match.group(0)} embeds multiple camera setups in shot-size or viewpoint field; "
                    "start a new numbered shot"
                )
        if len(list(FULL_SHOT_HEADER.finditer(picture))) != len(headers):
            errors.append(
                "shot header must include shot size, camera/viewpoint, and camera path/transition; "
                "complex headers may append composition and rhythm summaries"
            )
        for position, match in enumerate(headers):
            stop = headers[position + 1].start() if position + 1 < len(headers) else len(picture)
            body = picture[match.end():stop]
            header = match.group(0)
            if not VISIBLE_EVIDENCE.search(body):
                errors.append(f"{header} missing visible starting evidence")
            if not CHANGE_EVIDENCE.search(body):
                errors.append(f"{header} missing triggered screen/sound change")
            if not ENDPOINT_EVIDENCE.search(body):
                errors.append(f"{header} missing visible/audible endpoint")
            if INTRASHOT_CUT.search(body):
                errors.append(f"{header} contains an intrashot cut; end the shot and start a new numbered shot")

    if ABSOLUTE_TIME.search(view) and policy is None:
        errors.append("absolute second range found")
    if NEGATIVE_INSTRUCTION.search(negative_view):
        errors.append("direct negative generation instruction found")
    if AUTHOR_EXPLANATION.search(view):
        errors.append("author explanation found")
    if CONTRASTIVE.search(view):
        errors.append("contrastive author explanation found")
    if AMBIGUOUS_FOCUS.search(view):
        errors.append("ambiguous focus/camera movement phrase found")
    if DETACHED_DIALOGUE.search(view):
        errors.append("detached dialogue rail found; dialogue must be embedded in shot prose")
    # F01 资产资格只在引用/身份上下文成立；摄影 F1.4 一类光圈写法不是资产引用。
    for match in F_REFERENCE.finditer(view):
        window = view[max(0, match.start() - 24):match.end() + 24]
        before = view[match.start() - 1] if match.start() else ""
        if before in {"@", "【"} or F_CONTEXT.search(window):
            errors.append(
                "F portrait reference is a B-only production intermediate and cannot enter video prompts"
            )
            break
    return errors


def translate(errors):
    translated = []
    for error in errors:
        for pattern, replacement in N04_ERROR_TEXT:
            if pattern.match(error):
                error = pattern.sub(replacement, error)
                break
        translated.append(error)
    return list(dict.fromkeys(translated))


def report(result, limit, policy):
    errors = translate(result["errors"] + result["semantic"])
    line = "block=%d chars=%d limit=%s shots=%d status=%s" % (
        result["block"], result["characters"], limit if limit is not None else "none",
        result["shots"], "FAIL" if errors else "PASS",
    )
    if policy:
        line += f" timing_policy={policy}"
    if errors:
        line += " errors=" + "; ".join(errors)
    print(line)
    return bool(errors)


def collect(lex, source, profile, limit, explicit):
    if explicit is not None:
        return lex.inspect_markdown(source, profile, limit, explicit), []
    selected, card_failures = card_selection(source, lex, profile)
    if selected is None:
        return lex.inspect_markdown(source, profile, limit), []
    blocks = lex.scan_fences(source)
    results = []
    for index in selected:
        item = lex.inspect_prompt(blocks[index - 1].text, profile, limit)
        item["block"] = index
        results.append(item)
    if not results and not card_failures:
        raise lex.LexError("NO_SELECTED_PROMPT_BLOCK")
    return results, card_failures


def main(argv):
    lexing_path, file_path, profile, limit_raw, blocks_raw = argv
    lex = load_lexing(lexing_path)
    limit = int(limit_raw) if limit_raw else None
    explicit = [int(item) for item in blocks_raw.split(",") if item] if blocks_raw else None
    try:
        source = Path(file_path).read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        print(f"Cannot read {file_path}: {exc}", file=sys.stderr)
        return 2
    try:
        results, card_failures = collect(lex, source, profile, limit, explicit)
    except lex.LexError as exc:
        if "NO_SELECTED_PROMPT_BLOCK" in str(exc):
            print(f"No video prompt text block found: {file_path}", file=sys.stderr)
        elif "UNCLOSED_FENCE" in str(exc):
            print(f"Unclosed code block found: {file_path}", file=sys.stderr)
        else:
            print(f"Requested prompt block does not exist: {file_path}", file=sys.stderr)
        return 2

    policy, policy_errors = timing_policy(outside_fences(source, lex))
    failed = bool(policy_errors)
    for message in policy_errors:
        print(f"document status=FAIL errors={message}")
    for name in card_failures:
        print(f"card={name} status=FAIL errors=declares a prompt but has no code block")
        failed = True
    for result in results:
        result["semantic"] = semantic_errors(result["control_view"], policy)
        failed = report(result, limit, policy) or failed
    # 词法通过只证明结构与分区检查；引用清单、实际文件、标签语义和演员是否真在说话
    # 仍由检视逐项进行，本脚本不改写这四项的 NOT_CHECKED 结论。
    print(
        "note=syntax_only reference=NOT_CHECKED semantic=NOT_CHECKED "
        "provider=NOT_CHECKED media=NOT_CHECKED",
        file=sys.stderr,
    )
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:6]))
PY
exit "$status"
