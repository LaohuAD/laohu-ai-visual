#!/usr/bin/env bash
set -euo pipefail
PACKAGE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
exec python3 - "$PACKAGE" <<'PYCODE'
from pathlib import Path
import sys,re
root=Path(sys.argv[1]);errors=[]
for p in root.rglob('SKILL.md'):
 t=p.read_text()
 if not re.search(r'^name: .+',t,re.M) or not re.search(r'^description: .+',t,re.M):errors.append(str(p))
for p in root.rglob('*'):
 if p.is_symlink():errors.append('symlink: '+str(p))
print('package structure:', 'PASS' if not errors else 'FAIL', errors)
raise SystemExit(bool(errors))
PYCODE
