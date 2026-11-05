# Maps source

@~/Dev/RectoVerso/agents/decks.md

Above: the rules every RectoVerso gallery deck follows (`agents/decks.md` in RectoVerso, `~/Dev/RectoVerso` on the owner's Mac). Below: this repository's own.

- **Read first:** README.md, README.fr.md and source/geography/policy.json.
- **Where things are:** the root keeps the READMEs, the license and notice, this file, the manifest and the Python dependencies. Content in source/, map references in source/geography/, vector originals in artwork/svg/, tools in scripts/, the map tooling and its Node dependencies in scripts/maps/, validators in scripts/checks/, regression tests in tests/, guides in docs/. Build outputs and caches stay outside Git.
- **Coverage:** the approved roster is the 249 places with an ISO 3166-1 code plus 39 named regional questions, 288 a language. Keep the namespaces apart, every published identity, each region's exact polygon fingerprint, and the composite overviews except the approved France and Portugal core questions. Approved boundaries, names, ISO coverage and the sample artwork never change silently: they're the owner's. The frozen ISO reference checks the recorded registry snapshot, not live freshness or territorial policy.
- **Before a commit:** scripts/checks/verify-coverage.py, tests/test-source.py and tests/test-render-pngs.py. A builder change also needs a fresh-clone build, Anki validation and scripts/checks/validate-rebuild.py against the previous release; changed geometry, scripts/maps/regenerate.sh's full comparison and a visual review.
- **The note type:** read docs/continent-search.md before changing its schema or the upgrade checks. Keep the Merge-note-types / If-newer diagnostic (check-default-schema-upgrade.py) apart from the explicit Always check; neither certifies Anki's default update. build.py dates note types and notes at contentModifiedAt.
- **Keep failed evidence and old working trees** outside Git, with the rest.
