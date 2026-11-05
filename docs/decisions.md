# Decisions

## 2026-11-05 — Continents and corrected French (0.3.0-rc.3)

The owner's plan on #7 (2026-11-04): the continent update is redone on the gallery layout as 0.3.0-rc.3. `scripts/source_data.py`'s field additions were re-applied by hand to the layout's per-language reading and the packages rebuilt; #7's field IDs, `continents.json` and diagnostics carry over. The 41 assignments that differ from Flags were checked against independent sources (`independentCheck` in `continents.json`; [Continents and search](continent-search.md#independent-fact-check)); Madeira and Amsterdam and Saint Paul rest on conventions no source states as a continent, which the owner reviews before release. The French notes and deck description use a narrow no-break space before « ; » and « : » and inside « », and « deck » for « jeu » (RectoVerso's French rules): 40 notes change, the 39 named in the plan and Kosovo's. Anki's default import doesn't add the new fields to an earlier installation (#8, 1.1.1); the release notes say how to get them and what **Always** replaces, and claim nothing about who has the earlier packages. The safer-upgrade probes stay at #7's last commit, a9bf5e0.

## 2026-11-05 — Publication preparation for 0.3.0-rc.2

The owner asked for this preparation before releasing 0.3.0-rc.2, as for Flags and Capitals 0.1.0-rc.2. The READMEs point to 0.3.0-rc.2 and say that updating from 0.3.0-rc.1 keeps every note identity and the learner's progress; the building guides describe the release and the upgrade test from the published 0.3.0-rc.1; `status` in `rectoverso.json` is `prerelease`, as in Flags and Capitals. The Anki deck descriptions already describe the published deck and are unchanged. Cards, notes, identities and pictures are unchanged; `contentModifiedAt` stays, since no card changed. The French typography of the notes and deck description (a narrow no-break space before « ; » and « : », « deck » for « jeu ») is corrected in the continent release, 0.3.0-rc.3, by the owner's plan on #7.

## 2026-11-04 — Gallery copy and sample question

The owner approved the gallery copy in `rectoverso.json`: the headline "Know a place by its shape on the map." / « Reconnaître un lieu à sa forme sur la carte. » and the description that names the 288 places, the 249 with an ISO 3166-1 country code and 39 parts of 11 of them. The sample question is Italy (`rv-map-en-ita`, `rv-map-fr-ita`), one large gold shape with a one-word answer in each language.
