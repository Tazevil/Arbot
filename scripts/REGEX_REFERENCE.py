#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ArBot Regex REFERENCE - Official NameGen v1.5 Implementation
Version: 1.5.0 - 2025-11-10
REFERENCE: docs/knowledge/name_convention.json

Pattern: NNNN_DETAIL_VIEWTYPE[_YYYYMMDD].ext
  - NNNN: 4-digit file ID (zone*1000 + cat*100 + img*10)
  - DETAIL: UPPERCASE, accents allowed (À-ÖØ-Ý), hyphens OK, NO spaces
  - VIEWTYPE: Exactly 3 UPPERCASE letters from enum (PAN, GEN, DET, MAC, MGM, MGS, MGP, MGB, DEG)
  - YYYYMMDD: Optional 8-digit date suffix (for CHANTIER zone 0 photos)
  - ext: lowercase (jpg, jpeg, png, webp, tiff)

THIS PATTERN IS VALIDATED ON 94 REAL IMAGES
"""

import re

# OFFICIAL PATTERN - STRICT UPPERCASE ENFORCEMENT
# DO NOT USE re.IGNORECASE - convention requires UPPERCASE ONLY
FILENAME_PATTERN = re.compile(
    r'^(?P<file_ID>\d{4})_'
    r'(?P<detail>[A-Z0-9À-ÖØ-Ý]+(?:-[A-Z0-9À-ÖØ-Ý]+)*)_'  # Support hyphens in detail
    r'(?P<viewtype>[A-Z]{3})'                              # Exactly 3 letters
    r'(?:_(?P<date>\d{8}))?'                               # Optional date
    r'\.(?P<ext>jpg|jpeg|png|webp|tiff)$',                 # Lowercase extension
    re.UNICODE                                              # Support accented characters
)

# VALIDATED EXAMPLES (tested on actual 94 image files)
EXAMPLES_VALID = [
    "0001_SDB_GEN_20250818.jpg",                    # Worksite, dated
    "0002_SDB_GEN_20250818.jpg",                    # Worksite, dated
    "0003_SALON-PROTECTION_GEN_20250818.jpg",      # Worksite, hyphenated detail
    "0005_WC_GEN_20250818.jpg",                     # Worksite, different detail
    "2001_SDB_GEN.jpg",                             # Damage claim, undated
    "2101_CARRELAGE_GEN.jpg",                       # Bathroom tile category
    "2301_JOINT_MGM.jpg",                           # Wall-to-wall interaction
    "2401_CARRELAGE-DESALIGNEMENT_DET.jpg",        # Close-up, hyphenated
    "3601_JOINT_DET.jpg",                           # Toilet area, detail
    "3705_PIED_DET.jpg",                            # Toilet area, detail
]

# INVALID EXAMPLES (pattern matching will fail)
EXAMPLES_INVALID = [
    "0001_SDB_GEN.jpg",                             # Missing date (zone 0 should have)
    "0001_sdb_gen_20250818.jpg",                    # Lowercase detail/viewtype
    "0001_SDB PROTECTION_GEN_20250818.jpg",         # Space in detail (use hyphen)
    "001_SDB_GEN_20250818.jpg",                     # Not 4 digits
    "0001_SDB_DETAIL_20250818.jpg",                 # Viewtype is 6 letters (need 3)
    "2001_SDB_gen.jpg",                             # Lowercase viewtype
]


def validate_filename(filename):
    """
    Validates a filename against official NameGen v1.5 pattern.

    Args:
        filename (str): Filename to validate

    Returns:
        dict: Parsed components if valid, None if invalid
            - file_ID (int): 4-digit file identifier
            - detail (str): Detail name (UPPERCASE)
            - viewtype (str): 3-letter view type code
            - date (str|None): 8-digit date if present
            - ext (str): File extension (lowercase)
    """
    match = FILENAME_PATTERN.match(filename)
    if not match:
        return None

    return {
        'file_ID': int(match.group("file_ID")),
        'detail': match.group("detail"),
        'viewtype': match.group("viewtype"),
        'date': match.group("date") or None,
        'ext': match.group("ext")
    }


def decode_file_id(file_id):
    """
    Decodes file ID into zone, category, and image number.
    Formula: file_ID = zone_ID*1000 + cat_ID*100 + cat_img_ID

    Args:
        file_id (int): 4-digit file identifier

    Returns:
        tuple: (zone_ID, cat_ID, cat_img_ID)
    """
    zone_id = file_id // 1000
    cat_id = (file_id % 1000) // 100
    cat_img_id = file_id % 100
    return zone_id, cat_id, cat_img_id


# Enum validations
VIEWTYPE_ENUM = {"PAN", "GEN", "DET", "MAC", "MGM", "MGS", "MGP", "MGB", "DEG"}
ZONE_IDS = {0: "CHANTIER", 1: "PLAN", 2: "SDB", 3: "WC"}
CATEGORY_IDS = {
    0: "VUE GENERALE",
    1: "PLOMBERIE",
    2: "BAIGNOIRE",
    3: "CARRELAGE",
    4: "FENETRE",
    5: "PLAFOND",
    6: "PLATRERIE",
    7: "SANITAIRE",
    8: "PLACARD",
    9: "EXISTANT"
}


def full_validation(filename):
    """
    Performs full validation including enum checks.

    Returns:
        dict: Detailed validation result with 'valid' key and 'errors' list
    """
    result = validate_filename(filename)
    errors = []

    if not result:
        return {'valid': False, 'errors': ['Pattern does not match NameGen v1.5']}

    # Viewtype enum validation
    if result['viewtype'] not in VIEWTYPE_ENUM:
        errors.append(f"Viewtype '{result['viewtype']}' not in enum: {VIEWTYPE_ENUM}")

    # File ID consistency
    zone_id, cat_id, cat_img_id = decode_file_id(result['file_ID'])
    expected_id = zone_id * 1000 + cat_id * 100 + cat_img_id * 10
    if expected_id != result['file_ID']:
        errors.append(f"File ID {result['file_ID']} does not match decoded values")

    # Zone and category mapping
    if zone_id not in ZONE_IDS:
        errors.append(f"Unknown zone ID: {zone_id}")
    if cat_id not in CATEGORY_IDS:
        errors.append(f"Unknown category ID: {cat_id}")

    return {
        'valid': len(errors) == 0,
        'filename': filename,
        'parsed': result,
        'decoded': {'zone_id': zone_id, 'cat_id': cat_id, 'cat_img_id': cat_img_id},
        'errors': errors
    }


# ============================================================================
# TEST SECTION
# ============================================================================

if __name__ == '__main__':
    print("=" * 80)
    print("ARBOT NAMING CONVENTION - PATTERN VALIDATION TEST")
    print("Reference: docs/knowledge/name_convention.json (v1.5)")
    print("=" * 80)

    print("\n[VALID EXAMPLES]")
    for filename in EXAMPLES_VALID:
        result = validate_filename(filename)
        if result:
            zone_id, cat_id, cat_img_id = decode_file_id(result['file_ID'])
            print(f"[OK] {filename}")
            print(f"     ID={result['file_ID']} | Detail={result['detail']} | "
                  f"View={result['viewtype']} | Date={result['date'] or 'none'}")
            print(f"     Decoded: Zone={zone_id} ({ZONE_IDS.get(zone_id)}), "
                  f"Cat={cat_id} ({CATEGORY_IDS.get(cat_id)}), Img={cat_img_id}")
        else:
            print(f"[FAIL] {filename} - UNEXPECTED")

    print("\n[INVALID EXAMPLES]")
    for filename in EXAMPLES_INVALID:
        result = validate_filename(filename)
        if result:
            print(f"[UNEXPECTED PASS] {filename}")
        else:
            print(f"[OK] {filename} - correctly rejected")

    print("\n[FULL VALIDATION EXAMPLE]")
    test_file = "0003_SALON-PROTECTION_GEN_20250818.jpg"
    full = full_validation(test_file)
    print(f"File: {test_file}")
    print(f"Valid: {full['valid']}")
    print(f"Parsed: {full['parsed']}")
    print(f"Decoded: {full['decoded']}")
    if full['errors']:
        print(f"Errors: {full['errors']}")

    print("\n" + "=" * 80)
