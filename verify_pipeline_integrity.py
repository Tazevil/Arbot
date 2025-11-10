#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
verify_pipeline_integrity.py
Comprehensive verification of ArBot-MiniDB data pipeline integrity.
Checks: JSON structure, file existence, URL validity, data consistency, cross-references.
"""

from pathlib import Path
import json
import sys
from urllib.parse import quote
from collections import defaultdict

class IntegrityChecker:
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.info = []
        self.images_db = None
        self.docs_db = None

    def load_databases(self):
        """Load both JSON databases"""
        print("[*] Loading databases...")

        images_path = Path("json/images_db.json")
        docs_path = Path("json/docs_index.json")

        if not images_path.exists():
            self.errors.append(f"MISSING: json/images_db.json")
            return False

        if not docs_path.exists():
            self.errors.append(f"MISSING: json/docs_index.json")
            return False

        try:
            self.images_db = json.loads(images_path.read_text(encoding="utf-8"))
            self.info.append(f"[OK] Loaded images_db.json with {self.images_db.get('count', 0)} items")
        except Exception as e:
            self.errors.append(f"PARSE ERROR in images_db.json: {e}")
            return False

        try:
            self.docs_db = json.loads(docs_path.read_text(encoding="utf-8"))
            self.info.append(f"[OK] Loaded docs_index.json with {self.docs_db.get('total_documents', 0)} documents")
        except Exception as e:
            self.errors.append(f"PARSE ERROR in docs_index.json: {e}")
            return False

        return True

    def check_images_db_structure(self):
        """Verify images_db.json structure"""
        print("[*] Checking images_db.json structure...")

        required_fields = ["db_name", "created_at", "count", "items"]
        for field in required_fields:
            if field not in self.images_db:
                self.errors.append(f"MISSING FIELD in images_db root: {field}")

        items = self.images_db.get("items", [])
        required_item_fields = ["id", "title", "url", "url_preview", "phase", "roi_hints", "created_at", "tags"]

        for idx, item in enumerate(items):
            for field in required_item_fields:
                if field not in item:
                    self.errors.append(f"Item {idx} missing field: {field}")

        self.info.append(f"[OK] images_db structure validated ({len(items)} items)")

    def check_docs_db_structure(self):
        """Verify docs_index.json structure"""
        print("[*] Checking docs_index.json structure...")

        required_fields = ["db_name", "version", "created_at", "total_documents", "documents"]
        for field in required_fields:
            if field not in self.docs_db:
                self.errors.append(f"MISSING FIELD in docs_index root: {field}")

        docs = self.docs_db.get("documents", [])
        required_doc_fields = ["id", "filename", "path", "type", "category", "url", "size_kb", "tags"]

        for idx, doc in enumerate(docs):
            for field in required_doc_fields:
                if field not in doc:
                    self.errors.append(f"Document {idx} missing field: {field}")

        self.info.append(f"[OK] docs_index structure validated ({len(docs)} documents)")

    def check_file_existence(self):
        """Verify that all referenced files exist on disk"""
        print("[*] Checking file existence on disk...")

        missing_images = []
        missing_previews = []
        missing_docs = []

        # Check images
        for item in self.images_db.get("items", []):
            image_path = Path(item.get("title", ""))
            if image_path.name:
                full_path = Path("images") / image_path.name
                if not full_path.exists():
                    missing_images.append(full_path)

            # Check preview
            preview_name = item.get("title", "").rsplit(".", 1)[0] + ".webp"
            preview_path = Path("images/preview") / preview_name
            if not preview_path.exists():
                missing_previews.append(preview_path)

        # Check documents
        for doc in self.docs_db.get("documents", []):
            doc_path = Path(doc.get("path", ""))
            if doc_path.parts:
                full_path = doc_path
                if not full_path.exists():
                    missing_docs.append(full_path)

        if missing_images:
            for img in missing_images:
                self.errors.append(f"MISSING IMAGE: {img}")
        else:
            self.info.append(f"[OK] All {len(self.images_db.get('items', []))} images found on disk")

        if missing_previews:
            for prev in missing_previews[:5]:
                self.errors.append(f"MISSING PREVIEW: {prev}")
            if len(missing_previews) > 5:
                self.errors.append(f"... and {len(missing_previews) - 5} more missing previews")
        else:
            self.info.append(f"[OK] All {len(self.images_db.get('items', []))} WebP previews found")

        if missing_docs:
            for doc in missing_docs:
                self.warnings.append(f"MISSING DOC: {doc}")
        else:
            self.info.append(f"[OK] All {len(self.docs_db.get('documents', []))} documents found")

    def check_data_quality(self):
        """Check for data quality issues"""
        print("[*] Checking data quality...")

        issues_found = 0

        # Check images_db data quality
        for idx, item in enumerate(self.images_db.get("items", [])):
            title = item.get("title", "")

            # Check ID format (should be 4 digits)
            item_id = item.get("id", "")
            if not item_id.isdigit() or len(item_id) != 4:
                self.warnings.append(f"Item {idx}: Invalid ID format '{item_id}'")
                issues_found += 1

            # Check phase value
            phase = item.get("phase", "")
            if phase not in ["chantier", "sinistre", "UNKNOWN"]:
                self.warnings.append(f"Item {idx}: Invalid phase '{phase}'")
                issues_found += 1

            # Check ROI hints format
            roi = item.get("roi_hints", [])
            if not isinstance(roi, list) or len(roi) == 0:
                self.warnings.append(f"Item {idx}: Missing or invalid roi_hints")
                issues_found += 1

        # Check docs_db data quality
        for idx, doc in enumerate(self.docs_db.get("documents", [])):
            filename = doc.get("filename", "")
            path = doc.get("path", "")
            code = doc.get("code", None)

            # Check for double extensions
            if filename.endswith(".docx.pdf"):
                self.errors.append(f"Doc {idx}: Double extension in '{filename}'")
                issues_found += 1

            # Check for double dots
            if ".." in filename:
                self.errors.append(f"Doc {idx}: Double dot in filename '{filename}'")
                issues_found += 1

            # Check for spaces in filename (should be URL-encoded)
            if " " in filename:
                self.warnings.append(f"Doc {idx}: Spaces in filename '{filename}' (check URL encoding)")
                issues_found += 1

            # Check for trailing spaces or dots in code
            if isinstance(code, str) and (code != code.strip() or code.endswith(".")):
                self.warnings.append(f"Doc {idx}: Code has whitespace/dots: '{code}'")
                issues_found += 1

        if issues_found == 0:
            self.info.append("[OK] No data quality issues found")
        else:
            self.info.append(f"[!] Found {issues_found} data quality issues")

    def check_url_consistency(self):
        """Verify URL format and consistency"""
        print("[*] Checking URL consistency...")

        base_url = "https://raw.githubusercontent.com/Tazevil/ArBot-MiniDB/main/"
        issues = 0

        # Check images URLs
        for item in self.images_db.get("items", []):
            url = item.get("url", "")
            url_preview = item.get("url_preview", "")

            if not url.startswith(base_url):
                self.warnings.append(f"Image {item.get('id')}: URL doesn't match expected base")
                issues += 1

            if not url_preview.startswith(base_url):
                self.warnings.append(f"Image {item.get('id')}: Preview URL doesn't match expected base")
                issues += 1

            # Check for spaces in URLs (should be %20)
            if " " in url or " " in url_preview:
                self.warnings.append(f"Image {item.get('id')}: URL contains unencoded spaces")
                issues += 1

        # Check docs URLs
        for doc in self.docs_db.get("documents", []):
            url = doc.get("url", "")

            if not url.startswith(base_url):
                self.warnings.append(f"Doc {doc.get('id')}: URL doesn't match expected base")
                issues += 1

            if " " in url:
                self.warnings.append(f"Doc {doc.get('id')}: URL contains unencoded spaces")
                issues += 1

        if issues == 0:
            self.info.append("[OK] All URLs follow consistent format")
        else:
            self.info.append(f"[!] Found {issues} URL consistency issues")

    def check_cross_references(self):
        """Verify cross-reference integrity"""
        print("[*] Checking cross-references...")

        # Check that image count matches
        items = self.images_db.get("items", [])
        count = self.images_db.get("count", 0)

        if len(items) != count:
            self.errors.append(f"COUNT MISMATCH: images_db.count={count} but items={len(items)}")
        else:
            self.info.append(f"[OK] images_db count matches items ({count})")

        # Check that docs count matches
        docs = self.docs_db.get("documents", [])
        total = self.docs_db.get("total_documents", 0)

        if len(docs) != total:
            self.errors.append(f"COUNT MISMATCH: docs_index.total_documents={total} but documents={len(docs)}")
        else:
            self.info.append(f"[OK] docs_index count matches documents ({total})")

        # Check for duplicate IDs
        image_ids = [item.get("id") for item in items]
        if len(image_ids) != len(set(image_ids)):
            duplicates = [id for id in set(image_ids) if image_ids.count(id) > 1]
            self.errors.append(f"DUPLICATE IMAGE IDs: {duplicates}")

        doc_ids = [doc.get("id") for doc in docs]
        if len(doc_ids) != len(set(doc_ids)):
            duplicates = [id for id in set(doc_ids) if doc_ids.count(id) > 1]
            self.errors.append(f"DUPLICATE DOC IDs: {duplicates}")
        else:
            self.info.append(f"[OK] No duplicate IDs in either database")

    def generate_report(self):
        """Generate comprehensive integrity report"""
        print("\n" + "="*70)
        print("PIPELINE INTEGRITY VERIFICATION REPORT")
        print("="*70)

        print("\n[INFO MESSAGES]")
        for msg in self.info:
            print(msg)

        if self.warnings:
            print("\n[WARNINGS] - Non-critical issues to review:")
            for warning in self.warnings:
                print(f"  WARNING: {warning}")

        if self.errors:
            print("\n[ERRORS] - Critical issues requiring attention:")
            for error in self.errors:
                print(f"  ERROR: {error}")
            print(f"\nTotal Errors: {len(self.errors)}")
            print(f"Total Warnings: {len(self.warnings)}")
            return False
        else:
            items = self.images_db.get("items", [])
            docs = self.docs_db.get("documents", [])
            print("\n" + "="*70)
            print("STATUS: ALL PIPELINE INTEGRITY CHECKS PASSED")
            print("="*70)
            print(f"[OK] Images database: {len(items)} items")
            print(f"[OK] Docs database: {len(docs)} documents")
            print(f"[OK] All files found on disk")
            print(f"[OK] Data quality verified")
            print(f"[OK] URLs consistent")
            print(f"[OK] Cross-references valid")
            if self.warnings:
                print(f"\nNote: {len(self.warnings)} minor warnings (see above)")
            return True

def main():
    checker = IntegrityChecker()

    if not checker.load_databases():
        print("\n[FATAL] Could not load databases")
        return 1

    checker.check_images_db_structure()
    checker.check_docs_db_structure()
    checker.check_file_existence()
    checker.check_data_quality()
    checker.check_url_consistency()
    checker.check_cross_references()

    success = checker.generate_report()

    # Write detailed report to file
    report_file = Path("json/INTEGRITY_REPORT.json")
    report_data = {
        "status": "PASS" if success else "FAIL",
        "errors": checker.errors,
        "warnings": checker.warnings,
        "info": checker.info,
        "summary": {
            "total_errors": len(checker.errors),
            "total_warnings": len(checker.warnings),
            "images_count": len(checker.images_db.get("items", [])),
            "docs_count": len(checker.docs_db.get("documents", []))
        }
    }

    report_file.parent.mkdir(parents=True, exist_ok=True)
    report_file.write_text(json.dumps(report_data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n[OK] Detailed report saved to: {report_file}")

    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
