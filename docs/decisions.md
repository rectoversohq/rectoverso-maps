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

## 2026-11-06 — 1.0.0, the first release learners get

The owner (2026-11-06): the deck's first release in RectoVerso's Deck gallery is 1.0.0, after the owner's review, its tag and release on the owner's go. It has the same cards as the last prerelease, 0.3.0-rc.3: version, tag and release address move to 1.0.0 in `rectoverso.json`, the READMEs and the review page, and `status` says `release`. No `whatsNew` (nothing changed for a learner since 0.3.0-rc.3) and no gallery covers yet (the app shows placeholders until the deck's own). `contentModifiedAt` stays.

## 2026-11-06 — Canada and Thailand gallery covers

The owner asked to rebuild the two screenshot studies with NASA imagery
and the deck’s own outlines. The covers show Canada on a day–night globe
and Thailand at night, in that order. Both are shared across languages
and appearances. The render and CI verify the two JPEGs before review.

## 2026-11-06 — 1.0.0 lists the gallery covers

The owner approved the two covers and the 1.0.0 release (2026-11-06), with no `whatsNew`: the cards are those of 0.3.0-rc.3. `rectoverso.json` lists `rv-map-cover-1.jpg` (Canada on a day–night globe) and `rv-map-cover-2.jpg` (Thailand at night), in that order, in every language and both appearances: neither has words, and each serves light and dark. The release attaches the two JPEGs beside the packages.


## 2026-11-06 — 1.0.1 credits the covers' NASA imagery in the deck's sources

The owner (2026-11-06, #15): RectoVerso's About for the deck shows its `sources`, not its `credits` text, so the NASA imagery behind the gallery covers goes into `sources` too: NASA Blue Marble: Next Generation (August 2004 base map) and NASA Black Marble (2016 color map, 3 km), each with its NASA page and "Public domain" (NASA: its images "generally are not subject to copyright in the United States", and "NASA should be acknowledged as the source"). The `credits` text names them in English and French. The Black Marble credit is now NASA's own (Scientific Visualization Studio, 30876: NASA's Goddard Space Flight Center; scientist Miguel Román, NASA/GSFC; image processing Joshua Stevens, SSAI), for "NASA Earth Observatory / NASA and NOAA"; Blue Marble's is the Earth Observatory's ("produced by Reto Stöckli, NASA Earth Observatory (NASA Goddard Space Flight Center)"). Released as 1.0.1, a patch, with its `whatsNew`; the cards, notes, identities, pictures and covers are those of 1.0.0, and `contentModifiedAt` stays.

## 2026-11-10 — 1.0.2 titles the French deck « Atlas »

The owner (2026-11-10, #19): « Cartes » collided with the app's word for a flashcard (« carte »): beside its card count the deck read « Cartes · 288 cartes ». The French deck is titled « Atlas » from 1.0.2, in `rectoverso.json`, as the deck's name in Anki and in its package's file name (`Atlas-fr-288.apkg`); the English deck stays Maps. Identities don't change: the notes' GUIDs, the note types, the deck's id and the package id `rectoverso-maps-fr` are those of 1.0.1, and so are the cards. In Anki, an update files its cards by the deck's name: imported over 1.0.1, the 288 cards and their history stay in the learner's « Cartes » and an empty « Atlas » appears beside it (checked with Anki 26.9.3, with both update settings); renaming the deck to « Atlas » first avoids it, and the READMEs say so. « Planisphère » and « Cartes du monde » were set aside: the first names one world map where the deck shows each place on its own, the second keeps the colliding word.
