# Fabrication et vérification de Cartes

[Retour à Cartes / Maps](../README.fr.md) · [English](building.md)

Pour le candidat 0.4 non publié, lire [la migration des champs continent](continent-search.fr.md). La CI utilise désormais 0.3.0-rc.1 (288 cartes), indique Toujours comme contrôle diagnostique uniquement, non accepté pour publier, et conserve le contrôle du défaut non pris en charge. Les exemples historiques de 249 cartes ci-dessous concernent la release régionale précédente.

## Empaqueter les cartes existantes

Suivre la [préparation du README](../README.fr.md#construire-pour-anki). Exécuter les commandes à la racine du dépôt. `requirements.txt` fixe les dépendances Python directes : Anki 26.9.3 et Shapely 2.1.2. Shapely sert à régénérer la géométrie ; les images stockées suffisent pour construire les paquets Anki.

```sh
ANKI_PYTHON="$PWD/.venv/bin/python" ./scripts/build.sh /chemin/absolu/vers/nouveaux-paquets
```

La commande crée `Maps-en-288.apkg`, `Cartes-fr-288.apkg`, un fichier `.rectoverso.json` par paquet et `evidence/anki-validation.json`. Elle refuse un dossier déjà présent ou situé dans le dépôt. Les fichiers temporaires de fabrication et d’Anki restent à côté des paquets de sortie.

Chaque paquet contient 288 notes et cartes : les 249 identités ISO et 39 régions nommées. Le script combine noms, GUID et champs géographiques partagés avec les modèles, noms de champs et notes sur les limites de chaque langue. Il ne télécharge pas de données et ne modifie pas les sources. Les horodatages d’Anki peuvent changer les octets d’une archive reconstruite : comparer son contenu et ses identités. Les empreintes des métadonnées désignent les candidats exacts préparés pour une release.

## Vérifier les sources et les identités

Utiliser l’environnement Python créé lors de la préparation. Les tests copient des fichiers temporaires ; faire pointer `TMPDIR` vers un dossier existant sur le disque de données.

```sh
mkdir -p /chemin/absolu/vers/cartes-test-tmp
.venv/bin/python scripts/checks/verify-coverage.py
TMPDIR=/chemin/absolu/vers/cartes-test-tmp .venv/bin/python tests/test-source.py
TMPDIR=/chemin/absolu/vers/cartes-test-tmp .venv/bin/python tests/test-render-pngs.py
```

Le contrôle de couverture vérifie l’empreinte de l’instantané ISO, les 249 codes et leurs formats, les noms officiels et annotations bilingues, les noms usuels, les crédits des images et les identités distinctes des langues. Il contrôle la référence conservée, pas le registre actuel. Les tests endommagent volontairement une copie : pays ou image absent, nom usuel changé, chemin invalide, note sur une limite inconnue, modèles aux identités identiques ou URL de release incorrecte doivent être refusés.

Les tests de conversion vérifient les reprises bornées, le délai maximal, l’isolation des fichiers partiels et le refus d’une sortie existante. Ils utilisent un petit convertisseur simulé ; ils ne certifient pas l’apparence des images réelles.

Après une fabrication indépendante, comparer chaque langue à son candidat précédent :

```sh
.venv/bin/python scripts/checks/validate-rebuild.py /chemin/precedent/Maps-en-288.apkg /chemin/nouveau/Maps-en-288.apkg /chemin/preuves/identity-en.json
.venv/bin/python scripts/checks/validate-rebuild.py /chemin/precedent/Cartes-fr-288.apkg /chemin/nouveau/Cartes-fr-288.apkg /chemin/preuves/identity-fr.json
```

Ce contrôle compare les GUID, les identités de jeux, types de notes, champs et modèles de cartes, puis importe réellement la mise à jour dans une collection avec des progrès planifiés. Anki peut attribuer une identité locale au jeu lors du premier import ; les imports suivants doivent la conserver avec les progrès. Les deux langues peuvent coexister avec des révisions indépendantes.

L’ancien schéma de revue non publié de 243 cartes constitue une migration distincte : 231 GUID communs, 18 ajouts et 12 anciennes cartes conservées par Anki. La migration testée exige la fusion des types de notes et la mise à jour des notes et de leurs types. Elle ne supprime pas automatiquement les cartes pour obtenir une collection de 249 cartes. Le contrôle de reconstruction à schéma constant ne prouve pas cette ancienne migration.

## Régénérer les images

Cette étape est facultative pour fabriquer un paquet Anki. Elle est nécessaire après un changement des données cartographiques ou du moteur de rendu.

Utiliser macOS avec `swiftc`, AppKit et WebKit disponibles, Node 22 ou ultérieur avec npm, et l’environnement Python ci-dessus. Git conserve les SVG originaux et les PNG. `scripts/maps/package-lock.json` fixe les dépendances JavaScript. Les empreintes des données Natural Earth 5.1.2 sont contrôlées au téléchargement ; le complément McDonald et sa provenance sont dans `source/geography/supplements/`.

```sh
DRAWING_PYTHON="$PWD/.venv/bin/python" ./scripts/maps/regenerate.sh /chemin/absolu/cache-natural-earth /chemin/absolu/nouveaux-dessins
```

La commande récupère les données manquantes avec contrôle d’empreinte, prépare la géométrie, lance `npm ci`, dessine les SVG, compile le convertisseur PNG et compare les 288 SVG, PNG et données de lieux aux sources. Utiliser un nouveau dossier de sortie ; il conserve les dessins, caches du compilateur et fichiers temporaires. npm peut contacter son registre ; définir `npm_config_cache` pour placer son cache sur le disque de données. Le premier dossier fourni conserve les téléchargements Natural Earth.

Chaque conversion PNG dispose de trois processus distincts au maximum, chacun limité à 60 secondes. Un fichier partiel ne peut pas être accepté à l’essai suivant. L’épuisement des essais ou une différence finale d’octets fait échouer la commande. Une comparaison exacte exige le même environnement macOS/WebKit ; un autre environnement peut produire des octets différents, à examiner sans remplacer silencieusement les références. Les anciens échecs WebKit étaient intermittents : la reprise est bornée, sans prétendre corriger leur cause profonde.

## Métadonnées et publication

`rectoverso.json` utilise `schemaVersion: 2`. Titres, crédits, couverture, chemins communs, crédits des images et version n’apparaissent qu’une fois. `languages.en` et `languages.fr` contiennent identifiants stables, noms, empreintes et URL des paquets, ainsi que les chemins des définitions localisées. `scripts/source_data.py` compose les métadonnées de chaque paquet, avec `language` et le `deckID` commun.

[0.3.0-rc.1](https://github.com/rectoversohq/rectoverso-maps/releases/tag/v0.3.0-rc.1) contient 288 cartes par langue. Son étiquette identifie les sources approuvées ; ses quatre fichiers sont les paquets français et anglais exacts soumis à revue, avec leurs métadonnées. `rectoverso.json`, à cette étiquette, indique la taille et l’empreinte de chaque paquet. Les horodatages d’Anki peuvent faire varier les octets d’une reconstruction, tout en conservant contenus et identités. La [release 0.2.0-rc.2](https://github.com/rectoversohq/rectoverso-maps/releases/tag/v0.2.0-rc.2), son étiquette et ses fichiers de 249 cartes restent intacts ; les sources régionales précédentes les utilisaient comme référence figée de mise à jour. L’étiquette v0.2.0-rc.1 conserve l’ancienne organisation des outils. Les étiquettes ne sont pas déplacées, les paquets restent hors de Git et les anciens dossiers de travail par langue et leurs historiques sont conservés.

La CI du dépôt de jeu doit contrôler les sources, Anki et les identités des reconstructions. Le dépôt de l’application RectoVerso assure sa compatibilité d’import/export et l’intégration de la galerie. Son passage à un sous-module unique est suivi dans simonpinkas/RectoVerso#633 ; le workflow source est implémenté ici, avec un workflow explicite de compatibilité dans le dépôt de l’application. La CI source est active sur GitHub. Le workflow de l’application est intégré à la branche de galerie ; sa disponibilité manuelle hébergée attend que #616 atteigne main ; la CI source ne publie ni paquets ni ressources Apple. Anki utilise les images stockées ; les limites du globe interactif de l’application pour l’Antarctique et les îles dispersées restent un sujet distinct, en attente.

## Interface de validation de la galerie

L’interface organisée comprend `scripts/source_data.py`, `scripts/build.sh`, `scripts/checks/validate-anki.py` et `scripts/checks/validate-rebuild.py`. L’application conserve l’interface à la racine pour les anciennes étiquettes immuables. Elle ne mélange pas les deux structures et refuse une structure organisée incomplète.

Le dépôt de l’application vérifie d’abord le commit, l’étiquette et la propreté du sous-module. Il appelle ensuite `scripts/source_data.py` (`inputs(language)`) dans un processus Python distinct, sans écrire de fichiers. Cette fonction retourne `(metadata, notes, model, deck)`, sérialisables en JSON. Les métadonnées développées doivent correspondre exactement aux données communes et à l’entrée de langue déclarées. La construction des notes reste dans ce dépôt ; l’application ne duplique pas la logique géographique.

## Contrôles automatiques

`.github/workflows/anki.yml` lance **Anki packages** sur les pull requests, les pushes de branches et les demandes manuelles, sur un Mac hébergé par GitHub avec Python 3.14.7. Les actions sont figées par commit et les permissions du dépôt sont en lecture seule. Aucun Anki desktop lancé, identifiant, signature ni jeton de release n’est nécessaire. Ce workflow ne publie aucune release.

Pour exécuter la même suite localement, avec l’environnement du README :

```sh
.venv/bin/python scripts/ci.py --output /chemin/absolu/vers/nouvelle-sortie-ci --base SHA_COMPLET_DU_COMMIT_PRECEDENT
```

La référence doit exister dans l’historique Git local. La CI utilise la base de la PR ou le commit précédant le push. Un premier push de branche ou une demande manuelle sans `base` conserve une référence nulle : seule la comparaison des identités entre commits est omise ; la mise à jour depuis la release figée reste testée. Pour contrôler manuellement une mise à jour, fournir le commit source précédemment approuvé dans `base`.

La suite contrôle la couverture, les tests des sources, du rendu et des identités, puis compare les GUID et les identités des jeux, modèles, champs et modèles de cartes à la référence, sans exécuter son code. Elle construit deux fois les deux langues, vérifie les deux constructions avec Anki et importe la reconstruction sur des cartes déjà révisées. Les ajouts sont signalés ; supprimer une langue ou une carte, ou modifier une identité, échoue et exige une migration explicitement conçue. La référence ISO reste exactement de 249 entrées ; 39 questions régionales sont vérifiées séparément, pour un total de 288. Ce contrôle protège les identités entre commits sans certifier toutes les migrations historiques possibles.

Dans Actions, ouvrir l’exécution et télécharger `maps-anki-RUN_ID-ATTEMPT`. L’archive contient les deux `.apkg` et leurs métadonnées de la première construction, les rapports Anki, journaux, comparaison et `ci.json`. Ces résultats restent disponibles 14 jours, y compris les journaux disponibles en cas d’échec. Une valeur `passed` absente ou fausse dans `ci.json` ne vaut pas réussite. Ce sont des artefacts de test, pas des releases publiées. Leurs empreintes décrivent ces nouvelles constructions ; les métadonnées de release décrivent toujours le lot exact soumis à revue.

Actions est activé pour ce dépôt public. Dans les paramètres, autoriser `actions/checkout`, `actions/setup-python` et `actions/upload-artifact`, puis rendre **Anki packages** obligatoire dans les règles de la branche par défaut après une première réussite. Le workflow doit atteindre cette branche avant que le bouton Run workflow soit disponible. Les contributions passent par une branche et une PR dans ce dépôt. Les changements d’images exigent toujours une régénération complète et une revue visuelle humaine ; cette CI ne certifie ni l’esthétique des cartes ni le globe interactif de l’application.

## Questions régionales et mise à jour additive

La version 0.3.0-rc.1 contient 288 cartes par langue : 249 entités ISO et 39 régions supplémentaires. Les noms historiques des champs de réponse restent stables ; les nouveaux modèles Anki s’appellent **Carte → Lieu**. RectoVerso déduit son en-tête **Carte → Pays ou territoire** des noms de champs conservés : les métadonnées gardent donc ce libellé, y compris pour les questions régionales. Une modification du texte de l’app dépasse cette mise à jour des sources. Les fichiers rc.2 publiés restent intacts. `tests/test-regions.py` et les tests de sources corrompues contrôlent l’affectation exacte des polygones, les groupes manquants ou superposés et les fausses classifications ISO ; ces tests sont exécutés en CI.

```sh
.venv/bin/python scripts/checks/validate-upgrade.py /chemin/rc2/Cartes-fr-249.apkg /chemin/candidat/Cartes-fr-288.apkg /chemin/preuves/upgrade-fr.json --update-existing always
```

Répétez en anglais. Le contrôle programme une révision pour chaque ancienne carte, importe le candidat et vérifie identités, schéma, échéances, total, médias et rendu. Il est distinct de la comparaison de deux constructions. La régénération complète des images et leur examen visuel restent obligatoires ; la CI des sources ne certifie pas le globe de l’app.

La CI télécharge aussi la référence rc.2 explicitement figée, avec vérification de l’URL, de la taille et du SHA-256, puis teste la mise à jour additive dans les deux langues. Durée et taille des téléchargements sont bornées ; ils restent dans le dossier externe fourni et ne constituent pas une nouvelle publication.

Anki peut conserver le nom local du modèle de carte et les anciennes images inutilisées lors d’un conflit de noms de fichiers. Le contrôle compare les octets des nouvelles images réellement référencées et le schéma de rendu ; il conserve aussi la mémoire FSRS de chaque carte existante.
