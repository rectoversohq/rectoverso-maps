# Maps source rules

Read README.md, README.fr.md and source/policy.json before editing. This repository belongs to RectoVerso's gallery work, tracked in simonpinkas/RectoVerso#631 and PR #633. The owner settles coverage, learner names, territorial conventions and publication decisions in chat.

- Maintain one multilingual repository: shared geometry, media, roster and builders, with English/French definitions under source/languages. Produce separate Anki packages; preserve every published note GUID and deck/model/field/template identity.
- Never silently change approved boundaries, names, ISO coverage or the sample artwork. The frozen ISO reference checks the recorded registry snapshot, not live freshness or territorial policy.
- Packages and large build/test evidence belong outside Git on the external media drive. Tools take paths as arguments; never hard-code that drive. Preserve the old working trees and failed evidence.
- Before a change is committed, run verify-coverage.py, test-source.py and test-render-pngs.py. Builder changes also require a fresh-clone build, Anki validation and validate-rebuild.py against the previous candidate. Changed geometry requires full regenerate.sh comparison and visual review.
- Keep English/French documentation current and record implementation, evidence and remaining gates in the app PR and its agents/gallery-handoff.md. Never claim local results certify remote releases or the app's live globe.
- Commit only named files on the task branch. No force pushes, history rewrites, source publication, tags, releases or merges without the owner's explicit go for the reviewed batch. Deck-source CI and the app compatibility workflow remain separate responsibilities.
