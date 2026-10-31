#!/bin/bash
# Regenerate source drawings outside the checkout, then compare every source byte.
set -euo pipefail
here=$(cd "$(dirname "$0")" && pwd)
sources=${1:?Supply a Natural Earth cache directory}
out=${2:?Supply an output directory}
mkdir -p "$sources" "$out" "$out/tmp" "$out/swift-cache"
sources=$(cd "$sources" && pwd)
out=$(cd "$out" && pwd)
python3 "$here/fetch-sources.py" "$sources"
"${DRAWING_PYTHON:-python3}" "$here/prepare.py" "$sources" "$out/prepared"
(cd "$here" && npm ci --silent)
node "$here/render.mjs" "$out/prepared/places.geojson" "$out/prepared/places.json" "$sources/ne_50m_admin_0_countries.geojson" "$out/drawn" "$out/prepared/neutral-areas.geojson"
TMPDIR="$out/tmp" swiftc -module-cache-path "$out/swift-cache" "$here/svg-to-png.swift" -o "$out/svg-to-png"
TMPDIR="$out/tmp" python3 "$here/render-pngs.py" "$out/svg-to-png" "$out/drawn" 900
python3 "$here/verify-drawings.py" "$out/drawn"
