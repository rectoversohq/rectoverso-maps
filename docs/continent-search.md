# Continent search and the 0.4 source migration

The owner approved this source-only addition on 1–2 November 2026, tracked in [Maps #6](https://github.com/rectoversohq/rectoverso-maps/issues/6). This batch is an unpublished review candidate. **The owner chose to hold release and seek a safer upgrade on 2 November 2026. The manual Always workaround is not accepted for publication.** Generic extra-field search belongs to a separate app feature branch.

## Content and identities

All **288 questions, answers, pictures and published card identities** remain intact. The original four fields retain their IDs and order. Two fields are appended with stable IDs: `Continent` for Anki editors and `RectoVerso search` for explicit discovery metadata. Neither appears in the study templates.

The latter contains plain JSON, for example:

```json
{"v":1,"fields":[{"name":"Continent","values":["Europe","Asia"],"aliases":["Europe","Asia","Asie"]}]}
```

The actual records also expose localized region and learner-facing place names. Technical geometry, codes and license text are excluded. English/French packages retain independent identities and review progress.

## Geographic convention

[continents.json](../source/geography/continents.json) accounts for every published question and records the boundary choices. Seven discovery groups are used: Africa, Antarctica, Asia, Europe, North America, South America and Oceania. Oceania includes Australia and the Pacific islands.

Multiple memberships describe the actual geography asked by a question, not its sovereign parent. France/Portugal core questions are European; Clipperton is North American and Madeira African. The USA and U.S. Minor Outlying Islands span North America/Oceania. Russia, Turkey and the specified Ural/Caucasus-border cases span Europe/Asia. The subantarctic grouping is a documented discovery convention, not an ISO/UN classification, Antarctic Treaty area or territorial claim.

## Anki migration: the default does not suffice

Actual **0.3.0-rc.1 → 0.4 candidate** imports in Anki 26.09.3 preserve all 288 card/note/deck identities, schedules and FSRS memory when using **Merge note types + Always update existing notes and note types**. Every new continent/search value is applied. This is diagnostic evidence only: Always can overwrite edited note content and is not the approved release migration.

The ordinary **If newer** option adds the two fields but leaves their values empty. This is not caused by old incoming note dates. Anki's schema-merge step rewrites existing notes, marks them modified at import time, and only then compares the incoming notes. The original builder also left model modification dates at zero; this candidate fixes both model and note dates using the reviewed `contentModifiedAt` epoch. The corrected-date control still reproduces the schema-merge failure. No future date is forged.

| Example control | Note modified (Unix seconds) | Model modified | Fields |
|---|---:|---:|---:|
| Published 0.3 source | 1793489879 | 0 | 4 |
| Correctly dated candidate | 1793573700 | 1793573700 | 6 |
| After default schema merge | 1793574576 | 1793574576 | 6; appended values blank |

This produced 0 updated notes and 288 duplicates. Primary code: [Anki field-schema rewriting](https://github.com/ankitects/anki/blob/26.09.3/rslib/src/notetype/schemachange.rs) and [note-type-before-note package import](https://github.com/ankitects/anki/blob/26.09.3/rslib/src/import_export/package/apkg/import/notes.rs). The headless validator also clears Anki's Python model cache after backend import so it observes the imported schema.

`validate-upgrade.py` keeps **If newer as its default**. CI explicitly requests Always as a diagnostic control and separately records the default failure with exact timestamps and counts. A green diagnostic is not a default-upgrade compatibility pass.

```sh
python scripts/checks/validate-upgrade.py /old/Maps-en-288.apkg /new/Maps-en-288.apkg /evidence/upgrade.json --update-existing always
python scripts/checks/check-default-schema-upgrade.py /old/Maps-en-288.apkg /new/Maps-en-288.apkg /evidence/default-control.json
```

Repeat in French. The previous published 288-card release is checksum-pinned as CI's upgrade baseline. The earlier 249-card packages and all release tags remain immutable. Independent rebuild checks remain distinct from a real schema migration.

## Validation and remaining gates

The local CI round passes source, identity and regional geometry tests, both language builds, independent rebuilds and the explicit Always migration. The separate default-control reports retain `defaultContentApplied: false` for all 288 existing notes in both languages. An initial run stopped because its environment lacked the pinned Shapely dependency; the complete dependency environment passes. No validator was relaxed to hide that failure.

The separate app search branch imported Maps/Cartes 288 successfully and verified authored metadata and bilingual continent discovery. Native app presentation remains a separate review from the backend import probe.

A clean-clone run is required for the committed source. Release stays held until a safer upgrade is verified, followed by approval of the concrete release batch. The owner rejected adopting the manual Always workaround as the release path.

No tag, release, submodule pointer or public catalog was changed. No map artwork changed, and this source work makes no claim about live-globe rendering.

## Additional depicted-region audit

Colombia and Venezuela metadata now include North America as well as South America: the unchanged approved outlines actually contain San Andrés/Providencia and Isla de Aves. France/Portugal core questions remain Europe. No artwork, geometry or identity changed. The owner approved the named BVT/HMD/SGS/southern-ATF Antarctic search grouping on 2 November 2026; it is not inferred from Antarctic-program management and is not expanded to Australia, New Zealand, South Africa or Saint Helena.

## Approved Antarctic-island convention

This is a named discovery-classification choice, not uncertainty about where the islands are. [GeoNames’ continent register](https://download.geonames.org/export/dump/countryInfo.txt) groups the four entries below with Antarctica; [UN M49’s statistical geography](https://unstats.un.org/unsd/methodology/m49/) groups them differently.

| Entry | Approved search groups | UN M49 comparison |
|---|---|---|
| Bouvet Island | Antarctica | South America |
| Heard Island and McDonald Islands | Antarctica | Oceania |
| South Georgia and South Sandwich Islands | Antarctica | South America |
| French Southern Territories | Africa + Antarctica | Eastern Africa |

Owner decision, 2 November 2026: retain the explicitly named GeoNames Antarctic group while preserving ATF’s African Scattered Islands separately. Its Kerguelen, Crozet and Amsterdam/Saint-Paul groups use AN; Glorioso, Juan de Nova, Europa, Bassas da India and Tromelin use AF. There is no automatic Antarctica membership for Australia, New Zealand, South Africa or Saint Helena merely because an Antarctic program operates on an island. This wording does not say the named islands are on the Antarctic continental landmass.

The owner approved these existing candidate assignments, so this decision changes no package content, card count, artwork or boundary. The exact decision and source comparison remain under `taxonomyReview` in the continent JSON. This geographic classification is settled; publication gates are tracked separately.

## Safer-upgrade research — 2 November 2026

The owner chose **keep release held; seek a safer upgrade**. The following is a bounded backend experiment, not a release procedure or a default-import pass.

The same six cases were run against both published 0.3.0-rc.1 packages and the 0.4 candidates in disposable Anki 26.09.3 collections. Every old note received a custom personal field and tag, selected answers were edited, note-type CSS was customized, and all cards received review schedules and FSRS memory before the update.

| Import case | New metadata values applied, per language | Result |
|---|---:|---|
| Merge disabled | 0 / 288 | Notes conflict with the appended schema. |
| Merge + If newer | 0 / 288 | New fields appear, values remain blank. |
| Merge + Never update note types | 0 / 288 | Does not avoid schema rewrite. |
| Merge + Always update note types, notes If newer | 0 / 288 | Also replaces personal CSS. |
| Repeat the default merge import | 0 / 288 | A second import does not repair values. |
| Default merge, then GUID-matched text import of **only the two new fields** | 288 / 288 | Existing answers, custom fields, tags, CSS, note/card/field identities, schedules and FSRS memory preserved. |

Anki's package importer replaces notes as a unit; its [note update logic](https://github.com/ankitects/anki/blob/26.09.3/rslib/src/import_export/package/apkg/import/notes.rs) does not fill only the newly merged fields. Its [text importer](https://github.com/ankitects/anki/blob/26.09.3/rslib/src/import_export/text/import.rs), however, leaves unmapped fields alone. That explains the successful additive control without using future timestamps or changing any published identity.

The text-import result is a possible foundation for an explicitly reviewed migration. It still needs a guarded design: validate stable GUIDs and field identities, require that target metadata fields are absent/empty or already match, reject personal target-field conflicts, demonstrate backup/recovery and repeatability, and verify the actual desktop import mappings. Ordinary packaged-deck import remains insufficient. No personal Anki collection was opened or modified.

Reproduce the research on local packages, once per language:

```sh
python scripts/checks/probe-safer-upgrade.py /published/Maps-en-288.apkg /candidate/Maps-en-288.apkg /new/evidence/safer-upgrade-en
python scripts/checks/probe-safer-upgrade.py /published/Cartes-fr-288.apkg /candidate/Cartes-fr-288.apkg /new/evidence/safer-upgrade-fr
```

This script creates disposable collections under the explicitly supplied output directory. It is **not a migration tool** for an existing profile. Its generated TSV is research evidence, not an approved release asset.
