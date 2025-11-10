#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ArBot Image Validation Script
Validates all images in the images/ folder against naming convention v1.5

Usage:
  python validate_images.py [--images ./images] [--output ./report.json]
"""

import os
import re
import json
import argparse
from pathlib import Path
from collections import defaultdict
from datetime import datetime

# Official NameGen v1.5 pattern
PATTERN = re.compile(
    r'^(?P<file_ID>\d{4})_'
    r'(?P<detail>[A-Z0-9À-ÖØ-Ý]+(?:-[A-Z0-9À-ÖØ-Ý]+)*)_'
    r'(?P<viewtype>[A-Z]{3})'
    r'(?:_(?P<date>\d{8}))?'
    r'\.(?P<ext>jpg|jpeg|png|webp|tiff)$',
    re.UNICODE
)

VIEWTYPE_ENUM = {"PAN", "GEN", "DET", "MAC", "MGM", "MGS", "MGP", "MGB", "DEG"}
ZONE_NAMES = {0: "CHANTIER", 1: "PLAN", 2: "SDB", 3: "WC"}
CATEGORY_NAMES = {
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


def validate_filename(filename):
    """Validate a single filename and return detailed results."""
    match = PATTERN.match(filename)
    if not match:
        return {
            'filename': filename,
            'valid': False,
            'error': 'Pattern does not match NameGen v1.5',
            'parsed': None
        }

    gd = match.groupdict()
    file_id = int(gd['file_ID'])

    # Decode file ID
    # Formula: file_ID = zone_ID*1000 + cat_ID*100 + cat_img_ID
    zone_id = file_id // 1000
    cat_id = (file_id % 1000) // 100
    cat_img_id = file_id % 100

    # Check consistency
    expected_id = zone_id * 1000 + cat_id * 100 + cat_img_id
    id_consistent = (file_id == expected_id)

    # Check enums
    viewtype = gd['viewtype']
    viewtype_valid = viewtype in VIEWTYPE_ENUM
    zone_valid = zone_id in ZONE_NAMES
    cat_valid = cat_id in CATEGORY_NAMES

    # Build errors list
    errors = []
    if not id_consistent:
        errors.append(f"File ID {file_id} inconsistent with zone/cat/img: {zone_id}/{cat_id}/{cat_img_id}")
    if not viewtype_valid:
        errors.append(f"Viewtype '{viewtype}' not in enum: {VIEWTYPE_ENUM}")
    if not zone_valid:
        errors.append(f"Zone ID {zone_id} unknown")
    if not cat_valid:
        errors.append(f"Category ID {cat_id} unknown")

    is_valid = len(errors) == 0

    return {
        'filename': filename,
        'valid': is_valid,
        'errors': errors,
        'parsed': {
            'file_ID': file_id,
            'file_ID_str': gd['file_ID'],
            'detail': gd['detail'],
            'viewtype': gd['viewtype'],
            'viewtype_name': {
                'PAN': 'Panoramic',
                'GEN': 'General',
                'DET': 'Detail',
                'MAC': 'Macro',
                'MGM': 'Wall-Wall',
                'MGS': 'Wall-Floor',
                'MGP': 'Wall-Ceiling',
                'MGB': 'Wall-Tub',
                'DEG': 'Damage'
            }.get(gd['viewtype']),
            'date': gd.get('date'),
            'ext': gd['ext'],
            'zone_ID': zone_id,
            'zone_name': ZONE_NAMES.get(zone_id),
            'cat_ID': cat_id,
            'cat_name': CATEGORY_NAMES.get(cat_id),
            'cat_img_ID': cat_img_id
        }
    }


def validate_all_images(images_dir):
    """Validate all image files in directory."""
    results = {
        'timestamp': datetime.utcnow().isoformat() + 'Z',
        'images_dir': str(images_dir),
        'total_files': 0,
        'valid': 0,
        'invalid': 0,
        'validations': [],
        'summary_by_zone': defaultdict(lambda: {'total': 0, 'valid': 0}),
        'summary_by_category': defaultdict(lambda: {'total': 0, 'valid': 0}),
        'errors': []
    }

    images_path = Path(images_dir)
    if not images_path.exists():
        results['errors'].append(f"Images directory not found: {images_dir}")
        return results

    # Get all image files
    image_extensions = {'.jpg', '.jpeg', '.png', '.webp', '.tiff'}
    files = sorted([
        f.name for f in images_path.iterdir()
        if f.is_file() and f.suffix.lower() in image_extensions
    ])

    results['total_files'] = len(files)

    # Validate each file
    for filename in files:
        validation = validate_filename(filename)
        results['validations'].append(validation)

        if validation['valid']:
            results['valid'] += 1
        else:
            results['invalid'] += 1

        # Track by zone and category
        if validation['parsed']:
            zone_name = validation['parsed']['zone_name']
            cat_name = validation['parsed']['cat_name']
            results['summary_by_zone'][zone_name]['total'] += 1
            results['summary_by_category'][cat_name]['total'] += 1

            if validation['valid']:
                results['summary_by_zone'][zone_name]['valid'] += 1
                results['summary_by_category'][cat_name]['valid'] += 1

    # Convert defaultdicts to regular dicts
    results['summary_by_zone'] = dict(results['summary_by_zone'])
    results['summary_by_category'] = dict(results['summary_by_category'])

    return results


def print_report(results):
    """Print formatted validation report."""
    total = results['total_files']
    valid = results['valid']
    invalid = results['invalid']

    print("\n" + "=" * 80)
    print("ARBOT IMAGE VALIDATION REPORT")
    print("=" * 80)
    print(f"Directory: {results['images_dir']}")
    print(f"Timestamp: {results['timestamp']}")
    print()

    print(f"TOTAL FILES: {total}")
    print(f"  Valid:     {valid} ({100*valid//total if total > 0 else 0}%)")
    print(f"  Invalid:   {invalid} ({100*invalid//total if total > 0 else 0}%)")
    print()

    if invalid > 0:
        print("=" * 80)
        print("INVALID FILES:")
        print("=" * 80)
        for v in results['validations']:
            if not v['valid']:
                print(f"\n[FAIL] {v['filename']}")
                for error in v['errors']:
                    print(f"       - {error}")
        print()

    print("=" * 80)
    print("SUMMARY BY ZONE:")
    print("=" * 80)
    for zone, stats in sorted(results['summary_by_zone'].items()):
        pct = 100 * stats['valid'] // stats['total'] if stats['total'] > 0 else 0
        print(f"  {zone:20} {stats['valid']:3}/{stats['total']:3} valid ({pct:3}%)")
    print()

    print("=" * 80)
    print("SUMMARY BY CATEGORY:")
    print("=" * 80)
    for cat, stats in sorted(results['summary_by_category'].items()):
        pct = 100 * stats['valid'] // stats['total'] if stats['total'] > 0 else 0
        print(f"  {cat:20} {stats['valid']:3}/{stats['total']:3} valid ({pct:3}%)")
    print()

    if results['errors']:
        print("=" * 80)
        print("ERRORS:")
        print("=" * 80)
        for error in results['errors']:
            print(f"  - {error}")
        print()

    if invalid == 0:
        print("=" * 80)
        print("ALL FILES VALID - CONGRATULATIONS!")
        print("=" * 80)
    else:
        print("=" * 80)
        print(f"REVIEW REQUIRED - {invalid} file(s) need renaming")
        print("=" * 80)

    print()


def main():
    parser = argparse.ArgumentParser(description='Validate ArBot image filenames')
    parser.add_argument('--images', default='images', help='Images directory (default: images)')
    parser.add_argument('--output', help='Output JSON report file')
    parser.add_argument('--verbose', action='store_true', help='Show all files including valid ones')
    args = parser.parse_args()

    results = validate_all_images(args.images)
    print_report(results)

    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"JSON report saved to: {args.output}")

    if args.verbose:
        print("\n" + "=" * 80)
        print("ALL FILES DETAIL:")
        print("=" * 80)
        for v in results['validations']:
            status = "OK" if v['valid'] else "FAIL"
            print(f"[{status}] {v['filename']}")
            if v['parsed']:
                p = v['parsed']
                print(f"      Zone: {p['zone_name']} ({p['zone_ID']})")
                print(f"      Category: {p['cat_name']} ({p['cat_ID']})")
                print(f"      Detail: {p['detail']}")
                print(f"      View: {p['viewtype_name']} ({p['viewtype']})")
                if p['date']:
                    print(f"      Date: {p['date']}")
            if not v['valid']:
                for error in v['errors']:
                    print(f"      ERROR: {error}")
            print()

    return 0 if results['invalid'] == 0 else 1


if __name__ == '__main__':
    exit(main())
