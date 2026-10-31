# Sources, couverture et limites

[Retour à Cartes / Maps](../README.fr.md) · [English](sources.md)

## Couverture, noms et limites

Tous les codes de cette version sont des codes ISO 3166-1 alpha-3. Les territoires ayant leur propre code ont leur propre contour : la France exclut ses territoires codés séparément mais comprend Clipperton ; la Norvège exclut Svalbard et Jan Mayen ; le Portugal comprend les Açores et Madère ; l’Espagne comprend les Canaries. `codebook.json` et `source/geometry-selections.json` exposent chaque sélection. `source/picture-groups.json` regroupe les polygones existants pour les vues détaillées, sans inventer ni découper de littoral.

Le jeu applique une convention territoriale documentée, éclairée par des sources de l’ONU, sans approbation de l’ONU ni de l’ISO. L’Ukraine comprend la Crimée ; la Géorgie, l’Abkhazie et l’Ossétie du Sud ; la Serbie, le Kosovo avec une note sur la résolution 1244 ; la Moldavie, la Transnistrie ; la Somalie, le Somaliland ; Chypre, sa partie nord, sans les zones de souveraineté britanniques. Le Maroc exclut tout le territoire géographique du Sahara occidental, qui a sa propre carte ESH. La Syrie comprend le plateau du Golan ; la Palestine comprend Jérusalem-Est. Le contour ne détermine ni la souveraineté ni la reconnaissance.

Les zones explicitement indéterminées sont en gris neutre, avec des limites en pointillés : le différend du Cachemire sur les cartes de l’Inde, du Pakistan et de la Chine, et Abyei sur celles du Soudan et du Soudan du Sud. Elles ne sont attribuées à aucune partie en doré et ne deviennent pas des cartes supplémentaires. `source/neutral-areas.json` et `source/policy.json` donnent les éléments sources exacts et les cartes de référence. Les autres littoraux et le contexte viennent des données généralisées de Natural Earth : ils ne constituent ni un relevé précis ni une vérification indépendante de chaque frontière.

Les noms usuels pour l’apprentissage sont distincts des noms formels de référence : **Cité du Vatican**, **Taïwan**, **Palestine**, **Sahara occidental**. Les deux Saint-Martin ont des qualificatifs distincts. La référence ISO est datée et versionnée ; sa vérification établit les codes et les noms courts officiels, pas la convention des limites cartographiques. Il faudra la vérifier de nouveau avant une version ultérieure, sans considérer cet instantané comme toujours actuel.

Le champ géométrique conserve les petites composantes. La simplification préserve le nombre de polygones et la topologie, avec une tolérance relative plus fine pour les petites îles. Ce sont des cartes pédagogiques : les cercles ne représentent pas des terres et les vues détaillées ont des échelles indépendantes. Natural Earth reste généralisé, notamment pour les atolls de Tokelau. Les îles McDonald utilisent un littoral de 2020 crédité séparément. La carte interactive utilise la caméra et la projection existantes de l’application, vérifiées séparément des images.

## Crédits et licence

Jeu, style et dessins originaux : © Simon Pinkas, [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). [Natural Earth v5.1.2](https://www.naturalearthdata.com/about/terms-of-use/) est dans le domaine public. Littoral des îles McDonald : Geoscience Australia / Australian Antarctic Data Centre, `McDonald_Island_Coastline_2020`, relevé du 25 juin 2020, [CC BY 4.0](https://data.aad.gov.au/docs/conditions-of-use), obtenu via le [service cartographique officiel](https://www.antarctica.gov.au/antarctic-operations/stations-and-field-locations/heard-island/mapping/). La réponse WFS, son empreinte et les modifications sont conservées dans `source/geometry/`.

Les noms usuels proviennent en partie d’[Ultimate Geography 5.3](https://github.com/anki-geo/ultimate-geography/tree/v5.3), par les contributeurs d’anki-geo ; son [texte est dans le domaine public](https://github.com/anki-geo/ultimate-geography/blob/v5.3/LICENSE.md). Aucune image d’origine n’est réutilisée. `rectoverso.json` crédite chaque dessin. Dépôt : `rectoversohq/rectoverso-maps`.
