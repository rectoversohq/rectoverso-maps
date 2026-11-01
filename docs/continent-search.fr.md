# Recherche par continent et migration 0.4

Ajout approuvé le 1er/2 novembre 2026, suivi dans [Maps #6](https://github.com/rectoversohq/rectoverso-maps/issues/6). Ce candidat n’est pas publié. **Le 2 novembre 2026, le propriétaire a maintenu la publication en attente d’une mise à jour plus sûre. Le contournement manuel Toujours n’est pas accepté pour publier.** La recherche générique de l’application relève d’une branche distincte.

Les **288 questions, réponses, images et identités publiées** sont conservées. Les quatre champs historiques gardent leur ordre et leurs identités. `Continent` et `RectoVerso search` sont ajoutés à la fin avec des identités stables, sans apparaître dans les modèles d’étude. Le second contient un JSON v1 de valeurs localisées et d’alias français/anglais : continent, région et nom usuel du lieu. La géométrie, les codes et les licences restent hors de la recherche.

## Convention géographique

[continents.json](../source/geography/continents.json) décrit les sept groupes : Afrique, Antarctique, Asie, Europe, Amérique du Nord, Amérique du Sud et Océanie. L’Océanie comprend l’Australie et les îles du Pacifique. Un lieu peut appartenir à plusieurs groupes ; les territoires suivent leur géographie réelle, pas le continent de l’État souverain.

Les questions centrales France/Portugal restent européennes ; Clipperton relève de l’Amérique du Nord et Madère de l’Afrique. Les États-Unis et les îles mineures éloignées relèvent de l’Amérique du Nord et de l’Océanie. Les limites Europe/Asie et le regroupement subantarctique sont explicités dans les données. Cette convention sert à la découverte : elle ne constitue ni une classification ISO/ONU, ni une règle du traité sur l’Antarctique, ni une revendication territoriale.

## Réglage Anki nécessaire

La migration réelle de **0.3.0-rc.1 vers ce candidat** conserve les identités, échéances et mémoires FSRS des 288 cartes dans Anki 26.09.3 avec **Fusionner les types de notes + Toujours mettre à jour les notes et leurs types**. Les nouvelles valeurs sont bien appliquées. Il s’agit uniquement d’un diagnostic : Toujours peut remplacer le contenu édité et n’est pas la migration approuvée.

Le contrôle **Si plus récent** reste insuffisant. Lors de l’ajout de champs, Anki marque d’abord les notes locales comme modifiées à l’heure de l’import ; elles paraissent alors plus récentes que les notes du paquet. Les deux champs apparaissent mais restent vides. Les horodatages du candidat sont pourtant postérieurs à la release. Le script fixe désormais aussi les dates des modèles et notes à l’instant de source revu, `contentModifiedAt`, sans date future artificielle ; le problème reste reproductible.

Le vérificateur garde Si plus récent par défaut. La CI indique explicitement `--update-existing always` pour le contrôle diagnostique et conserve un rapport séparé du défaut. Sa réussite ne certifie donc pas un import par défaut. [Diagnostic chiffré et références Anki](continent-search.md#anki-migration-the-default-does-not-suffice).

```sh
python scripts/checks/validate-upgrade.py /ancien/Cartes-fr-288.apkg /nouveau/Cartes-fr-288.apkg /preuves/migration.json --update-existing always
python scripts/checks/check-default-schema-upgrade.py /ancien/Cartes-fr-288.apkg /nouveau/Cartes-fr-288.apkg /preuves/controle-defaut.json
```

Répéter en anglais. La référence CI est la release publiée de 288 cartes, vérifiée par taille et empreinte. Les anciens paquets de 249 cartes et toutes les étiquettes restent intacts. La compatibilité native de l’application, la revue du propriétaire et l’approbation de cette publication restent distinctes. Aucun sous-module, catalogue, dessin, globe interactif ni release n’a été modifié par ce travail.

## Validation du candidat

La CI locale passe les tests de source, identités et régions, les constructions bilingues, la reproductibilité sémantique et la migration explicite Toujours. Le contrôle distinct conserve `defaultContentApplied: false` pour les 288 notes existantes dans chaque langue. Le premier essai a signalé l’absence de Shapely dans son environnement ; le nouvel environnement contient toutes les dépendances fixées.

La branche séparée de recherche importe bien les deux paquets et leurs métadonnées de continent. Cela ne remplace pas une revue visuelle native. Une construction du commit depuis un clone propre reste requise ; la publication reste suspendue jusqu’à la vérification d’une mise à jour plus sûre.

## Contrôle des régions effectivement dessinées

Les métadonnées de la Colombie et du Venezuela comprennent désormais les Amériques du Sud et du Nord : les contours approuvés, inchangés, comprennent bien San Andrés/Providencia et Isla de Aves. Les questions centrales France/Portugal restent européennes. Aucun dessin, contour ni identifiant n’a changé. Le choix précis entre les regroupements GeoNames et ONU M49 pour BVT/HMD/SGS/ATF est documenté dans le tableau anglais et dans `taxonomyReview`. Le propriétaire a approuvé le 2 novembre 2026 le groupe antarctique nommé de GeoNames et les îles Éparses africaines d’ATF, sans déduire un continent de l’administration par un programme antarctique. Ce choix est tranché et ne change pas le contenu du candidat.

## Recherche d’une migration plus sûre — 2 novembre 2026

Le propriétaire maintient la publication en attente d’une solution plus sûre. Six contrôles ont été exécutés dans chaque langue, dans des collections jetables contenant des réponses modifiées, un champ personnel, des tags, un style personnalisé, les échéances et la mémoire FSRS.

Les cinq variantes d’import de paquet — fusion désactivée, fusion Si plus récent, types Jamais, types Toujours, puis second import par défaut — remplissent **0/288** valeurs nouvelles. Le réglage Toujours des types remplace aussi le CSS personnel. Un contrôle distinct réussit : après ajout des champs vides par la fusion par défaut, un import texte associé par GUID et limité aux **deux nouveaux champs** remplit **288/288** valeurs tout en conservant les réponses, champs et tags personnels, le style, les identités et les progrès.

Ce résultat est une piste, pas une migration approuvée. Il reste à valider les identités et associations de champs, refuser les conflits avec un contenu personnel préexistant dans les champs cibles, démontrer sauvegarde/restauration et répétabilité, puis vérifier les réglages dans l’interface native Anki. L’import habituel du paquet reste insuffisant. Aucune collection personnelle n’a été ouverte. Le [script de recherche et le tableau détaillé](continent-search.md#safer-upgrade-research--2-november-2026) restent distincts d’un outil destiné aux utilisateurs.
