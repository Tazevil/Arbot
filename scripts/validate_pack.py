#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ArBot · Validate & Index Images
Version: 1.0.0  |  Date: 2025-11-06

Fonctions:
- Validation des filenames selon 3 cas (A/B/C) et contraintes communes.
- Décodage Id_File → Id_Zone, Id_Cat, id_image.
- Classification: "chantier" si yyyyMMdd avant l'extension, sinon "sinistre".
- Vérifs: regex par cas, extension, cohérence Id_File, unicité id_image par (Id_Zone, Id_Cat) et unicité Id_File.
- Génère:
  - csv: images_sidecar.csv
  - json: images_db.json (URLs RAW GitHub)

Usage (exemple):
  python validate_pack.py --images ./images --out ./json \
    --owner Tazevil --repo ArBot-MiniDB --branch main
"""

import argparse, csv, json, re, sys
from pathlib import Path
from collections import defaultdict

# ----- Config dictionnaires (donnés par l'utilisateur)
# REFERENCE: docs/knowledge/name_convention.json (v1.5, 2025-10-15)
ZONES = {0: "CHANTIER", 1: "PLAN", 2: "SDB", 3: "WC"}
CATS  = {0: "VUE GENERALE", 1: "PLOMBERIE", 2: "BAIGNOIRE", 3: "CARRELAGE", 4: "FENETRE",
         5: "PLAFOND", 6: "PLATRERIE", 7: "SANITAIRE", 8: "PLACARD", 9: "EXISTANT"}
SPECS_ALLOWED = {"PAN","GEN","DET","MAC","MGM","MGS","MGP","MGB","DEG"}
EXT_ALLOWED = {"jpg","jpeg","png","webp","tiff"}

# Optionnel: mapping numérique pour Id_Spec (non fourni) → UNKNOWN par défaut
SPEC2ID = {s: "UNKNOWN" for s in SPECS_ALLOWED}

# ----- Regex (Official NameGen v1.5 pattern - sensibles à la casse: majuscules attendues)
# REFERENCE: docs/knowledge/name_convention.json
# Pattern: NNNN_DETAIL_VIEWTYPE[_YYYYMMDD].ext
# - NNNN: 4 digits (file ID = zone*1000 + cat*100 + img*10)
# - DETAIL: UPPERCASE, accents allowed (À-ÖØ-Ý), hyphens OK, NO spaces
# - VIEWTYPE: EXACTLY 3 UPPERCASE letters (PAN, GEN, DET, MAC, MGM, MGS, MGP, MGB, DEG)
# - YYYYMMDD: Optional 8-digit date suffix (for CHANTIER zone 0 photos)
# - ext: lowercase (jpg, jpeg, png, webp, tiff)
RX_OFFICIAL = re.compile(
    r'^(?P<file_ID>\d{4})_'
    r'(?P<detail>[A-Z0-9À-ÖØ-Ý]+(?:-[A-Z0-9À-ÖØ-Ý]+)*)_'
    r'(?P<viewtype>[A-Z]{3})'
    r'(?:_(?P<date>\d{8}))?'
    r'\.(?P<ext>jpg|jpeg|png|webp|tiff)$',
    re.UNICODE
)

def decode_id_file(id_file: int):
    id_zone = id_file // 1000
    id_cat  = (id_file // 100) - 10 * (id_file // 1000)
    id_image = id_file - 100 * (id_file // 100)
    return id_zone, id_cat, id_image

def build_raw_url(owner, repo, branch, fname):
    return f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/images/{fname}"

def classify(has_date: bool) -> str:
    return "chantier" if has_date else "sinistre"

def parse_filename(fname: str):
    """Retourne dict normalisé ou lève ValueError détaillé.
    Utilise pattern officiel NameGen v1.5 (NNNN_DETAIL_VIEWTYPE[_YYYYMMDD].ext)
    """
    name = fname
    lowext = fname.split('.')[-1].lower()
    if lowext not in EXT_ALLOWED:
        raise ValueError(f"extension interdite: .{lowext}")

    m = RX_OFFICIAL.match(fname)
    if not m:
        raise ValueError("Fichier n'adhère pas au pattern officiel NameGen v1.5: NNNN_DETAIL_VIEWTYPE[_YYYYMMDD].ext")

    gd = m.groupdict()
    id_file = int(gd["file_ID"])
    detail = gd["detail"]
    viewtype = gd["viewtype"]
    date = gd.get("date") or ""
    ext = gd["ext"].lower()

    if viewtype not in SPECS_ALLOWED:
        raise ValueError(f"Viewtype '{viewtype}' not in approved enum: {SPECS_ALLOWED}")

    id_zone, id_cat, id_image = decode_id_file(id_file)

    return {
        "id_file": id_file,
        "Id_File_str": gd["file_ID"],  # garde le padding "0001"
        "Id_Zone": id_zone,
        "Id_Cat": id_cat,
        "id_image": id_image,
        "detail": detail,
        "Spec": viewtype,
        "Id_Spec": SPEC2ID.get(viewtype, "UNKNOWN"),
        "ext": ext,
        "date_yyyymmdd": date,
        "year": "",
        "classification": classify(bool(date))
    }

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--images", required=True, help="dossier des images")
    ap.add_argument("--out", required=True, help="dossier sortie pour CSV/JSON")
    ap.add_argument("--owner", required=True, help="GitHub owner (ex: Tazevil)")
    ap.add_argument("--repo", required=True, help="GitHub repo (ex: ArBot-MiniDB)")
    ap.add_argument("--branch", default="main")
    ap.add_argument("--strict", action="store_true", help="stoppe au premier échec")
    args = ap.parse_args()

    images_dir = Path(args.images)
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    rows = []
    items = []
    seen_idfile = set()
    seen_per_cat = defaultdict(set)  # key=(Id_Zone, Id_Cat) -> set(id_image)
    errors = []

    for p in sorted(images_dir.iterdir()):
        if not p.is_file():
            continue
        try:
            parsed = parse_filename(p.name)
            id_zone, id_cat, id_image = parsed["Id_Zone"], parsed["Id_Cat"], parsed["id_image"]
            id_file = parsed["id_file"]

            # Vérifs communes
            # 1) id_image 00..99
            if not (0 <= id_image <= 99):
                raise ValueError(f"id_image hors plage 00..99: {id_image}")

            # 2) Cohérence formule
            expect = id_zone*1000 + id_cat*100 + id_image
            if expect != id_file:
                raise ValueError(f"Incohérence Id_File: attendu {expect}, obtenu {id_file}")

            # 3) Unicité par (Id_Zone, Id_Cat) pour id_image
            key = (id_zone, id_cat)
            if id_image in seen_per_cat[key]:
                raise ValueError(f"Duplicat id_image {id_image:02d} pour (Id_Zone={id_zone}, Id_Cat={id_cat})")
            seen_per_cat[key].add(id_image)

            # 4) Unicité Id_File
            if id_file in seen_idfile:
                raise ValueError(f"Duplicat Id_File {id_file}")
            seen_idfile.add(id_file)

            zone_label = ZONES.get(id_zone, f"ZONE_{id_zone}")
            cat_label  = CATS.get(id_cat, f"CAT_{id_cat}")
            url = build_raw_url(args.owner, args.repo, args.branch, p.name)

            # Sidecar CSV row
            rows.append({
                "filename": p.name,
                "Zone": zone_label,
                "Id_Zone": id_zone,
                "Cat": cat_label,
                "Id_Cat": id_cat,
                "id_image": id_image,
                "detail": parsed["detail"],
                "Spec": parsed["Spec"],
                "Id_Spec": parsed["Id_Spec"],
                "ext": parsed["ext"],
                "Id_File": id_file,
                "Id_File_str": parsed["Id_File_str"],
                "notes": f"classification={parsed['classification']}",
                "date_yyyymmdd": parsed["date_yyyymmdd"],
                "year": parsed["year"]
            })

            # images_db.json item
            items.append({
                "id": f"{id_file:04d}",
                "title": f"{cat_label.title()} · {parsed['detail'].replace('-', ' ')} · {parsed['Spec']}",
                "url": url,
                "tags": [zone_label.lower(), cat_label.lower(), parsed["detail"].lower(), parsed["Spec"].lower()],
                "classification": parsed["classification"]
            })

        except Exception as e:
            msg = f"{p.name}: {e}"
            if args.strict:
                print(msg)
                sys.exit(1)
            errors.append(msg)

    # Ecriture CSV
    csv_path = out_dir / "images_sidecar.csv"
    fieldnames = ['filename','Zone','Id_Zone','Cat','Id_Cat','id_image','detail','Spec','Id_Spec',
                  'ext','Id_File','Id_File_str','notes','date_yyyymmdd','year']
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in rows:
            # règles: date requis si Id_Zone=0, year requis si Id_Zone=1
            if r["Id_Zone"]==0 and not r["date_yyyymmdd"]:
                errors.append(f"{r['filename']}: date_yyyymmdd requis pour Id_Zone=0")
            if r["Id_Zone"]==1 and not r["year"]:
                errors.append(f"{r['filename']}: year requis pour Id_Zone=1")
            w.writerow(r)

    # Ecriture JSON
    json_path = out_dir / "images_db.json"
    payload = {
        "db_name": "ArBotMiniDB_Auto",
        "created_at": __import__("datetime").datetime.utcnow().strftime("%Y-%m-%d"),
        "count": len(items),
        "items": items
    }
    with json_path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    # Rapport
    print(f"[OK] CSV: {csv_path}")
    print(f"[OK] JSON: {json_path}")
    if errors:
        print("\n[WARN] Incidents détectés:")
        for e in errors:
            print(" -", e)
        sys.exit(2)

if __name__ == "__main__":
    main()