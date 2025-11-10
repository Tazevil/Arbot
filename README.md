# ArBot-MiniDB

Comprehensive dataset for ArBot Vision AI training and water damage assessment case studies.

## Project Overview

**ArBot-MiniDB** is a complete, production-quality dataset containing:
- **94 technical photographs** of construction/bathroom renovation work
- **Insurance claim documentation** from a real-world water damage case (#25-001508-RLY-M1)
- **Regulatory & compliance documentation** (French DTU standards, technical specifications)
- **Knowledge base** with construction ontologies, taxonomies, and contractual clauses
- **AI analysis outputs** from ArBot-Core v1.4 computer vision analysis

**Case Study**: Water damage in apartment bathroom (Villeurbanne, France) - July 2024 to August 2025

---

## Directory Structure

```
ArBot-MiniDB/
├── README.md                           # This file
├── LICENSE                             # MIT License
├── manifest.json                       # Project metadata & naming conventions
├── validate_pack.py                    # Image validation and cataloging script
├── index.html                          # Interactive photo gallery viewer
│
├── images/                             # 94 technical photographs (NNNN_DETAIL_VIEWTYPE.ext)
│   ├── 0001_SDB_GEN_20250818.jpg      # Worksite photos (dated, zone 0)
│   ├── 0002_SDB_GEN_20250818.jpg
│   ├── 2001_SDB_GEN.jpg               # Damage/sinistre photos (zone 2, undated)
│   ├── 2002_BAIGNOIRE_GEN.jpg
│   └── [89 more images following naming convention]
│
├── docs/
│   ├── Context/                        # Insurance claim and project context
│   │   ├── arbotvision_context.json    # Claim details, stakeholders, timeline
│   │   ├── ARCHIVE/                    # Communications and records
│   │   │   ├── #1_Acteurs.csv         # Stakeholder contact database
│   │   │   ├── #2_Communications.csv  # Email/SMS message log
│   │   │   ├── #MASTER.csv            # Timeline of events
│   │   │   ├── Call History.txt       # Phone call records
│   │   │   ├── contacts.csv
│   │   │   ├── emails.csv
│   │   │   └── sms.csv
│   │   ├── RAW/                        # Raw data exports
│   │   └── *.zip                       # Communication archives
│   │
│   ├── knowledge/                      # AI training knowledge base
│   │   ├── name_convention.json        # IMAGE NAMING STANDARD (v1.5)
│   │   ├── taxonomie_01.json           # Building element taxonomy
│   │   ├── taxonomie_02.json           # Extended taxonomy
│   │   ├── ontology.validated.json     # Validated building ontology
│   │   ├── ontology.enriched.json      # Extended ontology (210 KB)
│   │   ├── clauses_validated.jsonl     # Legal/insurance clauses
│   │   ├── clauses_full.jsonl          # Complete clause database
│   │   ├── articles_validated.jsonl    # Regulatory articles
│   │   └── index_keywords.jsonl        # Searchable keywords
│   │
│   ├── Normes/                         # French building standards & specs
│   │   ├── DTU/                        # Official building standards
│   │   │   ├── DTU_25.41_1993.pdf     # Waterproofing
│   │   │   ├── DTU_25.42.P2_2012.pdf  # Waterproofing (part 2)
│   │   │   ├── DTU_52.2_2022.pdf      # Wall/floor finishes & tiling
│   │   │   └── DTU_60.1_2012.pdf      # Electrical installations
│   │   ├── FT/                         # Product technical datasheets
│   │   │   ├── FT_Baignoire_E6D122.pdf    # Bathtub specifications
│   │   │   ├── FT_Vidange_E6D124.pdf     # Drain specifications
│   │   │   └── [4 more product specs]
│   │   └── CR/                         # Compliance reports
│   │       ├── CR_SDB-REF_2025.docx    # Bathroom reference
│   │       ├── CR_Normes-SDB_2025.pdf  # Standard compliance
│   │       └── [3 more compliance reports]
│   │
│   ├── To validate/                    # Analysis outputs and validation (IGNORED FOR NOW)
│   │   ├── build_manifest_strict.py
│   │   ├── ArBot-Core,_v1.4_OUT_JSON/  # 60+ analysis result files
│   │   └── [Various analysis documents]
│   │
│   └── Les travaux prévus en détails.docx  # Detailed work plan
│
├── json/
│   └── images_sidecar.csv              # Image metadata and classification (94 rows)
│
└── scripts/
    └── index.html                      # GitHub Pages template
```

---

## IMAGE NAMING CONVENTION (CRITICAL)

### Pattern
```
NNNN_DETAIL_VIEWTYPE.ext
```

### Components

| Component | Format | Example | Notes |
|-----------|--------|---------|-------|
| **NNNN** | 4-digit padded | `0001`, `2301` | Encodes zone + category + image # |
| **DETAIL** | UPPERCASE | `SDB`, `BAIGNOIRE`, `ALIMENTATION-EVACUATION` | Accents OK, hyphens OK, NO SPACES |
| **VIEWTYPE** | 3-letter code | `GEN`, `DET`, `MAC`, `MGM` | Must be from approved enum |
| **ext** | lowercase | `.jpg` | jpg, jpeg, png, webp, tiff |

### File ID Decoding
```
File ID = Zone_ID * 1000 + Cat_ID * 100 + Cat_Img_ID * 10

Example: 2301 = (2*1000) + (3*100) + (1*10)
  → Zone 2 (SDB), Category 3 (CARRELAGE), Image #1
```

### Zone IDs (first digit)
- **0** = CHANTIER (worksite/construction) - MUST HAVE DATE: `YYYYMMDD`
- **1** = PLAN (plans and designs)
- **2** = SDB (bathroom damage/repair documentation)
- **3** = WC (toilet damage/repair documentation)

### View Type Codes (3-letter enum)
| Code | Meaning | Use Case |
|------|---------|----------|
| **PAN** | Panoramic view | Full room overview |
| **GEN** | General view | Standard room photo |
| **DET** | Close-up detail | Problem area close-up |
| **MAC** | Macro view | Very close inspection |
| **MGM** | Wall-to-Wall | Corner or junction |
| **MGS** | Wall-to-Floor | Base or floor junction |
| **MGP** | Wall-to-Ceiling | Ceiling junction |
| **MGB** | Wall-to-Tub | Tub edge interactions |
| **DEG** | Damage existing | Existing damage documentation |

### Valid Examples
```
0001_SDB_GEN_20250818.jpg          ✓ Worksite photo, dated
0003_SALON-PROTECTION_GEN_20250818.jpg  ✓ Multi-word detail with hyphen
2001_SDB_GEN.jpg                   ✓ Damage claim photo, undated
2301_JOINT_MGM.jpg                 ✓ Wall-to-wall interaction
3705_PIED_DET.jpg                  ✓ Close-up detail
```

### Invalid Examples
```
0001_SDB_GEN.jpg                   ✗ Worksite photo MUST have date
0001_SDB_gen.jpg                   ✗ VIEWTYPE must be uppercase
0001_SDB PROTECTION_GEN.jpg        ✗ No spaces in DETAIL (use hyphen)
001_SDB_GEN_20250818.jpg           ✗ File ID must be 4 digits (padded)
2301_JOINT_DETAIL.jpg              ✗ VIEWTYPE must be 3 letters (DETAIL is 6)
```

---

## Key Files

### Configuration & Manifests
- **manifest.json** - Project metadata with embedded naming convention rules
- **docs/knowledge/name_convention.json** - Complete naming specification (v1.5)

### Image Metadata
- **json/images_sidecar.csv** - Catalog of all 94 images with parsed metadata

### Documentation
- **index.html** - Interactive photo gallery and viewer
- **validate_pack.py** - Python script for validating image filenames

---

## Data Statistics

| Category | Count |
|----------|-------|
| **Images** | 94 JPG files |
| **Documentation** | 40+ PDF/DOCX files |
| **Knowledge Base** | 15 JSON/JSONL files |
| **Total Data** | ~150 MB (including archives) |
| **Claim Coverage** | 13 months (July 2024 - August 2025) |

---

## Use Cases

1. **Computer Vision Training** - 94 annotated construction photos with defect analysis
2. **Document Management** - Complete insurance claim workflow example
3. **Knowledge Base** - French building standards and construction ontology
4. **Compliance Verification** - Mapping work to regulatory requirements (DTU standards)
5. **Dispute Resolution** - Evidence documentation for construction disputes
6. **Case Study** - Real-world water damage claim processing

---

## Insurance Claim Reference

**Claim #:** 25-001508-RLY-M1
**Incident:** Water damage, July 21, 2024
**Location:** 123 rue Château Gaillard, 69100 Villeurbanne, France
**Work Period:** August 18-29, 2025
**Claim Amount:** €4,287.06 TTC
**Insurer:** MAAF Assurances (Habitation Tempo product)

---

## License

MIT License - See LICENSE file
