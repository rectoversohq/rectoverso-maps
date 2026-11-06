# Decisions

## 2026-11-05 — The owner's answers on 0.3.0-rc.3

The owner, on the fact check and the release notes:
- "Madeira → Europe, not Africa. Follow the sources." UN M49, GeoNames and the Factbook classify Portugal in Europe, and no source assigns Madeira to Africa; its place on the African plate doesn't make it African.
- "Amsterdam and Saint Paul → Africa, as UN M49 has it, not Antarctica. This replaces the 2 November call for those two islands." Kerguelen, Crozet and the other named Antarctic-island groups stay as decided on 2 November.
- The release notes' Anki-update paragraph is the corrected text: Anki's default import (with **Merge note types** off) doesn't add the new fields and adds an unused "+" copy of the note type, rather than adding them empty as the earlier draft said.
- "Maps' French docs and READMEs are fixed in rc.3": a narrow no-break space before « ; » and « : » and inside « », and « deck » for « jeu », as in the notes.

## 2026-11-05 — Continents and corrected French (0.3.0-rc.3)

The owner's plan on #7 (2026-11-04): the continent update is redone on the gallery layout as 0.3.0-rc.3. `scripts/source_data.py`'s field additions were re-applied by hand to the layout's per-language reading and the packages rebuilt; #7's field IDs, `continents.json` and diagnostics carry over. The 41 assignments that differ from Flags were checked against independent sources (`independentCheck` in `continents.json`; [Continents and search](continent-search.md#independent-fact-check)); the owner settled the two points it raised (next entry). The French notes and deck description use a narrow no-break space before « ; » and « : » and inside « », and « deck » for « jeu » (RectoVerso's French rules): 40 notes change, the 39 named in the plan and Kosovo's. Anki's default import doesn't add the new fields to an earlier installation (#8, 1.1.1); the release notes say how to get them and what **Always** replaces, and claim nothing about who has the earlier packages. The safer-upgrade probes stay at #7's last commit, a9bf5e0.

## 2026-11-05 — Publication preparation for 0.3.0-rc.2

The owner asked for this preparation before releasing 0.3.0-rc.2, as for Flags and Capitals 0.1.0-rc.2. The READMEs point to 0.3.0-rc.2 and say that updating from 0.3.0-rc.1 keeps every note identity and the learner's progress; the building guides describe the release and the upgrade test from the published 0.3.0-rc.1; `status` in `rectoverso.json` is `prerelease`, as in Flags and Capitals. The Anki deck descriptions already describe the published deck and are unchanged. Cards, notes, identities and pictures are unchanged; `contentModifiedAt` stays, since no card changed. The French typography of the notes and deck description (a narrow no-break space before « ; » and « : », « deck » for « jeu ») is corrected in the continent release, 0.3.0-rc.3, by the owner's plan on #7.

## 2026-11-04 — Gallery copy and sample question

The owner approved the gallery copy in `rectoverso.json`: the headline "Know a place by its shape on the map." / « Reconnaître un lieu à sa forme sur la carte. » and the description that names the 288 places, the 249 with an ISO 3166-1 country code and 39 parts of 11 of them. The sample question is Italy (`rv-map-en-ita`, `rv-map-fr-ita`), one large gold shape with a one-word answer in each language.


## 2026-11-06 — One complete AGENTS.md for every agent, by kind of work

The owner: a single `AGENTS.md`, read by any agent (Codex, Claude Code or another) and complete on its own, organized around the three kinds of work done here: deck authoring (the content), contract honoring (what RectoVerso's gallery and Anki read: rectoverso.json, identities, packages, versions and releases) and cover making (the gallery's pictures: the specification, the names, the masters, renderer and check). It restates RectoVerso's `agents/decks.md`, the Library page's deck contract and cover specification and its French, with this repository's own rules; where they disagree, RectoVerso's pages win and this file is corrected. The `CLAUDE.md` first proposed here, importing RectoVerso's page, isn't kept.

## 2026-11-06 — Canada and Thailand gallery covers

The owner asked to rebuild the two screenshot studies with NASA imagery
and the deck’s own outlines. The covers show Canada on a day–night globe
and Thailand at night, in that order. Both are shared across languages
and appearances. The render and CI verify the two JPEGs before review.
