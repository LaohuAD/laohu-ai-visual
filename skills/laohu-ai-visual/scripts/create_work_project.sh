#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"

# Python validates all arguments before writing and reads the same startup template
# that people use. The project remains IDEA regardless of its directory category.
exec python3 - "$ROOT" "$@" <<'PY'
import argparse
from datetime import date
from pathlib import Path
import re
import shutil
import subprocess
import sys

root = Path(sys.argv[1])
parser = argparse.ArgumentParser(
    prog="create_work_project.sh",
    description="按作品类型建立最小入口；目录分类不代表生产进度。",
)
parser.add_argument("name", help="作品名，不得含路径分隔符或控制字符")
parser.add_argument("date", nargs="?", default=date.today().isoformat(), help="yyyy-mm-dd")
parser.add_argument("status", nargs="?", default="进行中", choices=("进行中", "已完成", "已发布"))
parser.add_argument("--kind", choices=("story", "image", "mv"), default="story")
args = parser.parse_intermixed_args(sys.argv[2:])
if (not args.name.strip() or args.name != args.name.strip() or args.name in (".", "..")
        or any(c in "/\\" or ord(c) < 32 or ord(c) == 127 for c in args.name)):
    parser.error("作品名不能为空，不能含路径分隔符、控制字符、首尾空白或仅为 . / ..")
if len(args.name.encode("utf-8")) > 244:
    parser.error("作品名 UTF-8 编码不得超过 244 字节，须为日期前缀预留文件名空间")
try:
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", args.date):
        raise ValueError
    date.fromisoformat(args.date)
except ValueError:
    parser.error("日期必须是有效的 yyyy-mm-dd 日历日期")

project = root / "01_作品项目" / args.status / f"{args.date}_{args.name}"
if project.exists() or project.is_symlink():
    parser.exit(1, f"Project already exists: {project}\n")

template = root / "02_共享资产库/01_模板库/项目启动模板/模板_作品项目启动包.md"
renderer = root / "scripts/render_delivery_html.py"
try:
    source = template.read_text(encoding="utf-8")
    def section(name):
        match = re.search(rf"<!-- {name} -->\n(.*?)\n<!-- /{name} -->", source, re.S)
        if not match:
            raise ValueError(f"启动模板缺少区块：{name}")
        return match.group(1)

    values = {"作品名": args.name, "创建日期": args.date, "目录状态": args.status,
              "作品类型": args.kind, "分支路线": section(args.kind)}
    def fill(text):
        # One pass preserves literal placeholder-like text in user-provided names.
        return re.sub(r"\{\{([^{}]+)\}\}", lambda m: values[m[1]], text) + "\n"

    overview = fill(section("overview"))
    record = fill(section("record"))
    if not renderer.is_file():
        raise ValueError(f"缺少 HTML 交付渲染器：{renderer}")
except (OSError, ValueError, KeyError) as exc:
    parser.exit(1, f"无法准备作品入口：{exc}\n")

# Claim the destination once. On later failure, remove only the tree owned by
# this invocation; an existing work is never overwritten or cleaned up.
project.parent.mkdir(parents=True, exist_ok=True)
try:
    project.mkdir()
except FileExistsError:
    parser.exit(1, f"Project already exists: {project}\n")
try:
    (project / "00_原始输入/文本").mkdir(parents=True)
    if args.kind == "mv":
        (project / "00_原始输入/音频").mkdir()
    (project / "00_项目总览.md").write_text(overview, encoding="utf-8")
    (project / "00_阶段确认记录.md").write_text(record, encoding="utf-8")
    result = subprocess.run([sys.executable, str(renderer), "--project", str(project)],
                            text=True, capture_output=True)
    if result.returncode:
        raise RuntimeError(result.stderr or result.stdout or "HTML 渲染失败")
except (OSError, RuntimeError) as exc:
    shutil.rmtree(project)
    parser.exit(1, f"创建失败，已撤回本次作品入口：{exc}\n")
print(project)
PY
