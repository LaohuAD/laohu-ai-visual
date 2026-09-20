"""Resolve and reconstruct pre-package files for historical audits, never for runtime skills."""
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = "04_诊断与系统日志/五包迁移清单.json"


def physical_path(path, root=ROOT):
    path = Path(path)
    relative = str(path.relative_to(root)) if path.is_absolute() else str(path)
    manifest = Path(root) / MANIFEST
    if manifest.is_file():
        data = json.loads(manifest.read_text())
        if relative in data.get("shared_moves", {}):
            return Path(root) / data["shared_moves"][relative]
        for old, new in sorted(data.get("layout", {}).items(), key=lambda item: -len(item[0])):
            if relative == old or relative.startswith(old + "/"):
                return Path(root) / (new + relative[len(old):])
    return Path(root) / relative


def read_pre_package(path, root=ROOT):
    current_path = physical_path(path, root)
    relative = str(current_path.relative_to(root))
    current = current_path.read_text()
    manifest = Path(root) / MANIFEST
    if not manifest.is_file():
        return relative, current
    record = next((r for r in json.loads(manifest.read_text()).get("files", []) if r["new_path"] == relative), None)
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
