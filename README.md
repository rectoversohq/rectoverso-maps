# Maps / Cartes

**Recognize a place. Learn its name.** 288 map questions: countries, territories and named regions, in English or French, for Anki.

[Français](README.fr.md) · [Build the decks](#build-for-anki) · [Sources and boundaries](docs/sources.md) · [CC BY 4.0](LICENSE)

<img src="source/media/rv-map-ita.png" alt="Example card: Italy highlighted in gold against blue water and slate neighboring countries." width="640">

*One map on the front. Its name on the back. Italy / Italie, shown here.*

## What you get

| Language | Deck in Anki | Cards | Built file |
| --- | --- | ---: | --- |
| English | Maps | 288 | `Maps-en-288.apkg` |
| Français | Cartes | 288 | `Cartes-fr-288.apkg` |

Choose either language, or install both. The two packages share their artwork and geometry, with separate note identities so reviews stay independent. Each includes every picture; no RectoVerso account or app is needed to study in Anki.

This source candidate retains all **249 ISO country/territory card identities** and adds **39 named regional questions**, for **288 cards per language**. France and Portugal now ask their metropolitan/mainland geography, with separate outlying-region questions; other composite ISO entries retain their overview and gain individual regional questions. This is **not a list of 288 countries**. The extra regions use explicit deck-local codes, not invented ISO codes. Common learner names are separate from formal ISO names. [Read the coverage and boundary convention](docs/sources.md), including the neutral treatment of Kashmir and Abyei.

**Development candidate:** this branch builds **0.3.0-rc.1 (288 cards)**; it is **not published**. The latest downloadable release remains [0.2.0-rc.2 (249 cards)](https://github.com/rectoversohq/rectoverso-maps/releases/tag/v0.2.0-rc.2), with an English and a French Anki package. Download that published `.apkg` for the existing 249-card deck, or build this source to review the 288-card candidate. The release notes include exact checksums and validation details. Published tags and release assets remain immutable. Updating from rc.2 keeps existing note identities and review progress; 39 new questions are added.

## Build for Anki

The package build uses the pictures already in this repository. **You do not need Node, Swift or map-data downloads for this step.**

Requirements: Git, Bash and **Python 3.14** with `venv` and `pip`. The documented build is tested on macOS with Anki's pinned Python library, **26.9.3**. Other operating systems have not been verified. Anki desktop is needed to study the resulting deck, but does not need to be running to build it.

Clone the repository and create the environment. These instructions describe this revision; older tags include their own README. If you already have this source checkout, start with `cd`:

```sh
git clone https://github.com/rectoversohq/rectoverso-maps.git
cd rectoverso-maps
python3.14 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

While the 288-card candidate is under review, check out `codex/4-regional-cards` after cloning and before creating the environment. The default branch still describes the published 249-card deck until this PR merges. Run `git switch codex/4-regional-cards`; confirm `rectoverso.json` says `0.3.0-rc.1` and `288` cards before building.

Build both languages into a **new directory outside the checkout**. The source tree includes large SVG originals; use a disk with room for the checkout, packages and temporary build files. Replace the example output path with one on your data drive:

```sh
ANKI_PYTHON="$PWD/.venv/bin/python" ./scripts/build.sh /absolute/path/to/maps-build
```

The command checks the source, creates both `.apkg` files and their `.rectoverso.json` metadata, then imports each package using Anki's own library. It checks card counts, rendered fronts and backs, missing media, unique note IDs and review preservation on repeat import. Results are saved in `evidence/anki-validation.json` inside the output directory. A failed check exits with an error; keep that output for diagnosis and use a fresh directory when retrying.

Open the `.apkg` for the language you want in Anki desktop. The `.rectoverso.json` files are build metadata; **do not import them**. Keep the packages intact so their stable identities can preserve your learning progress on later updates.

## Working on the source

Artwork, geographic data and the build tools live once. English and French definitions live beside them:

```text
rectoverso.json          Shared metadata, version and language artifacts
source/
  places.json           Bilingual names, stable GUIDs and place geometry
  media/                Ready-to-package PNG maps
  languages/en/         English deck, note type and translations
  languages/fr/         French deck, note type and translations
  style.css             Shared Anki card appearance
  geography/            Coverage, references and map-generation inputs
artwork/svg/            Editable vector originals
scripts/
  build.sh              Build and validate both language packages
  source_data.py        Compose notes from shared and localized inputs
  ci.py                 Run the complete Anki CI pipeline
  checks/               Source, package and identity validators
  maps/                 Map-generation tools and Node dependencies
tests/                  Source, identity and renderer regression tests
docs/                   English and French build/source guides
.github/workflows/      GitHub Actions configuration
```

Edit deck content in `source/`; maintain tools in `scripts/` and their regression cases in `tests/`. Map generation is optional when packaging the stored pictures. Build outputs and caches stay outside the checkout.

[Build and verification reference](docs/building.md) covers source tests, rebuilding pictures, identities and the metadata schema. [Source and boundary notes](docs/sources.md) explain the map choices and attribution. Contributions should preserve stable note, deck, model, field and template IDs; discuss coverage, names and boundary changes before editing them.

## License and attribution

Our authored deck content, maps, metadata and build source are **© Simon Pinkas, CC BY 4.0**. You may share and adapt them, including commercially, under that license's attribution and other terms. Credit the author, link the license and identify your changes. [LICENSE](LICENSE) contains the full license; [NOTICE.md](NOTICE.md) records its scope and upstream credits. Dependency licenses remain their own.

The geometry comes primarily from **Natural Earth 5.1.2** (public domain). McDonald Islands use coastline data from **Geoscience Australia / Australian Antarctic Data Centre** (CC BY 4.0). Some common names derive from **Ultimate Geography 5.3** (public-domain text); none of its pictures are reused. Every generated picture has an entry in `rectoverso.json`'s `imageCredits`. [Full source details](docs/sources.md#credits-and-license).
