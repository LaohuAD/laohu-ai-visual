#!/usr/bin/env python3
"""Verify the actual capability graph and verbatim migration units; does not score output quality."""
from pathlib import Path
import hashlib
import json
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
REGISTRY = ROOT / '02_共享资产库/05_工具流程/能力注册表.json'
MANIFEST = ROOT / '04_诊断与系统日志/视觉能力重构迁移清单.json'

def sha(text):
    return hashlib.sha256(text.encode()).hexdigest()

def check(root=ROOT, require_manifest=True):
    failures=[]
    registry=json.loads((root/REGISTRY.relative_to(ROOT)).read_text())
    nodes=registry['skills']; names={n['name'] for n in nodes}
    actual={str(p.relative_to(root)) for p in (root/'skills').rglob('SKILL.md')}
    declared={n['path'] for n in nodes}
    if len(names)!=len(nodes): failures.append('duplicate professional names')
    if actual!=declared: failures.append(f'registry drift: extra={actual-declared}; missing={declared-actual}')
    entries=[n for n in nodes if n['parent'] is None]
    if len(entries)!=registry['entry_count']: failures.append('entry count drift')
    if len(nodes)-len(entries)!=registry['specialist_count']: failures.append('specialist count drift')
    for n in nodes:
        p=root/n['path']
        if not p.exists(): continue
        text=p.read_text()
        if not re.search(r'^name: '+re.escape(n['name'])+r'\s*$',text,re.M): failures.append(f"metadata mismatch: {p}")
        if not re.search(r'^description: .+',text,re.M): failures.append(f"missing trigger: {p}")
        if n['parent'] and n['parent'] not in names: failures.append(f"unknown parent: {p}")
        if n['kind']=='specialist' and n['parent']!='laohu-script-writer':
            for layer in ['灵魂','筋骨','血肉','表皮']:
                if not re.search(r'^#{2,3} .*'+layer,text,re.M): failures.append(f"missing concrete layer {layer}: {p}")
            refs=list((p.parent/'references').glob('*.md'))
            if not refs: failures.append(f"no professional reference: {p}")
            if not any(len(r.read_text())>=500 for r in refs): failures.append(f"empty professional reference: {p}")
        for doc in [p,*list((p.parent/'references').glob('*.md'))]:
            body=doc.read_text()
            if body.count('```')%2: failures.append(f"unclosed code fence: {doc}")
            for link in re.findall(r'\]\(([^)]+)\)',body):
                val=link.split('#',1)[0]
                if not val or re.match(r'^[a-z]+:',val): continue
                if not (doc.parent/val).exists(): failures.append(f"broken method link: {doc} -> {val}")
    if require_manifest:
        manifest=json.loads((root/MANIFEST.relative_to(ROOT)).read_text())
        if manifest['status']!='COMPLETE': failures.append('migration not complete')
        base=manifest['baseline_ref']; cache={}; coverage={}
        for unit in manifest.get('units',[]):
            src=unit['source_path']; target=root/unit['target_path'] if unit.get('target_path') else None
            if src not in cache: cache[src]=subprocess.check_output(['git','show',base+':'+src],cwd=root,text=True)
            original=cache[src][unit['source_start']:unit['source_end']]
            if sha(original)!=unit['source_sha256']: failures.append(f"source unit changed: {unit['id']}")
            coverage.setdefault(src,[]).append((unit['source_start'],unit['source_end']))
            if unit.get('action') == 'RETIRE':
                if not unit.get('retirement_evidence') or unit.get('retired_text') != original: failures.append(f"unjustified retirement: {unit['id']}")
                continue
            if not target.exists(): failures.append(f"target missing: {unit['id']}"); continue
            from scripts.validate_segmentation_migration import read_before
            current=read_before(target,root); a=unit['target_start']; chunk=current[a:a+unit['target_characters']]
            if sha(chunk)!=unit['target_sha256']: failures.append(f"target unit changed: {unit['id']}")
        for src,spans in coverage.items():
            cursor=0
            for a,b in sorted(spans):
                if a!=cursor: failures.append(f'gap/overlap in source coverage: {src}:{cursor}->{a}')
                cursor=b
            if cursor!=len(cache[src]): failures.append(f'incomplete source coverage: {src}')
        expected={x['path'] for x in manifest['baseline_files']}
        if expected!=set(coverage): failures.append('baseline file coverage drift')
    return failures

if __name__=='__main__':
    failures=check(require_manifest='--structure-only' not in sys.argv)
    for error in failures: print('FAIL:',error)
    print(f"visual restructure: {'FAIL' if failures else 'PASS'} ({len(failures)} errors; text/structure only)")
    sys.exit(bool(failures))
