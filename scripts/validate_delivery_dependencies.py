#!/usr/bin/env python3
"""Track reviewed file dependencies inside an existing stage record.

UNCHANGED means bytes match the review snapshot, never that pixels or prose are correct.
Only an explicit record command after professional review refreshes the snapshot.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import tempfile
from datetime import datetime, timezone
from pathlib import Path

MARKER = '<!-- delivery-dependencies -->'
BLOCK = re.compile(re.escape(MARKER) + r'\s*```json\n(.*?)\n```', re.S)
ROLES = {'first_frame', 'last_frame', 'style', 'identity', 'content', 'audio'}


def local_file(root, relative):
    root = Path(root).resolve()
    path = (root / relative).resolve()
    if not path.is_relative_to(root) or not path.is_file():
        raise ValueError(f'文件不存在或越出作品目录：{relative}')
    # resolve() does not restore actual spelling on a case-insensitive volume.
    canonical = root
    for part in path.relative_to(root).parts:
        target = canonical / part
        entries = list(canonical.iterdir())
        exact = next((p for p in entries if p.name == part), None)
        canonical = exact or next(p for p in entries if p.samefile(target))
    return canonical


def digest(path):
    result = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            result.update(chunk)
    return result.hexdigest()


def review_digest(entry):
    return hashlib.sha256(json.dumps(entry, sort_keys=True, ensure_ascii=False).encode()).hexdigest() if entry else None


def validate_graph(reviews):
    graph = {r['consumer']: [s['path'] for s in r['sources']] for r in reviews}
    visiting, done = set(), set()
    def visit(node):
        if node in visiting:
            raise ValueError('依赖图成环；按决定的实际先后拆清权威来源')
        if node in done:
            return
        visiting.add(node)
        for child in graph.get(node, []):
            visit(child)
        visiting.remove(node)
        done.add(node)
    for node in graph:
        visit(node)


def valid_relative(value):
    return isinstance(value, str) and bool(value) and not Path(value).is_absolute() and '..' not in Path(value).parts and Path(value).as_posix() == value and value != '.'


def valid_hash(value):
    return isinstance(value, str) and re.fullmatch('[0-9a-f]{64}', value) is not None


def read_record(record):
    text = Path(record).read_text(encoding='utf-8')
    matches = list(BLOCK.finditer(text))
    if text.count(MARKER) != len(matches) or len(matches) > 1:
        raise ValueError('依赖记录重复或格式损坏；保留原文，先修复记录')
    data = json.loads(matches[0].group(1)) if matches else {'schema': 1, 'reviews': []}
    if not isinstance(data, dict) or data.get('schema') != 1 or not isinstance(data.get('reviews'), list):
        raise ValueError('不支持的依赖记录格式')
    seen = set()
    for entry in data['reviews']:
        if not isinstance(entry, dict) or not all(entry.get(k) for k in ('consumer', 'sha256', 'sources', 'reason', 'reviewer', 'reviewed_at')):
            raise ValueError('依赖复验记录缺失来源、理由或审核身份')
        if not all(isinstance(entry[k], str) and entry[k].strip() for k in ('reason', 'reviewer', 'reviewed_at')):
            raise ValueError('复验说明、身份、时间必须为有效文本')
        try:
            timestamp = datetime.fromisoformat(entry['reviewed_at'])
            if timestamp.tzinfo is None:
                raise ValueError('复验时间需要时区')
        except ValueError as error:
            raise ValueError('无效复验时间') from error
        if not valid_relative(entry['consumer']) or not valid_hash(entry['sha256']):
            raise ValueError('消费者路径或哈希无效')
        if entry['consumer'] in seen:
            raise ValueError('同一消费者存在重复记录')
        seen.add(entry['consumer'])
        if not isinstance(entry['sources'], list) or not all(isinstance(s, dict) and isinstance(s.get('role'), str) and s['role'] in ROLES and valid_relative(s.get('path')) and valid_hash(s.get('sha256')) and 'review_sha256' in s and (s['review_sha256'] is None or valid_hash(s['review_sha256'])) for s in entry['sources']):
            raise ValueError('来源职责或哈希缺失')
    validate_graph(data['reviews'])
    return text, matches, data


def check_reviews(root, record):
    _, _, data = read_record(record)
    if not data['reviews']:
        raise ValueError('尚无实际复验记录；不能视为通过')
    # Reject hand-edited aliases and hard links that would create two graph identities.
    identities = {}
    for entry in data['reviews']:
        for relative in [entry['consumer']] + [s['path'] for s in entry['sources']]:
            try:
                path = local_file(root, relative)
            except ValueError:
                continue  # A missing source is reported as pending below.
            canonical = path.relative_to(Path(root).resolve()).as_posix()
            info = path.stat()
            identity = (info.st_dev, info.st_ino)
            if canonical != relative or identity in identities and identities[identity] != relative:
                raise ValueError(f'依赖路径存在别名，需使用唯一实际文件路径：{relative}')
            identities[identity] = relative
    results = []
    indexed = {r['consumer']: r for r in data['reviews']}
    for entry in data['reviews']:
        reasons = []
        for source in entry['sources']:
            if source['review_sha256'] != review_digest(indexed.get(source['path'])):
                reasons.append(f"上游复验依据改变：{source['path']}")
        for relative, expected in [(entry['consumer'], entry['sha256'])] + [(s['path'], s['sha256']) for s in entry['sources']]:
            try:
                changed = digest(local_file(root, relative)) != expected
            except ValueError:
                changed = True
            if changed:
                reasons.append(f'文件变化或缺失：{relative}')
        results.append(dict(entry, status='PENDING_REVIEW' if reasons else 'UNCHANGED', changes=reasons))
    # Propagate stale review conclusions even when a downstream source file is unchanged.
    while True:
        stale = {r['consumer'] for r in results if r['status'] == 'PENDING_REVIEW'}
        affected = [r for r in results if r['status'] == 'UNCHANGED' and any(s['path'] in stale for s in r['sources'])]
        if not affected:
            break
        for entry in affected:
            entry['status'] = 'PENDING_REVIEW'
            entry['changes'].append('上游依赖的复验结论已失效')
    return results


def record_review(root, record, consumer, sources, reason, reviewer):
    if not reason.strip() or not reviewer.strip() or not sources:
        raise ValueError('完成专业复验后才可记录；必须提供具体理由、审核身份和来源')
    root = Path(root).resolve()
    record = local_file(root, Path(record))
    consumer_path = local_file(root, consumer)
    if consumer_path == record:
        raise ValueError('阶段记录不能依赖自身哈希')
    canonical_consumer = consumer_path.relative_to(root).as_posix()
    text, matches, data = read_record(record)
    indexed = {r['consumer']: r for r in data['reviews']}
    source_records = []
    for role, relative in sources:
        path = local_file(root, relative)
        if role not in ROLES or path.samefile(consumer_path) or path.samefile(record):
            raise ValueError('来源职责无效或存在自依赖')
        source_path = path.relative_to(root).as_posix()
        source_records.append({'role': role, 'path': source_path, 'sha256': digest(path), 'review_sha256': review_digest(indexed.get(source_path))})
    entry = {'consumer': canonical_consumer, 'sha256': digest(consumer_path), 'sources': source_records,
             'reason': reason.strip(), 'reviewer': reviewer.strip(), 'reviewed_at': datetime.now(timezone.utc).isoformat()}
    data['reviews'] = [r for r in data['reviews'] if r['consumer'] != canonical_consumer] + [entry]
    # A cyclic evidence chain cannot establish which input was reviewed first.
    validate_graph(data['reviews'])
    block = MARKER + '\n```json\n' + json.dumps(data, ensure_ascii=False, indent=2) + '\n```'
    updated = text[:matches[0].start()] + block + text[matches[0].end():] if matches else text + '\n' + block + '\n'
    # Same-volume staging preserves the original record on ordinary write failure.
    with tempfile.NamedTemporaryFile('w', encoding='utf-8', dir=record.parent, delete=False) as handle:
        pending = Path(handle.name)
        try:
            handle.write(updated)
            handle.flush()
        except BaseException:
            pending.unlink(missing_ok=True)
            raise
    try:
        pending.replace(record)
    finally:
        pending.unlink(missing_ok=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['check', 'record'])
    parser.add_argument('--project', type=Path, required=True)
    parser.add_argument('--record', required=True, help='作品内既有阶段记录路径')
    parser.add_argument('--consumer')
    parser.add_argument('--source', action='append', default=[], help='职责=作品内路径；可重复')
    parser.add_argument('--reason')
    parser.add_argument('--reviewer')
    args = parser.parse_args()
    try:
        record = local_file(args.project, args.record)
        if args.action == 'record':
            if not args.consumer or not args.reason or not args.reviewer or any('=' not in s for s in args.source):
                raise ValueError('record 需要 consumer/source/reason/reviewer')
            record_review(args.project, record, args.consumer, [s.split('=', 1) for s in args.source], args.reason, args.reviewer)
        results = check_reviews(args.project, record)
        print(json.dumps({'evidence': 'FILE_FRESHNESS_ONLY', 'reviews': results}, ensure_ascii=False, indent=2))
        return int(any(r['status'] != 'UNCHANGED' for r in results))
    except (ValueError, OSError, TypeError, KeyError) as error:
        parser.exit(2, f'ERROR: {error}\n')


if __name__ == '__main__':
    raise SystemExit(main())
