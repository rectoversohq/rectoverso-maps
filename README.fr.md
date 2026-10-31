# Cartes / Maps

**Reconnaître un lieu. Apprendre son nom.** 249 pays et territoires, en français ou en anglais, pour Anki.

[English](README.md) · [Construire les jeux](#construire-pour-anki) · [Sources et limites](docs/sources.fr.md) · [CC BY 4.0](LICENSE)

<img src="source/media/rv-map-ita.png" alt="Exemple de carte : l’Italie en doré, entourée d’une mer bleue et de pays voisins gris ardoise." width="640">

*Une carte au recto. Son nom au verso. Ici, Italie / Italy.*

## Ce que vous obtenez

| Langue | Jeu dans Anki | Cartes | Fichier produit |
| --- | --- | ---: | --- |
| English | Maps | 249 | `Maps-en-249.apkg` |
| Français | Cartes | 249 | `Cartes-fr-249.apkg` |

Choisissez une langue ou installez les deux. Les paquets partagent leurs images et leur géométrie, mais leurs identités de notes sont distinctes : les révisions restent indépendantes. Chaque paquet contient toutes ses images ; aucun compte ni application RectoVerso n’est nécessaire pour étudier dans Anki.

La sélection suit les 249 codes de pays et territoires officiellement attribués par l’ISO 3166-1 dans la référence conservée. Elle comprend des territoires inhabités : **ce n’est pas une liste de 249 États souverains**. Les noms usuels sont distincts des noms formels de l’ISO. [Lire la convention de couverture et de limites](docs/sources.fr.md), notamment le traitement neutre du Cachemire et d’Abyei.

**État de la version :** `0.2.0-rc.1` est un candidat de revue non publié. Les URL de release dans les métadonnées sont des destinations prévues. Aucune release n’est encore téléchargeable ; la publication des sources reste à faire. Le [workflow de CI Anki](docs/building.fr.md#contrôles-automatiques) est prêt ; sa première exécution GitHub attend cette publication.

## Construire pour Anki

La fabrication utilise les images déjà présentes dans ce dépôt. **Ni Node, ni Swift, ni téléchargement de données cartographiques ne sont nécessaires pour cette étape.**

Prérequis : Git, Bash et **Python 3.14**, avec `venv` et `pip`. La procédure est testée sur macOS avec la bibliothèque Python d’Anki figée à **26.9.3**. Les autres systèmes n’ont pas été vérifiés. Anki desktop permet d’étudier le jeu obtenu, mais n’a pas besoin d’être lancé pendant sa fabrication.

Une fois cette branche source publiée, clonez le dépôt et créez l’environnement. Si vous disposez déjà des sources, commencez par `cd` :

```sh
git clone https://github.com/rectoversohq/rectoverso-maps.git
cd rectoverso-maps
python3.14 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

Construisez les deux langues dans un **nouveau dossier hors du dépôt**. Les SVG originaux occupent une place importante ; prévoyez de l’espace pour les sources, les paquets et les fichiers temporaires. Remplacez le chemin d’exemple par un chemin sur votre disque de données :

```sh
ANKI_PYTHON="$PWD/.venv/bin/python" ./build.sh /chemin/absolu/vers/cartes-build
```

La commande vérifie les sources, crée les deux fichiers `.apkg` et leurs métadonnées `.rectoverso.json`, puis importe chaque paquet avec la bibliothèque d’Anki. Elle contrôle le nombre de cartes, les rectos et versos rendus, les médias manquants, l’unicité des notes et la conservation des progrès lors d’un nouvel import. Les résultats sont enregistrés dans `evidence/anki-validation.json`, dans le dossier de sortie. Un contrôle échoué interrompt la commande avec une erreur ; gardez ses résultats pour le diagnostic et utilisez un nouveau dossier pour réessayer.

Ouvrez le `.apkg` de la langue choisie dans Anki desktop. Les fichiers `.rectoverso.json` sont des métadonnées de fabrication : **ne les importez pas**. Conservez les paquets intacts afin que leurs identités stables puissent préserver vos progrès lors des mises à jour.

## Modifier les sources

Les images, les données géographiques et les outils sont partagés. Les définitions françaises et anglaises vivent à côté :

```text
rectoverso.json         Métadonnées communes, version et paquets par langue
source/
  places.json           Noms bilingues, GUID stables et géométrie des lieux
  media/                249 cartes PNG prêtes à empaqueter
  svg/                  Dessins vectoriels originaux
  languages/en/         Jeu, type de note et traductions en anglais
  languages/fr/         Jeu, type de note et traductions en français
  style.css             Apparence Anki commune
source_data.py          Compose les notes à partir des sources
build.sh                Construit et valide les deux langues
```

La [référence de fabrication et de vérification](docs/building.fr.md) couvre les tests, la régénération des images, les identités et le schéma des métadonnées. Les [notes sur les sources et les limites](docs/sources.fr.md) expliquent les choix cartographiques et les crédits. Toute contribution doit préserver les identités des notes, jeux, modèles, champs et modèles de cartes ; discutez les changements de couverture, de noms et de limites avant de les modifier.

## Licence et crédits

Nos contenus originaux, cartes, métadonnées et outils sont **© Simon Pinkas, CC BY 4.0**. Vous pouvez les partager et les adapter, y compris commercialement, selon les conditions d’attribution et les autres termes de cette licence. Créditez l’auteur, liez la licence et indiquez vos modifications. [LICENSE](LICENSE) contient la licence complète ; [NOTICE.md](NOTICE.md) précise son périmètre et les crédits des sources. Les dépendances conservent leurs propres licences.

La géométrie vient principalement de **Natural Earth 5.1.2** (domaine public). Les îles McDonald utilisent le littoral de **Geoscience Australia / Australian Antarctic Data Centre** (CC BY 4.0). Certains noms usuels proviennent d’**Ultimate Geography 5.3** (texte dans le domaine public) ; aucune de ses images n’est réutilisée. Chaque image produite est créditée dans `imageCredits`, dans `rectoverso.json`. [Détail des sources](docs/sources.fr.md#crédits-et-licence).
