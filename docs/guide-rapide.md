# Vespa Travel Content Organizer — mode d’emploi

Application de bureau pour ranger, géolocaliser et documenter les médias d’un roadtrip.
Un seul fichier Python, sans installation ni dépendance.

---

## 1. Avant de lancer

**Vérifier Python.** Dans un terminal :

```
python3 --version
```

Il faut 3.9 ou plus récent. Si la commande est inconnue sous Windows, essayez `py --version`.

**Lancer l’application.** Placez-vous dans le dossier contenant le fichier, puis :

```
python3 vespa_organizer.py
```

Sous Windows : `py vespa_organizer.py`. Vous pouvez aussi créer un raccourci vers cette commande — vous la taperez tous les soirs pendant deux mois.

**Si rien ne s’ouvre et que le terminal parle de Tkinter :** sous Linux, `sudo apt install python3-tk`. Sous macOS et Windows, réinstallez Python depuis python.org — la version fournie avec le système est parfois amputée de Tkinter.

**exiftool est optionnel.** Son chemin apparaît dans le journal de bord au démarrage quand il est trouvé, et les instructions d’installation s’y affichent sinon. Sans lui, l’application fonctionne, mais deux choses se dégradent : les dates de prise de vue des vidéos deviennent moins fiables, et l’écriture des coordonnées de l’onglet 2 est impossible. Installation : `brew install exiftool` sur macOS, `sudo apt install libimage-exiftool-perl` sous Linux, ou l’archive de exiftool.org sous Windows — en renommant `exiftool(-k).exe` en `exiftool.exe` et en le plaçant dans `C:\Windows`. S’il est installé mais non trouvé, ouvrez **À propos** et cliquez sur *Localiser exiftool…* pour le désigner à la main.

---

## 2. Ce soir, en dix minutes

La séquence pour vos deux journées de Vespa, dans l’ordre. Ne sautez pas l’étape 1.

### Étape 1 — Récupérer les photos du Pixel 11 via Google Photos

C’est la voie la plus simple, et elle évite de brancher le téléphone.

1. Dans **Google Photos**, sélectionnez les photos et vidéos des journées concernées et mettez-les dans un **album dédié** — un album par voyage suffit.
2. Ouvrez l’album sur `photos.google.com`, menu **⋮ → Tout télécharger**. Vous obtenez un ZIP.
3. Décompressez-le dans un dossier temporaire.
4. Ajoutez ce dossier comme source dans l’application.

**Pourquoi l’album est mieux que le câble.** Le problème que résolvait le branchement USB était la contamination de la pellicule : les applications Insta360 et DJI Fly y déversent leurs exports, et on ne distingue plus ce qu’on a photographié de ce qu’on a recadré. L’album règle cela plus proprement, parce que le tri se fait **par sélection** et non par ordre chronologique des opérations. Vous choisissez vos prises de vue, les recadrages restent dehors.

> **Vérifiez un point après le premier import.** Le journal de bord de l’application affiche d’où viennent les dates : `Dates : exif 28, nom 15`. Selon la qualité de sauvegarde et la voie de téléchargement, Google Photos ne restitue pas toujours les EXIF intacts. Ce n’est pas bloquant : Google conserve les **noms de fichiers d’origine** (`PXL_20260905_103012000.jpg`), et l’application sait lire la date dans le nom. Le classement par journée reste donc correct dans les deux cas. Si vous voyez beaucoup de `nom` et peu d’`exif`, c’est simplement que les EXIF ont été rabotés au passage.

**Deux réglages à contrôler une fois pour toutes**, dans les paramètres de sauvegarde Google Photos :

- **Qualité de sauvegarde sur « Originale »**, et non « Économiseur d’espace » : cette dernière rééchantillonne les photos et recompresse les vidéos, notamment la 4K.
- Si les EXIF vous importent vraiment — pour la géolocalisation notamment — **Google Takeout** restitue les fichiers tels quels, sans transcodage, mais c’est bien plus lourd qu’un album et cela demande d’attendre la préparation de l’archive. Réservez-le à une sauvegarde annuelle, pas à la routine du soir.

**Ce que Google Photos ne couvre pas.** Uniquement ce qui est sur le téléphone. Les fichiers de la X5 (`.insv`), du drone et la trace Garmin viennent de leurs cartes et de leurs exports — rien ne change pour eux.

#### Plan B — le câble USB

Si vous n’avez pas eu de connexion et que rien n’a été sauvegardé dans le cloud, branchez le Pixel 11 et copiez sa pellicule dans un dossier temporaire — **avant d’exporter quoi que ce soit** depuis Insta360 ou DJI Fly, pour la raison expliquée plus haut. C’est aussi la voie à choisir si vous voulez les fichiers strictement d’origine, sans passage par les serveurs de Google.

### Étape 1 bis — Le tri et les découpes, faits avant l’import

Vous préparez la matière avant de la donner à l’application. C’est le bon ordre : ce qui entre dans le voyage est déjà trié, et l’arborescence ne se remplit pas de rebuts. Trois outils, et une conséquence chacun.

#### LosslessCut — sélection et découpe des vidéos du drone

La découpe est sans réencodage, donc sans perte, et LosslessCut recopie les métadonnées de la source. Deux points à vérifier une fois :

- **Le réglage « Set file modification date/time of output files to ».** S’il est sur *Current time*, vos extraits porteront la date de ce soir et non celle du tournage. Laissez-le sur la valeur qui conserve la date d’origine — c’est le comportement par défaut depuis longtemps, mais il se change par mégarde.
- **LosslessCut ne peut pas réécrire la date de *création*** du fichier, seulement la date de modification. Sur les MP4, les tags internes ne sont pas mis à jour non plus. Si vos extraits arrivent tous datés d’aujourd’hui, c’est ce mécanisme qui est en cause.

Bonne nouvelle : le nom de sortie conserve le préfixe d’origine — `DJI_0001.MP4-00.00.11.431-00.00.20.182.MP4` — donc la reconnaissance du drone par le nom continue de fonctionner.

#### FastRawViewer — sélection des photos, RAW et JPG ensemble

Gardez **Préférences → File formats → Handle raw+jpg together** activé : c’est ce qui écarte les deux versions d’une photo ratée d’un seul geste.

> **Attention, et c’est le piège :** FastRawViewer ne *supprime* pas, il **déplace** les fichiers écartés dans un sous-dossier `_Rejected`. Sans précaution, ce dossier étant à l’intérieur de la source, tous vos rebuts reviendraient à l’import. **L’application ignore désormais automatiquement les dossiers `_Rejected`** ainsi que les corbeilles système, et vous indique combien de fichiers ont été écartés à ce titre. Pour libérer réellement la place sur la carte, utilisez *Fichier → Clear _Rejected*.

#### Insta360 Studio — rendu des séquences 360

L’export produit un MP4 ordinaire : plus d’extension `.insv`, et le plus souvent plus d’EXIF de la caméra. C’est le cas décrit plus bas — précisez l’appareil sur la source, ou exportez dans un dossier nommé `X5`.

#### La vérification commune aux trois

Tout réexport peut perdre la date de prise de vue. Après l’analyse, **lisez la ligne `Dates :` du journal de bord**. Si elle annonce surtout `date fichier` et que tout s’est rangé sous la date d’aujourd’hui, c’est que les dates d’origine n’ont pas survécu. Le rattrapage existe : dans le dialogue de la source, **Imposer une journée** force tout le dossier dans la bonne journée. C’est précisément à cela que sert ce champ.

Un point de rangement qui découle de tout cela : comme vous sélectionnez et découpez **avant** l’import, vos fichiers déjà traités *sont* vos sources. Ils vont donc directement dans le dossier de leur appareil. L’application ne crée aucun dossier de travail intermédiaire — il n’y aurait rien à y mettre.

### Étape 2 — Créer le voyage

Dans l’application, bouton **Nouveau…** en haut à droite. Choisissez où le créer, indiquez la date de départ et un nom court. Le dossier est créé au bon format — par exemple `2026-09-05_valais-2j` — avec son manifeste `trip.md`.

> La date du nom de dossier fixe le **jour 1**. C’est elle qui détermine la numérotation `01_`, `02_` des journées. Si vous vous trompez, renommez le dossier avant d’importer.

### Étape 3 — Ajouter les sources

Onglet **1 · Importer**, bouton **Ajouter…**. Le dialogue *Configurer une source* s’ouvre : choisissez le dossier, et — **facultativement** — précisez l’appareil.

**Le plus simple : ajoutez le dossier racine de la journée et laissez « Détection automatique ».** Si vos sous-dossiers portent des noms parlants — `Mini 4 Pro`, `Neo 2`, `Ace Pro 2`, `X5`, `Pixel`, `Garmin`, `Geo-Log` —, l’application les reconnaît et range tout correctement, y compris les sous-sous-dossiers du type `X5\EXPORTS`. Une seule source suffit alors pour toute la journée.

Le nom du dossier l’emporte sur tout le reste, extension et EXIF compris. C’est ce qui permet de séparer automatiquement le GPX de la Garmin de celui de Geo-Log, que rien d’autre ne distingue.

Si vous préférez le contrôle, ajoutez les dossiers un par un :

- le dossier téléchargé depuis Google Photos → *Pixel 11 Pro*, ou laissez en automatique,
- le dossier des vidéos recadrées de la X5 → **Insta360 X5**,
- les séquences POV de l’Ace Pro 2 → **Insta360 Ace Pro 2 — POV**,
- la carte du drone → *DJI Mini 4 Pro* ou *DJI Air 3* selon celui que vous aviez,
- la carte du Neo 2 → **DJI Neo 2**,
- les GPX de la Garmin → *Garmin Instinct 3*,
- l’export Geo-Log → **Geo-Log**.

Vous pouvez en ajouter autant que nécessaire. Ajouter par erreur un dossier **et** son parent n’est pas grave : les fichiers ne sont comptés qu’une fois, et c’est la source configurée qui l’emporte sur celle en détection automatique.

### Étape 4 — Analyser

Bouton **Analyser**. Rien n’est écrit. Deux tableaux se remplissent :

- **Par journée et par appareil** — le décompte, avec une ligne TOTAL en ambre.
- **Par type de fichier** — combien de `.jpg`, `.insv`, `.mp4`, `.gpx`, et de quels appareils ils viennent.

**Lisez ces chiffres, c’est le contrôle qualité de la soirée.** Si le nombre de fichiers d’un appareil vous paraît faux, quelque chose ne va pas — carte oubliée, dossier non ajouté, ou horloge décalée. Le journal de bord en bas de fenêtre indique aussi d’où viennent les dates : `exif`, `nom`, ou `date fichier`.

### Étape 5 — Importer

Bouton **Importer**, en ambre. Il ne s’active qu’après une analyse. Les fichiers sont **copiés**, jamais déplacés : vos cartes restent intactes.

L’arborescence se crée toute seule :

```
2026-09-05_valais-2j/
  trip.md
  01_2026-09-05/
    01_GARMIN/
    02_PIXEL11/        PHOTO/  VIDEO/
    03_INSTA360_X5/    PHOTO/  VIDEO/
    05_DJI_NEO2/       PHOTO/  VIDEO/
    06_DJI_MINI4PRO/   PHOTO/  VIDEO/
    08_GEOLOG/
    30_PUBLICATION/    WHATSAPP/  INSTAGRAM_FACEBOOK/
    work/
    out/
  02_2026-09-06/
```

### Étape 6 — Exporter Geo-Log depuis le Pixel 8

Depuis l’application Geo-Log, exportez la route de chaque journée en GPX ou KML, et déposez le fichier dans le `raw/geolog/` de la journée correspondante. C’est une opération manuelle : l’application ne peut pas aller chercher dans le téléphone.

### Étape 7 — Générer le journal

Onglet **3 · Journal**. Choisissez la journée, bouton **Aperçu** pour voir le résultat, puis **Écrire journal.md**.

Vous obtenez, pour chaque waypoint, son heure, ses coordonnées, votre note — et en dessous, **la liste des médias pris dans les dix minutes autour**. C’est ce qui vous évite de chercher quelle séquence X5 correspond à « super route ». Le fichier contient aussi la distance du jour calculée depuis la trace Garmin, un décompte par appareil, les médias qui ne correspondent à aucun waypoint, et un bloc vide pour votre sélection du soir.

### Étape 8 — Sauvegarder

Copiez tout le dossier du voyage sur le SSD. **Ne formatez une carte qu’une fois son contenu présent à deux endroits.**

La géolocalisation (onglet 2) peut attendre le retour à la maison. Rien ne presse.

---

## 3. Onglet 1 · Importer, en détail

| Contrôle | Ce qu’il fait |
|---|---|
| **Ajouter… / Modifier… / Retirer** | Gère la liste des sources. **Ajouter…** ouvre le dialogue *Configurer une source* (ci-dessous) ; **Modifier…** le rouvre sur la ligne sélectionnée. |
| **Exclure les RAW / DNG** | Cochée par défaut. Ne copie pas les fichiers bruts (DNG, RAW, ARW, CR2…). Pour publier, les JPG suffisent, et vos cartes gardent les originaux le temps que vous décidiez. |
| **Bascule de journée** | Heure à laquelle on change de jour. À 4 h par défaut : une photo prise à 1 h 10 du matin compte pour la journée de route précédente, ce qui est presque toujours ce que vous voulez. |
| **Exclure les SRT / LRV** | Cochée par défaut. Écarte les fichiers annexes : proxys basse définition `.lrv`, télémétrie `.srt` des drones, vignettes `.thm`. Aucun usage à la publication, et ils gonflent les sauvegardes. |
| **Analyser** | Lecture seule. À faire systématiquement avant d’importer. |
| **Importer** | Écrit. Le résumé à côté du bouton annonce ce qui va se passer. |

### Comment l’application reconnaît chaque appareil

Elle décide dans cet ordre, et s’arrête au premier critère qui tranche :

1. **L’appareil choisi dans le dialogue** — c’est vous qui décidez, rien ne peut le contredire.

2. **L’extension** — `.insv`, `.insp`, `.lrv` sont forcément une Insta360.
3. **L’EXIF marque et modèle** — fiable, mais seulement si exiftool est installé et si les métadonnées ont survécu.
4. **Le nom du dossier** — un dossier nommé `X5`, `Insta360`, `drone`, `neo`, `pixel` suffit à classer son contenu.
5. **La signature du nom de fichier** — `PXL_…` pour le Pixel, `DJI_…` pour un drone, et le motif `_00_001` propre à Insta360.

#### Le dialogue « Configurer une source »

| Champ | À quoi il sert |
|---|---|
| **Dossier source** | Le dossier à lire, sous-dossiers compris. |
| **Appareil / contenu** | Facultatif. Impose l’appareil au lieu de le deviner. Trois cas le rendent utile : les MP4 recadrés de la X5, la distinction entre la X5 et l’Ace Pro 2, et l’export Geo-Log — qui est un GPX, exactement comme la trace Garmin, et que rien ne permet donc de distinguer d’elle automatiquement. |
| **Corriger l’horloge** | Décale les dates de **cette source seulement**, avant le classement par journée. Pour un appareil dont l’heure est fausse ou resté sur le mauvais fuseau. |
| **Imposer une journée** | Force tout le dossier dans la journée 1, 2, 3… quelles que soient les dates. Dernier recours, pour un appareil sans date exploitable. |

Deux entrées du menu méritent un mot :

- **Insta360 Ace Pro 2 — POV** range dans son propre dossier. Un dossier distinct de la X5, parce que les deux caméras ne jouent pas le même rôle au montage : la X5 se recadre après coup, l’Ace Pro est déjà cadrée. Les retrouver séparées le soir fait gagner du temps.

#### Les traces et les carnets sont datés par leur contenu

Un GPX ou un KML ne contient aucune date de prise de vue, et son nom n’en porte pas toujours. Sa date de fichier est celle de **l’export** — souvent plusieurs jours après le voyage. Un carnet Geo-Log exporté au retour se serait donc rangé sous la date de l’export, en dehors des journées du voyage.

L’application lit désormais **le premier horodatage à l’intérieur du fichier** et s’en sert comme date. Un carnet exporté le 9 septembre mais contenant des points du 7 est rangé au 7. Le journal de bord l’indique par la mention `contenu` dans la ligne `Dates :`.

> **Exportez une route par journée.** Si un seul fichier couvre plusieurs jours, il est rangé au premier, et les journées suivantes se retrouvent sans carnet — l’onglet Journal n’aurait alors rien à lire pour elles. L’application vous avertit quand elle détecte un export à cheval sur plusieurs dates.

#### Les paramètres du voyage décident de tout

Un bouton **Paramètres du voyage…** ouvre trois colonnes de cases : les **appareils** emportés, les **logiciels** utilisés, les **réseaux** où vous publiez. Ce qui n’est pas coché n’existe nulle part — ni dans le menu des sources, ni dans l’arborescence, ni dans les colonnes des statistiques. Un aperçu de l’arborescence se met à jour à chaque clic.

Les réglages sont enregistrés dans le dossier du voyage et recopiés dans `trip.md`. Des **presets** permettent d’enregistrer une configuration et de la recharger : « court roadtrip (quelques jours) » et « long roadtrip (quelques semaines) » couvrent déjà l’essentiel des cas.

Trois conséquences pratiques :

- **Un dossier par appareil**, numéroté de façon fixe : ajouter l’Air 3 un jour ne renumérote jamais les autres. Les trous dans la numérotation sont normaux — ils disent quel matériel est resté à la maison.
- **Photo et vidéo sont séparées** pour tout appareil capable des deux, et le sous-dossier n’est créé que s’il reçoit réellement des fichiers. Un Neo 2 qui n’a que filmé n’aura pas de `PHOTO/` vide.
- **Les réglages lèvent l’ambiguïté de détection.** Si un seul drone est coché, un fichier DJI que l’EXIF n’identifie pas lui revient nécessairement. Cela rend exiftool moins critique.

Insta360 Studio est en lecture seule : il s’active et se désactive tout seul, en suivant l’Insta360 X5 — sans elle, rien à recadrer. LosslessCut reste une case libre, puisqu’il sert à raccourcir n’importe quelle vidéo, d’où qu’elle vienne. Aucun des deux ne crée de dossier : ils décrivent le flux de travail et servent d’aide-mémoire.

Instagram et Facebook partagent `INSTAGRAM_FACEBOOK/` : le média est identique, seule la légende change.

#### Les dates se calculent entre elles

Le nom du voyage et la date de départ sont demandés une seule fois, au moment de **Nouveau…** ; les paramètres les reprennent. Dans les paramètres, *Début*, *Fin* et *Jours* se déduisent l’un de l’autre : indiquez deux dates et la durée s’affiche, indiquez une durée et la date de retour se calcule.

#### Le journal de `trip.md` se remplit tout seul

Dans les paramètres, le champ **Jours** indique la durée du voyage. À l’enregistrement, l’application écrit dans `trip.md` une table de journal avec une ligne par jour et **la colonne des dates déjà calculée** depuis la date du dossier. Il ne reste qu’à remplir les étapes et les remarques. Elle ne touche à rien si vous avez déjà saisi des lignes à la main.

#### Des infobulles partout

Chaque bouton et chaque case affiche, au survol de la souris, ce qu’il fait exactement et quand s’en servir. C’est la documentation la plus proche du geste — le manuel ne sert qu’en cas de doute plus large. Les infobulles se repositionnent pour rester entièrement à l’écran, y compris celles des contrôles collés au bord droit.

#### Version et À propos

La barre de titre affiche le numéro de version. Le bouton **À propos**, à droite de *Paramètres du voyage…*, donne la version, la date de compilation et les technologies utilisées. C’est aussi là que se trouve le bouton **Localiser exiftool…**, qui n’apparaît que si exiftool n’a pas été trouvé.

Le numérotage suit trois niveaux : le premier chiffre change quand une mise à jour casse l’existant — arborescence ou format des réglages —, le deuxième pour une nouvelle fonction, le troisième pour une correction.

#### Le journal de diagnostic

L’application tient un journal technique dans `~/.vespa-organizer/diagnostic.log`, limité à 1 Mo avec une génération conservée. Il enregistre à chaque démarrage la version, la date de compilation, la version de Python, la plateforme et l’état d’exiftool ; puis pour chaque analyse les sources lues, le nombre de fichiers, le détail du plan et l’origine des dates ; et toute erreur avec sa trace complète.

Le menu **Aide** propose *Exporter le journal de diagnostic…*, qui rassemble les deux générations dans un fichier daté. C’est ce fichier à joindre en cas de comportement inexpliqué.

#### Rien n’est rangé au hasard

Un fichier que l’application ne sait pas attribuer à un appareil du voyage est **refusé**. Il n’est pas copié, il reste sur la source, et son nom apparaît dans le journal de bord. Le résumé à côté du bouton Importer les compte séparément : `31 à copier · 1 refusé`. Pour le récupérer, précisez l’appareil sur sa source, ou cochez l’appareil dans les paramètres.

#### Un dossier par appareil, numéroté de façon fixe

Chaque appareil a un numéro permanent : Garmin 01, Pixel 11 02, X5 03, Ace Pro 04, Neo 2 05, Mini 4 Pro 06, Air 3 07, Geo-Log 08. Ajouter un appareil un jour ne renumérote jamais les autres, et le même dossier porte le même numéro d’un voyage à l’autre. Les trous dans la numérotation sont normaux : ils disent quel matériel est resté à la maison.

Le Pixel 8 n’a pas de dossier — il ne produit aucun média, il héberge OsmAnd et Geo-Log.

Un seul dossier de travail complète la journée : `30_PUBLICATION/`, avec un sous-dossier par réseau retenu. Il n’y a pas de dossier d’étape intermédiaire, puisque vos fichiers arrivent déjà triés et découpés.

#### X5 et Ace Pro 2 : deux MP4 que le nom ne sépare pas

Les deux caméras sont des Insta360 et nomment leurs fichiers de la même façon — `VID_20260905_140000_00_001.mp4`. Rien dans le nom ne permet de les distinguer, et comme elles ont chacune leur dossier, il faut trancher.

Deux façons de le faire : avec exiftool installé, le modèle est lu dans l’EXIF et la distinction se fait toute seule ; sans lui, précisez l’appareil sur la source.

Si une seule des deux est cochée dans les paramètres du voyage, la question ne se pose pas : le fichier lui revient nécessairement.

#### Le cas des MP4 recadrés de la X5

Une fois recadrées et coupées dans l’application Insta360, vos séquences ne sont plus des `.insv` mais des **MP4 ordinaires**. L’extension ne dit donc plus rien, et l’EXIF a le plus souvent disparu à l’export. Trois façons de les faire reconnaître, de la plus simple à la plus sûre :

- **Ne renommez pas les exports.** L’application Insta360 reprend le nom du fichier source — `VID_20260905_110000_00_001.mp4` — et le motif `_00_001` (numéro d’objectif puis séquence) est propre à la famille Insta360. C’est reconnu automatiquement.
- **Exportez dans un dossier nommé `X5`.** Le nom du dossier suffit à classer tout son contenu, quel que soit le nom des fichiers.
- **Choisissez « Insta360 X5 »** dans le dialogue. C’est la méthode qui ne peut pas échouer, y compris si vous avez renommé vos exports en `col_stelvio_arriere.mp4`.

Sans aucune de ces trois précautions, un MP4 recadré au nom libre finit dans `autre/` — pas perdu, mais mal rangé.

**Relancer ne coûte rien.** Les fichiers déjà présents et identiques sont détectés et ignorés — l’application compare la taille et une empreinte. Si vous doutez d’avoir tout importé, relancez : le décompte vous le dira.

---

## 4. Onglet 2 · Géolocaliser

Applique la trace Garmin de la journée aux fichiers qui n’ont pas de coordonnées. Ne présumez pas de ce qui est déjà géotagué : les fichiers DJI le sont en général, mais un Pixel dont le GPS est coupé pour économiser la batterie produit des photos sans coordonnées, et les vidéos recadrées perdent souvent ce qu’elles avaient. L’analyse vous dit combien de fichiers sont concernés avant toute écriture.

1. Choisissez la journée.
2. **Analyser** — combien de fichiers tombent dans la trace, combien sont hors plage, l’écart médian. Aucune écriture, aucune installation nécessaire.
3. Si beaucoup sont hors plage : **Détecter le décalage**. L’application propose la correction d’horloge qui fait le mieux coïncider les fichiers avec la trace, ou vous dit qu’aucune correction n’améliore rien — auquel cas les horloges étaient justes et les fichiers hors plage le sont réellement (pris avant le départ, après l’arrivée, ou hors trace).
4. **Écrire** — nécessite exiftool.

> Un décalage proposé proche d’un nombre entier d’heures signale un **fuseau horaire**, pas une dérive d’horloge. Avant d’écrire, vérifiez sur une photo dont vous savez où elle a été prise.

**Tolérance** : écart maximal accepté entre l’heure d’un fichier et un point de la trace. 900 s (15 min) convient. Augmentez si votre Garmin enregistre par intervalles espacés.

---

## 5. Onglet 3 · Journal

| Contrôle | Ce qu’il fait |
|---|---|
| **Journée** | La journée à traiter. |
| **Fenêtre** | Écart maximal entre un waypoint et un média pour qu’ils soient rattachés. 600 s (±10 min) par défaut. Réduisez si vos waypoints sont très rapprochés. |
| **Aperçu** | Affiche sans rien écrire. |
| **Écrire journal.md** | Écrit dans le dossier de la journée. Un `journal.md` existant est d’abord sauvegardé en `.md.bak`. |
| **Ouvrir le dossier** | Ouvre la journée dans le Finder ou l’Explorateur. |

Le journal sert de brouillon pour vos légendes Instagram et pour le message WhatsApp du soir. Écrivez dedans : c’est un fichier Markdown ordinaire.

**S’il annonce « aucun waypoint »**, c’est que l’export Geo-Log n’est pas dans `raw/geolog/`. Voir l’étape 6.

---

## 6. Ce que l’application ne fait pas

- Elle ne va pas chercher dans les téléphones : les exports Geo-Log et les GPX Garmin sont déposés à la main.
- Elle ne recadre pas les 360 : c’est l’application Insta360.
- Elle ne sauvegarde pas sur le SSD et ne formate aucune carte.

---

## 7. Application Windows portable

L’application peut tourner comme un simple script, ou être transformée en un **exécutable unique et portable**, avec son icône Vespa dans la barre des tâches.

### Sans rien construire

Double-cliquez sur **`Vespa Organizer.bat`**, placé à côté de `vespa_organizer.py`. Python doit être installé. Pour avoir l’icône sur le bureau : clic droit sur le `.bat` → *Envoyer vers → Bureau*, puis sur le raccourci créé, *Propriétés → Changer d’icône* → choisissez `vespa.ico`.

### Construire l’exécutable portable

À faire **une seule fois**, sur le PC Windows. Placez dans le même dossier `vespa_organizer.py`, `vespa.ico` et `build_windows.bat`, puis double-cliquez sur ce dernier. Il installe PyInstaller, construit l’application et vous indique le résultat :

```
dist\Vespa Organizer.exe
```

Ce fichier est autonome : copiez-le où vous voulez, y compris sur une clé USB. Aucune installation, et aucun Python nécessaire sur la machine qui l’exécute.

**Au premier lancement**, Windows SmartScreen affichera probablement un avertissement, car l’exécutable n’est pas signé numériquement. Cliquez sur *Informations complémentaires* puis *Exécuter quand même*. Cela n’arrive qu’une fois.

**Pour l’épingler à la barre des tâches** : lancez-le, puis clic droit sur son icône dans la barre des tâches → *Épingler à la barre des tâches*.

> L’exécutable doit être construit sur Windows : un `.exe` ne peut pas être fabriqué depuis macOS ou Linux. Le script `build_windows.bat` fait tout le travail, mais il faut le lancer depuis la machine cible.

---

## 8. Dépannage

| Symptôme | Cause et remède |
|---|---|
| « Le nom du dossier doit commencer par une date ISO » | Renommez le dossier du voyage en `AAAA-MM-JJ_nom`, ou utilisez le bouton **Nouveau…**. |
| Des fichiers signalés « antérieurs au jour 1 » | Soit ils sont réellement antérieurs, soit l’horloge d’un appareil a dérivé. Vérifiez la date affichée dans le message. |
| « 0 fichiers prêts » | Tout est déjà importé. C’est normal si vous relancez. |
| Des MP4 de la X5 refusés | Ce sont des exports recadrés : plus d’extension `.insv`, plus d’EXIF. Choisissez « Insta360 X5 » sur la source, ou exportez dans un dossier nommé `X5`. |
| L’export Geo-Log atterri dans `garmin/` | Les deux sont des GPX. Précisez « Geo-Log » sur cette source. |
| Les deux drones dans le même `drone/` | C’est voulu : le rangement se fait par famille. Le modèle reste dans les EXIF. |
| Le bouton Importer reste grisé | Lancez **Analyser** d’abord. |
| L’analyse se bloque ou n’aboutit pas | Corrigé en v2.9.0 : les chemins étaient passés à exiftool sur la ligne de commande, plafonnée sous Windows, et les accents d’un dossier la faisaient échouer. Si cela persiste, exportez le journal de diagnostic. |
| « … portent les marques d’un autre appareil » | Une source typée contient des fichiers venus d’ailleurs — typiquement des photos DJI Fly remontées par l’album Google Photos. Votre choix de source l’emporte ; le message est une vérification, pas une erreur. |
| L’écriture GPS refuse de démarrer | exiftool absent. Ouvrez **À propos** → *Localiser exiftool…*, ou installez-le. |
| Le carnet Geo-Log rangé hors du voyage | Corrigé : les GPX et KML sont datés par leur contenu. Si cela se reproduit, c’est que le fichier ne contient aucun horodatage — utilisez alors « Imposer une journée ». |
| Beaucoup de dates issues du « nom » | Normal après un téléchargement Google Photos : les EXIF ont été rabotés, le nom de fichier prend le relais. Le classement par journée reste juste. |
| SmartScreen bloque l’exécutable | Normal, il n’est pas signé. *Informations complémentaires → Exécuter quand même*, une seule fois. |
| La fenêtre semble figée | Une opération est en cours : la barre de progression et le statut au-dessus du journal de bord l’indiquent. Les traitements tournent en arrière-plan, l’interface reste utilisable. |

---

## 9. Les mêmes opérations en ligne de commande

Utiles pour un traitement par lots ou à distance.

```
python3 vespa_ingest.py  --src /Volumes/SD --trip ~/Vespa/2026-09-05_valais-2j --dry-run
python3 vespa_geotag.py  --day ~/Vespa/2026-09-05_valais-2j/01_2026-09-05 --auto-offset --dry-run
python3 vespa_journal.py --day ~/Vespa/2026-09-05_valais-2j/01_2026-09-05
```

---

## Rappel de la routine du soir

1. Album Google Photos du jour → **Tout télécharger** → décompresser.
2. Analyser, lire les chiffres, importer.
3. Exporter Geo-Log du Pixel 8 vers `raw/geolog/`.
4. Générer le journal.
5. Copier le dossier sur le SSD.
6. Ne formater aucune carte avant que son contenu existe à deux endroits.
