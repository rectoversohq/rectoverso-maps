#!/bin/bash
# Build and validate both language artifacts from shared source.
set -euo pipefail
here=$(cd "$(dirname "$0")" && pwd)
out=${1:?Supply a new output directory outside the checkout}
python=${ANKI_PYTHON:-python3}
"$python" "$here/verify-coverage.py"
# Preflight every destination before writing either package.
"$python" - "$here" "$out" <<'CHECK'
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
done < <("$python" - "$here/rectoverso.json" <<'LANGUAGES'
import json, sys
for language, artifact in json.load(open(sys.argv[1]))['languages'].items():
    print(language + '\t' + artifact['package']['file'])
LANGUAGES
)
"$python" "$here/validate-anki.py" --output "$out/evidence" "$out/"*.apkg
