#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fix_pipeline_issues.py
Fix critical and non-critical issues identified by pipeline integrity verification.

Critical Issues:
1. CR_*.docx.pdf files (double extension)
2. CR_Renovation-SDB_2025.docx..pdf (double dots)

Data Quality Issues:
1. Filenames with trailing spaces (DTU files)
2. Code fields with trailing whitespace
3. Filenames with unencoded spaces
"""

from pathlib import Path
import json
import shutil
from datetime import datetime, timezone

class PipelineFixture:
    def __init__(self):
        self.changes = []
        self.errors = []

    def fix_filenames(self):
        """Rename files with issues"""
        print("[*] Fixing filenames...")

        docs_root = Path("docs/Normes")
        if not docs_root.exists():
            print(f"[ERROR] docs_root not found: {docs_root}")
            return False

        # Define fixes: old_name -> new_name
        fixes = {
            "CR/CR_60.1_2025.docx.pdf": "CR/CR_60.1_2025.pdf",
            "CR/CR_Normes-SDB_2025.docx.pdf": "CR/CR_Normes-SDB_2025.pdf",
            "CR/CR_Placo-SDB_2025.docx.pdf": "CR/CR_Placo-SDB_2025.pdf",
            "CR/CR_Renovation-SDB_2025.docx..pdf": "CR/CR_Renovation-SDB_2025.pdf",
            "DTU/DTU _25.41_1993.pdf": "DTU/DTU_25.41_1993.pdf",  # Remove leading space
            "DTU/DTU _25.42.P2_2012.pdf": "DTU/DTU_25.42.P2_2012.pdf",
            "DTU/DTU _52.2_2022.pdf": "DTU/DTU_52.2_2022.pdf",
            "DTU/DTU _60.1_2012.pdf": "DTU/DTU_60.1_2012.pdf",
            "FT/NOTICE_Bain-Acrylique_v7 .pdf": "FT/NOTICE_Bain-Acrylique_v7.pdf",  # Remove trailing space
        }

        for old_rel, new_rel in fixes.items():
            old_path = docs_root / old_rel
            new_path = docs_root / new_rel

            if old_path.exists():
                try:
                    shutil.move(str(old_path), str(new_path))
                    self.changes.append(f"RENAMED: {old_rel} -> {new_rel}")
                    print(f"  [OK] {old_rel} -> {new_rel}")
                except Exception as e:
                    self.errors.append(f"FAILED to rename {old_rel}: {e}")
                    print(f"  [ERROR] {old_rel}: {e}")
            else:
                print(f"  [SKIP] Not found: {old_rel}")

        return len(self.errors) == 0

    def regenerate_docs_index(self):
        """Regenerate docs_index.json with corrected metadata"""
        print("[*] Regenerating docs_index.json...")

        docs_root = Path("docs/Normes")
        out_json = Path("json/docs_index.json")

        def get_doc_type(filepath):
            """Determine document type from filename"""
            name = filepath.name.upper()
            if name.startswith("DTU"):
                return "DTU"
            elif name.startswith("FT"):
                return "FT"
            elif name.startswith("CR"):
                return "CR"
            elif name.startswith("NOTICE"):
                return "NOTICE"
            else:
                return "OTHER"

        def get_doc_category(filepath):
            """Determine category from folder structure"""
            if "DTU" in str(filepath):
                return "Standards"
            elif "FT" in str(filepath):
                return "Technical Sheets"
            elif "CR" in str(filepath):
                return "Compliance Reports"
            else:
                return "Documentation"

        def build_raw(owner, repo, branch, relpath):
            """Build GitHub RAW URL"""
            return f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{relpath}"

        def extract_metadata(filepath):
            """Extract metadata from document file"""
            try:
                size_bytes = filepath.stat().st_size
                size_kb = round(size_bytes / 1024, 1)
            except:
                size_kb = 0

            # Extract code from filename
            name_clean = filepath.stem  # Remove extension
            code = None

            if "_" in name_clean:
                code = name_clean.split("_")[0].strip()  # Remove any trailing spaces

            return {
                "size_bytes": size_bytes,
                "size_kb": size_kb,
                "code": code
            }

        # Scan all PDF files
        items = []
        count = 0

        for pdf_file in sorted(docs_root.rglob("*.pdf")):
            count += 1

            rel_path = pdf_file.relative_to(Path(".")).as_posix()
            url = build_raw("Tazevil", "ArBot-MiniDB", "main", rel_path)
            doc_type = get_doc_type(pdf_file)
            category = get_doc_category(pdf_file)
            metadata = extract_metadata(pdf_file)

            item = {
                "id": f"{doc_type}-{count:03d}",
                "filename": pdf_file.name,
                "path": rel_path,
                "type": doc_type,
                "category": category,
                "code": metadata["code"],
                "title": pdf_file.stem.replace("_", " "),  # Clean title
                "url": url,
                "size_kb": metadata["size_kb"],
                "created_at": datetime.now(timezone.utc).date().isoformat(),
                "tags": [doc_type.lower(), category.lower().replace(" ", "-")]
            }
            items.append(item)

        # Create output structure
        payload = {
            "db_name": "ArBot_Docs_Index",
            "version": "1.0.1",  # Bumped version for fix
            "created_at": datetime.now(timezone.utc).isoformat() + "Z",
            "total_documents": len(items),
            "documents": items
        }

        # Write JSON
        out_json.parent.mkdir(parents=True, exist_ok=True)
        out_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

        self.changes.append(f"REGENERATED: docs_index.json with {len(items)} documents (v1.0.1)")
        print(f"  [OK] Generated docs_index.json with {len(items)} documents")

        # Summary by type
        by_type = {}
        for item in items:
            t = item["type"]
            by_type[t] = by_type.get(t, 0) + 1

        print("\n  Documents by type:")
        for doc_type in sorted(by_type.keys()):
            print(f"    {doc_type:10} {by_type[doc_type]:3} files")

        return True

    def generate_report(self):
        """Generate summary report"""
        print("\n" + "="*70)
        print("PIPELINE FIX REPORT")
        print("="*70)

        if self.changes:
            print("\n[CHANGES MADE]")
            for change in self.changes:
                print(f"  * {change}")

        if self.errors:
            print("\n[ERRORS]")
            for error in self.errors:
                print(f"  * {error}")
            return False
        else:
            print("\nStatus: ALL FIXES APPLIED SUCCESSFULLY")
            return True

def main():
    fixture = PipelineFixture()

    if not fixture.fix_filenames():
        print("\n[ERROR] Failed to fix filenames")
        fixture.generate_report()
        return 1

    if not fixture.regenerate_docs_index():
        print("\n[ERROR] Failed to regenerate docs_index")
        fixture.generate_report()
        return 1

    success = fixture.generate_report()
    return 0 if success else 1

if __name__ == "__main__":
    import sys
    sys.exit(main())
