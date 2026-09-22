"""Resolve where a migrated skill file lives today, for audits and history tools.

The six top-level skill packages are the only skill holders in this repository. When a
whole capability is extracted into another package, the historical migration ledger
(``04_诊断与系统日志/五包迁移清单.json``) still records the pre-extraction address while
the file exists at its new address. This module holds that address translation once, so
``sync_skill_packages``, ``package_history`` and ``record_method_evolution`` resolve the
same canonical file instead of each guessing a path.
"""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACKAGES = (
    "laohu-ai-visual",
    "laohu-script-writer",
    "laohu-image-creation",
    "laohu-video-prompt",
    "laohu-language-mode",
    "laohu-inspection",
)
ENTRY_PACKAGES = frozenset(PACKAGES)

# Capabilities extracted into the sixth package. The record is keyed by the historical
# directory, and every file under it keeps its relative address inside the new package.
PACKAGE_EXTRACTIONS = {
    ".agents/skills/laohu-ai-visual/skills/laohu-generation-review":
        ".agents/skills/laohu-inspection/skills/laohu-generation-review",
    ".agents/skills/laohu-video-prompt/scripts":
        ".agents/skills/laohu-inspection/scripts",
}

# Files that were also renamed while moving, keyed by their historical address.
MOVED_FILES = {
    # renamed inside the package that later received the review capability
    ".agents/skills/laohu-video-prompt/references/模板_视频生成质量检查清单.md":
        ".agents/skills/laohu-inspection/references/视频生成质量检查清单.md",
    # renamed in place while the review/verification content was extracted
    ".agents/skills/laohu-video-prompt/references/交接与验收.md":
        ".agents/skills/laohu-video-prompt/references/交接与路由.md",
    ".agents/skills/laohu-image-creation/references/图片验收与封面交接.md":
        ".agents/skills/laohu-image-creation/references/图片生成执行与封面交接.md",
    ".agents/skills/laohu-script-writer/references/剧本质量取舍与综合验收.md":
        ".agents/skills/laohu-script-writer/references/剧本质量取舍.md",
    ".agents/skills/laohu-ai-visual/skills/laohu-mv-director/references/03_MV导演交接与文本验收.md":
        ".agents/skills/laohu-ai-visual/skills/laohu-mv-director/references/03_MV导演交接.md",
    ".agents/skills/laohu-video-prompt/skills/laohu-video-compilation/references/镜头特征取舍与质量验收.md":
        ".agents/skills/laohu-video-prompt/skills/laohu-video-compilation/references/镜头特征取舍.md",
}


def current_location(relative: str, root: Path = ROOT) -> str:
    """Return the address that holds ``relative`` today.

    A recorded address is kept whenever the file is really there; otherwise the rename
    records are applied first and the extraction records second, because a file can be
    renamed inside the package that later receives it. Paths outside the packages return
    unchanged, so this function never invents an address for an ordinary file.
    """
    relative = str(relative)
    root = Path(root)
    if (root / relative).is_file():
        return relative
    if relative in MOVED_FILES:
        return MOVED_FILES[relative]
    for old, new in sorted(PACKAGE_EXTRACTIONS.items(), key=lambda item: -len(item[0])):
        if relative == old or relative.startswith(old + "/"):
            return new + relative[len(old):]
    path = Path(relative)
    if path.name.startswith("reference") and path.suffix == ".md":
        candidate = (path.parent / "references" / path.name).as_posix()
        if (root / candidate).is_file():
            return candidate
    return relative
