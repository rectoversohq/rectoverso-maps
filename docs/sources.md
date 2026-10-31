# Sources, coverage and boundaries

[Back to Maps / Cartes](../README.md) · [Français](sources.fr.md)

## Coverage, names and boundaries

The reference remains the 249 officially assigned ISO 3166-1 country/territory codes. This candidate adds 39 regional questions from **all existing named picture groups**. These are learning questions, not extra sovereign countries or new ISO assignments. Existing GUIDs/schema IDs are retained; FRA/PRT now use their core group, while other ISO composites retain their full overview. No already separate ISO territory is duplicated.

`source/geography/regional-questions.json` owns the explicit roster, bilingual names/hints, stable deck-local codes (`rectoverso-maps-regions-v1`) and frozen polygon fingerprints. Every regional field contains precisely its named group's original polygons. The union of the separate questions equals the old complete parent geometry, without clipping, duplication or loss. Insets are static Anki images; no app interaction is added.

| Existing entry | New regional questions |
| --- | --- |
| France | Clipperton Island |
| Portugal | Azores, Madeira |
| Svalbard and Jan Mayen | Svalbard, Jan Mayen |
| Bonaire, Sint Eustatius and Saba | Bonaire, Sint Eustatius, Saba |
| Heard Island and McDonald Islands | Heard Island, McDonald Islands |
| Tokelau | Atafu, Nukunonu, Fakaofo |
| Saint Helena, Ascension and Tristan da Cunha | Saint Helena, Ascension, Tristan da Cunha group |
| South Georgia and the South Sandwich Islands | South Georgia, South Sandwich Islands |
| Pitcairn Islands | Pitcairn, Henderson, Oeno, Ducie |
| French Southern Territories | Kerguelen Islands, Crozet Islands, Amsterdam and Saint Paul, Glorioso Islands, Juan de Nova, Europa, Bassas da India, Tromelin |
| United States Minor Outlying Islands | Johnston Atoll, Jarvis Island, Baker Island, Howland Island, Wake Atoll, Midway Islands, Navassa Island, Palmyra Atoll, Kingman Reef |

France’s primary question includes Corsica but excludes Clipperton; Portugal’s primary question excludes the Azores and Madeira. Their answers remain France/Portugal, with explicit scope notes. Other worldwide subdivisions (for example Spain’s outlying geography) are not silently added by this rule; they require a separately reviewed named-group definition. Region hints identify geographic context, never sovereignty.


The deck uses a documented territorial convention informed by UN sources, not an endorsement by the UN or ISO. Ukraine includes Crimea; Georgia includes Abkhazia and South Ossetia; Serbia includes Kosovo with a resolution 1244 status note; Moldova includes Transnistria; Somalia includes Somaliland; Cyprus includes northern Cyprus and excludes the British Sovereign Base Areas. Morocco excludes the whole Western Sahara geographic territory, which has its own ESH card. Syria includes the Golan Heights; Palestine includes East Jerusalem. The outline does not determine sovereignty or recognition.

Explicitly undetermined areas use neutral gray context and dashed boundaries: the Kashmir dispute on the India, Pakistan and China cards, and Abyei on the Sudan and South Sudan cards. They are not assigned to a claimant's gold target or made into extra cards. The exact source features and primary map references are in `source/geography/neutral-areas.json` and `source/geography/policy.json`. Other coastlines and context are generalized Natural Earth data, not a survey or a claim that every border has been independently adjudicated.

Common learner names are distinct from formal reference metadata: **Vatican City**, **Taiwan**, **Palestine**, **Western Sahara**. The French twin distinguishes the two Saint-Martin entries. The ISO reference is dated and versioned; its registry check establishes the code roster and official short names, not the map boundary convention. Recheck it before a later release rather than treating this snapshot as permanently current.

The full field geometry retains small components. Simplification preserves polygon count/topology and uses a finer relative tolerance for small islands. Pictures are teaching maps: locator rings are not land; inset panels have independent scales. Natural Earth remains generalized, including Tokelau's atoll outlines. McDonald Islands use a separately credited 2020 coastline. The live map uses the app's existing camera/projection behavior, which is checked separately from static pictures.

## Credits and license

Deck, original styling and drawings: © Simon Pinkas, [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). [Natural Earth v5.1.2](https://www.naturalearthdata.com/about/terms-of-use/) is public domain. McDonald Islands coastline: Geoscience Australia / Australian Antarctic Data Centre, `McDonald_Island_Coastline_2020`, captured 2020-06-25, [CC BY 4.0](https://data.aad.gov.au/docs/conditions-of-use), retrieved through the [official mapping service](https://www.antarctica.gov.au/antarctic-operations/stations-and-field-locations/heard-island/mapping/). The source WFS response, hash and modifications are tracked in `source/geography/supplements/`.

Common names partly derive from [Ultimate Geography 5.3](https://github.com/anki-geo/ultimate-geography/tree/v5.3), by the anki-geo contributors; its [text is public domain](https://github.com/anki-geo/ultimate-geography/blob/v5.3/LICENSE.md). No upstream pictures are reused. `rectoverso.json` credits each generated image. Repository: `rectoversohq/rectoverso-maps`.
