# Journal des versions

Le numérotage suit trois niveaux : le premier chiffre change quand une mise à
jour casse l’existant — arborescence ou format des réglages —, le deuxième pour
une nouvelle fonction, le troisième pour une correction.

## 2.9.0

- Mode automatique fondé sur les noms de dossiers, qui l’emportent sur
  l’extension et sur l’EXIF. Une seule source suffit pour toute une journée :
  la racine du voyage. Sépare au passage le GPX Garmin de celui de Geo-Log.
- Journal de diagnostic avec rotation dans `~/.vespa-organizer/`, et menu
  **Aide** pour l’exporter.
- Correction : les chemins passés à exiftool transitaient par la ligne de
  commande, plafonnée à ~32 000 caractères sous Windows, ce qui bloquait
  l’analyse d’un gros lot. Ils passent désormais par un fichier d’arguments,
  avec `-charset filename=UTF8` pour les dossiers accentués.

## 2.8.0

- Le nom du voyage est demandé une seule fois, à la création ; le slug du
  dossier en découle.
- *Début*, *Fin* et *Jours* se déduisent l’un de l’autre dans les paramètres.

## 2.7.0

- Les dossiers `00_trip` et `99_admin`, qui ne recevaient plus rien, ne sont
  plus créés.
- Avertissement quand une source typée contient des fichiers portant les
  marques d’un autre appareil ; le choix de la source l’emporte toujours.

## 2.6.x

- Correction : les onglets Géolocaliser et Journal cherchaient encore les
  anciens chemins `raw/garmin/` et `raw/geolog/`, disparus avec les dossiers
  numérotés. L’onglet Géolocaliser ne fonctionnait plus du tout.
- Correction : le journal attribuait les médias au dossier `PHOTO`/`VIDEO` au
  lieu de l’appareil.
- Correction : l’alerte « export à cheval sur plusieurs journées » comparait des
  dates calendaires au lieu de journées de voyage, et se déclenchait à tort sur
  une route se prolongeant après minuit.
- La date de compilation est lue sur le fichier lui-même.
- Infobulles en bulles compactes, repositionnées pour rester à l’écran.
- L’Insta360 X5 et l’Ace Pro 2 peuvent produire des photos.
- « Déplacer au lieu de copier » remplacé par « Exclure les SRT / LRV ».
- `20_SELECTION` supprimé : la sélection et les découpes se font avant l’import.

## 2.5.x

- Exclusion des RAW/DNG, cochée par défaut.
- Animation du scooter dans l’en-tête, images embarquées en couleur — Tk ne
  rend pas les polices emoji en couleur sous Windows.
- Infobulles sur les contrôles.

## 2.4.x

- Fenêtre « À propos », version dans la barre de titre.

## Avant

Paramètres du voyage comme source de vérité, dossiers par appareil avec
numérotation fixe, séparation photo/vidéo, refus des fichiers non attribuables,
datage des GPX et KML par leur contenu, exclusion des dossiers `_Rejected`,
dédoublonnage des sources imbriquées, thème sombre, onglets Géolocaliser et
Journal.
