#!/usr/bin/env python3
"""Verify the authorized contract evolution and recover previous text for historical migrations."""
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
MANIFEST='04_诊断与系统日志/视频分段迁移清单.json'


def sha(text):
    return hashlib.sha256(text.encode()).hexdigest()


def read_before(path,root=ROOT):
    path=Path(path)
    relative=str(path.relative_to(root)) if path.is_absolute() else str(path)
    from scripts.package_history import read_pre_package
    relative,current=read_pre_package(relative,root)
    # Reverse only explicitly recorded subsequent evolution, then audit the historical migration.
    update=root/'04_诊断与系统日志/外部能力同步清单.json'
    if update.exists():
        newer=json.loads(update.read_text()).get('evolution_files',[])
        evolved=next((r for r in newer if r['path']==relative),None)
        if evolved:
            if sha(current)!=evolved['after_sha256']:
                raise ValueError('current external evolution target changed: '+relative)
            for edit in reversed(evolved['edits']):
                current=current[:edit['after_start']]+edit['before_text']+current[edit['after_end']:]
            if sha(current)!=evolved['before_sha256']:
                raise ValueError('external evolution reconstruction failed: '+relative)
    records=json.loads((root/MANIFEST).read_text())['files']
    record=next((r for r in records if r['path']==relative),None)
    if record is None:return current
    if sha(current)!=record['after_sha256']:
        raise ValueError('current segmentation target changed: '+relative)
    previous=current
    for edit in reversed(record['edits']):
        a,b=edit['after_start'],edit['after_end']
        previous=previous[:a]+edit['before_text']+previous[b:]
    if sha(previous)!=record['before_sha256']:
        raise ValueError('segmentation baseline reconstruction failed: '+relative)
    return previous


def check(root=ROOT):
    data=json.loads((root/MANIFEST).read_text());errors=[]
    for record in data['files']:
        try:read_before(record['path'],root)
        except (ValueError,OSError) as exc:errors.append(str(exc))
    for unit in data['semantic_units']:
        for target in unit['targets']:
            from scripts.package_history import physical_path
            text=physical_path(target['path'],root).read_text()
            for anchor in target['anchors']:
                if anchor not in text:errors.append(unit['id']+': missing '+anchor)
    return errors


if __name__=='__main__':
    errors=check()
    for error in errors:print('FAIL:',error)
    print('segmentation migration:', 'FAIL' if errors else 'PASS', '(source/route only)')
    raise SystemExit(bool(errors))
