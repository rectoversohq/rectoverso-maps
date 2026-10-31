# Sources, coverage and boundaries

[Back to Maps / Cartes](../README.md) · [Français](sources.fr.md)

## Coverage, names and boundaries

Every code in this version uses the ISO 3166-1 alpha-3 namespace. Separate ISO territories have separate outlines: France excludes its separately coded territories but includes Clipperton; Norway excludes Svalbard and Jan Mayen; Portugal includes the Azores and Madeira; Spain includes the Canaries. `source/geography/codebook.json` and `source/geography/geometry-selections.json` expose each selection. `source/geography/picture-groups.json` partitions existing polygons into named groups for insets; it never invents or clips coastline.

The deck uses a documented territorial convention informed by UN sources, not an endorsement by the UN or ISO. Ukraine includes Crimea; Georgia includes Abkhazia and South Ossetia; Serbia includes Kosovo with a resolution 1244 status note; Moldova includes Transnistria; Somalia includes Somaliland; Cyprus includes northern Cyprus and excludes the British Sovereign Base Areas. Morocco excludes the whole Western Sahara geographic territory, which has its own ESH card. Syria includes the Golan Heights; Palestine includes East Jerusalem. The outline does not determine sovereignty or recognition.

Explicitly undetermined areas use neutral gray context and dashed boundaries: the Kashmir dispute on the India, Pakistan and China cards, and Abyei on the Sudan and South Sudan cards. They are not assigned to a claimant's gold target or made into extra cards. The exact source features and primary map references are in `source/geography/neutral-areas.json` and `source/geography/policy.json`. Other coastlines and context are generalized Natural Earth data, not a survey or a claim that every border has been independently adjudicated.

Common learner names are distinct from formal reference metadata: **Vatican City**, **Taiwan**, **Palestine**, **Western Sahara**. The French twin distinguishes the two Saint-Martin entries. The ISO reference is dated and versioned; its registry check establishes the code roster and official short names, not the map boundary convention. Recheck it before a later release rather than treating this snapshot as permanently current.

The full field geometry retains small components. Simplification preserves polygon count/topology and uses a finer relative tolerance for small islands. Pictures are teaching maps: locator rings are not land; inset panels have independent scales. Natural Earth remains generalized, including Tokelau's atoll outlines. McDonald Islands use a separately credited 2020 coastline. The live map uses the app's existing camera/projection behavior, which is checked separately from static pictures.

## Credits and license

Deck, original styling and drawings: © Simon Pinkas, [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). [Natural Earth v5.1.2](https://www.naturalearthdata.com/about/terms-of-use/) is public domain. McDonald Islands coastline: Geoscience Australia / Australian Antarctic Data Centre, `McDonald_Island_Coastline_2020`, captured 2020-06-25, [CC BY 4.0](https://data.aad.gov.au/docs/conditions-of-use), retrieved through the [official mapping service](https://www.antarctica.gov.au/antarctic-operations/stations-and-field-locations/heard-island/mapping/). The source WFS response, hash and modifications are tracked in `source/geography/supplements/`.

Common names partly derive from [Ultimate Geography 5.3](https://github.com/anki-geo/ultimate-geography/tree/v5.3), by the anki-geo contributors; its [text is public domain](https://github.com/anki-geo/ultimate-geography/blob/v5.3/LICENSE.md). No upstream pictures are reused. `rectoverso.json` credits each generated image. Repository: `rectoversohq/rectoverso-maps`.
