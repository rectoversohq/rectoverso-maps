# Maps: rules for agents

**Read `kit/AGENTS.md` first.** The deck kit ([rectoverso-deck-kit](https://github.com/rectoversohq/rectoverso-deck-kit), a submodule at `kit/`: `git submodule update --init kit`) holds what every deck follows: the deck contract, its check, and the rules for authoring, covers, languages, versions and releases. This file adds only this deck's own rules and checks.

## This deck
- **Maps** (« Atlas »), `rectoversohq/rectoverso-maps`, public. GUID prefix `rv-map`; languages English and French; license CC BY 4.0. Asks each place on a map: 288 questions a language, the 249 places with an ISO 3166-1 code and 39 named regional questions.
- **Our own material here is CC BY 4.0, © Simon Pinkas** (never another name or a company).
- **The deck's own issues are in this repository;** the app's side of the deck (its pin, the catalog, the gallery) is an issue in simonpinkas/RectoVerso.

## This repository
- **Read first:** README.md, README.fr.md and source/geography/policy.json; docs/building.md how the deck is built, docs/sources.md its sources, docs/continent-search.md the note type's search and upgrade checks, docs/decisions.md the dated decisions. French versions beside each (`.fr.md`).
- **Where things are:** the root keeps the READMEs, the license and notice, this file, rectoverso.json and the Python dependencies. Content in source/, map references in source/geography/, vector originals in artwork/svg/, tools in scripts/, the map tooling and its Node dependencies in scripts/maps/, validators in scripts/checks/, regression tests in tests/, guides in docs/. Build outputs and caches stay outside Git, as do old working trees.
- **Before a commit:** scripts/checks/verify-coverage.py, tests/test-source.py and tests/test-render-pngs.py. A builder change also needs a fresh-clone build, Anki validation and scripts/checks/validate-rebuild.py against the previous release; changed geometry, scripts/maps/regenerate.sh's full comparison and a visual review. `python scripts/ci.py --output <folder> --base <the pull request's base>` runs CI's checks.

## This deck's content
- **Coverage:** the approved roster is the 249 places with an ISO 3166-1 code plus 39 named regional questions, 288 a language. Keep the namespaces apart, every published identity, each region's exact polygon fingerprint, and the composite overviews except the approved France and Portugal core questions.
- **Approved boundaries, names, ISO coverage and the sample artwork never change silently:** they're the owner's. The frozen ISO reference checks the recorded registry snapshot, not live freshness or territorial policy.
- **Continents** (source/geography/) are the reference the other geography decks agree with; a change is the owner's call.
- **The note type:** read docs/continent-search.md before changing its schema or the upgrade checks. Keep the Merge-note-types / If-newer diagnostic (check-default-schema-upgrade.py) apart from the explicit Always check; neither certifies Anki's default update. build.py dates note types and notes at contentModifiedAt.

## This deck's checks
- `python3 kit/check.py --rectoverso`: the deck contract, as RectoVerso's gallery takes a deck, by the kit pinned here (`kit/docs/check.md` explains each refusal). The workflow runs it first.
- `scripts/checks/validate-anki.py` and `validate-rebuild.py`, the two every deck has (`kit/docs/getting-started.md`); scripts/checks/ also holds check-identities.py, verify-drawings.py and the upgrade checks (validate-upgrade.py, fetch-upgrade-baseline.py); tests in tests/.
- Anki desktop's look and RectoVerso's own are separate checks: a rendering in Anki's backend isn't a visual approval.

## This deck's covers
- **Two photographic covers:** Canada on a day–night globe, then Thailand at night, shared across languages and appearances. See [Building](docs/building.md#gallery-covers) for the NASA source rasters and reconstruction command.
- **PNG** for drawn art (a JPEG only for a photograph); small files (they ship inside the app's download: aim under 400 KB).
- **Accurate:** whatever real place, flag, element, name or shape a cover shows is right, checked against the deck's own sources.
- **Masters** in artwork/covers/, SVG, named with the same stem as the rendered covers, with lettering outlined (or a pinned, embedded font) so every render is identical; no external resource.
- **scripts/covers.py** renders every master to its cover at 2010 × 1340 (JPEG for this deck’s photographic covers), called by scripts/build.py, into the build's output folder, never into the repository (nothing rendered is committed). Two independent builds give the same bytes.
- **scripts/checks/verify-covers.py,** run by the deck's CI, refuses a wrong size or name, a language without a light and a dark cover, a worded cover missing in a language, an ambiguous set, and anything but background in the top-trailing corner the gallery keeps for the language's pill (within 4 per channel of the corner's dominant color). Its tests in tests/.
- **A new or changed cover** is shown to the owner as rendered covers, light and dark, every language, before it's merged.

## The kit
- **Pinned at `kit/`, at a tag.** Moving it is a pull request of its own, with the check run again (`kit/docs/versioning.md`). Never edit a file under `kit/` from here.
- **A new field, value or form** is a change to the kit, made there first (`kit/CONTRIBUTING.md`): this deck never uses one alone.
