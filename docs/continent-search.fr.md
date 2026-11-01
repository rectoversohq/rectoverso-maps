# Recherche par continent et migration 0.4

Ajout approuvé le 1er/2 novembre 2026, suivi dans [Maps #6](https://github.com/rectoversohq/rectoverso-maps/issues/6). Ce candidat n’est pas publié. **La revue de publication est bloquée jusqu’à l’acceptation de la migration manuelle, ou la vérification d’une correction compatible avec le réglage par défaut.** La recherche générique de l’application relève d’une branche distincte.

Les **288 questions, réponses, images et identités publiées** sont conservées. Les quatre champs historiques gardent leur ordre et leurs identités. `Continent` et `RectoVerso search` sont ajoutés à la fin avec des identités stables, sans apparaître dans les modèles d’étude. Le second contient un JSON v1 de valeurs localisées et d’alias français/anglais : continent, région et nom usuel du lieu. La géométrie, les codes et les licences restent hors de la recherche.

## Convention géographique

[continents.json](../source/geography/continents.json) décrit les sept groupes : Afrique, Antarctique, Asie, Europe, Amérique du Nord, Amérique du Sud et Océanie. L’Océanie comprend l’Australie et les îles du Pacifique. Un lieu peut appartenir à plusieurs groupes ; les territoires suivent leur géographie réelle, pas le continent de l’État souverain.

Les questions centrales France/Portugal restent européennes ; Clipperton relève de l’Amérique du Nord et Madère de l’Afrique. Les États-Unis et les îles mineures éloignées relèvent de l’Amérique du Nord et de l’Océanie. Les limites Europe/Asie et le regroupement subantarctique sont explicités dans les données. Cette convention sert à la découverte : elle ne constitue ni une classification ISO/ONU, ni une règle du traité sur l’Antarctique, ni une revendication territoriale.

## Réglage Anki nécessaire

La migration réelle de **0.3.0-rc.1 vers ce candidat** conserve les identités, échéances et mémoires FSRS des 288 cartes dans Anki 26.09.3 avec **Fusionner les types de notes + Toujours mettre à jour les notes et leurs types**. Les nouvelles valeurs sont bien appliquées. Sauvegarder les modifications personnelles : Toujours peut remplacer le contenu édité.

Le contrôle **Si plus récent** reste insuffisant. Lors de l’ajout de champs, Anki marque d’abord les notes locales comme modifiées à l’heure de l’import ; elles paraissent alors plus récentes que les notes du paquet. Les deux champs apparaissent mais restent vides. Les horodatages du candidat sont pourtant postérieurs à la release. Le script fixe désormais aussi les dates des modèles et notes à l’instant de source revu, `contentModifiedAt`, sans date future artificielle ; le problème reste reproductible.

Le vérificateur garde Si plus récent par défaut. La CI indique explicitement `--update-existing always` pour le cas pris en charge et conserve un rapport séparé du défaut. Sa réussite ne certifie donc pas un import par défaut. [Diagnostic chiffré et références Anki](continent-search.md#anki-migration-the-default-does-not-suffice).

```sh
python scripts/checks/validate-upgrade.py /ancien/Cartes-fr-288.apkg /nouveau/Cartes-fr-288.apkg /preuves/migration.json --update-existing always
python scripts/checks/check-default-schema-upgrade.py /ancien/Cartes-fr-288.apkg /nouveau/Cartes-fr-288.apkg /preuves/controle-defaut.json
```

Répéter en anglais. La référence CI est la release publiée de 288 cartes, vérifiée par taille et empreinte. Les anciens paquets de 249 cartes et toutes les étiquettes restent intacts. La compatibilité native de l’application, la revue du propriétaire et l’approbation de cette publication restent distinctes. Aucun sous-module, catalogue, dessin, globe interactif ni release n’a été modifié par ce travail.

## Validation du candidat

La CI locale passe les tests de source, identités et régions, les constructions bilingues, la reproductibilité sémantique et la migration explicite Toujours. Le contrôle distinct conserve `defaultContentApplied: false` pour les 288 notes existantes dans chaque langue. Le premier essai a signalé l’absence de Shapely dans son environnement ; le nouvel environnement contient toutes les dépendances fixées.

La branche séparée de recherche importe bien les deux paquets et leurs métadonnées de continent. Cela ne remplace pas une revue visuelle native. Une construction du commit depuis un clone propre reste requise ; la publication attend le choix du propriétaire sur la migration.
