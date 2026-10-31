# Fabrication et vérification de Cartes

[Retour à Cartes / Maps](../README.fr.md) · [English](building.md)

## Empaqueter les cartes existantes

Suivre la [préparation du README](../README.fr.md#construire-pour-anki). Exécuter les commandes à la racine du dépôt. `requirements.txt` fixe les dépendances Python directes : Anki 26.9.3 et Shapely 2.1.2. Shapely sert à régénérer la géométrie ; les images stockées suffisent pour construire les paquets Anki.

```sh
ANKI_PYTHON="$PWD/.venv/bin/python" ./build.sh /chemin/absolu/vers/nouveaux-paquets
```

La commande crée `Maps-en-249.apkg`, `Cartes-fr-249.apkg`, un fichier `.rectoverso.json` par paquet et `evidence/anki-validation.json`. Elle refuse un dossier déjà présent ou situé dans le dépôt. Les fichiers temporaires de fabrication et d’Anki restent à côté des paquets de sortie.

Chaque paquet contient 249 notes et cartes. Le script combine noms, GUID et champs géographiques partagés avec les modèles, noms de champs et notes sur les limites de chaque langue. Il ne télécharge pas de données et ne modifie pas les sources. Les horodatages d’Anki peuvent changer les octets d’une archive reconstruite : comparer son contenu et ses identités. Les empreintes des métadonnées désignent les candidats exacts préparés pour une release.

## Vérifier les sources et les identités

Utiliser l’environnement Python créé lors de la préparation. Les tests copient des fichiers temporaires ; faire pointer `TMPDIR` vers un dossier existant sur le disque de données.

```sh
mkdir -p /chemin/absolu/vers/cartes-test-tmp
.venv/bin/python verify-coverage.py
TMPDIR=/chemin/absolu/vers/cartes-test-tmp .venv/bin/python test-source.py
TMPDIR=/chemin/absolu/vers/cartes-test-tmp .venv/bin/python test-render-pngs.py
```

Le contrôle de couverture vérifie l’empreinte de l’instantané ISO, les 249 codes et leurs formats, les noms officiels et annotations bilingues, les noms usuels, les crédits des images et les identités distinctes des langues. Il contrôle la référence conservée, pas le registre actuel. Les tests endommagent volontairement une copie : pays ou image absent, nom usuel changé, chemin invalide, note sur une limite inconnue, modèles aux identités identiques ou URL de release incorrecte doivent être refusés.

Les tests de conversion vérifient les reprises bornées, le délai maximal, l’isolation des fichiers partiels et le refus d’une sortie existante. Ils utilisent un petit convertisseur simulé ; ils ne certifient pas l’apparence des images réelles.

Après une fabrication indépendante, comparer chaque langue à son candidat précédent :

```sh
.venv/bin/python validate-rebuild.py /chemin/precedent/Maps-en-249.apkg /chemin/nouveau/Maps-en-249.apkg /chemin/preuves/identity-en.json
.venv/bin/python validate-rebuild.py /chemin/precedent/Cartes-fr-249.apkg /chemin/nouveau/Cartes-fr-249.apkg /chemin/preuves/identity-fr.json
```

Ce contrôle compare les GUID, les identités de jeux, types de notes, champs et modèles de cartes, puis importe réellement la mise à jour dans une collection avec des progrès planifiés. Anki peut attribuer une identité locale au jeu lors du premier import ; les imports suivants doivent la conserver avec les progrès. Les deux langues peuvent coexister avec des révisions indépendantes.

L’ancien schéma de revue non publié de 243 cartes constitue une migration distincte : 231 GUID communs, 18 ajouts et 12 anciennes cartes conservées par Anki. La migration testée exige la fusion des types de notes et la mise à jour des notes et de leurs types. Elle ne supprime pas automatiquement les cartes pour obtenir une collection de 249 cartes. Le contrôle de reconstruction à schéma constant ne prouve pas cette ancienne migration.

## Régénérer les images

Cette étape est facultative pour fabriquer un paquet Anki. Elle est nécessaire après un changement des données cartographiques ou du moteur de rendu.

Utiliser macOS avec `swiftc`, AppKit et WebKit disponibles, Node 22 ou ultérieur avec npm, et l’environnement Python ci-dessus. Git conserve les SVG originaux et les PNG. `package-lock.json` fixe les dépendances JavaScript. Les empreintes des données Natural Earth 5.1.2 sont contrôlées au téléchargement ; le complément McDonald et sa provenance sont dans `source/geometry/`.

```sh
DRAWING_PYTHON="$PWD/.venv/bin/python" ./regenerate.sh /chemin/absolu/cache-natural-earth /chemin/absolu/nouveaux-dessins
```

La commande récupère les données manquantes avec contrôle d’empreinte, prépare la géométrie, lance `npm ci`, dessine les SVG, compile le convertisseur PNG et compare les 249 SVG, PNG et données de lieux aux sources. Utiliser un nouveau dossier de sortie ; il conserve les dessins, caches du compilateur et fichiers temporaires. npm peut contacter son registre ; définir `npm_config_cache` pour placer son cache sur le disque de données. Le premier dossier fourni conserve les téléchargements Natural Earth.

Chaque conversion PNG dispose de trois processus distincts au maximum, chacun limité à 60 secondes. Un fichier partiel ne peut pas être accepté à l’essai suivant. L’épuisement des essais ou une différence finale d’octets fait échouer la commande. Une comparaison exacte exige le même environnement macOS/WebKit ; un autre environnement peut produire des octets différents, à examiner sans remplacer silencieusement les références. Les anciens échecs WebKit étaient intermittents : la reprise est bornée, sans prétendre corriger leur cause profonde.

## Métadonnées et publication

`rectoverso.json` utilise `schemaVersion: 2`. Titres, crédits, couverture, chemins communs, crédits des images et version n’apparaissent qu’une fois. `languages.en` et `languages.fr` contiennent identifiants stables, noms, empreintes et URL des paquets, ainsi que les chemins des définitions localisées. `source_data.py` compose les métadonnées de chaque paquet, avec `language` et le `deckID` commun.

Le candidat actuel est `0.2.0-rc.1`. Ses métadonnées nomment l’étiquette prévue `v0.2.0-rc.1`, sans affirmer l’existence d’une étiquette, release, validation distante ou CI terminée. Les paquets vont dans les releases versionnées, jamais dans Git. Les anciens dossiers de travail par langue et leurs historiques Git ont été conservés séparément avant consolidation.

La CI du dépôt de jeu doit contrôler les sources, Anki et les identités des reconstructions. Le dépôt de l’application RectoVerso assure sa compatibilité d’import/export et l’intégration de la galerie. Son passage à un sous-module unique et les deux workflows restent à faire. Anki utilise les images stockées ; les limites du globe interactif de l’application pour l’Antarctique et les îles dispersées restent un sujet distinct, en attente.
