#!/usr/bin/env python3
"""Check declared screenplay coverage and production references, not artistic quality."""
import argparse
import hashlib
import json
import re
from pathlib import Path


def validate(data):
    errors = []
    source = data['source']
    if hashlib.sha256(source.encode()).hexdigest() != data['source_sha256']:
        errors.append('source changed: revalidate affected parts and neighbors')
    assets = {a['id']: a for a in data.get('assets', [])}
    units = data['units']
    parts = data['parts']
    ids = [p['id'] for p in parts]
    if len(ids) != len(set(ids)):
        errors.append('duplicate part id')
    limits = data.get('duration_limits', [4, 30])
    expected_order = []
    for unit in units:
        a, b = unit['start'], unit['end']
        if not 0 <= a < b <= len(source):
            errors.append('invalid source unit range')
            continue
        selected = [p for p in parts if p.get('scene') == unit['scene']]
        cursor = a
        for p in selected:
            start, end = p['source_start'], p['source_end']
            if start != cursor or not start < end <= b:
                errors.append(f"{p['id']}: source gap, overlap or cross-scene range")
            if source[start:end] != p['excerpt']:
                errors.append(f"{p['id']}: excerpt differs from source")
            cursor = end
            expected_order.append(p['id'])
        if cursor != b:
            errors.append(f"{unit['scene']}: incomplete source coverage")
    if expected_order != ids:
        errors.append('source order or scene ownership mismatch')
    for left, right in zip(units, units[1:]):
        if left['end'] > right['start']:
            errors.append('source units overlap or reorder')
    for p in parts:
        if not re.fullmatch(re.escape(p['scene']) + r'-P\d{2,}', p['id']):
            errors.append(f"{p['id']}: invalid P namespace")
        lo, hi = p['seconds']
        handles = p.get('handles_seconds', 0)
        if not (handles >= 0 and 0 < lo <= hi and limits[0] <= lo + handles <= hi + handles <= limits[1]):
            errors.append(f"{p['id']}: duration including handles out of bounds")
        if not p.get('timing_basis'):
            errors.append(f"{p['id']}: missing performance timing basis")
        for ref in p.get('asset_refs', []):
            if ref not in assets:
                errors.append(f"{p['id']}: unknown base asset {ref}")
        for ref in p.get('bound_assets', []):
            asset = assets.get(ref, {})
            if asset.get('status') != 'verified' or not asset.get('path'):
                errors.append(f"{p['id']}: unavailable real binding {ref}")
        for ref in p.get('state_refs', []):
            if ref['method'] not in ['text', 'extract', 'precreate']:
                errors.append(f"{p['id']}: unknown state route")
            if ref.get('consumer') not in ids:
                errors.append(f"{p['id']}: unknown state consumer")
            if ref.get('status') == 'verified' and not ref.get('path'):
                errors.append(f"{p['id']}: planned state passed off as real")
        previous = p.get('continues')
        if previous:
            index = ids.index(p['id'])
            if index == 0 or ids[index - 1] != previous:
                errors.append(f"{p['id']}: continuation is not adjacent")
            elif parts[index - 1].get('end_state') != p.get('start_state'):
                errors.append(f"{p['id']}: direct continuation state mismatch")
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('plan', type=Path)
    args = parser.parse_args()
    try:
        errors = validate(json.loads(args.plan.read_text()))
    except (KeyError, TypeError, ValueError) as exc:
        errors = [f'invalid check data: {exc}']
    for error in errors:
        print('FAIL:', error)
    print('segmentation:', 'FAIL' if errors else 'PASS', '(declared coverage only; no performance test)')
    return bool(errors)


if __name__ == '__main__':
    raise SystemExit(main())
