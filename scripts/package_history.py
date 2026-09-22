"""Resolve and reconstruct pre-package files for historical audits, never for runtime skills."""
from pathlib import Path
import hashlib
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.skill_package_layout import current_location

MANIFEST = "04_诊断与系统日志/五包迁移清单.json"


def physical_path(path, root=ROOT):
    """Return the file that holds a recorded path today.

    The migration ledger resolves old tree layouts, moved files and merged methods; what
    it cannot resolve is a capability extracted into another top-level package, so that
    last step is delegated to the shared package-layout record.
    """
    path = Path(path)
    root = Path(root)
    relative = str(path.relative_to(root)) if path.is_absolute() else str(path)
    mapped = relative
    manifest = root / MANIFEST
    if manifest.is_file():
        data = json.loads(manifest.read_text())
        if relative in data.get("shared_moves", {}):
            return root / data["shared_moves"][relative]
        # Methods merged into another file this round: the successor holds the text.
        if relative in data.get("method_redirects", {}):
            return root / data["method_redirects"][relative]
        for old, new in sorted(data.get("layout", {}).items(), key=lambda item: -len(item[0])):
            if relative == old or relative.startswith(old + "/"):
                mapped = new + relative[len(old):]
                if (root / mapped).is_file():
                    return root / mapped
                break
    return root / current_location(mapped, root)


_RECORD_CACHE: dict = {}


def _records_by_current_path(root):
    """Map each recorded target to the address that holds it today.

    Records are keyed by the name a file carried when the migration was written; a later
    rename must still find them, so the lookup follows the same rename and extraction
    records as ``current_location``. The mapping is rebuilt only when the ledger changes,
    because historical audits resolve it once per unit.
    """
    manifest = Path(root) / MANIFEST
    if not manifest.is_file():
        return {}
    stamp = manifest.stat().st_mtime_ns
    cached = _RECORD_CACHE.get(str(manifest))
    if cached and cached[0] == stamp:
        return cached[1]
    mapping = {}
    for record in json.loads(manifest.read_text()).get("files", []):
        mapping.setdefault(current_location(record["new_path"], root), record)
    _RECORD_CACHE[str(manifest)] = (stamp, mapping)
    return mapping


def read_pre_package(path, root=ROOT):
    current_path = physical_path(path, root)
    relative = str(current_path.relative_to(root))
    current = current_path.read_text()
    manifest = Path(root) / MANIFEST
    if not manifest.is_file():
        return relative, current
    record = _records_by_current_path(root).get(relative)
    if record is None:
        return relative, current
    digest = lambda text: hashlib.sha256(text.encode()).hexdigest()
    if digest(current) != record["after_sha256"]:
        raise ValueError("package target changed without recorded evolution: " + relative)
    for edit in reversed(record.get("inverse_edits", [])):
        current = current[:edit["after_start"]] + edit["before_text"] + current[edit["after_end"]:]
    if digest(current) != record["before_sha256"]:
        raise ValueError("package reconstruction failed: " + relative)
    return record["old_path"], current
