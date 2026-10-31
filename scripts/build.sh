#!/bin/bash
# Build and validate both language artifacts from shared source.
set -euo pipefail
here=$(cd "$(dirname "$0")" && pwd)
root=$(cd "$here/.." && pwd)
out=${1:?Supply a new output directory outside the checkout}
python=${ANKI_PYTHON:-python3}
"$python" "$here/checks/verify-coverage.py"
# Preflight every destination before writing either package.
"$python" - "$root" "$out" <<'CHECK'
import json, sys
from pathlib import Path
root, out = map(lambda p: Path(p).resolve(), sys.argv[1:])
if out.is_relative_to(root) or out.exists():
    raise ValueError('Use a new output directory outside the source repository')
CHECK
mkdir -p "$out"
out=$(cd "$out" && pwd)
while IFS=$'\t' read -r language file; do
    "$python" "$here/build.py" --language "$language" --out "$out/$file"
done < <("$python" - "$root/rectoverso.json" <<'LANGUAGES'
import json, sys
for language, artifact in json.load(open(sys.argv[1]))['languages'].items():
    print(language + '\t' + artifact['package']['file'])
LANGUAGES
)
"$python" "$here/checks/validate-anki.py" --output "$out/evidence" "$out/"*.apkg
