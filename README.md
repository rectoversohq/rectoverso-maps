# Maps / Cartes

**Recognize a place. Learn its name.** 249 countries and territories, in English or French, for Anki.

[Français](README.fr.md) · [Build the decks](#build-for-anki) · [Sources and boundaries](docs/sources.md) · [CC BY 4.0](LICENSE)

<img src="source/media/rv-map-ita.png" alt="Example card: Italy highlighted in gold against blue water and slate neighboring countries." width="640">

*One map on the front. Its name on the back. Italy / Italie, shown here.*

## What you get

| Language | Deck in Anki | Cards | Built file |
| --- | --- | ---: | --- |
| English | Maps | 249 | `Maps-en-249.apkg` |
| Français | Cartes | 249 | `Cartes-fr-249.apkg` |

Choose either language, or install both. The two packages share their artwork and geometry, with separate note identities so reviews stay independent. Each includes every picture; no RectoVerso account or app is needed to study in Anki.

Coverage follows the 249 officially assigned ISO 3166-1 country and territory codes in the recorded reference. It includes uninhabited territories and is **not a list of 249 sovereign states**. Common learner names are separate from formal ISO names. [Read the coverage and boundary convention](docs/sources.md), including the neutral treatment of Kashmir and Abyei.

**Release status:** `0.2.0-rc.1` is an unpublished review candidate. Source and tag are published; no package release is downloadable yet. This branch reorganizes the source after the original tag, which retains its original layout. The [Anki CI workflow](docs/building.md#automated-checks) runs on source branches and pull requests. Release publication remains separately reviewed.

## Build for Anki

The package build uses the pictures already in this repository. **You do not need Node, Swift or map-data downloads for this step.**

Requirements: Git, Bash and **Python 3.14** with `venv` and `pip`. The documented build is tested on macOS with Anki's pinned Python library, **26.9.3**. Other operating systems have not been verified. Anki desktop is needed to study the resulting deck, but does not need to be running to build it.

Clone the repository and create the environment. Until the layout PR is merged, run `git switch codex/631-multilingual-source` after cloning and entering the directory. These instructions describe this revision; older tags include their own README. If you already have this source checkout, start with `cd`:

```sh
git clone https://github.com/rectoversohq/rectoverso-maps.git
cd rectoverso-maps
python3.14 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

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
