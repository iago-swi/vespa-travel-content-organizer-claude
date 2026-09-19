#!/usr/bin/env python3
"""
Vespa Travel Content Organizer
==============================

Interface graphique pour ranger, géolocaliser et documenter les médias d'un
roadtrip à Vespa. Remplace les trois scripts en ligne de commande.

Lancement :
    python3 vespa_organizer.py

Aucune dépendance : Python 3.9+ et Tkinter (fourni avec Python sur Windows et
macOS ; sous Linux : sudo apt install python3-tk).
exiftool est optionnel mais recommandé — sans lui, les dates de prise de vue
des vidéos sont moins fiables et l'écriture des coordonnées est impossible.
"""

from __future__ import annotations

import base64
import hashlib
import unicodedata
import json
import os
import queue
import re
import shutil
import subprocess
import sys
import tempfile
import threading
import traceback
import xml.etree.ElementTree as ET
import zipfile
from bisect import bisect_left
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from math import asin, cos, radians, sin, sqrt
from pathlib import Path

APP_NAME = "Vespa Travel Content Organizer"
# Versionnage sémantique : MAJEUR.MINEUR.CORRECTIF
#   MAJEUR    changement qui casse l'existant — arborescence, format des
#             réglages, quelque chose à refaire à la main.
#   MINEUR    nouvelle fonction ou nouveau comportement visible.
#   CORRECTIF correction, ajustement d'interface, retouche de texte.
APP_VERSION = "2.9.0"
BUILD_DATE = "14.09.2026"          # repli si la date du fichier est illisible


def build_date() -> str:
    """Date de compilation lue sur le fichier lui-même : l'exécutable quand
    l'application est gelée par PyInstaller, le script sinon. Une constante
    tenue à la main finit toujours par mentir."""
    try:
        cible = Path(sys.executable) if getattr(sys, "frozen", False) else Path(__file__)
        return datetime.fromtimestamp(cible.stat().st_mtime).strftime("%d.%m.%Y")
    except Exception:
        return BUILD_DATE
# Ligne de crédit affichée dans « À propos » — modifiable librement.
CREDIT = "Vibe-codé avec Claude"

# Icône embarquée (PNG 128 px) — sert d'icône de fenêtre et de barre des tâches.
ICON_B64 = (
    "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"
    "RU5ErkJggg=="
)

# --------------------------------------------------------------------------- #
# Palette (reprise du guide : charbon + ambre)

INK = "#16171a"
AMBER = "#d99b2b"
PAPER = "#faf8f4"
LINE = "#e0dcd4"
MUTED = "#6b655e"
OK = "#2f7a4f"
WARN = "#a83a1e"

# --------------------------------------------------------------------------- #
# Cœur métier (indépendant de l'interface)

MEDIA_EXT = {
    ".jpg", ".jpeg", ".png", ".heic", ".dng", ".raw",
    ".mp4", ".mov", ".m4v", ".avi", ".lrv",
    ".insv", ".insp", ".srt", ".thm",
    ".gpx", ".kml", ".kmz", ".csv",
}
PHOTO_EXT = {".jpg", ".jpeg", ".png", ".heic", ".dng", ".raw", ".insp"}
# Formats bruts : inutiles pour publier, lourds à copier et à sauvegarder.
RAW_EXT = {".dng", ".raw", ".arw", ".cr2", ".cr3", ".nef", ".orf", ".rw2", ".raf"}
# Fichiers annexes produits par les appareils : proxys basse définition des
# Insta360 et DJI, et pistes de télémétrie des drones. Aucun usage à la
# publication, et ils gonflent inutilement les sauvegardes.
PROXY_EXT = {".lrv", ".srt", ".thm"}
VIDEO_EXT = {".mp4", ".mov", ".m4v", ".avi", ".insv", ".lrv"}
TRACE_EXT = {".gpx", ".kml", ".kmz", ".csv"}
TAGGABLE_EXT = {".jpg", ".jpeg", ".heic", ".dng", ".png", ".mp4", ".mov", ".insp", ".insv"}


def media_kind(path: Path) -> str:
    ext = path.suffix.lower()
    if ext in PHOTO_EXT:
        return "PHOTO"
    if ext in VIDEO_EXT:
        return "VIDEO"
    return "TRACE"


# --------------------------------------------------------------------------- #
# Catalogue du matériel. C'est la source de vérité : rien de ce qui n'est pas
# coché dans les paramètres du voyage n'existe dans l'ingestion, dans
# l'arborescence ou dans les statistiques.
#
#   clé, libellé, rôle, n° de dossier, nom de dossier, types de médias, défaut
# Le numéro est FIXE : ajouter un appareil ne renumérote jamais les autres.

DEVICE_CATALOG = [
    ("garmin",  "Garmin Instinct 3 Solar", "tracking",             1,  "GARMIN",            ("TRACE",),          True),
    ("pixel11", "Pixel 11 Pro",            "vidéo + photo",        2,  "PIXEL11",           ("PHOTO", "VIDEO"),  True),
    ("x5",      "Insta360 X5",             "vidéo + photo",        3,  "INSTA360_X5",       ("PHOTO", "VIDEO"),  True),
    ("ace",     "Insta360 Ace Pro 2",      "vidéo + photo",        4,  "INSTA360_ACEPRO2",  ("PHOTO", "VIDEO"),  False),
    ("neo2",    "DJI Neo 2",               "vidéo + photo",        5,  "DJI_NEO2",          ("PHOTO", "VIDEO"),  True),
    ("mini4",   "DJI Mini 4 Pro",          "vidéo + photo",        6,  "DJI_MINI4PRO",      ("PHOTO", "VIDEO"),  True),
    ("air3",    "DJI Air 3",               "vidéo + photo",        7,  "DJI_AIR3",          ("PHOTO", "VIDEO"),  False),
    ("pixel8",  "Pixel 8 Pro",             "tracking, navigation", None, None,              (),                  True),
]
DEV = {d[0]: {"key": d[0], "label": d[1], "role": d[2], "num": d[3],
              "folder": d[4], "kinds": d[5], "default": d[6]}
       for d in DEVICE_CATALOG}

# Logiciels : informatifs, sauf Geo-Log qui produit des fichiers.
SOFTWARE_CATALOG = [
    ("geolog",      "Geo-Log",         "tracking, journal", 8,  "GEOLOG",     True,  None),
    ("studio",      "Insta360 Studio", "édition",           None, None,       True,  ("x5",)),
    ("losslesscut", "LosslessCut",     "découpe de toute vidéo", None, None,   True,  None),
]
SOFT = {s[0]: {"key": s[0], "label": s[1], "role": s[2], "num": s[3],
               "folder": s[4], "default": s[5], "auto_from": s[6]}
        for s in SOFTWARE_CATALOG}

# Instagram et Facebook partagent un dossier : le média est le même, seule la
# légende change. Inutile de dupliquer un Reel de 200 Mo.
NETWORK_CATALOG = [
    ("whatsapp",  "WhatsApp",   "photo + vidéo du jour", "WHATSAPP",             True),
    ("instagram", "Instagram",  "dossier commun avec Facebook", "INSTAGRAM_FACEBOOK", True),
    ("facebook",  "Facebook",   "dossier commun avec Instagram", "INSTAGRAM_FACEBOOK", True),
]
NET = {n[0]: {"key": n[0], "label": n[1], "role": n[2], "folder": n[3],
              "default": n[4]} for n in NETWORK_CATALOG}

PUBLICATION_DIR = "30_PUBLICATION"
# Ancien dossier de travail, plus créé : la sélection et les découpes se font
# avant l'ingestion. On continue de l'ignorer s'il traîne dans un ancien voyage.
SELECTION_DIR = "20_SELECTION"

# Familles utilisées par la détection automatique : on identifie d'abord la
# famille, puis on choisit dans les appareils cochés de cette famille.
FAMILIES = {"drone": ("mini4", "air3", "neo2"),
            "insta360": ("x5", "ace"),
            "pixel": ("pixel11",),
            "garmin": ("garmin",),
            "geolog": ("geolog",)}

MODEL_RULES = [
    (r"\bneo\b|neo\s*2", "neo2"),
    (r"mini\s*4", "mini4"),
    (r"air\s*3", "air3"),
    (r"\bace\s*pro|\bacepro", "ace"),
    (r"\bx5\b|insta360\s*x5", "x5"),
    (r"mavic|fc\d{3,4}|\bdji\b", "drone"),
    (r"insta360|insta\b|360", "insta360"),
    (r"pixel|google", "pixel"),
]
NAME_RULES = [
    (r"^dji_fly_", "drone"),
    (r"_\d{2}_\d{3}(?:_|\.|$)", "insta360"),
    (r"^lrv_|^vid_\d{8}_\d{6}_\d{2}_", "insta360"),
    (r"^dji_", "drone"),
    (r"^pxl_|^img_\d", "pixel"),
]
EXT_SOURCE = {".insv": "insta360", ".insp": "insta360", ".lrv": "insta360",
              ".gpx": "garmin", ".kml": "geolog", ".kmz": "geolog"}

# Mode automatique : les noms de dossiers sont la meilleure indication, parce
# que c'est vous qui les avez écrits. Ils l'emportent sur tout le reste, et
# c'est ce qui permet d'ajouter la racine d'un voyage comme source unique.
FOLDER_RULES = [
    (r"geo[\s_\-]*log", "geolog"),
    (r"garmin|instinct", "garmin"),
    (r"\bneo\b|neo\s*2", "neo2"),
    (r"mini\s*4", "mini4"),
    (r"air\s*3", "air3"),
    (r"ace\s*pro|acepro", "ace"),
    (r"\bx5\b|insta\s*360\s*x5", "x5"),
    (r"pixel", "pixel11"),
    (r"insta\s*360", "insta360"),
    (r"drone|dji", "drone"),
]


def folder_signal(path: Path, root: Path | None) -> str | None:
    """Appareil déduit des dossiers traversés, du plus profond au plus haut."""
    try:
        parts = list(path.relative_to(root).parts[:-1]) if root else [path.parent.name]
    except ValueError:
        parts = [path.parent.name]
    for nom in reversed(parts):
        n = nom.lower()
        for motif, dev in FOLDER_RULES:
            if re.search(motif, n):
                return dev
    return None

SKIP_DIRS = {"garmin", "geolog", "GARMIN", "GEOLOG"}
# FastRawViewer DÉPLACE les photos écartées dans _Rejected au lieu de les
# supprimer : sans cette exclusion, tous les rebuts reviendraient à l'import.
EXCLUDE_DIRS = {"_rejected", "_corbeille", ".trash", ".trashes",
                "$recycle.bin", "system volume information",
                SELECTION_DIR.lower(), PUBLICATION_DIR.lower()}

SETTINGS_FILE = ".vespa-trip.json"

# --------------------------------------------------------------------------- #
# Journal de diagnostic. Écrit à côté des préférences, tourne à 1 Mo et
# conserve une génération. C'est ce fichier qu'on envoie pour analyser un bug.

LOG_DIR = Path.home() / ".vespa-organizer"
LOG_FILE = LOG_DIR / "diagnostic.log"
LOG_MAX = 1_000_000


def log_event(message: str) -> None:
    try:
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        if LOG_FILE.exists() and LOG_FILE.stat().st_size > LOG_MAX:
            vieux = LOG_FILE.with_suffix(".log.1")
            if vieux.exists():
                vieux.unlink()
            LOG_FILE.rename(vieux)
        with LOG_FILE.open("a", encoding="utf-8") as fh:
            fh.write(f"{datetime.now():%Y-%m-%d %H:%M:%S}  {message}\n")
    except Exception:
        pass          # le diagnostic ne doit jamais faire échouer le traitement


def log_exception(contexte: str, exc: BaseException) -> None:
    log_event(f"ERREUR {contexte} : {exc!r}")
    log_event(traceback.format_exc().rstrip())


def log_session_header() -> None:
    log_event("=" * 62)
    log_event(f"démarrage v{APP_VERSION} · build {build_date()}")
    log_event(f"python {sys.version.split()[0]} · {sys.platform}"
              + (" · gelé" if getattr(sys, "frozen", False) else ""))
    log_event(f"exiftool : {exiftool_path() or 'absent'}")
PRESETS_FILE = Path.home() / ".vespa-organizer-presets.json"


def jours_entre(debut: str, fin: str) -> int | None:
    """Nombre de journées de voyage, bornes comprises."""
    try:
        d1 = datetime.strptime(debut.strip(), "%Y-%m-%d")
        d2 = datetime.strptime(fin.strip(), "%Y-%m-%d")
    except Exception:
        return None
    n = (d2 - d1).days + 1
    return n if n >= 1 else None


def fin_depuis(debut: str, jours: str) -> str | None:
    try:
        d1 = datetime.strptime(debut.strip(), "%Y-%m-%d")
        n = int(str(jours).strip())
    except Exception:
        return None
    if n < 1:
        return None
    return (d1 + timedelta(days=n - 1)).strftime("%Y-%m-%d")


def default_settings() -> dict:
    return {
        "appareils": {k: DEV[k]["default"] for k in DEV},
        "logiciels": {k: SOFT[k]["default"] for k in SOFT},
        "réseaux": {k: NET[k]["default"] for k in NET},
        "infos": {"nom": "", "debut": "", "fin": "", "region": "", "jours": ""},
    }


def apply_auto_software(cfg: dict) -> dict:
    """Insta360 Studio suit la présence d'une Insta360, LosslessCut celle d'un
    drone. Ces deux-là ne créent aucun dossier : ils décrivent le flux."""
    for key, meta in SOFT.items():
        if meta["auto_from"]:
            cfg["logiciels"][key] = any(cfg["appareils"].get(d) for d in meta["auto_from"])
    return cfg


def load_settings(trip: Path) -> dict:
    cfg = default_settings()
    try:
        raw = json.loads((trip / SETTINGS_FILE).read_text(encoding="utf-8"))
        for cat in ("appareils", "logiciels", "réseaux"):
            for k in cfg[cat]:
                if isinstance(raw.get(cat), dict) and k in raw[cat]:
                    cfg[cat][k] = bool(raw[cat][k])
        if isinstance(raw.get("infos"), dict):
            cfg["infos"].update({k: str(v) for k, v in raw["infos"].items()})
    except Exception:
        pass
    return apply_auto_software(cfg)


def save_settings(trip: Path, cfg: dict) -> None:
    trip.mkdir(parents=True, exist_ok=True)
    (trip / SETTINGS_FILE).write_text(
        json.dumps(cfg, ensure_ascii=False, indent=2), encoding="utf-8")
    write_manifest_settings(trip, cfg)


def load_presets() -> dict:
    try:
        return json.loads(PRESETS_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {}


def save_presets(data: dict) -> None:
    try:
        PRESETS_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2),
                                encoding="utf-8")
    except Exception:
        pass


def checked(cfg: dict, cat: str) -> list[str]:
    return [k for k, on in cfg[cat].items() if on]


def write_manifest_settings(trip: Path, cfg: dict) -> None:
    md = trip / "trip.md"
    start, end = "<!-- réglages -->", "<!-- /réglages -->"
    lines = [start, ""]
    inf = cfg.get("infos", {})
    if inf.get("nom"):
        lines.append("- **Nom** : " + inf["nom"])
    if inf.get("debut") or inf.get("fin"):
        lines.append("- **Dates** : " + inf.get("debut", "") + " → " + inf.get("fin", ""))
    if inf.get("region"):
        lines.append("- **Région** : " + inf["region"])
    lines.append("- **Appareils** : " +
                 (", ".join(DEV[k]["label"] for k in checked(cfg, "appareils")) or "—"))
    lines.append("- **Logiciels** : " +
                 (", ".join(SOFT[k]["label"] for k in checked(cfg, "logiciels")) or "—"))
    lines.append("- **Publication** : " +
                 (", ".join(NET[k]["label"] for k in checked(cfg, "réseaux")) or "—"))
    lines.append("")
    lines.append(end)
    block = "\n".join(lines)
    try:
        if md.exists():
            txt = md.read_text(encoding="utf-8")
        else:
            d = trip_start_date(trip) or datetime.now()
            txt = TRIP_MD.format(slug=trip.name, start=d.date().isoformat())
        if start in txt and end in txt:
            txt = txt[:txt.index(start)] + block + txt[txt.index(end) + len(end):]
        elif "## Journal" in txt:
            txt = txt.replace("## Journal", block + "\n\n## Journal", 1)
        else:
            txt = txt + "\n" + block + "\n"

        # table du journal : remplie si la durée est connue et si aucune ligne
        # n'a encore été saisie à la main.
        try:
            jours = int(str(inf.get("jours", "")).strip() or 0)
        except ValueError:
            jours = 0
        if jours and "## Journal" in txt:
            head, _, tail = txt.partition("## Journal")
            deja = [l for l in tail.splitlines()
                    if l.startswith("|") and not l.startswith("|---")
                    and "Jour |" not in l and l.strip("| ").strip()]
            if not deja:
                txt = head + "## Journal\n\n" + journal_rows(trip, jours) + "\n"
        md.write_text(txt, encoding="utf-8")
    except Exception:
        pass


TRIP_MD = """# {slug}

- **Dates** : {start} → (à compléter)
- **Itinéraire** :
- **Cartes SD** :
- **Notes** :

## Journal

| Jour | Date | Étape | Remarque |
|------|------|-------|----------|
"""


def journal_rows(trip: Path, jours: int) -> str:
    """Table du journal pré-remplie : une ligne par jour, dates calculées à
    partir de la date du dossier. Il ne reste qu'à remplir les étapes."""
    start = trip_start_date(trip) or datetime.now()
    lines = ["| Jour | Date | Étape | Remarque |",
             "|------|------|-------|----------|"]
    for n in range(1, max(1, jours) + 1):
        d = (start + timedelta(days=n - 1)).date()
        lines.append(f"| {n:02d} | {d.isoformat()} |  |  |")
    return "\n".join(lines)


def full_label(key: str) -> str:
    meta = DEV.get(key) or SOFT.get(key) or NET.get(key)
    return meta["label"] if meta else key


def short_label(key: str) -> str:
    return {"garmin": "Garmin", "pixel11": "Pixel 11", "x5": "X5",
            "ace": "Ace Pro", "neo2": "Neo 2", "mini4": "Mini 4",
            "air3": "Air 3", "geolog": "Geo-Log",
            "autre": "Autre"}.get(key, key)


def device_dirname(key: str) -> str | None:
    meta = DEV.get(key) or SOFT.get(key)
    if not meta or not meta.get("folder"):
        return None
    return f"{meta['num']:02d}_{meta['folder']}"


def preview_tree(cfg: dict, trip_name: str = "2026-09-07_exemple",
                 kinds_seen: dict | None = None) -> str:
    """Arborescence telle qu'elle sera créée. `kinds_seen` limite les
    sous-dossiers PHOTO/VIDEO à ceux qui reçoivent réellement des fichiers."""
    lines = [trip_name + "/", "  trip.md", "  01_" + (trip_name[:10] or "jour") + "/"]
    lines = [trip_name + "/", "  trip.md", "  <journée>/"]
    entries = []
    for key in [k for k, *_ in DEVICE_CATALOG] + [k for k, *_ in SOFTWARE_CATALOG]:
        meta = DEV.get(key) or SOFT.get(key)
        cat = "appareils" if key in DEV else "logiciels"
        if not cfg[cat].get(key) or not meta.get("folder"):
            continue
        kinds = meta.get("kinds", ("TRACE",))
        if kinds_seen is not None:
            kinds = tuple(k for k in kinds if kinds_seen.get((key, k)))
            if not kinds:
                continue
        entries.append((meta["num"], device_dirname(key), kinds))
    for _n, name, kinds in sorted(entries):
        lines.append("    " + name + "/")
        if kinds != ("TRACE",):
            for k in kinds:
                lines.append("      " + k + "/")
    nets = checked(cfg, "réseaux")
    if nets:
        lines.append("    " + PUBLICATION_DIR + "/")
        for folder in sorted({NET[k]["folder"] for k in nets}):
            lines.append("      " + folder + "/")
    return "\n".join(lines)


# Chemin d'exiftool : résolu une fois, mémorisé. On cherche au-delà du PATH,
# parce que sous Windows et macOS il est souvent installé hors PATH.
_EXIFTOOL: str | None = None
_EXIFTOOL_DONE = False

CANDIDATE_PATHS = [
    "/opt/homebrew/bin/exiftool",
    "/usr/local/bin/exiftool",
    "/usr/bin/exiftool",
    r"C:\Windows\exiftool.exe",
    r"C:\Program Files\exiftool\exiftool.exe",
    r"C:\exiftool\exiftool.exe",
]


def exiftool_path() -> str | None:
    """Chemin d'exiftool, ou None. Ordre : variable d'environnement
    VESPA_EXIFTOOL, PATH, emplacements d'installation habituels."""
    global _EXIFTOOL, _EXIFTOOL_DONE
    if _EXIFTOOL_DONE:
        return _EXIFTOOL
    _EXIFTOOL_DONE = True
    tries = []
    env = os.environ.get("VESPA_EXIFTOOL")
    if env:
        tries.append(env)
    found = shutil.which("exiftool")
    if found:
        tries.append(found)
    tries += CANDIDATE_PATHS
    for cand in tries:
        try:
            if Path(cand).exists() or cand == found:
                subprocess.run([cand, "-ver"], capture_output=True, check=True)
                _EXIFTOOL = cand
                return _EXIFTOOL
        except Exception:
            continue
    return None


def set_exiftool(path: str) -> bool:
    global _EXIFTOOL, _EXIFTOOL_DONE
    try:
        subprocess.run([path, "-ver"], capture_output=True, check=True)
    except Exception:
        return False
    _EXIFTOOL, _EXIFTOOL_DONE = path, True
    return True


def have_exiftool() -> bool:
    return exiftool_path() is not None


def exif_batch(paths: list[Path]) -> dict[Path, dict]:
    """Métadonnées de tout un lot. Les chemins passent par un fichier d'arguments
    (-@) et non par la ligne de commande : sous Windows celle-ci est limitée à
    environ 32 000 caractères, ce qui saute dès quelques centaines de fichiers
    aux chemins longs. Le jeu de caractères est forcé en UTF-8, sans quoi les
    accents d'un dossier comme « Préalpes » font échouer l'appel."""
    out: dict[Path, dict] = {}
    exe = exiftool_path()
    if not exe or not paths:
        return out
    for i in range(0, len(paths), 500):
        chunk = paths[i:i + 500]
        args = tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False,
                                           encoding="utf-8")
        try:
            for pth in chunk:
                args.write(str(pth) + "\n")
            args.close()
            cmd = [exe, "-charset", "filename=UTF8", "-j", "-n", "-fast2",
                   "-api", "QuickTimeUTC",
                   "-DateTimeOriginal", "-CreateDate", "-MediaCreateDate",
                   "-Make", "-Model", "-GPSLatitude", "-SourceFile",
                   "-@", args.name]
            res = subprocess.run(cmd, capture_output=True, text=True,
                                 encoding="utf-8", errors="replace", timeout=900)
            for item in json.loads(res.stdout or "[]"):
                sf = item.get("SourceFile")
                if sf:
                    out[Path(sf)] = item
        except Exception as e:
            log_event(f"exif_batch: échec sur {len(chunk)} fichiers — {e!r}")
        finally:
            try:
                os.unlink(args.name)
            except Exception:
                pass
    return out


def parse_exif_date(item: dict) -> datetime | None:
    for key in ("DateTimeOriginal", "CreateDate", "MediaCreateDate"):
        val = item.get(key)
        if isinstance(val, str):
            m = re.match(r"(\d{4})[:\-](\d{2})[:\-](\d{2})[ T](\d{2}):(\d{2}):(\d{2})", val.strip())
            if m and int(m.group(1)) > 1980:
                return datetime(*(int(x) for x in m.groups()))
    return None


def date_from_name(path: Path) -> datetime | None:
    m = re.search(r"(20\d{2})[-_]?(\d{2})[-_]?(\d{2})[-_T]?(\d{2})?(\d{2})?(\d{2})?", path.name)
    if not m:
        return None
    try:
        return datetime(int(m.group(1)), int(m.group(2)), int(m.group(3)),
                        int(m.group(4) or 12), int(m.group(5) or 0), int(m.group(6) or 0))
    except ValueError:
        return None


def content_dates(path: Path) -> tuple[datetime, datetime] | None:
    """Premier et dernier horodatage trouvés DANS un GPX/KML/KMZ.
    Un export de trace ou de carnet ne porte aucune date de prise de vue : sa
    date de fichier est celle de l'export, souvent postérieure au voyage.
    Le contenu, lui, dit exactement quand les points ont été enregistrés."""
    ext = path.suffix.lower()
    if ext not in (".gpx", ".kml", ".kmz"):
        return None
    try:
        if ext == ".kmz":
            with zipfile.ZipFile(path) as z:
                name = next((n for n in z.namelist() if n.lower().endswith(".kml")), None)
                if not name:
                    return None
                raw = z.read(name).decode("utf-8", "ignore")
        else:
            raw = path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return None
    stamps = []
    for m in re.finditer(r"(20\d{2})-(\d{2})-(\d{2})[T ](\d{2}):(\d{2}):(\d{2})", raw):
        try:
            stamps.append(datetime(*(int(x) for x in m.groups())))
        except ValueError:
            continue
    if not stamps:
        return None
    return min(stamps), max(stamps)


def capture_datetime(path: Path, exif: dict) -> tuple[datetime, str]:
    span = content_dates(path)
    if span:
        return span[0], "contenu"
    dt = parse_exif_date(exif)
    if dt:
        return dt, "exif"
    dt = date_from_name(path)
    if dt:
        return dt, "nom"
    return datetime.fromtimestamp(path.stat().st_mtime), "date fichier"


def detect_family(path: Path, exif: dict, root: Path | None = None) -> str:
    """Famille probable : drone, insta360, pixel, garmin, geolog — ou un
    appareil précis si l'EXIF le nomme."""
    par_dossier = folder_signal(path, root)
    if par_dossier:
        return par_dossier
    ext = path.suffix.lower()
    if ext in EXT_SOURCE:
        return EXT_SOURCE[ext]
    hay = " ".join([str(exif.get("Make", "")), str(exif.get("Model", ""))]).lower()
    for pattern, res in MODEL_RULES:
        if re.search(pattern, hay):
            return res
    name = path.name.lower()
    for pattern, res in NAME_RULES:
        if re.search(pattern, name):
            return res
    return "autre"


def strong_signal(path: Path, exif: dict) -> str | None:
    """Indice propre au FICHIER : modèle EXIF, puis signature du nom. On ignore
    volontairement le nom du dossier, qui ne dit rien du fichier lui-même."""
    hay = " ".join([str(exif.get("Make", "")), str(exif.get("Model", ""))]).lower().strip()
    if hay:
        for pattern, res in MODEL_RULES:
            if re.search(pattern, hay):
                return res
    name = path.name.lower()
    for pattern, res in NAME_RULES:
        if re.search(pattern, name):
            return res
    return None


def family_of(dev: str) -> str:
    for fam, membres in FAMILIES.items():
        if dev in membres:
            return fam
    return dev


def resolve_device(path: Path, exif: dict, forced: str | None, cfg: dict,
                   root: Path | None = None) -> str:
    """Appareil retenu. Les réglages du voyage lèvent l'ambiguïté : si un seul
    drone est coché, un fichier DJI non identifié lui revient forcément."""
    if forced:
        return forced
    res = detect_family(path, exif, root)
    if res in DEV or res in SOFT:
        return res
    members = FAMILIES.get(res)
    if not members:
        return "autre"
    on = [k for k in members
          if (cfg["appareils"].get(k) if k in DEV else cfg["logiciels"].get(k))]
    if len(on) == 1:
        return on[0]
    if on:
        return on[0] if len(set(on)) == 1 else "autre"
    return "autre"


def quick_hash(path: Path, limit: int = 4 << 20) -> str:
    h = hashlib.sha1()
    with path.open("rb") as fh:
        h.update(fh.read(limit))
    h.update(str(path.stat().st_size).encode())
    return h.hexdigest()


def free_destination(dest: Path, src: Path) -> Path | None:
    if not dest.exists():
        return dest
    if dest.stat().st_size == src.stat().st_size and quick_hash(dest) == quick_hash(src):
        return None
    for n in range(1, 100):
        alt = dest.with_name(f"{dest.stem}__{n}{dest.suffix}")
        if not alt.exists():
            return alt
        if alt.stat().st_size == src.stat().st_size and quick_hash(alt) == quick_hash(src):
            return None
    return dest.with_name(f"{dest.stem}__x{dest.suffix}")


def trip_start_date(trip: Path) -> datetime | None:
    m = re.match(r"(\d{4})-(\d{2})-(\d{2})", trip.name)
    return datetime(*(int(x) for x in m.groups())) if m else None


def scan_sources(sources) -> list[tuple[Path, dict]]:
    """Fichiers médias de toutes les sources, dédoublonnés, chacun accompagné
    de la configuration de sa source : appareil imposé, emplacement, décalage
    d'horloge, journée forcée. Une source configurée l'emporte sur une source
    en détection automatique si un fichier apparaît dans les deux."""
    seen: dict[Path, tuple[Path, dict]] = {}
    excluded: list[Path] = []
    for item in sources:
        cfg = dict(item)
        root = Path(cfg["path"])
        if not root.exists():
            continue
        for p in sorted(root.rglob("*")):
            if not (p.is_file() and p.suffix.lower() in MEDIA_EXT
                    and not p.name.startswith(".")):
                continue
            if any(part.lower() in EXCLUDE_DIRS for part in p.relative_to(root).parts[:-1]):
                excluded.append(p)
                continue
            key = p.resolve()
            if key not in seen or (cfg.get("slug") and not seen[key][1].get("slug")):
                seen[key] = (p, cfg)
    scan_sources.excluded = excluded
    return sorted(seen.values(), key=lambda t: t[0])


def plan_ingest(files, trip: Path, day_start: int, cfg: dict,
                skip_raw: bool = False, skip_proxy: bool = True):
    """Construit le plan de rangement. Retourne aussi le détail photo/vidéo
    par appareil, qui alimente les statistiques et l'aperçu d'arborescence."""
    start = trip_start_date(trip)
    plan: list[tuple[Path, Path, str, str]] = []
    per_day: dict[str, Counter] = defaultdict(Counter)
    per_kind: dict[tuple[str, str], int] = Counter()
    date_origin = Counter()
    duplicates = 0
    outside: list[tuple[Path, datetime]] = []
    multiday: list[tuple[Path, tuple[datetime, datetime]]] = []
    rejected: list[Path] = []
    raw_skipped: list[Path] = []
    proxy_skipped: list[Path] = []
    mismatch: dict[str, list[Path]] = {}

    for item in files:
        p, scfg = item if isinstance(item, tuple) else (item, {})
        ext = p.suffix.lower()
        if skip_raw and ext in RAW_EXT:
            raw_skipped.append(p)
            continue
        if skip_proxy and ext in PROXY_EXT:
            proxy_skipped.append(p)
            continue
        exif = exif_map_global.get(p, {})
        dt, how = capture_datetime(p, exif)
        date_origin[how] += 1
        dt = dt + timedelta(seconds=int(scfg.get("offset", 0) or 0))
        if how == "contenu":
            span = content_dates(p)
            if span:
                # on compare des journées de voyage, pas des dates calendaires :
                # une route de 23 h 30 à 00 h 30 reste une seule journée.
                j1 = (span[0] - timedelta(hours=day_start)).date()
                j2 = (span[1] - timedelta(hours=day_start)).date()
                if j1 != j2:
                    multiday.append((p, span))

        dev = resolve_device(p, exif, scfg.get("device"), cfg, scfg.get("path"))
        # Le choix de la source fait foi, mais on prévient si le fichier
        # lui-même dit clairement autre chose.
        if scfg.get("device") and media_kind(p) != "TRACE":
            signal = strong_signal(p, exif)
            if signal and family_of(signal) not in (family_of(dev), dev):
                mismatch.setdefault(dev, []).append(p)
        meta = DEV.get(dev) or SOFT.get(dev)
        kind = media_kind(p)

        forced_day = scfg.get("day")
        if forced_day:
            n = int(forced_day)
            day = (start + timedelta(days=n - 1)).date()
        else:
            day = (dt - timedelta(hours=day_start)).date()
            n = (day - start.date()).days + 1
        if n < 1:
            outside.append((p, dt))
            continue
        day_key = f"{n:02d}_{day.isoformat()}"

        if not (meta and meta.get("folder")):
            # Rien n'est rangé au hasard : un fichier qu'on ne sait pas
            # attribuer est refusé, listé, et laissé sur la source.
            rejected.append(p)
            continue
        folder = device_dirname(dev)
        kinds = meta.get("kinds", ("TRACE",))
        if kinds == ("TRACE",) or kind == "TRACE":
            dest_dir = trip / day_key / folder
        else:
            dest_dir = trip / day_key / folder / kind
        dest = dest_dir / p.name
        final = free_destination(dest, p) if dest.exists() else dest
        if final is None:
            duplicates += 1
            continue
        plan.append((p, final, day_key, dev))
        per_day[day_key][dev] += 1
        per_kind[(dev, kind)] += 1

    plan_ingest.multiday = multiday
    plan_ingest.per_kind = per_kind
    plan_ingest.rejected = rejected
    plan_ingest.raw_skipped = raw_skipped
    plan_ingest.proxy_skipped = proxy_skipped
    plan_ingest.mismatch = mismatch
    return plan, per_day, per_kind, date_origin, duplicates, outside


exif_map_global: dict = {}


# ---- GPX / waypoints ------------------------------------------------------- #

def iso_utc(s: str) -> datetime | None:
    s = (s or "").strip().replace("Z", "+00:00")
    try:
        dt = datetime.fromisoformat(s)
    except ValueError:
        m = re.match(r"(\d{4})[-:](\d{2})[-:](\d{2})[T ](\d{2}):(\d{2}):(\d{2})", s)
        if not m:
            return None
        dt = datetime(*(int(x) for x in m.groups()))
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def strip_ns(tag: str) -> str:
    return tag.split("}")[-1]


def read_track(folder: Path):
    pts = []
    for p in sorted(folder.glob("*.gpx")):
        try:
            root = ET.parse(p).getroot()
        except ET.ParseError:
            continue
        for tp in root.iter():
            if strip_ns(tp.tag) != "trkpt":
                continue
            t = next((c for c in tp if strip_ns(c.tag) == "time"), None)
            dt = iso_utc(t.text) if t is not None and t.text else None
            if dt:
                pts.append((dt, float(tp.get("lat")), float(tp.get("lon"))))
    pts.sort(key=lambda x: x[0])
    return pts


def track_distance_km(pts) -> float:
    total = 0.0
    for (_, la1, lo1), (_, la2, lo2) in zip(pts, pts[1:]):
        dla, dlo = radians(la2 - la1), radians(lo2 - lo1)
        a = sin(dla / 2) ** 2 + cos(radians(la1)) * cos(radians(la2)) * sin(dlo / 2) ** 2
        total += 6371.0 * 2 * asin(sqrt(a))
    return total


def read_waypoints(folder: Path) -> list[dict]:
    wpts: list[dict] = []
    if not folder.is_dir():
        return wpts
    for p in sorted(folder.glob("*")):
        if p.suffix.lower() not in {".gpx", ".kml", ".kmz"}:
            continue
        try:
            if p.suffix.lower() == ".kmz":
                with zipfile.ZipFile(p) as z:
                    name = next((n for n in z.namelist() if n.lower().endswith(".kml")), None)
                    if not name:
                        continue
                    root = ET.fromstring(z.read(name))
            else:
                root = ET.parse(p).getroot()
        except Exception:
            continue
        for el in root.iter():
            tag = strip_ns(el.tag)
            if tag == "wpt":
                sub = {strip_ns(c.tag): (c.text or "").strip() for c in el}
                wpts.append({"time": iso_utc(sub.get("time", "")),
                             "name": sub.get("name", ""),
                             "note": sub.get("desc") or sub.get("cmt") or "",
                             "lat": float(el.get("lat")) if el.get("lat") else None,
                             "lon": float(el.get("lon")) if el.get("lon") else None,
                             "ele": float(sub["ele"]) if sub.get("ele") else None})
            elif tag == "Placemark":
                name = note = ""
                coord = when = None
                for c in el.iter():
                    ct = strip_ns(c.tag)
                    if ct == "name" and c.text and not name:
                        name = c.text.strip()
                    elif ct == "description" and c.text and not note:
                        note = c.text.strip()
                    elif ct == "coordinates" and c.text and coord is None:
                        parts = c.text.strip().split(",")
                        if len(parts) >= 2:
                            coord = (float(parts[1]), float(parts[0]))
                    elif ct in ("when", "begin") and c.text and when is None:
                        when = iso_utc(c.text)
                wpts.append({"time": when, "name": name, "note": note,
                             "lat": coord[0] if coord else None,
                             "lon": coord[1] if coord else None, "ele": None})
    wpts = [w for w in wpts if w["time"]]
    wpts.sort(key=lambda w: w["time"])
    return wpts


def find_day_dir(day: Path, key: str) -> Path | None:
    """Dossier d'un appareil dans une journée. On cherche d'abord le nom
    numéroté actuel (01_GARMIN), puis les emplacements des versions
    antérieures, pour que les anciens voyages restent lisibles."""
    noms = []
    num = device_dirname(key)
    if num:
        noms.append(num)
    noms += [key, key.upper()]
    for n in noms:
        for cand in (day / n, day / "raw" / n, day / "work" / n):
            if cand.is_dir():
                return cand
    return None


def device_of(path: Path, day: Path) -> str:
    """Appareil auquel appartient un fichier, déduit du dossier numéroté
    présent quelque part au-dessus de lui."""
    connus = {}
    for k in list(DEV) + list(SOFT):
        d = device_dirname(k)
        if d:
            connus[d.lower()] = k
            connus[d.split("_", 1)[1].lower()] = k
    try:
        parts = [x.lower() for x in path.relative_to(day).parts[:-1]]
    except ValueError:
        parts = [path.parent.name.lower()]
    for x in parts:
        if x in connus:
            return connus[x]
    return path.parent.name


def walk_day_media(day: Path, exts=MEDIA_EXT):
    """Tous les médias d'une journée, quel que soit le plan de rangement.
    Les livrables (out/) et les fichiers de trace ou de carnet sont exclus."""
    if not day.is_dir():
        return
    for p in sorted(day.rglob("*")):
        if (not p.is_file() or p.suffix.lower() not in exts
                or p.name.startswith(".")):
            continue
        parts = [x.lower() for x in p.relative_to(day).parts[:-1]]
        if any(x in EXCLUDE_DIRS or x.endswith("publication") for x in parts):
            continue
        if any(x.endswith(("garmin", "geolog")) for x in parts):
            continue
        yield p


def day_media(day: Path) -> list[tuple[datetime, Path, str]]:
    out = []
    for p in walk_day_media(day):
        dt = None
        m = re.search(r"(20\d{2})[-_]?(\d{2})[-_]?(\d{2})[-_T]?(\d{2})(\d{2})(\d{2})", p.name)
        if m:
            try:
                dt = datetime(*(int(x) for x in m.groups()), tzinfo=timezone.utc)
            except ValueError:
                dt = None
        if dt is None:
            dt = datetime.fromtimestamp(p.stat().st_mtime, timezone.utc)
        out.append((dt, p, device_of(p, day)))
    out.sort(key=lambda x: x[0])
    return out


def nearest_point(track, when: datetime, tol: int):
    times = [t[0] for t in track]
    i = bisect_left(times, when)
    best, gap = None, None
    for j in (i - 1, i):
        if 0 <= j < len(track):
            d = abs((times[j] - when).total_seconds())
            if gap is None or d < gap:
                best, gap = track[j], d
    if best is None or gap > tol:
        return None, gap
    return best, gap


def build_journal(day: Path, window: int) -> tuple[str, dict]:
    m = re.match(r"(\d+)_(\d{4}-\d{2}-\d{2})", day.name)
    day_no, day_date = (m.group(1), m.group(2)) if m else ("?", day.name)
    wpts = read_waypoints(find_day_dir(day, "geolog") or day / device_dirname("geolog"))
    media = day_media(day)
    track = read_track(find_day_dir(day, "garmin") or day / device_dirname("garmin"))
    dist = track_distance_km(track) if len(track) > 1 else None

    lines = [f"# Jour {day_no} — {day_date}", ""]
    facts = []
    if dist:
        facts.append(f"**{dist:.0f} km**")
    if track:
        facts.append(f"{track[0][0]:%H:%M} → {track[-1][0]:%H:%M}")
    if media:
        c = Counter(s for _, _, s in media)
        facts.append(" · ".join(f"{full_label(k)} {v}" for k, v in sorted(c.items())))
    if facts:
        lines += ["  ·  ".join(facts), ""]

    if not wpts:
        lines += ["> Aucun waypoint Geo-Log trouvé pour cette journée.",
                  "> Exportez la route du jour depuis le Pixel 8, puis relancez.", ""]
    else:
        lines += [f"## {len(wpts)} waypoint" + ("s" if len(wpts) > 1 else ""), ""]

    used = set()
    for w in wpts:
        head = f"### {w['time']:%H:%M}" + (f" — {w['name']}" if w["name"] else "")
        lines.append(head)
        if w["lat"] is not None:
            coord = f"{w['lat']:.5f}, {w['lon']:.5f}"
            if w["ele"]:
                coord += f" · {w['ele']:.0f} m"
            lines.append(f"`{coord}`")
        if w["note"]:
            lines += ["", w["note"]]
        lo, hi = w["time"] - timedelta(seconds=window), w["time"] + timedelta(seconds=window)
        near = [x for x in media if lo <= x[0] <= hi]
        if near:
            lines += ["", "<!-- médias -->"]
            for dt, p, src in near:
                used.add(p)
                lines.append(f"- `{src}/{p.name}` ({dt:%H:%M})")
        lines += ["", "**À écrire :** ", ""]

    orphans = [x for x in media if x[1] not in used]
    if orphans:
        lines += ["---", "", f"## Médias non rattachés ({len(orphans)})", ""]
        lines += [f"- {dt:%H:%M}  `{src}/{p.name}`" for dt, p, src in orphans]
        lines.append("")

    lines += ["---", "", "## Sélection du soir", "", "- **Reel** : ",
              "- **Carrousel** : ", "- **WhatsApp** : ",
              "- **Chiffre pour la légende** : " + (f"{dist:.0f} km" if dist else ""), ""]

    return "\n".join(lines), {"waypoints": len(wpts), "media": len(media),
                              "orphans": len(orphans), "km": dist}


# --------------------------------------------------------------------------- #
# Interface

# Le scooter et son nuage d'échappement, pré-rendus en couleur depuis les
# emoji 🛵 et 💨. Tk n'affiche pas les polices emoji en couleur sous Windows —
# il les rend en silhouette noire — donc on embarque des images plutôt que du
# texte. Aucune dépendance de police, rendu identique sur les trois systèmes.
SCOOTER_B64 = (
    "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"
    "AKQ/6az/A1kaGec0tpoeAAAAAElFTkSuQmCC"
)

PUFF_B64 = (
    "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"
    "TkSuQmCC"
)


class VespaRide:
    """Un scooter qui traverse l'écran pendant les traitements, et qui fait
    un saut si on lui clique dessus. À l'arrêt, il est garé."""

    def __init__(self, parent, bg, accent, line, dim, w=236, h=68, size=34,
                 small=False):
        import tkinter as tk
        self.tk = tk
        self.w, self.h = w, h
        self.line, self.bg = line, bg
        self.c = tk.Canvas(parent, width=w, height=h, bg=bg,
                           highlightthickness=0, bd=0, cursor="hand2")
        try:
            self.img = tk.PhotoImage(data=SCOOTER_B64)
            self.puff = tk.PhotoImage(data=PUFF_B64)
            if small:                      # moitié de taille, pour l'en-tête
                self.img = self.img.subsample(2)
                self.puff = self.puff.subsample(2)
        except Exception:
            self.img = self.puff = None
        self.small = small
        self.x = w * 0.62
        self.road = 0.0
        self.bob = 0.0
        self.hop = 0.0
        self.running = False
        self.c.bind("<Button-1>", lambda _e: self.jump())
        self._draw()

    # -- API utilisée par l'application ---------------------------------- #
    def grid(self, **kw):
        self.c.grid(**kw)

    def bind(self, *a, **kw):
        self.c.bind(*a, **kw)

    def winfo_exists(self):
        return self.c.winfo_exists()

    def winfo_rootx(self):
        return self.c.winfo_rootx()

    def winfo_rooty(self):
        return self.c.winfo_rooty()

    def winfo_height(self):
        return self.c.winfo_height()

    def start(self):
        if self.running:
            return
        self.running = True
        self._tick()

    def stop(self):
        self.running = False
        self.x = self.w * 0.62
        self.bob = self.hop = 0.0
        self._draw()

    def jump(self):
        if self.hop <= 0:
            self.hop = 1.0
            if not self.running:
                self._hop_tick()

    # -- animation -------------------------------------------------------- #
    def _hop_tick(self):
        if not self.c.winfo_exists() or self.running:
            return
        self.hop = max(0.0, self.hop - 0.08)
        self._draw()
        if self.hop > 0:
            self.c.after(40, self._hop_tick)

    def _tick(self):
        if not self.running or not self.c.winfo_exists():
            return
        self.x -= 2.6
        if self.x < -40:
            self.x = self.w + 40
        self.road = (self.road + 3.2) % 18
        self.bob += 0.55
        self.hop = max(0.0, self.hop - 0.06)
        self._draw()
        self.c.after(45, self._tick)

    def _draw(self):
        from math import sin, pi
        c, w, h = self.c, self.w, self.h
        c.delete("all")
        base = h - (7 if self.small else 14)
        pas = 12 if self.small else 18
        trait = 7 if self.small else 10
        x = -pas + self.road % pas
        while x < w:
            c.create_line(x, base + 5, x + trait, base + 5, fill=self.line, width=2)
            x += pas

        if not self.img:
            return

        saut = sin(self.hop * pi) * (8 if self.small else 13)
        y = base - abs(sin(self.bob)) * 1.6 - saut
        if self.running:
            dx = 17 if self.small else 34
            c.create_image(self.x + dx, y - (5 if self.small else 10),
                           image=self.puff, anchor="sw")
        c.create_image(self.x, y, image=self.img, anchor="s")


def simple_prompt(parent, title, default=""):
    import tkinter as tk
    from tkinter import ttk, simpledialog
    return simpledialog.askstring(title, title, initialvalue=default, parent=parent)


def run_gui() -> int:
    try:
        import tkinter as tk
        import tkinter.font as tkfont
        from tkinter import filedialog, messagebox, ttk
    except ImportError:
        print("Tkinter est absent.\n"
              "  Linux : sudo apt install python3-tk\n"
              "  macOS/Windows : réinstallez Python depuis python.org", file=sys.stderr)
        return 3

    # -- palette sombre ----------------------------------------------------- #
    BG = "#191b1f"          # fond général
    PANEL = "#212429"       # cartes, champs
    PANEL2 = "#2a2e34"      # en-têtes de tableau, survol
    LINE = "#33383f"
    FG = "#e6e2db"
    DIM = "#948d84"
    ACCENT = "#e0a336"
    ACCENT_DK = "#b8801f"
    GOOD = "#6fbf87"
    BAD = "#e2795c"

    F = "Helvetica"
    MONO = "Menlo" if sys.platform == "darwin" else "Consolas" if sys.platform.startswith("win") else "DejaVu Sans Mono"
    S_BASE = 10
    S_SMALL = 9
    S_HEAD = 10

    class App(tk.Tk):
        def __init__(self):
            super().__init__()
            self.title(f"{APP_NAME} v{APP_VERSION}")
            self._set_icon()
            self.geometry("1160x780")
            self.minsize(980, 600)
            self.configure(bg=BG)
            self.queue: queue.Queue = queue.Queue()
            self.plan = None
            self.sources: list[Path] = []
            self.busy = False
            self.settings = default_settings()
            self._style()
            self._menu()
            self._header()
            self._footer()
            self._body()
            self.after(80, self._pump)
            log_session_header()
            self.report_exiftool()

        def _set_icon(self):
            """Icône de fenêtre et de barre des tâches. Sous Windows, un .ico
            posé à côté du script est préféré ; sinon on utilise l'icône
            embarquée dans ce fichier."""
            try:
                ico = Path(__file__).with_name("vespa.ico")
                if sys.platform.startswith("win") and ico.exists():
                    self.iconbitmap(default=str(ico))
                    return
            except Exception:
                pass
            try:
                self._icon_img = tk.PhotoImage(data=base64.b64decode(ICON_B64))
                self.iconphoto(True, self._icon_img)
            except Exception:
                pass

        # ------------------------------------------------------------------ #
        def _style(self):
            s = ttk.Style(self)
            try:
                s.theme_use("clam")
            except Exception:
                pass
            s.configure(".", background=BG, foreground=FG, font=(F, S_BASE),
                        bordercolor=LINE, darkcolor=PANEL, lightcolor=PANEL,
                        troughcolor=PANEL, focuscolor=ACCENT)
            s.configure("TFrame", background=BG)
            s.configure("Card.TFrame", background=PANEL)
            s.configure("TLabel", background=BG, foreground=FG)
            s.configure("Card.TLabel", background=PANEL, foreground=FG)
            s.configure("Dim.TLabel", background=BG, foreground=DIM, font=(F, S_SMALL))
            s.configure("DimCard.TLabel", background=PANEL, foreground=DIM, font=(F, S_SMALL))
            s.configure("H.TLabel", background=BG, foreground=FG, font=(F, S_HEAD, "bold"))
            s.configure("HCard.TLabel", background=PANEL, foreground=ACCENT,
                        font=(F, S_SMALL, "bold"))

            s.configure("TNotebook", background=BG, borderwidth=0, tabmargins=(0, 4, 0, 0))
            s.configure("TNotebook.Tab", background=BG, foreground=DIM,
                        padding=(16, 6), borderwidth=0, font=(F, S_BASE))
            s.map("TNotebook.Tab",
                  background=[("selected", PANEL)],
                  foreground=[("selected", ACCENT)])

            s.configure("TButton", background=PANEL2, foreground=FG, borderwidth=0,
                        padding=(11, 5), font=(F, S_SMALL))
            s.map("TButton", background=[("active", "#363b43"), ("disabled", "#23262b")],
                  foreground=[("disabled", "#5d5850")])
            s.configure("Accent.TButton", background=ACCENT, foreground="#17191c",
                        font=(F, S_SMALL, "bold"), padding=(13, 5), borderwidth=0)
            s.map("Accent.TButton",
                  background=[("active", ACCENT_DK), ("disabled", "#4a4133")],
                  foreground=[("disabled", "#7d766c")])
            s.configure("Link.TButton", background=BG, foreground=DIM,
                        borderwidth=0, padding=(6, 2), font=(F, S_SMALL))
            s.map("Link.TButton", background=[("active", BG)],
                  foreground=[("active", ACCENT)])

            s.configure("TEntry", fieldbackground=PANEL, foreground=FG,
                        insertcolor=FG, borderwidth=0, padding=5)
            s.configure("TSpinbox", fieldbackground=PANEL, foreground=FG,
                        arrowcolor=DIM, borderwidth=0, padding=3)
            s.configure("TCombobox", fieldbackground=PANEL, background=PANEL2,
                        foreground=FG, arrowcolor=DIM, borderwidth=0, padding=3)
            s.map("TCombobox", fieldbackground=[("readonly", PANEL)],
                  foreground=[("readonly", FG)], arrowcolor=[("active", ACCENT)])
            self.option_add("*TCombobox*Listbox.background", PANEL)
            self.option_add("*TCombobox*Listbox.foreground", FG)
            self.option_add("*TCombobox*Listbox.selectBackground", ACCENT_DK)
            self.option_add("*TCombobox*Listbox.font", (F, S_SMALL))

            s.configure("TCheckbutton", background=BG, foreground=FG, font=(F, S_SMALL))
            s.map("TCheckbutton", background=[("active", BG)],
                  indicatorcolor=[("selected", ACCENT)])

            s.configure("Treeview", background=PANEL, fieldbackground=PANEL,
                        foreground=FG, borderwidth=0, rowheight=21, font=(F, S_SMALL))
            s.map("Treeview", background=[("selected", "#3a3f47")],
                  foreground=[("selected", FG)])
            s.configure("Treeview.Heading", background=PANEL2, foreground=DIM,
                        borderwidth=0, font=(F, S_SMALL, "bold"), padding=(4, 4))
            s.map("Treeview.Heading", background=[("active", PANEL2)])

            s.configure("Vertical.TScrollbar", background=PANEL2, troughcolor=BG,
                        borderwidth=0, arrowcolor=DIM, width=9)
            s.map("Vertical.TScrollbar", background=[("active", "#41464e")])
            s.configure("Thin.Horizontal.TProgressbar", background=ACCENT,
                        troughcolor=PANEL, borderwidth=0, thickness=3)

        def _menu(self):
            barre = tk.Menu(self)
            aide = tk.Menu(barre, tearoff=0, bg=PANEL, fg=FG,
                           activebackground=ACCENT_DK, activeforeground=FG)
            aide.add_command(label="À propos", command=self.about_dialog)
            aide.add_separator()
            aide.add_command(label="Exporter le journal de diagnostic…",
                             command=self.export_log)
            aide.add_command(label="Ouvrir le dossier du journal",
                             command=self.open_log_dir)
            barre.add_cascade(label="Aide", menu=aide)
            self.config(menu=barre)

        def export_log(self):
            if not LOG_FILE.exists():
                messagebox.showinfo(APP_NAME, "Le journal est encore vide.")
                return
            cible = filedialog.asksaveasfilename(
                title="Exporter le journal de diagnostic",
                defaultextension=".log",
                initialfile=f"vespa-organizer-{datetime.now():%Y%m%d-%H%M}.log",
                filetypes=[("Journal", "*.log"), ("Tous les fichiers", "*.*")])
            if not cible:
                return
            try:
                morceaux = []
                vieux = LOG_FILE.with_suffix(".log.1")
                if vieux.exists():
                    morceaux.append(vieux.read_text(encoding="utf-8", errors="replace"))
                morceaux.append(LOG_FILE.read_text(encoding="utf-8", errors="replace"))
                Path(cible).write_text("\n".join(morceaux), encoding="utf-8")
                self.log(f"Journal exporté : {cible}", "ok")
            except Exception as e:
                log_exception("export du journal", e)
                messagebox.showerror(APP_NAME, f"Export impossible : {e}")

        def open_log_dir(self):
            try:
                LOG_DIR.mkdir(parents=True, exist_ok=True)
                if sys.platform == "darwin":
                    subprocess.run(["open", str(LOG_DIR)])
                elif sys.platform.startswith("win"):
                    subprocess.run(["explorer", str(LOG_DIR)])
                else:
                    subprocess.run(["xdg-open", str(LOG_DIR)])
            except Exception as e:
                log_exception("ouverture du dossier du journal", e)

        # ------------------------------------------------------------------ #
        def _header(self):
            bar = tk.Frame(self, bg=BG, height=52)
            bar.pack(fill="x", padx=16, pady=(12, 0))
            bar.pack_propagate(False)
            tk.Label(bar, text="Vespa Travel Content Organizer", bg=BG, fg=FG,
                     font=("Georgia", 15, "bold")).pack(side="left")
            tk.Label(bar, text="importer · géolocaliser · pré-rédiger le journal",
                     bg=BG, fg=DIM, font=(F, S_SMALL)).pack(side="left", padx=(12, 0),
                                                            pady=(5, 0))
            self.vespa = VespaRide(bar, bg=BG, accent=ACCENT, line=LINE, dim=DIM,
                                   w=168, h=42, small=True)
            self.vespa.grid_forget = None
            self.vespa.c.pack(side="right", pady=(6, 0))
            self.tip(self.vespa, "Elle roule pendant les traitements. "
                                 "Cliquez dessus, elle saute.")
            tk.Frame(self, bg=LINE, height=1).pack(fill="x", padx=16, pady=(6, 0))

        def _body(self):
            top = ttk.Frame(self, padding=(16, 10, 16, 0))
            top.pack(fill="x")
            ttk.Label(top, text="Voyage", style="H.TLabel").pack(side="left", padx=(0, 10))
            self.trip_var = tk.StringVar()
            ttk.Entry(top, textvariable=self.trip_var).pack(side="left", fill="x",
                                                            expand=True)
            b = ttk.Button(top, text="Parcourir…", command=self.pick_trip)
            b.pack(side="left", padx=(8, 0))
            self.tip(b, "Choisir un dossier de voyage existant.")
            b = ttk.Button(top, text="Nouveau…", command=self.new_trip)
            b.pack(side="left", padx=(6, 0))
            self.tip(b, "Créer un dossier de voyage au bon format de nom : une date "
                        "ISO suivie d’un nom court. C’est cette date qui fixe le jour 1.")
            b = ttk.Button(top, text="Paramètres du voyage…",
                           command=self.trip_settings_dialog)
            b.pack(side="left", padx=(6, 0))
            self.tip(b, "Cocher le matériel emporté, les logiciels et les réseaux. "
                        "Ce qui n’est pas coché n’existe ni à l’ingestion, ni dans "
                        "l’arborescence, ni dans les statistiques.")
            b = ttk.Button(top, text="À propos", command=self.about_dialog)
            b.pack(side="left", padx=(6, 0))
            self.tip(b, "Version, date de compilation et technologies utilisées.")
            hint = ttk.Frame(self, padding=(16, 2, 16, 0))
            hint.pack(fill="x")
            ttk.Label(hint, style="Dim.TLabel",
                      text="Le nom du dossier commence par une date ISO — "
                           "2026-09-05_valais-2j — qui fixe le jour 1.").pack(anchor="w")
            self.trip_var.trace_add("write", lambda *_: self.on_trip_change())

            nb = ttk.Notebook(self)
            nb.pack(fill="both", expand=True, padx=16, pady=(10, 0))
            self.nb = nb
            self.tab_import = ttk.Frame(nb, padding=12, style="Card.TFrame")
            self.tab_geo = ttk.Frame(nb, padding=12, style="Card.TFrame")
            self.tab_journal = ttk.Frame(nb, padding=12, style="Card.TFrame")
            nb.add(self.tab_import, text="1 · Importer")
            nb.add(self.tab_geo, text="2 · Géolocaliser")
            nb.add(self.tab_journal, text="3 · Journal")
            self._tab_import()
            self._tab_geo()
            self._tab_journal()
            self._buttons = []
            self._collect_buttons(self)

        # -- onglet 1 -------------------------------------------------------- #
        def _tab_import(self):
            f = self.tab_import
            f.columnconfigure(0, weight=1)
            f.rowconfigure(2, weight=1)

            head = ttk.Frame(f, style="Card.TFrame")
            head.grid(row=0, column=0, sticky="nsew")
            head.columnconfigure(0, weight=1)

            ttk.Label(head, text="SOURCES", style="HCard.TLabel").grid(
                row=0, column=0, sticky="w")
            lb = tk.Frame(head, bg=LINE)
            lb.grid(row=1, column=0, sticky="nsew", pady=(4, 6), padx=(0, 16))
            self.src_list = tk.Listbox(lb, height=8, bd=0, highlightthickness=0,
                                       bg=PANEL, fg=FG, selectbackground="#3a3f47",
                                       selectforeground=FG, activestyle="none",
                                       font=(MONO, S_SMALL))
            self.src_list.pack(side="left", fill="both", expand=True, padx=1, pady=1)
            sbl = ttk.Scrollbar(lb, orient="vertical", command=self.src_list.yview)
            sbl.pack(side="right", fill="y", padx=(0, 1), pady=1)
            self.autohide(self.src_list, sbl)
            brow = ttk.Frame(head, style="Card.TFrame")
            brow.grid(row=2, column=0, sticky="w")
            b = ttk.Button(brow, text="Ajouter…", command=self.add_source)
            b.pack(side="left")
            self.tip(b, "Ajouter un dossier à lire : carte SD, dossier téléchargé "
                        "depuis Google Photos, export Geo-Log. Sous-dossiers compris.")
            b = ttk.Button(brow, text="Modifier…", command=self.edit_source)
            b.pack(side="left", padx=6)
            self.tip(b, "Rouvrir la configuration de la source sélectionnée : "
                        "appareil, correction d’horloge, journée imposée.")
            b = ttk.Button(brow, text="Retirer", command=self.remove_source)
            b.pack(side="left")
            self.tip(b, "Retirer de la liste la ou les sources sélectionnées. "
                        "Aucun fichier n’est supprimé.")

            opt = ttk.Frame(head, style="Card.TFrame")
            opt.grid(row=0, column=1, rowspan=3, sticky="nw")
            ttk.Label(opt, text="OPTIONS", style="HCard.TLabel").grid(
                row=0, column=0, columnspan=3, sticky="w")
            ttk.Label(opt, text="Bascule de journée", style="Card.TLabel").grid(
                row=1, column=0, sticky="w", pady=(6, 0))
            self.daystart = tk.IntVar(value=4)
            sp = ttk.Spinbox(opt, from_=0, to=12, width=3, textvariable=self.daystart)
            sp.grid(row=1, column=1, sticky="w", padx=(8, 4), pady=(6, 0))
            self.tip(sp, "Heure à laquelle on change de journée. À 4 h, une photo "
                         "prise à 1 h 10 du matin compte pour la journée de route "
                         "précédente — ce qui est presque toujours ce que vous voulez.")
            ttk.Label(opt, text="h", style="DimCard.TLabel").grid(row=1, column=2, sticky="w",
                                                                  pady=(6, 0))
            ttk.Label(opt, text="une photo de 1 h compte pour la veille",
                      style="DimCard.TLabel").grid(row=2, column=0, columnspan=3,
                                                   sticky="w", pady=(1, 0))
            self.skipraw = tk.BooleanVar(value=True)
            cb = ttk.Checkbutton(opt, text="Exclure les RAW / DNG",
                                 variable=self.skipraw)
            cb.grid(row=3, column=0, columnspan=3, sticky="w", pady=(10, 0))
            self.tip(cb, "Ne copie pas les fichiers bruts (DNG, RAW, ARW, CR2…). "
                         "Pour publier sur les réseaux, les JPG suffisent — et vos "
                         "cartes conservent les originaux le temps que vous décidiez.")
            ttk.Label(opt, text="les JPG suffisent pour publier",
                      style="DimCard.TLabel").grid(row=4, column=0, columnspan=3,
                                                   sticky="w", pady=(1, 0))
            self.skipproxy = tk.BooleanVar(value=True)
            cb = ttk.Checkbutton(opt, text="Exclure les SRT / LRV",
                                 variable=self.skipproxy)
            cb.grid(row=5, column=0, columnspan=3, sticky="w", pady=(4, 0))
            self.tip(cb, "Écarte les fichiers annexes : proxys basse définition "
                         "(.lrv), pistes de télémétrie des drones (.srt) et "
                         "vignettes (.thm). Aucun usage pour publier, et ils "
                         "gonflent les sauvegardes.")
            ttk.Label(opt, text="proxys et télémétrie, inutiles à la publication",
                      style="DimCard.TLabel").grid(row=6, column=0, columnspan=3,
                                                   sticky="w", pady=(1, 0))

            self.tip(self.vespa, "Elle roule pendant les traitements. "
                                 "Cliquez dessus, elle saute.")

            act = ttk.Frame(f, style="Card.TFrame")
            act.grid(row=1, column=0, sticky="w", pady=(8, 6))
            b = ttk.Button(act, text="Analyser", command=self.do_analyse)
            b.pack(side="left")
            self.tip(b, "Lecture seule : rien n’est écrit. Affiche ce qui serait "
                        "rangé, où, et ce qui serait refusé. À faire systématiquement "
                        "avant d’importer.")
            self.btn_import = ttk.Button(act, text="Importer", style="Accent.TButton",
                                         command=self.do_import, state="disabled")
            self.btn_import.pack(side="left", padx=8)
            self.tip(self.btn_import, "Copie les fichiers dans l’arborescence du "
                                      "voyage. Les fichiers déjà présents à "
                                      "l’identique sont ignorés : relancer ne coûte "
                                      "rien.")
            self.sum_lbl = ttk.Label(act, text="", style="DimCard.TLabel")
            self.sum_lbl.pack(side="left", padx=8)

            res = ttk.Frame(f, style="Card.TFrame")
            res.grid(row=2, column=0, sticky="nsew")
            res.columnconfigure(0, weight=1)
            res.rowconfigure(1, weight=1)

            ttk.Label(res, text="PAR JOURNÉE ET PAR APPAREIL",
                      style="HCard.TLabel").grid(row=0, column=0, sticky="w")
            dayw = tk.Frame(res, bg=LINE)
            dayw.grid(row=1, column=0, sticky="nsew", pady=(3, 7))
            # Colonnes reconstruites à chaque analyse : un appareil non coché
            # n'a pas de colonne.
            self.tree_day = ttk.Treeview(dayw, columns=("jour", "total"),
                                         show="headings", height=6)
            self.tree_day.heading("jour", text="Jour")
            self.tree_day.heading("total", text="Total")
            self.tree_day.tag_configure("total", font=(F, S_SMALL, "bold"),
                                        foreground=ACCENT)
            self.tree_day.tag_configure("kind", foreground=DIM)
            self.tree_day.pack(side="left", fill="both", expand=True, padx=1, pady=1)
            sb1 = ttk.Scrollbar(dayw, orient="vertical", command=self.tree_day.yview)
            sb1.pack(side="right", fill="y", padx=(0, 1), pady=1)
            self.autohide(self.tree_day, sb1)


        # -- onglet 2 -------------------------------------------------------- #
        def _tab_geo(self):
            f = self.tab_geo
            f.columnconfigure(4, weight=1)
            f.rowconfigure(2, weight=1)
            ttk.Label(f, style="DimCard.TLabel",
                      text="Applique la trace Garmin du jour aux fichiers sans "
                           "coordonnées. L’analyse ne demande rien ; l’écriture "
                           "demande exiftool.").grid(row=0, column=0, columnspan=6,
                                                     sticky="w", pady=(0, 8))
            row = ttk.Frame(f, style="Card.TFrame")
            row.grid(row=1, column=0, columnspan=6, sticky="w")
            ttk.Label(row, text="Journée", style="Card.TLabel").pack(side="left")
            self.geo_day = tk.StringVar()
            self.geo_combo = ttk.Combobox(row, textvariable=self.geo_day, width=18,
                                          state="readonly", font=(F, S_SMALL))
            self.geo_combo.pack(side="left", padx=(6, 16))
            ttk.Label(row, text="Tolérance", style="Card.TLabel").pack(side="left")
            self.geo_tol = tk.IntVar(value=900)
            ttk.Spinbox(row, from_=60, to=7200, increment=60, width=6,
                        textvariable=self.geo_tol).pack(side="left", padx=(6, 2))
            ttk.Label(row, text="s", style="DimCard.TLabel").pack(side="left", padx=(0, 16))
            ttk.Label(row, text="Décalage", style="Card.TLabel").pack(side="left")
            self.geo_off = tk.IntVar(value=0)
            ttk.Spinbox(row, from_=-43200, to=43200, increment=60, width=8,
                        textvariable=self.geo_off).pack(side="left", padx=(6, 2))
            ttk.Label(row, text="s", style="DimCard.TLabel").pack(side="left", padx=(0, 16))
            ttk.Button(row, text="Analyser",
                       command=lambda: self.do_geo(False)).pack(side="left")
            ttk.Button(row, text="Détecter le décalage",
                       command=self.do_autooffset).pack(side="left", padx=6)
            ttk.Button(row, text="Écrire", style="Accent.TButton",
                       command=lambda: self.do_geo(True)).pack(side="left")

            box = tk.Frame(f, bg=LINE)
            box.grid(row=2, column=0, columnspan=6, sticky="nsew", pady=(10, 0))
            self.geo_out = tk.Text(box, wrap="word", bd=0, bg=PANEL, fg=FG,
                                   insertbackground=FG, highlightthickness=0,
                                   font=(MONO, S_SMALL), padx=10, pady=8)
            self.geo_out.pack(side="left", fill="both", expand=True, padx=1, pady=1)

        # -- onglet 3 -------------------------------------------------------- #
        def _tab_journal(self):
            f = self.tab_journal
            f.columnconfigure(5, weight=1)
            f.rowconfigure(2, weight=1)
            ttk.Label(f, style="DimCard.TLabel",
                      text="Construit le brouillon du jour depuis les waypoints "
                           "Geo-Log, en listant sous chacun les médias pris au "
                           "même moment.").grid(row=0, column=0, columnspan=6,
                                                sticky="w", pady=(0, 8))
            row = ttk.Frame(f, style="Card.TFrame")
            row.grid(row=1, column=0, columnspan=6, sticky="w")
            ttk.Label(row, text="Journée", style="Card.TLabel").pack(side="left")
            self.j_day = tk.StringVar()
            self.j_combo = ttk.Combobox(row, textvariable=self.j_day, width=18,
                                        state="readonly", font=(F, S_SMALL))
            self.j_combo.pack(side="left", padx=(6, 16))
            ttk.Label(row, text="Fenêtre", style="Card.TLabel").pack(side="left")
            self.j_win = tk.IntVar(value=600)
            ttk.Spinbox(row, from_=60, to=3600, increment=60, width=6,
                        textvariable=self.j_win).pack(side="left", padx=(6, 2))
            ttk.Label(row, text="s", style="DimCard.TLabel").pack(side="left", padx=(0, 16))
            ttk.Button(row, text="Aperçu",
                       command=lambda: self.do_journal(False)).pack(side="left")
            ttk.Button(row, text="Écrire journal.md", style="Accent.TButton",
                       command=lambda: self.do_journal(True)).pack(side="left", padx=6)
            ttk.Button(row, text="Ouvrir le dossier",
                       command=self.open_day_folder).pack(side="left")

            box = tk.Frame(f, bg=LINE)
            box.grid(row=2, column=0, columnspan=6, sticky="nsew", pady=(10, 0))
            self.j_out = tk.Text(box, wrap="word", bd=0, bg=PANEL, fg=FG,
                                 insertbackground=FG, highlightthickness=0,
                                 font=(MONO, S_SMALL), padx=10, pady=8)
            self.j_out.pack(side="left", fill="both", expand=True, padx=1, pady=1)
            sbj = ttk.Scrollbar(box, orient="vertical", command=self.j_out.yview)
            sbj.pack(side="right", fill="y", padx=(0, 1), pady=1)
            self.autohide(self.j_out, sbj)

        # -- pied ------------------------------------------------------------ #
        def _footer(self):
            wrap = ttk.Frame(self, padding=(16, 6, 16, 12))
            wrap.pack(fill="x", side="bottom")
            self.pb = ttk.Progressbar(wrap, style="Thin.Horizontal.TProgressbar")
            self.pb.pack(fill="x")
            self.status = ttk.Label(wrap, text="", style="Dim.TLabel")
            self.status.pack(anchor="w", pady=(3, 3))
            box = tk.Frame(wrap, bg=LINE)
            box.pack(fill="x")
            self.logbox = tk.Text(box, height=3, wrap="word", bd=0, bg=PANEL, fg=FG,
                                  highlightthickness=0, font=(MONO, S_SMALL),
                                  padx=9, pady=6)
            self.logbox.pack(fill="x", padx=1, pady=1)
            self.logbox.tag_config("warn", foreground=BAD)
            self.logbox.tag_config("ok", foreground=GOOD)
            self.logbox.tag_config("dim", foreground=DIM)

        # -- infobulles -------------------------------------------------------- #
        def tip(self, widget, text):
            """Infobulle simple : apparaît après un court délai, disparaît à la
            sortie de la souris."""
            state = {"win": None, "after": None}

            def show():
                if state["win"] or not widget.winfo_exists():
                    return
                KEY = "#ff00ff"          # couleur rendue transparente (Windows)
                w = tk.Toplevel(self)
                w.wm_overrideredirect(True)
                w.withdraw()
                arrondi = False
                try:
                    w.wm_attributes("-transparentcolor", KEY)
                    arrondi = True
                except Exception:
                    pass
                w.configure(bg=KEY if arrondi else LINE)

                pad, r = 7, 9
                f = tkfont.Font(family=F, size=S_SMALL - 1)
                lignes = []
                for para in text.split("\n"):
                    mot, cour = para.split(" "), ""
                    for m_ in mot:
                        essai = (cour + " " + m_).strip()
                        if f.measure(essai) > 270 and cour:
                            lignes.append(cour)
                            cour = m_
                        else:
                            cour = essai
                    lignes.append(cour)
                bw = max(f.measure(l) for l in lignes) + pad * 2
                bh = len(lignes) * f.metrics("linespace") + pad * 2

                cv = tk.Canvas(w, width=bw, height=bh, highlightthickness=0, bd=0,
                               bg=KEY if arrondi else PANEL2)
                cv.pack()
                if arrondi:
                    cv.create_polygon(
                        r, 0, bw - r, 0, bw, 0, bw, r, bw, bh - r, bw, bh,
                        bw - r, bh, r, bh, 0, bh, 0, bh - r, 0, r, 0, 0,
                        smooth=True, splinesteps=12, fill=PANEL2, outline=LINE)
                cv.create_text(pad, pad, text="\n".join(lignes), anchor="nw",
                               fill=ACCENT, font=f, justify="left")

                sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
                x = widget.winfo_rootx() + 14
                y = widget.winfo_rooty() + widget.winfo_height() + 6
                x = max(6, min(x, sw - bw - 6))
                if y + bh > sh - 6:
                    y = max(6, widget.winfo_rooty() - bh - 6)
                w.wm_geometry(f"{bw}x{bh}+{int(x)}+{int(y)}")
                w.deiconify()
                state["win"] = w

            def enter(_e=None):
                state["after"] = self.after(450, show)

            def leave(_e=None):
                if state["after"]:
                    self.after_cancel(state["after"])
                    state["after"] = None
                if state["win"]:
                    state["win"].destroy()
                    state["win"] = None

            widget.bind("<Enter>", enter, add="+")
            widget.bind("<Leave>", leave, add="+")
            widget.bind("<Button-1>", leave, add="+")
            return widget

        # -- verrouillage de l'interface pendant un traitement ---------------- #
        def _collect_buttons(self, widget):
            for child in widget.winfo_children():
                if isinstance(child, ttk.Button):
                    self._buttons.append(child)
                self._collect_buttons(child)

        def _lock(self):
            """Grise tous les boutons : deux clics sur Importer ne peuvent pas
            lancer deux traitements."""
            self._saved = {}
            for b in self._buttons:
                try:
                    self._saved[b] = str(b.cget("state"))
                    b.configure(state="disabled")
                except Exception:
                    pass
            self.configure(cursor="watch")

        def _unlock(self):
            for b, st in getattr(self, "_saved", {}).items():
                try:
                    b.configure(state=st)
                except Exception:
                    pass
            self._saved = {}
            self.configure(cursor="")
            try:
                self.vespa.stop()
            except Exception:
                pass
            self._sync_import_button()

        def _sync_import_button(self):
            ready = bool(self.plan and self.plan[0])
            self.btn_import.configure(state="normal" if ready else "disabled")

        # -- utilitaires ------------------------------------------------------ #
        @staticmethod
        def autohide(widget, bar, side="right"):
            """La barre ne s'affiche que si le contenu déborde."""
            def setter(first, last):
                bar.set(first, last)
                if float(first) <= 0.0 and float(last) >= 1.0:
                    bar.pack_forget()
                else:
                    bar.pack(side=side, fill="y", padx=(0, 1), pady=1)
            widget.configure(yscrollcommand=setter)
            bar.pack_forget()

        def log(self, msg, tag=None):
            self.logbox.insert("end", msg + "\n", tag or ())
            self.logbox.see("end")

        def report_exiftool(self):
            p = exiftool_path()
            if p:
                self.log(f"exiftool : {p}", "dim")
            else:
                self.log("exiftool introuvable. L’application fonctionne : les dates "
                         "viennent du nom de fichier puis de la date du fichier. "
                         "Mais l’écriture des coordonnées est impossible et les deux "
                         "drones ne sont pas distingués — utilisez « Forcer la source ».",
                         "warn")
                self.log("macOS : brew install exiftool · Windows : exiftool.org, "
                         "renommer exiftool(-k).exe en exiftool.exe · "
                         "Linux : sudo apt install libimage-exiftool-perl", "dim")

        def about_dialog(self):
            win = tk.Toplevel(self)
            win.title("À propos")
            win.configure(bg=BG)
            win.transient(self)
            win.resizable(False, False)
            try:
                win.iconphoto(False, self._icon_img)
            except Exception:
                pass

            head = tk.Frame(win, bg=BG)
            head.pack(anchor="w", padx=26, pady=(24, 18))
            try:
                self._about_img = tk.PhotoImage(data=SCOOTER_B64)
                tk.Label(head, image=self._about_img, bg=BG).pack(side="left",
                                                                  padx=(0, 16))
            except Exception:
                pass
            tk.Label(head, text=APP_NAME, bg=BG, fg=FG,
                     font=("Georgia", 15, "bold")).pack(side="left")

            body = tk.Frame(win, bg=BG)
            body.pack(anchor="w", fill="x", padx=26)
            tk.Label(body, text=f"Version {APP_VERSION}", bg=BG, fg=FG,
                     font=(F, S_BASE)).pack(anchor="w")
            tk.Label(body, text=f"Build du {build_date()}", bg=BG, fg=FG,
                     font=(F, S_BASE)).pack(anchor="w")

            tk.Label(body, text="Technologies utilisées", bg=BG, fg=FG,
                     font=(F, S_BASE, "bold")).pack(anchor="w", pady=(18, 8))
            exif_etat = "détecté" if exiftool_path() else "absent"
            for ligne in (
                "Python · Tkinter / ttk (interface graphique)",
                f"ExifTool (métadonnées, outil externe optionnel — {exif_etat})",
                "xml.etree · zipfile (traces GPX, KML, KMZ)",
                "hashlib (détection des doublons par empreinte)",
                "threading (traitements en arrière-plan)",
                "PyInstaller (packaging Windows)",
            ):
                tk.Label(body, text=ligne, bg=BG, fg=ACCENT,
                         font=(F, S_BASE)).pack(anchor="w", pady=1)

            tk.Label(body, text=CREDIT, bg=BG, fg=DIM,
                     font=(F, S_SMALL)).pack(anchor="w", pady=(18, 0))

            btns = ttk.Frame(win)
            btns.pack(anchor="e", padx=26, pady=(22, 20))
            if not exiftool_path():
                bl = ttk.Button(btns, text="Localiser exiftool…",
                                command=lambda: (win.destroy(), self.locate_exiftool()))
                bl.pack(side="left", padx=(0, 8))
            ttk.Button(btns, text="Fermer", command=win.destroy).pack(side="left")
            win.bind("<Escape>", lambda _e: win.destroy())
            win.grab_set()
            self.wait_window(win)

        def locate_exiftool(self):
            f = filedialog.askopenfilename(title="Où se trouve exiftool ?")
            if not f:
                return
            if set_exiftool(f):
                self.log(f"exiftool retenu : {f}", "ok")
            else:
                messagebox.showerror(APP_NAME, "Ce fichier ne répond pas comme exiftool.")

        def _pump(self):
            try:
                while True:
                    kind, payload = self.queue.get_nowait()
                    if kind == "log":
                        self.log(*payload)
                    elif kind == "status":
                        self.status.config(text=payload)
                    elif kind == "progress":
                        self.pb["value"] = payload
                    elif kind == "call":
                        payload()
            except queue.Empty:
                pass
            self.after(80, self._pump)

        def bg(self, fn):
            if self.busy:
                return          # ne devrait plus arriver : les boutons sont grisés
            self.busy = True
            self._lock()
            try:
                self.vespa.start()
            except Exception:
                pass

            def wrap():
                try:
                    fn()
                except Exception as e:
                    log_exception("traitement en arrière-plan", e)
                    self.queue.put(("log", (f"Erreur : {e} — détail dans le journal "
                                            f"de diagnostic.", "warn")))
                finally:
                    self.busy = False
                    self.queue.put(("status", ""))
                    self.queue.put(("progress", 0))
                    self.queue.put(("call", self._unlock))
            threading.Thread(target=wrap, daemon=True).start()

        def trip(self) -> Path | None:
            t = self.trip_var.get().strip()
            if not t:
                messagebox.showwarning(APP_NAME, "Choisissez d’abord le dossier du voyage.")
                return None
            p = Path(t).expanduser()
            if trip_start_date(p) is None:
                messagebox.showerror(APP_NAME,
                                     "Le nom du dossier doit commencer par une date ISO,\n"
                                     "par exemple 2026-09-05_valais-2j.")
                return None
            return p

        def pick_trip(self):
            d = filedialog.askdirectory(title="Dossier du voyage")
            if d:
                self.trip_var.set(d)

        def new_trip(self):
            parent = filedialog.askdirectory(title="Où créer le voyage ?")
            if not parent:
                return
            win = tk.Toplevel(self)
            win.title("Nouveau voyage")
            win.configure(bg=BG)
            win.resizable(False, False)
            ttk.Label(win, text="Nom du voyage").grid(row=0, column=0, sticky="w",
                                                      padx=14, pady=(14, 3))
            nv = tk.StringVar(value="")
            ttk.Entry(win, textvariable=nv, width=32).grid(row=1, column=0, columnspan=2,
                                                            padx=14, sticky="w")
            ttk.Label(win, text="Départ").grid(row=2, column=0, sticky="w",
                                               padx=14, pady=(10, 3))
            ttk.Label(win, text="Retour (facultatif)").grid(row=2, column=1, sticky="w",
                                                            pady=(10, 3))
            dv = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
            fv = tk.StringVar(value="")
            ttk.Entry(win, textvariable=dv, width=14).grid(row=3, column=0,
                                                           padx=14, sticky="w")
            ttk.Entry(win, textvariable=fv, width=14).grid(row=3, column=1, sticky="w")
            apercu = ttk.Label(win, text="", style="Dim.TLabel")
            apercu.grid(row=4, column=0, columnspan=2, sticky="w", padx=14, pady=(8, 0))

            def slug_de(nom: str) -> str:
                base = unicodedata.normalize("NFKD", nom).encode("ascii", "ignore").decode()
                return re.sub(r"[^a-z0-9]+", "-", base.lower()).strip("-") or "voyage"

            def maj(*_):
                d = dv.get().strip()
                apercu.config(text="Dossier : " + (d if re.match(r"\d{4}-\d{2}-\d{2}$", d)
                                                   else "????-??-??")
                                   + "_" + slug_de(nv.get()))
            nv.trace_add("write", maj)
            dv.trace_add("write", maj)
            maj()

            def create():
                d = dv.get().strip()
                if not re.match(r"\d{4}-\d{2}-\d{2}$", d):
                    messagebox.showerror(APP_NAME, "Date de départ invalide.")
                    return
                p = Path(parent) / f"{d}_{slug_de(nv.get())}"
                p.mkdir(parents=True, exist_ok=True)
                cfg = default_settings()
                cfg["infos"]["nom"] = nv.get().strip()
                cfg["infos"]["debut"] = d
                cfg["infos"]["fin"] = fv.get().strip()
                cfg["infos"]["jours"] = str(jours_entre(d, fv.get().strip()) or "")
                save_settings(p, cfg)
                self.trip_var.set(str(p))
                self.settings = cfg
                self.log(f"Voyage créé : {p}", "ok")
                win.destroy()
            ttk.Button(win, text="Créer", style="Accent.TButton",
                       command=create).grid(row=5, column=0, padx=14, pady=14, sticky="w")
            win.bind("<Return>", lambda _e: create())
            win.bind("<Escape>", lambda _e: win.destroy())
            win.grab_set()

        def _src_line(self, cfg):
            label = cfg.get("label") or "Détection automatique"
            short = label if len(label) <= 30 else label[:29] + "…"
            extra = []
            if cfg.get("offset"):
                sec = int(cfg["offset"])
                sign = "+" if sec >= 0 else "-"
                h, rem = divmod(abs(sec), 3600)
                extra.append(f"horloge {sign}{h}h{rem // 60:02d}")
            if cfg.get("day"):
                extra.append(f"jour {int(cfg['day']):02d}")
            tail = ("   " + " · ".join(extra)) if extra else ""
            return f"{short:<30}  {cfg['path']}{tail}"

        def _redraw_sources(self):
            self.src_list.delete(0, "end")
            for cfg in self.sources:
                self.src_list.insert("end", self._src_line(cfg))

        def add_source(self):
            cfg = self.source_dialog()
            if cfg:
                self.sources.append(cfg)
                self._redraw_sources()

        def edit_source(self):
            sel = self.src_list.curselection()
            if not sel:
                self.log("Sélectionnez d’abord une source dans la liste.", "warn")
                return
            i = sel[0]
            cfg = self.source_dialog(self.sources[i])
            if cfg:
                self.sources[i] = cfg
                self._redraw_sources()
                self.src_list.selection_set(i)

        def remove_source(self):
            for i in reversed(self.src_list.curselection()):
                del self.sources[i]
            self._redraw_sources()

        def source_dialog(self, existing=None):
            """Dialogue « Configurer une source ». Renvoie un dict ou None."""
            win = tk.Toplevel(self)
            win.title("Configurer une source")
            win.configure(bg=BG)
            win.transient(self)
            win.resizable(False, False)
            try:
                win.iconphoto(False, self._icon_img)
            except Exception:
                pass
            pad = {"padx": 16, "pady": 4}
            out = {}

            ttk.Label(win, text="Dossier source", style="H.TLabel").grid(
                row=0, column=0, sticky="w", padx=16, pady=(16, 4))
            pv = tk.StringVar(value=str(existing["path"]) if existing else "")
            ttk.Entry(win, textvariable=pv, width=52).grid(row=0, column=1, sticky="we",
                                                            padx=(0, 8), pady=(16, 4))

            def browse():
                d = filedialog.askdirectory(title="Dossier source", parent=win)
                if d:
                    pv.set(d)
            ttk.Button(win, text="Parcourir…", command=browse).grid(row=0, column=2,
                                                                     padx=(0, 16),
                                                                     pady=(16, 4))

            ttk.Label(win, text="Appareil / contenu").grid(row=1, column=0, sticky="w", **pad)
            dv = tk.StringVar(value=(existing or {}).get("label") or "Détection automatique")
            pairs = self.enabled_devices()
            labels = [lbl for _k, lbl in pairs]
            by_label = {lbl: k for k, lbl in pairs}
            if existing and existing.get("label") and existing["label"] not in labels:
                labels.append(existing["label"])
                by_label[existing["label"]] = existing.get("device")
            ttk.Combobox(win, textvariable=dv, state="readonly", width=38,
                         font=(F, S_SMALL),
                         values=labels).grid(row=1, column=1, sticky="w", pady=4)

            ttk.Label(win, text="Corriger l’horloge").grid(row=2, column=0, sticky="w", **pad)
            clk = ttk.Frame(win)
            clk.grid(row=2, column=1, sticky="w", pady=4)
            off = int(existing.get("offset", 0)) if existing else 0
            sign_v = tk.StringVar(value="−" if off < 0 else "+")
            hv = tk.IntVar(value=abs(off) // 3600)
            mv = tk.IntVar(value=(abs(off) % 3600) // 60)
            ttk.Combobox(clk, textvariable=sign_v, width=2, state="readonly",
                         values=["+", "−"]).pack(side="left")
            ttk.Spinbox(clk, from_=0, to=24, width=3, textvariable=hv).pack(side="left",
                                                                            padx=(6, 2))
            ttk.Label(clk, text="h", style="Dim.TLabel").pack(side="left")
            ttk.Spinbox(clk, from_=0, to=59, width=3, textvariable=mv).pack(side="left",
                                                                            padx=(6, 2))
            ttk.Label(clk, text="min", style="Dim.TLabel").pack(side="left")

            ttk.Label(win, text="Imposer une journée").grid(row=3, column=0, sticky="w", **pad)
            day_v = tk.StringVar(value=str(existing.get("day") or "") if existing else "")
            ttk.Entry(win, textvariable=day_v, width=6).grid(row=3, column=1, sticky="w",
                                                              pady=4)

            ttk.Label(win, justify="left", wraplength=430, style="Dim.TLabel",
                      text="L’appareil est facultatif : la détection automatique "
                           "suffit dans la plupart des cas, et les paramètres du voyage "
                           "lèvent l’ambiguïté — si un seul drone est coché, un fichier "
                           "DJI non identifié lui revient forcément.\n"
                           "« Corriger l’horloge » décale les dates de cette source "
                           "seulement, avant le classement par journée.\n"
                           "« Imposer une journée » (1, 2, 3…) force tout le dossier "
                           "dans cette journée. Dernier recours."
                      ).grid(row=4, column=0, columnspan=3, sticky="w", padx=16,
                             pady=(10, 4))

            def ok():
                if not pv.get().strip():
                    messagebox.showwarning("Configurer une source",
                                           "Choisissez un dossier.", parent=win)
                    return
                dev_key = by_label.get(dv.get())
                sec = hv.get() * 3600 + mv.get() * 60
                if sign_v.get() == "−":
                    sec = -sec
                d = day_v.get().strip()
                out.update({"path": Path(pv.get().strip()).expanduser(),
                            "label": dv.get(), "device": dev_key,
                            "base": "raw",
                            "offset": sec, "day": int(d) if d.isdigit() else None})
                win.destroy()

            btns = ttk.Frame(win)
            btns.grid(row=5, column=0, columnspan=3, sticky="e", padx=16, pady=(6, 16))
            ttk.Button(btns, text="Annuler", command=win.destroy).pack(side="left", padx=6)
            ttk.Button(btns, text="Valider", style="Accent.TButton",
                       command=ok).pack(side="left")
            win.columnconfigure(1, weight=1)
            win.bind("<Return>", lambda _e: ok())
            win.bind("<Escape>", lambda _e: win.destroy())
            win.grab_set()
            self.wait_window(win)
            return out or None

        def on_trip_change(self):
            t = self.trip_var.get().strip()
            p = Path(t).expanduser() if t else None
            self.settings = load_settings(p) if p and p.is_dir() else default_settings()
            self.refresh_days()

        def enabled_devices(self) -> list[tuple[str, str]]:
            """(clé, libellé) des appareils et logiciels cochés qui peuvent
            recevoir des fichiers, plus l'entrée de détection automatique."""
            cfg = self.settings
            out = [(None, "Détection automatique")]
            for k, *_ in DEVICE_CATALOG:
                if cfg["appareils"].get(k) and DEV[k]["folder"]:
                    out.append((k, DEV[k]["label"]))
            for k, *_ in SOFTWARE_CATALOG:
                if cfg["logiciels"].get(k) and SOFT[k]["folder"]:
                    out.append((k, SOFT[k]["label"]))
            return out

        def trip_settings_dialog(self):
            trip = self.trip()
            if not trip:
                return
            cfg = load_settings(trip)
            win = tk.Toplevel(self)
            win.title("Paramètres du voyage")
            win.configure(bg=BG)
            win.transient(self)
            try:
                win.iconphoto(False, self._icon_img)
            except Exception:
                pass

            head = ttk.Frame(win)
            head.grid(row=0, column=0, columnspan=4, sticky="we", padx=16, pady=(14, 6))
            ttk.Label(head, text=trip.name, style="H.TLabel").pack(side="left")
            ttk.Label(head, style="Dim.TLabel",
                      text="   ce qui n’est pas coché n’existe ni à l’ingestion, "
                           "ni dans l’arborescence, ni dans les statistiques"
                      ).pack(side="left")

            info = ttk.Frame(win)
            info.grid(row=1, column=0, columnspan=4, sticky="w", padx=16, pady=(0, 8))
            # ce qui a été saisi à la création du voyage sert de valeur initiale
            if not cfg["infos"].get("debut"):
                d0 = trip_start_date(trip)
                if d0:
                    cfg["infos"]["debut"] = d0.date().isoformat()
            iv = {}
            for col, (key, lbl, w) in enumerate((("nom", "Nom", 20), ("debut", "Début", 11),
                                                 ("fin", "Fin", 11), ("region", "Région", 14),
                                                 ("jours", "Jours", 5))):
                ttk.Label(info, text=lbl, style="Dim.TLabel").grid(row=0, column=col * 2,
                                                                   sticky="w", padx=(0, 5))
                iv[key] = tk.StringVar(value=cfg["infos"].get(key, ""))
                ttk.Entry(info, textvariable=iv[key], width=w).grid(row=0, column=col * 2 + 1,
                                                                     sticky="w", padx=(0, 14))

            # Fin et Jours se déduisent l'un de l'autre : on ne saisit jamais
            # deux fois la même information.
            recalc = {"actif": True}

            def sync_dates(source):
                if not recalc["actif"]:
                    return
                recalc["actif"] = False
                try:
                    if source in ("debut", "fin"):
                        n = jours_entre(iv["debut"].get(), iv["fin"].get())
                        if n:
                            iv["jours"].set(str(n))
                    elif source == "jours":
                        f = fin_depuis(iv["debut"].get(), iv["jours"].get())
                        if f:
                            iv["fin"].set(f)
                finally:
                    recalc["actif"] = True

            for k in ("debut", "fin", "jours"):
                iv[k].trace_add("write", lambda *_a, k=k: sync_dates(k))

            vars_ = {"appareils": {}, "logiciels": {}, "réseaux": {}}
            auto_lbls = {}

            def refresh_preview(*_):
                for cat in vars_:
                    for k, v in vars_[cat].items():
                        cfg[cat][k] = bool(v.get())
                apply_auto_software(cfg)
                for k, v in vars_["logiciels"].items():
                    if SOFT[k]["auto_from"]:
                        v.set(cfg["logiciels"][k])
                        auto_lbls[k].config(
                            text="      activé par " +
                                 ("une Insta360" if k == "studio" else "un drone")
                                 if cfg["logiciels"][k] else "      inactif")
                prev.configure(state="normal")
                prev.delete("1.0", "end")
                prev.insert("1.0", preview_tree(cfg, trip.name))
                prev.configure(state="disabled")

            for col, (cat, titre, catalog, meta) in enumerate((
                    ("appareils", "APPAREILS", DEVICE_CATALOG, DEV),
                    ("logiciels", "LOGICIELS", SOFTWARE_CATALOG, SOFT),
                    ("réseaux", "PUBLICATION", NETWORK_CATALOG, NET))):
                fr = ttk.Frame(win)
                fr.grid(row=2, column=col, sticky="nw", padx=(16, 14), pady=(0, 8))
                ttk.Label(fr, text=titre, style="HCard.TLabel").pack(anchor="w", pady=(0, 4))
                for entry in catalog:
                    k = entry[0]
                    m = meta[k]
                    v = tk.BooleanVar(value=cfg[cat].get(k, False))
                    vars_[cat][k] = v
                    auto = cat == "logiciels" and m.get("auto_from")
                    cb = ttk.Checkbutton(fr, text=m["label"], variable=v,
                                         command=refresh_preview)
                    cb.pack(anchor="w")
                    if auto:
                        cb.state(["disabled"])
                        auto_lbls[k] = ttk.Label(fr, text="", style="Dim.TLabel")
                        auto_lbls[k].pack(anchor="w")
                    elif m.get("role"):
                        ttk.Label(fr, text="      " + m["role"],
                                  style="Dim.TLabel").pack(anchor="w")

            pv = ttk.Frame(win)
            pv.grid(row=2, column=3, sticky="nsew", padx=(0, 16), pady=(0, 8))
            ttk.Label(pv, text="ARBORESCENCE GÉNÉRÉE", style="HCard.TLabel").pack(anchor="w",
                                                                                  pady=(0, 4))
            box = tk.Frame(pv, bg=LINE)
            box.pack(fill="both", expand=True)
            prev = tk.Text(box, width=34, height=20, wrap="none", bd=0, bg=PANEL, fg=FG,
                           highlightthickness=0, font=(MONO, S_SMALL), padx=8, pady=6)
            prev.pack(fill="both", expand=True, padx=1, pady=1)

            # --- presets ---------------------------------------------------- #
            pr = ttk.Frame(win)
            pr.grid(row=3, column=0, columnspan=4, sticky="w", padx=16, pady=(2, 6))
            ttk.Label(pr, text="Preset", style="Dim.TLabel").pack(side="left", padx=(0, 6))
            presets = load_presets()
            pvar = tk.StringVar()
            pcombo = ttk.Combobox(pr, textvariable=pvar, width=26, state="readonly",
                                  font=(F, S_SMALL), values=sorted(presets))
            pcombo.pack(side="left")

            def load_preset():
                data = load_presets().get(pvar.get())
                if not data:
                    return
                for cat in vars_:
                    for k, v in vars_[cat].items():
                        v.set(bool(data.get(cat, {}).get(k, False)))
                refresh_preview()

            def save_preset():
                name = pvar.get().strip()
                if not name:
                    name = simple_prompt(win, "Nom du preset", "Court roadtrip (quelques jours)")
                    if not name:
                        return
                for cat in vars_:
                    for k, v in vars_[cat].items():
                        cfg[cat][k] = bool(v.get())
                data = load_presets()
                data[name] = {c: dict(cfg[c]) for c in ("appareils", "logiciels", "réseaux")}
                save_presets(data)
                pcombo["values"] = sorted(data)
                pvar.set(name)
                self.log(f"Preset « {name} » enregistré.", "ok")

            def delete_preset():
                data = load_presets()
                if pvar.get() in data:
                    del data[pvar.get()]
                    save_presets(data)
                    pcombo["values"] = sorted(data)
                    pvar.set("")

            ttk.Button(pr, text="Charger", command=load_preset).pack(side="left", padx=6)
            ttk.Button(pr, text="Enregistrer…", command=save_preset).pack(side="left")
            ttk.Button(pr, text="Supprimer", command=delete_preset).pack(side="left", padx=6)

            def apply_and_close():
                for cat in vars_:
                    for k, v in vars_[cat].items():
                        cfg[cat][k] = bool(v.get())
                apply_auto_software(cfg)
                cfg["infos"] = {k: v.get().strip() for k, v in iv.items()}
                save_settings(trip, cfg)
                self.settings = cfg
                n = sum(len(checked(cfg, c)) for c in ("appareils", "logiciels", "réseaux"))
                self.log(f"Paramètres enregistrés — {n} éléments actifs.", "ok")
                win.destroy()

            def reset():
                d = default_settings()
                for cat in vars_:
                    for k, v in vars_[cat].items():
                        v.set(d[cat].get(k, False))
                refresh_preview()

            btns = ttk.Frame(win)
            btns.grid(row=4, column=0, columnspan=4, sticky="e", padx=16, pady=(0, 14))
            ttk.Button(btns, text="Valeurs par défaut", command=reset).pack(side="left", padx=6)
            ttk.Button(btns, text="Annuler", command=win.destroy).pack(side="left", padx=6)
            ttk.Button(btns, text="Valider", style="Accent.TButton",
                       command=apply_and_close).pack(side="left")
            win.columnconfigure(3, weight=1)
            win.rowconfigure(2, weight=1)
            refresh_preview()
            win.bind("<Escape>", lambda _e: win.destroy())
            win.grab_set()
            self.wait_window(win)

        def refresh_days(self):
            t = self.trip_var.get().strip()
            days = []
            if t:
                p = Path(t).expanduser()
                if p.is_dir():
                    days = sorted(d.name for d in p.iterdir()
                                  if d.is_dir() and re.match(r"\d+_\d{4}-\d{2}-\d{2}", d.name))
            for combo, var in ((self.geo_combo, self.geo_day), (self.j_combo, self.j_day)):
                combo["values"] = days
                if days and var.get() not in days:
                    var.set(days[-1])

        def day_path(self, name: str) -> Path | None:
            t = self.trip_var.get().strip()
            if not t or not name:
                messagebox.showwarning(APP_NAME, "Choisissez une journée.")
                return None
            return Path(t).expanduser() / name

        def open_day_folder(self):
            p = self.day_path(self.j_day.get())
            if not p or not p.is_dir():
                return
            try:
                if sys.platform == "darwin":
                    subprocess.run(["open", str(p)])
                elif sys.platform.startswith("win"):
                    subprocess.run(["explorer", str(p)])
                else:
                    subprocess.run(["xdg-open", str(p)])
            except Exception as e:
                self.log(f"Impossible d’ouvrir le dossier : {e}", "warn")

        # -- actions ---------------------------------------------------------- #
        def do_analyse(self):
            trip = self.trip()
            if not trip:
                return
            if not self.sources:
                messagebox.showwarning(APP_NAME, "Ajoutez au moins une source.")
                return
            self.bg(lambda: self._analyse(trip))

        def _analyse(self, trip: Path):
            q = self.queue
            q.put(("status", "Lecture des sources…"))
            log_event(f"analyse : {len(self.sources)} sources, voyage {trip.name}")
            for sc in self.sources:
                log_event(f"  source {sc.get('label') or 'auto'} :: {sc['path']}")
            files = scan_sources(self.sources)
            log_event(f"  {len(files)} fichiers médias trouvés")
            if not files:
                q.put(("log", ("Aucun fichier média trouvé dans les sources.", "warn")))
                return
            q.put(("status", f"{len(files)} fichiers — lecture des métadonnées…"))
            global exif_map_global
            exif_map_global = exif_batch([p for p, _ in files]) if have_exiftool() else {}
            plan, per_day, per_kind, origin, dups, outside = plan_ingest(
                files, trip, self.daystart.get(), self.settings,
                self.skipraw.get(), self.skipproxy.get())
            self.plan = (plan, trip)
            log_event(f"  plan : {len(plan)} à copier, {dups} doublons, "
                      f"{len(outside)} hors voyage, "
                      f"{len(getattr(plan_ingest, 'rejected', []))} refusés, "
                      f"{len(getattr(plan_ingest, 'raw_skipped', []))} RAW, "
                      f"{len(getattr(plan_ingest, 'proxy_skipped', []))} annexes")
            log_event("  dates : " + ", ".join(f"{k} {v}" for k, v in origin.items()))

            def fill():
                devs = []
                for k, *_ in DEVICE_CATALOG:
                    if self.settings["appareils"].get(k) and DEV[k]["folder"]:
                        devs.append(k)
                for k, *_ in SOFTWARE_CATALOG:
                    if self.settings["logiciels"].get(k) and SOFT[k]["folder"]:
                        devs.append(k)
                seen = {d for c in per_day.values() for d in c}
                devs += sorted(d for d in seen if d not in devs)
                cols = ["jour"] + devs + ["total"]
                self.tree_day.configure(columns=cols)
                for c in cols:
                    lbl = ("Jour" if c == "jour" else
                           "Total" if c == "total" else short_label(c))
                    self.tree_day.heading(c, text=lbl)
                    self.tree_day.column(c, width=118 if c == "jour" else 76,
                                         minwidth=44, stretch=True,
                                         anchor="w" if c == "jour" else "center")
                self.tree_day.delete(*self.tree_day.get_children())
                tot = Counter()
                for day in sorted(per_day):
                    c = per_day[day]
                    tot.update(c)
                    self.tree_day.insert("", "end", values=[day] +
                                         [c.get(d, "") or "" for d in devs] +
                                         [sum(c.values())])
                if per_day:
                    self.tree_day.insert("", "end", tags=("total",),
                                         values=["TOTAL"] +
                                         [tot.get(d, "") or "" for d in devs] +
                                         [sum(tot.values())])
                for kind, lbl in (("PHOTO", "dont photos"), ("VIDEO", "dont vidéos"),
                                  ("TRACE", "dont traces")):
                    row = [per_kind.get((d, kind), 0) for d in devs]
                    if not any(row):
                        continue
                    self.tree_day.insert("", "end", tags=("kind",),
                                         values=[lbl] + [n or "" for n in row]
                                         + [sum(row)])
                bits = [f"{len(plan)} à copier"]
                if dups:
                    bits.append(f"{dups} déjà présents")
                if outside:
                    bits.append(f"{len(outside)} hors voyage")
                nraw2 = len(getattr(plan_ingest, "raw_skipped", []))
                if nraw2:
                    bits.append(f"{nraw2} RAW écartés")
                npx = len(getattr(plan_ingest, "proxy_skipped", []))
                if npx:
                    bits.append(f"{npx} annexes écartés")
                nrej = len(getattr(plan_ingest, "rejected", []))
                if nrej:
                    bits.append(f"{nrej} refusé" + ("s" if nrej > 1 else ""))
                self.sum_lbl.config(text="  ·  ".join(bits))
            q.put(("call", fill))
            q.put(("log", ("Dates : " + ", ".join(f"{k} {v}" for k, v in origin.items()),
                           "dim")))
            if outside:
                ex = outside[0]
                q.put(("log", (f"{len(outside)} fichiers antérieurs au jour 1 — "
                               f"ex. {ex[0].name} daté {ex[1]:%Y-%m-%d %H:%M}. "
                               f"Horloge désynchronisée ?", "warn")))
            nraw = len(getattr(plan_ingest, "raw_skipped", []))
            if nraw:
                q.put(("log", (f"{nraw} fichiers RAW/DNG écartés à votre demande.", "dim")))
            npx = len(getattr(plan_ingest, "proxy_skipped", []))
            if npx:
                q.put(("log", (f"{npx} fichiers annexes écartés (.lrv, .srt, .thm).",
                               "dim")))
            mism = getattr(plan_ingest, "mismatch", {})
            for forced_dev, exemples in sorted(mism.items()):
                noms = ", ".join(p.name for p in exemples[:3])
                suite = f" (+{len(exemples) - 3})" if len(exemples) > 3 else ""
                q.put(("log", (f"{len(exemples)} fichiers rangés dans "
                               f"« {full_label(forced_dev)} » portent les marques d’un "
                               f"autre appareil : {noms}{suite}. C’est votre choix de "
                               f"source qui l’emporte — vérifiez s’il était voulu.",
                               "warn")))
            rej = getattr(plan_ingest, "rejected", [])
            if rej:
                noms = ", ".join(p.name for p in rej[:6])
                suite = f" (+{len(rej) - 6})" if len(rej) > 6 else ""
                q.put(("log", (f"{len(rej)} fichier" + ("s" if len(rej) > 1 else "") +
                               " REFUSÉ" + ("S" if len(rej) > 1 else "") +
                               ", non attribuable" + ("s" if len(rej) > 1 else "") + " à un "
                               f"appareil du voyage : {noms}{suite}. Rien n’a été "
                               f"copié pour eux. Précisez l’appareil sur cette source, "
                               f"ou cochez-le dans les paramètres du voyage.", "warn")))
            for p, span in getattr(plan_ingest, "multiday", []):
                q.put(("log", (f"{p.name} couvre du {span[0]:%d.%m} au {span[1]:%d.%m} : "
                               f"il est rangé au premier jour. Pour que chaque journée "
                               f"ait son carnet, exportez une route par jour depuis "
                               f"Geo-Log.", "warn")))
            nx = len(getattr(scan_sources, "excluded", []))
            if nx:
                q.put(("log", (f"{nx} fichiers ignorés dans des dossiers _Rejected "
                               f"ou corbeille.", "dim")))
            q.put(("log", (f"{len(plan)} fichiers prêts.", "ok")))

        def do_import(self):
            if not self.plan:
                return
            plan, trip = self.plan
            self.bg(lambda: self._import(plan, trip))

        def _import(self, plan, trip: Path):
            q = self.queue
            days = set()
            for i, (src, dest, day_key, _) in enumerate(plan, 1):
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dest)
                days.add(day_key)
                if i % 10 == 0 or i == len(plan):
                    q.put(("progress", 100 * i / len(plan)))
                    q.put(("status", f"{i}/{len(plan)}"))
            cfg = self.settings
            nets = checked(cfg, "réseaux")
            for d in days:
                for folder in sorted({NET[k]["folder"] for k in nets}):
                    (trip / d / PUBLICATION_DIR / folder).mkdir(
                        parents=True, exist_ok=True)
            md = trip / "trip.md"
            if not md.exists():
                md.write_text(TRIP_MD.format(slug=trip.name,
                                             start=trip_start_date(trip).date().isoformat()),
                              encoding="utf-8")
                q.put(("log", ("Manifeste trip.md créé.", "dim")))
            log_event(f"import terminé : {len(plan)} fichiers copiés")
            q.put(("log", (f"{len(plan)} fichiers copiés.", "ok")))
            q.put(("log", ("Cartes intactes — ne les formatez qu’après sauvegarde "
                           "sur le SSD.", "dim")))
            q.put(("call", self.refresh_days))
            self.plan = None
            q.put(("call", lambda: self.sum_lbl.config(text="")))

        def _geo_prepare(self):
            day = self.day_path(self.geo_day.get())
            if not day:
                return None
            track = read_track(find_day_dir(day, "garmin")
                               or day / device_dirname("garmin"))
            if not track:
                self.log(f"Aucune trace GPX dans {day.name}/{device_dirname('garmin')}/ "
                         f"— ajoutez l’export Garmin comme source et réimportez.", "warn")
                return None
            files = list(walk_day_media(day, TAGGABLE_EXT))
            return day, track, files

        def _file_times(self, files):
            out = {}
            if have_exiftool():
                for p, it in exif_batch(files).items():
                    dt = parse_exif_date(it)
                    out[p] = (dt.replace(tzinfo=timezone.utc) if dt
                              else datetime.fromtimestamp(p.stat().st_mtime, timezone.utc),
                              it.get("GPSLatitude") is not None)
            for p in files:
                out.setdefault(p, (datetime.fromtimestamp(p.stat().st_mtime, timezone.utc),
                                   False))
            return out

        def do_autooffset(self):
            prep = self._geo_prepare()
            if not prep:
                return
            day, track, files = prep

            def work():
                meta = self._file_times(files)
                tol = self.geo_tol.get()

                def score(off):
                    n, gaps = 0, []
                    for p in files:
                        dt, tagged = meta[p]
                        if tagged:
                            continue
                        pt, gap = nearest_point(track, dt + timedelta(seconds=off), tol)
                        if pt:
                            n += 1
                            gaps.append(gap)
                    return n, (sorted(gaps)[len(gaps) // 2] if gaps else 1e9)

                base = score(0)[0]
                cand = []
                for o in range(-7200, 7201, 30):
                    n, med = score(o)
                    cand.append((-n, med, abs(o), o))
                cand.sort()
                n_best, off_best = -cand[0][0], cand[0][3]
                if n_best > base:
                    h, rem = divmod(abs(off_best), 3600)
                    mm, ss = divmod(rem, 60)
                    sign = "+" if off_best >= 0 else "-"
                    self.queue.put(("call", lambda: self.geo_off.set(off_best)))
                    self.queue.put(("log", (
                        f"Décalage proposé {off_best:+d} s ({sign}{h}h{mm:02d}m{ss:02d}s) — "
                        f"{n_best} fichiers dans la trace contre {base}. Un décalage "
                        f"proche d’un nombre entier d’heures signale un fuseau, pas une "
                        f"dérive : vérifiez une photo dont vous savez où elle a été prise.",
                        "warn")))
                else:
                    self.queue.put(("log", (
                        "Aucune correction n’améliore le résultat : les horloges sont "
                        "d’accord.", "ok")))
            self.bg(work)

        def do_geo(self, write: bool):
            prep = self._geo_prepare()
            if not prep:
                return
            day, track, files = prep
            if not files:
                self.log("Aucun fichier à géolocaliser dans cette journée.", "warn")
                return
            if write and not have_exiftool():
                messagebox.showerror(APP_NAME,
                                     "exiftool est nécessaire pour écrire les coordonnées.")
                return

            def work():
                meta = self._file_times(files)
                off, tol = self.geo_off.get(), self.geo_tol.get()
                inside = already = 0
                gaps = []
                for p in files:
                    dt, tagged = meta[p]
                    if tagged:
                        already += 1
                        continue
                    pt, gap = nearest_point(track, dt + timedelta(seconds=off), tol)
                    if pt:
                        inside += 1
                        gaps.append(gap)
                outside = len(files) - inside - already
                med = sorted(gaps)[len(gaps) // 2] if gaps else None
                lines = [
                    f"Trace   {len(track)} points   "
                    f"{track[0][0]:%Y-%m-%d %H:%M} → {track[-1][0]:%H:%M} UTC",
                    "",
                    f"Fichiers          {len(files)}",
                    f"Dans la trace     {inside}",
                    f"Hors plage        {outside}",
                    f"Déjà géotagués    {already}",
                ]
                if med is not None:
                    lines.append(f"Écart médian      {med:.0f} s")
                if outside:
                    lines += ["", "Beaucoup de fichiers hors plage ? "
                                  "Essayez « Détecter le décalage »."]
                self.queue.put(("call", lambda: (
                    self.geo_out.delete("1.0", "end"),
                    self.geo_out.insert("1.0", "\n".join(lines) + "\n"))))
                if not write:
                    return
                gpx = sorted((find_day_dir(day, "garmin")
                              or day / device_dirname("garmin")).glob("*.gpx"))
                cmd = ([exiftool_path(), "-overwrite_original", "-api", "QuickTimeUTC",
                        f"-geosync={off}", "-api", f"GeoMaxIntSecs={tol}"]
                       + [f"-geotag={g}" for g in gpx]
                       + ["-if", "not $GPSLatitude"] + [str(p) for p in files])
                res = subprocess.run(cmd, capture_output=True, text=True)
                msg = (res.stdout or res.stderr).strip().splitlines()[-3:]
                self.queue.put(("log", ("exiftool : " + " | ".join(msg), "ok")))
            self.bg(work)

        def do_journal(self, write: bool):
            day = self.day_path(self.j_day.get())
            if not day or not day.is_dir():
                return

            def work():
                text, st = build_journal(day, self.j_win.get())
                self.queue.put(("call", lambda: (
                    self.j_out.delete("1.0", "end"), self.j_out.insert("1.0", text))))
                if write:
                    out = day / "journal.md"
                    if out.exists():
                        out.with_suffix(".md.bak").write_text(
                            out.read_text(encoding="utf-8"), encoding="utf-8")
                        self.queue.put(("log", ("Ancien journal sauvegardé en .md.bak",
                                                "dim")))
                    out.write_text(text, encoding="utf-8")
                    self.queue.put(("log", (f"Écrit : {out.name}", "ok")))
                self.queue.put(("log", (
                    f"{st['waypoints']} waypoints · {st['media']} médias · "
                    f"{st['orphans']} non rattachés"
                    + (f" · {st['km']:.0f} km" if st["km"] else ""), "dim")))
            self.bg(work)

    App().mainloop()
    return 0


if __name__ == "__main__":
    sys.exit(run_gui())
