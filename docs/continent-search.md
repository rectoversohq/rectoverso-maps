# Continents and search (0.3.0-rc.3)

[Back to Maps / Cartes](../README.md) · [Français](continent-search.fr.md)

Tracked in [Maps #6](https://github.com/rectoversohq/rectoverso-maps/issues/6); the Anki update limit is [Maps #8](https://github.com/rectoversohq/rectoverso-maps/issues/8). Version 0.3.0-rc.3 keeps all **288 questions, answers, pictures and published identities** and appends two fields to each note type, with stable field IDs: **Continent**, for Anki's editor and browser, and **RectoVerso search**, discovery metadata for RectoVerso. Neither appears in the study templates. The four existing fields keep their IDs and order.

**RectoVerso search** holds plain JSON with the localized continent, region and learner-facing place name, each with its English and French aliases, for example:

```json
{"v":1,"fields":[{"name":"Continent","values":["Europe","Asia"],"aliases":["Asia","Asie","Europe"]}, …]}
```

Geometry, codes and license text stay out of it. The English and French packages keep independent identities and review progress.

## Geographic convention

[continents.json](../source/geography/continents.json) assigns every question to one or more of seven groups: Africa, Antarctica, Asia, Europe, North America, South America and Oceania (Australia and the Pacific islands). A membership describes the place the card asks, not its whole sovereign state: the core France and Portugal questions are Europe; Clipperton is North America; Madeira and the Azores are Europe, as Portugal is in UN M49 and GeoNames; the United States and the U.S. Minor Outlying Islands span North America and Oceania; Russia, Turkey and the named Ural and Caucasus cases span Europe and Asia; Colombia and Venezuela include North America for San Andrés and Providencia and Isla de Aves, which their outlines contain.

The owner's Antarctic-island convention (`taxonomyReview`) groups Bouvet Island, Heard Island and McDonald Islands, South Georgia and the South Sandwich Islands, and the Kerguelen and Crozet Islands with **Antarctica**, after [GeoNames](https://download.geonames.org/export/dump/countryInfo.txt); [UN M49](https://unstats.un.org/unsd/methodology/m49/) groups them differently. Amsterdam and Saint Paul are Africa, as UN M49 classifies the French Southern Territories: they lie north of the Antarctic Convergence, and the owner moved them out of the Antarctic group. The French Scattered Islands are Africa. This is a discovery convention, not an ISO or UN classification, an Antarctic Treaty area or a territorial claim, and it doesn't say these islands are on the Antarctic landmass.

## Independent fact check

The 41 assignments that differ from the published Flags deck (the 39 regional questions and the core France and Portugal questions) were checked against sources independent of this deck: UN M49 and GeoNames (whole countries and areas only), the CIA World Factbook's final data (cia.gov retired it in 2026; read from the `factbook/factbook.json` mirror), territory and national sources (TAAF, IPEV, the Australian Antarctic Division, Geoscience Australia, the territory governments of SGSSI, Pitcairn, Saint Helena, Ascension and Tristan da Cunha, NZ MFAT, the US Department of the Interior and Fish and Wildlife Service, the Government of the Netherlands, the European Parliament, the Governor of Svalbard), and the Antarctic Convergence as CCAMLR defines it. `independentCheck` in `continents.json` records the result:

- **34 are supported** by every source that names a continent for them. Madeira, the Azores and the three Saint Helena, Ascension and Tristan da Cunha questions are supported only through their parent (Portugal, Saint Helena): no source names their own continent.
- **6 follow the owner's Antarctic-island convention where the sources disagree:** Heard Island, McDonald Islands, South Georgia, the South Sandwich Islands, Kerguelen and Crozet (GeoNames and the Factbook's map region say Antarctica; UN M49 says Oceania, South America or Africa).
- **Amsterdam and Saint Paul** (Africa) follow UN M49, which classifies the French Southern Territories in Eastern Africa; GeoNames says Antarctica for the whole territory, and [IPEV](https://institut-polaire.fr/fr/iles-subantarctiques/iles-subantarctiques/) counts the two islands as subantarctic. No source names their own continent, and at 37°50′S and 38°43′S they lie north of the Antarctic Convergence (45°S between 30°E and 80°E).

The owner settled the two points the check raised: Madeira is Europe, as the sources have it, rather than Africa by its position on the African plate; Amsterdam and Saint Paul are Africa, as UN M49 has it, rather than Antarctica.

The evidence (each source's quote, its address and the date it was read) is kept with the release evidence, outside Git.

## Updating in Anki

A new installation has both fields filled. An installation of 0.3.0-rc.1 or 0.3.0-rc.2 behaves like this in Anki 26.9.3, as checked in disposable collections with study progress, in both languages:

| Import options | Notes | Cards, schedules, review history |
|---|---|---|
| Anki's defaults (**Merge note types** off, **Update notes** and **Update note types** on **If newer**) | Keep their four fields; the two new fields aren't added. Anki adds an unused copy of the note type, named with a "+", that no note uses. | Kept |
| **Merge note types** on, the rest on **If newer** | Gain the two fields, empty. | Kept |
| **Merge note types** on, **Update notes** and **Update note types** on **Always** | Gain the two fields, filled; the learner's edits to these notes and to the note type's styling are replaced. | Kept |

The same holds for the corrected French of the notes (0.3.0-rc.3 uses a narrow no-break space before « ; » and « : » and inside « », and « deck » for « jeu »): an earlier installation receives it only with **Always**. Anki explains why in its own help for **Merge note types**: merging a changed schema "may mark existing notes as modified", so the package's notes no longer look newer. The cause is in Anki's [schema change](https://github.com/ankitects/anki/blob/26.09.3/rslib/src/notetype/schemachange.rs) and [package note import](https://github.com/ankitects/anki/blob/26.09.3/rslib/src/import_export/package/apkg/import/notes.rs). A safer update is tracked in #8. The research for it (a GUID-matched text import of only the two new fields, with its conflict and recovery probes) is in `scripts/checks/probe-safer-upgrade.py` and `probe-metadata-conflicts.py` at [a9bf5e0](https://github.com/rectoversohq/rectoverso-maps/tree/a9bf5e041bffd7c83cea98f7a9d6b50284127c45/scripts/checks); it isn't a migration tool.

## Checks

`scripts/ci.py` pins the published 0.3.0-rc.1 as its upgrade baseline (its notes are those of 0.3.0-rc.2). It runs `validate-upgrade.py --update-existing always`, a diagnostic that every identity, schedule and FSRS memory survives and the new content arrives, and `check-default-schema-upgrade.py`, which records what **Merge note types** with **If newer** does to the new fields (today it leaves them empty) and fails on any other result. `ci.json` says `"defaultSchemaUpgradeSafe": false`. Neither result is a default-upgrade pass.

```sh
python scripts/checks/validate-upgrade.py /old/Maps-en-288.apkg /new/Maps-en-288.apkg /evidence/upgrade.json --update-existing always
python scripts/checks/check-default-schema-upgrade.py /old/Maps-en-288.apkg /new/Maps-en-288.apkg /evidence/default-control.json
```

Repeat in French. `build.py` dates the note types and notes at `contentModifiedAt`, the reviewed source revision's time, which is always in the past.
