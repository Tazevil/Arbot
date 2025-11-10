#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generate_docs_index.py
Scans docs/Normes/ directory and creates json/docs_index.json
with metadata about all technical documents (DTU, FT, CR)
"""

from pathlib import Path
import json
import argparse
from datetime import datetime, timezone

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

def extract_metadata(filepath):
    """Extract metadata from document file"""
    try:
        size_bytes = filepath.stat().st_size
        size_kb = round(size_bytes / 1024, 1)
    except:
        size_kb = 0

    # Try to extract document code from filename
    name_clean = filepath.stem  # Remove extension
    code = None

    if "_" in name_clean:
        code = name_clean.split("_")[0]

    return {
        "size_bytes": size_bytes,
        "size_kb": size_kb,
        "code": code
    }

def build_raw(owner, repo, branch, relpath):
    """Build GitHub RAW URL"""
    return f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{relpath}"

def main():
    ap = argparse.ArgumentParser(description="Index all documents in docs/Normes/")
    ap.add_argument("--docs_root", default="docs/Normes", help="Root directory for documents")
    ap.add_argument("--out_json", default="json/docs_index.json", help="Output JSON file")
    ap.add_argument("--owner", default="Tazevil", help="GitHub owner")
    ap.add_argument("--repo", default="ArBot-MiniDB", help="GitHub repo")
    ap.add_argument("--branch", default="main", help="GitHub branch")
    args = ap.parse_args()

    docs_root = Path(args.docs_root)
    out_json = Path(args.out_json)

    if not docs_root.exists():
        print(f"[ERROR] Docs root not found: {docs_root}")
        return

    # Scan all PDF files
    items = []
    count = 0

    for pdf_file in sorted(docs_root.rglob("*.pdf")):
        count += 1

        rel_path = pdf_file.relative_to(Path(".")).as_posix()
        url = build_raw(args.owner, args.repo, args.branch, rel_path)
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
            "title": pdf_file.stem.replace("_", " ").replace(".docx", ""),
            "url": url,
            "size_kb": metadata["size_kb"],
            "created_at": datetime.now(timezone.utc).date().isoformat(),
            "tags": [doc_type.lower(), category.lower()]
        }
        items.append(item)

    # Create output structure
    payload = {
        "db_name": "ArBot_Docs_Index",
        "version": "1.0.0",
        "created_at": datetime.now(timezone.utc).isoformat() + "Z",
        "total_documents": len(items),
        "documents": items
    }

    # Write JSON
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"[OK] Scanned: {docs_root}")
    print(f"[OK] Documents found: {len(items)}")
    print(f"[OK] Index created: {out_json}")

    # Summary by type
    by_type = {}
    for item in items:
        t = item["type"]
        by_type[t] = by_type.get(t, 0) + 1

    print("\nDocuments by type:")
    for doc_type in sorted(by_type.keys()):
        print(f"  {doc_type:10} {by_type[doc_type]:3} files")

if __name__ == "__main__":
    main()
