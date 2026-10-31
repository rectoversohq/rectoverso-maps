# Building and verifying Maps

[Back to Maps / Cartes](../README.md) · [Français](building.fr.md)

## Package existing maps

Follow the [README setup](../README.md#build-for-anki). Run commands from the repository root. `requirements.txt` pins the direct Python dependencies: Anki 26.9.3 and Shapely 2.1.2. Shapely is used for geometry regeneration; Anki packages can be built from the stored pictures without regenerating geometry.

```sh
ANKI_PYTHON="$PWD/.venv/bin/python" ./build.sh /absolute/path/to/new-packages
```

This creates `Maps-en-249.apkg`, `Cartes-fr-249.apkg`, one `.rectoverso.json` sidecar per package, and `evidence/anki-validation.json`. A directory that already exists, or one inside the checkout, is rejected. Build and Anki temporary files are placed beside the output packages.

Each artifact contains 249 notes and cards. The builder combines shared names, GUIDs and place fields with language-specific templates, labels and boundary notes. It does not fetch data or change source files. Archive bytes can change between builds because Anki writes timestamps; compare content and identities, not whole-archive hashes, when checking a rebuild. Metadata hashes describe the exact candidate artifacts prepared for a release.

## Check sources and identity preservation

Use the Python environment from setup. Source tests make temporary copies; point `TMPDIR` to an existing directory on your data drive.

```sh
mkdir -p /absolute/path/to/maps-test-tmp
.venv/bin/python verify-coverage.py
TMPDIR=/absolute/path/to/maps-test-tmp .venv/bin/python test-source.py
TMPDIR=/absolute/path/to/maps-test-tmp .venv/bin/python test-render-pngs.py
```

The coverage check validates the frozen ISO reference checksum, all 249 codes and their formats, official English/French names and annotations, learner names, picture credits and distinct language identities. It checks the recorded snapshot, not today's live ISO registry. Source tests deliberately damage a copy to check that missing countries/images, changed learner names, invalid paths, unknown boundary notes, conflicting model IDs and incorrect release URLs are rejected.

The rendering tests exercise bounded process retries, timeout, partial-file isolation and rejection of existing output. They use a small fake converter; they do not certify real rendered map appearance.

After an independent package build, compare each language with its previous candidate:

```sh
.venv/bin/python validate-rebuild.py /path/to/previous/Maps-en-249.apkg /path/to/new/Maps-en-249.apkg /path/to/evidence/identity-en.json
.venv/bin/python validate-rebuild.py /path/to/previous/Cartes-fr-249.apkg /path/to/new/Cartes-fr-249.apkg /path/to/evidence/identity-fr.json
```

This checks source note GUIDs, deck/model IDs, field/template IDs, and an actual import over an existing collection with scheduled progress. Anki may assign a local deck ID on the first import; a subsequent import must preserve that local identity and progress. Both languages can coexist with independent reviews.

The older, unpublished 243-card review schema is a different upgrade case: 231 GUIDs are shared, 18 are added, and 12 retired cards remain in Anki. The tested upgrade needs Anki's merge-note-types option and note/type updates enabled. This is not automatic deletion to a 249-card collection. Do not use the same-schema rebuild check as proof of that older schema migration.

## Regenerate the pictures

This is optional for building an Anki package. It is required when changing map data or the renderer.

Use macOS with Swift's `swiftc`, AppKit and WebKit available, Node 22 or later with npm, and the Python environment above. Git stores the SVG originals and PNG results. `package-lock.json` pins the JavaScript dependency graph. Natural Earth 5.1.2 input hashes are checked on download; the McDonald coastline supplement and its provenance are stored in `source/geometry/`.

```sh
DRAWING_PYTHON="$PWD/.venv/bin/python" ./regenerate.sh /absolute/path/to/natural-earth-cache /absolute/path/to/new-drawings
```

The command fetches any missing checksum-pinned inputs, prepares geometry, runs `npm ci`, renders SVGs, compiles the PNG converter and compares all 249 SVGs, PNGs and place records against the stored source. Use a fresh output directory; it holds drawing outputs, compiler caches and temporary files. npm may contact its registry; set `npm_config_cache` if its cache should be on your data drive. Natural Earth downloads are cached in the first supplied directory.

PNG conversion gets at most three fresh processes, each with a 60-second limit. A failed attempt cannot leave a partial image accepted by the next one. Exhausted retries or a final byte difference fail the command. Exact PNG comparison needs the same macOS/WebKit environment; a different rendering environment may produce different bytes and requires investigation, not a silent reference replacement. Earlier WebKit snapshot failures were intermittent; recovery is bounded, not a claimed root-cause fix.

## Metadata and release boundaries

`rectoverso.json` uses `schemaVersion: 2`. Shared title, credits, coverage, source paths, image credits and version appear once. `languages.en` and `languages.fr` hold stable artifact IDs, package filenames/hashes/URLs and paths to localized definitions. `source_data.py` expands these to the per-package sidecars, including `language` and the common `deckID`.

The current candidate is `0.2.0-rc.1`. Its metadata names the intended tag `v0.2.0-rc.1`; prepared locally for the submodule; no remote tag, release, remote-checkout result or automated CI completion is implied. Packages belong on versioned releases, never in source Git. The original language working trees and Git histories were preserved separately before consolidation.

Deck-source CI is responsible for source checks, Anki checks and rebuild identities. The RectoVerso app repository is responsible for its own import/export compatibility and gallery integration. Its single-submodule migration is tracked in simonpinkas/RectoVerso#633; the source workflow is implemented here, with a separate explicit compatibility workflow in the app repository. Hosted execution awaits source publication and workflow activation. Anki uses these stored images; the app's Antarctica and dispersed-island live-globe limitations are separate and remain held.

## Gallery validation interface

The app repository first verifies the submodule commit, version tag and clean working tree. It then calls `source_data.inputs(language)` in a separate Python process without writing files. The function returns JSON-serializable `(metadata, notes, model, deck)` values. Expanded metadata must exactly match the declared shared metadata and language entry. Note construction stays in this repository; the app does not duplicate geography logic.

## Automated checks

`.github/workflows/anki.yml` runs **Anki packages** on pull requests, branch pushes and manual requests, on a GitHub-hosted macOS runner with Python 3.14.7. It uses read-only repository permissions and pinned actions. No desktop Anki process, credentials, signing or release token is needed. It never publishes releases.

Run the same pipeline locally with the environment from the README:

```sh
.venv/bin/python ci.py --output /absolute/path/to/new-ci-output --base FULL_PREVIOUS_COMMIT_SHA
```

The baseline must exist in the local Git history. CI uses the PR base or previous push commit. A first branch push or manual run without `base` records a null baseline: it certifies a rebuild only. For a manual update check, supply the previous approved source commit as `base`.

The pipeline runs the coverage audit and source/rendering/identity tests, checks existing GUIDs and deck/model/field/template identities against the baseline without executing baseline code, builds both languages twice, validates both builds with Anki, and imports the independent rebuild over scheduled cards. Source additions are reported; removed languages/cards or changed identities fail and require an explicitly designed migration. The ordinary 249-place coverage rule still applies. This protects stable identities across commits; it does not certify every possible historical schema migration.

In Actions, open the run and download `maps-anki-RUN_ID-ATTEMPT`. It contains the first build's two `.apkg` files and sidecars, Anki reports, logs, baseline comparison and `ci.json`. Evidence is retained for 14 days, including available failure logs. A missing or false `passed` in `ci.json` is not a pass. These are test artifacts, not published releases. CI archive hashes describe those new builds; the release metadata continues to describe the exact reviewed release batch.

After approved source publication, enable Actions in the repository settings, allow `actions/checkout`, `actions/setup-python` and `actions/upload-artifact`, and require the **Anki packages** status check in the default branch's ruleset after the first successful run. The workflow must reach the default branch before the manual Run workflow button is available. Ordinary contributions use a branch and PR in this repository. Map artwork changes still need full regeneration and human visual review; Anki CI does not certify map aesthetics or the app's live globe.
