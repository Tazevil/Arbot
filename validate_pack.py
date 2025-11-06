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
ZONES = {0: "CHANTIER", 1: "PLAN", 2: "SDB", 3: "WC"}
CATS  = {0: "VUE GENERALE", 1: "PLOMBERIE", 2: "BAIGNOIRE", 3: "CARRELAGE", 4: "FENETRE",
         5: "PLAFOND", 6: "PLATERIE", 7: "SANITAIRE", 8: "PLACARD"}
SPECS_ALLOWED = {"PAN","GEN","DET","MAC","MGM","MGS","MGP","MGB","DEG"}
EXT_ALLOWED = {"jpg","jpeg","png","webp","tiff"}

# Optionnel: mapping numérique pour Id_Spec (non fourni) → UNKNOWN par défaut
SPEC2ID = {s: "UNKNOWN" for s in SPECS_ALLOWED}

# ----- Regex (sensibles à la casse: majuscules attendues)
RX_A = re.compile(r'^(\d{4})_([A-Z0-9]+(?:-[A-Z0-9]+)*)_([A-Z0-9]{2,6})_(\d{8})\.(jpg|jpeg|png|webp|tiff)$')
RX_B = re.compile(r'^(\d{4})_([A-Z0-9]+(?:-[A-Z0-9]+)*)_(\d{4})\.(jpg|jpeg|png|webp|tiff)$')
RX_C = re.compile(r'^(\d{4})_([A-Z0-9]+(?:-[A-Z0-9]+)*)_([A-Z0-9]{2,6})\.(jpg|jpeg|png|webp|tiff)$')

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
    """Retourne dict normalisé ou lève ValueError détaillé."""
    name = fname
    lowext = fname.split('.')[-1].lower()
    if lowext not in EXT_ALLOWED:
        raise ValueError(f"extension interdite: .{lowext}")

    mA = RX_A.match(fname)
    mB = RX_B.match(fname)
    mC = RX_C.match(fname)

    if mA:
        id_file   = int(mA.group(1))
        detail    = mA.group(2)
        spec      = mA.group(3)
        date      = mA.group(4)
        ext       = mA.group(5).lower()
        id_zone, id_cat, id_image = decode_id_file(id_file)
        if id_zone != 0:
            raise ValueError("Cas A attendu uniquement si Id_Zone=0 (CHANTIER)")
        if spec not in SPECS_ALLOWED:
            raise ValueError(f"Spec inconnue pour cas A: {spec}")
        return {
            "case": "A",
            "id_file": id_file, "Id_File_str": f"{id_file}",
            "Id_Zone": id_zone, "Id_Cat": id_cat, "id_image": id_image,
            "detail": detail, "Spec": spec, "Id_Spec": SPEC2ID.get(spec, "UNKNOWN"),
            "ext": ext, "date_yyyymmdd": date, "year": "",
            "classification": classify(True)
        }

    if mB:
        id_file   = int(mB.group(1))
        detail    = mB.group(2)
        year      = mB.group(3)
        ext       = mB.group(4).lower() if hasattr(mB, "group") else lowext
        id_zone, id_cat, id_image = decode_id_file(id_file)
        if id_zone != 1:
            raise ValueError("Cas B attendu uniquement si Id_Zone=1 (PLAN)")
        # year → id_spec selon règle
        return {
            "case": "B",
            "id_file": id_file, "Id_File_str": f"{id_file}",
            "Id_Zone": id_zone, "Id_Cat": id_cat, "id_image": id_image,
            "detail": detail, "Spec": year, "Id_Spec": year,
            "ext": ext, "date_yyyymmdd": "", "year": year,
            "classification": classify(False)
        }

    if mC:
        id_file   = int(mC.group(1))
        detail    = mC.group(2)
        spec      = mC.group(3)
        ext       = mC.group(4).lower()
        id_zone, id_cat, id_image = decode_id_file(id_file)
        if id_zone in (0,1):
            raise ValueError("Cas C interdit pour Id_Zone in {0,1}")
        if spec not in SPECS_ALLOWED:
            raise ValueError(f"Spec inconnue pour cas C: {spec}")
        return {
            "case": "C",
            "id_file": id_file, "Id_File_str": f"{id_file}",
            "Id_Zone": id_zone, "Id_Cat": id_cat, "id_image": id_image,
            "detail": detail, "Spec": spec, "Id_Spec": SPEC2ID.get(spec, "UNKNOWN"),
            "ext": ext, "date_yyyymmdd": "", "year": "",
            "classification": classify(False)
        }

    raise ValueError("Aucun pattern ne correspond (A/B/C)")

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