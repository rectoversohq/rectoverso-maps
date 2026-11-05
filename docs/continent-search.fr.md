# Continents et recherche (0.3.0-rc.3)

[Retour à Cartes / Maps](../README.fr.md) · [English](continent-search.md)

Suivi dans [Maps #6](https://github.com/rectoversohq/rectoverso-maps/issues/6) ; la limite de la mise à jour dans Anki est [Maps #8](https://github.com/rectoversohq/rectoverso-maps/issues/8). La version 0.3.0-rc.3 conserve les **288 questions, réponses, images et identités publiées** et ajoute deux champs à la fin de chaque type de note, avec des identifiants stables : **Continent**, pour l’éditeur et le navigateur d’Anki, et **RectoVerso search**, des métadonnées de recherche pour RectoVerso. Aucun des deux n’apparaît dans les modèles d’étude. Les quatre champs existants gardent leurs identifiants et leur ordre.

**RectoVerso search** contient un JSON simple : le continent, la région et le nom usuel du lieu, localisés, chacun avec ses alias anglais et français. Géométrie, codes et licences n’y figurent pas. Les paquets anglais et français gardent des identités et des progrès indépendants.

## Convention géographique

[continents.json](../source/geography/continents.json) rattache chaque question à un ou plusieurs de sept groupes : Afrique, Antarctique, Asie, Europe, Amérique du Nord, Amérique du Sud et Océanie (l’Australie et les îles du Pacifique). Un rattachement décrit le lieu que la carte demande, pas l’ensemble de l’État souverain : les questions centrales France et Portugal relèvent de l’Europe ; Clipperton de l’Amérique du Nord ; Madère et les Açores de l’Europe, comme le Portugal dans la norme M49 et GeoNames ; les États-Unis et les îles mineures éloignées des États-Unis de l’Amérique du Nord et de l’Océanie ; la Russie, la Turquie et les cas nommés de l’Oural et du Caucase de l’Europe et de l’Asie ; la Colombie et le Venezuela comprennent l’Amérique du Nord pour San Andrés et Providencia et pour Isla de Aves, que leurs contours contiennent.

La convention des îles antarctiques, décidée par le propriétaire (`taxonomyReview`), rattache l’île Bouvet, les îles Heard et McDonald, la Géorgie du Sud et les îles Sandwich du Sud, et les îles Kerguelen et Crozet à l’**Antarctique**, d’après [GeoNames](https://download.geonames.org/export/dump/countryInfo.txt) ; la [norme M49 de l’ONU](https://unstats.un.org/unsd/methodology/m49/) les classe autrement. Amsterdam et Saint-Paul relèvent de l’Afrique, comme la norme M49 classe les Terres australes françaises : elles sont au nord de la convergence antarctique, et le propriétaire les a retirées du groupe antarctique. Les îles Éparses relèvent de l’Afrique. C’est une convention de recherche, pas une classification de l’ISO ou de l’ONU, ni une zone du traité sur l’Antarctique, ni une revendication territoriale ; elle ne dit pas que ces îles sont sur le continent antarctique.

## Vérification indépendante

Les 41 rattachements qui diffèrent du deck Drapeaux publié (les 39 questions régionales et les questions centrales France et Portugal) ont été vérifiés auprès de sources indépendantes de ce deck : M49 et GeoNames (pays et zones entiers seulement), les dernières données du World Factbook de la CIA (retiré de cia.gov en 2026 ; lu sur le miroir `factbook/factbook.json`), des sources territoriales et nationales, et la convergence antarctique telle que la définit la CCAMLR. `independentCheck`, dans `continents.json`, en garde le résultat :

- **34 sont confirmés** par toutes les sources qui leur donnent un continent. Madère, les Açores et les trois questions Sainte-Hélène, Ascension et Tristan da Cunha ne le sont que par leur entité (Portugal, Sainte-Hélène) : aucune source ne nomme leur propre continent.
- **6 suivent la convention du propriétaire là où les sources divergent :** île Heard, îles McDonald, Géorgie du Sud, îles Sandwich du Sud, Kerguelen et Crozet (GeoNames et la région de carte du Factbook disent Antarctique ; M49 dit Océanie, Amérique du Sud ou Afrique).
- **Amsterdam et Saint-Paul** (Afrique) suivent la norme M49, qui classe les Terres australes françaises en Afrique de l’Est ; GeoNames dit Antarctique pour l’ensemble du territoire, et l’[IPEV](https://institut-polaire.fr/fr/iles-subantarctiques/iles-subantarctiques/) compte les deux îles parmi les îles subantarctiques. Aucune source ne nomme leur propre continent, et à 37°50′S et 38°43′S elles sont au nord de la convergence antarctique (45°S entre 30°E et 80°E).

Le propriétaire a tranché les deux points soulevés par la vérification : Madère relève de l’Europe, comme le disent les sources, et non de l’Afrique par sa place sur la plaque africaine ; Amsterdam et Saint-Paul relèvent de l’Afrique, comme dans la norme M49, et non de l’Antarctique.

Les preuves (la citation de chaque source, son adresse et sa date de lecture) sont conservées avec celles de la release, hors de Git.

## Mise à jour dans Anki

Une nouvelle installation a les deux champs remplis. Une installation de la 0.3.0-rc.1 ou de la 0.3.0-rc.2 se comporte ainsi dans Anki 26.9.3, vérifié dans des collections jetables avec des progrès d’étude, dans les deux langues :

| Options d’import | Notes | Cartes, échéances, historique |
|---|---|---|
| Réglages par défaut d’Anki (**Fusionner les types de notes** désactivé, **Mettre à jour les notes** et **Mettre à jour les types de notes** sur **Si plus récent(es)**) | Gardent leurs quatre champs ; les deux nouveaux ne sont pas ajoutés. Anki ajoute une copie inutilisée du type de note, nommée avec un « + », qu’aucune note n’utilise. | Conservés |
| **Fusionner les types de notes** activé, le reste sur **Si plus récent(es)** | Reçoivent les deux champs, vides. | Conservés |
| **Fusionner les types de notes** activé, **Mettre à jour les notes** et **Mettre à jour les types de notes** sur **Toujours** | Reçoivent les deux champs, remplis ; les modifications de l’apprenant dans ces notes et dans le style du type de note sont remplacées. | Conservés |

Il en va de même du français corrigé des notes (0.3.0-rc.3 met une espace fine insécable avant « ; » et « : » et à l’intérieur des « », et « deck » pour « jeu ») : une installation précédente ne le reçoit qu’avec **Toujours**. L’aide d’Anki pour **Fusionner les types de notes** en donne la raison : fusionner un schéma modifié « risque de marquer les notes existantes comme modifiées », si bien que les notes du paquet ne paraissent plus plus récentes. Une mise à jour plus sûre est suivie dans #8 ; ses recherches sont dans `scripts/checks/probe-safer-upgrade.py` et `probe-metadata-conflicts.py`, au commit [a9bf5e0](https://github.com/rectoversohq/rectoverso-maps/tree/a9bf5e041bffd7c83cea98f7a9d6b50284127c45/scripts/checks) ; ce n’est pas un outil de migration.

## Contrôles

`scripts/ci.py` prend la 0.3.0-rc.1 publiée comme référence de mise à jour (ses notes sont celles de la 0.3.0-rc.2). Il exécute `validate-upgrade.py --update-existing always`, un diagnostic qui vérifie que chaque identité, échéance et mémoire FSRS est conservée et que le nouveau contenu arrive, et `check-default-schema-upgrade.py`, qui consigne ce que **Fusionner les types de notes** avec **Si plus récent(es)** fait des nouveaux champs (aujourd’hui, il les laisse vides) et échoue sur tout autre résultat. `ci.json` indique `"defaultSchemaUpgradeSafe": false`. Aucun de ces résultats ne valide la mise à jour par défaut. Les commandes sont dans la [page anglaise](continent-search.md#checks). `build.py` date les types de notes et les notes à `contentModifiedAt`, l’heure de la révision des sources examinée, toujours dans le passé.
