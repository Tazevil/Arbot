#!/usr/bin/env python3
"""
GPT-4o Vision Batch Analysis with OAuth Authentication

- Obtains/refreshes access tokens via OAuthTokenManager
- Iterates images in a folder and analyzes them with GPT-4o
- Saves one JSON result per image in the output directory
"""

import os
import json
import base64
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List

try:
    from openai import OpenAI
except Exception as e:
    OpenAI = None

from oauth_token_manager import OAuthTokenManager

# Defaults
DEFAULT_IMAGES_DIR = Path("images")
DEFAULT_OUTPUT_DIR = Path("docs/To validate/ArBot-Vision-GPT4o_v1.0/individual_analysis")
DEFAULT_MODEL = "gpt-4o"
SUPPORTED_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}


ANALYSIS_PROMPT = """You are an expert in construction damage assessment for French bathrooms.
Analyze the provided photo and produce a concise JSON with:
- defects: array of {type, location, severity(1-5), confidence(0-1), notes}
- probable_causes: array of short strings
- recommended_actions: array of short, actionable steps
- estimated_impact: {cost_low_eur, cost_high_eur, urgency(1-5)}
Be concrete and avoid speculation beyond the image. Output valid JSON only.
"""


def get_openai_client() -> "OpenAI":
    manager = OAuthTokenManager()
    token = manager.get_valid_token()
    if OpenAI is None:
        raise RuntimeError(
            "openai library not available. Install with: pip install openai>=1.0.0"
        )
    # Use OAuth access token as API key (SDK sends Bearer header)
    return OpenAI(api_key=token)


def encode_image_as_data_url(p: Path) -> str:
    mime = "image/jpeg"
    ext = p.suffix.lower()
    if ext == ".png":
        mime = "image/png"
    elif ext == ".webp":
        mime = "image/webp"
    elif ext == ".bmp":
        mime = "image/bmp"
    elif ext in (".jpg", ".jpeg"):
        mime = "image/jpeg"

    b = p.read_bytes()
    b64 = base64.b64encode(b).decode("utf-8")
    return f"data:{mime};base64,{b64}"


def analyze_image(client: "OpenAI", img_path: Path, model: str) -> Dict:
    data_url = encode_image_as_data_url(img_path)
    resp = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "image_url", "image_url": {"url": data_url, "detail": "high"}},
                    {"type": "text", "text": ANALYSIS_PROMPT},
                ],
            }
        ],
        temperature=0.2,
        max_tokens=2000,
    )

    content = resp.choices[0].message.content or "{}"
    try:
        parsed = json.loads(content)
    except json.JSONDecodeError:
        parsed = {
            "image_analysis": {
                "file_name": img_path.name,
                "model": model,
                "analysis_timestamp": datetime.utcnow().isoformat(),
                "raw_response": content,
                "parse_error": "Response was not valid JSON",
            }
        }
    return parsed


def collect_images(images_dir: Path, pattern: str | None = None, limit: int | None = None) -> List[Path]:
    if pattern:
        candidates = list(images_dir.rglob(pattern))
    else:
        candidates = [p for p in images_dir.rglob("*") if p.is_file()]
    imgs = [p for p in candidates if p.suffix.lower() in SUPPORTED_EXTS]
    imgs.sort()
    if limit is not None and limit > 0:
        imgs = imgs[:limit]
    return imgs


def save_result(output_dir: Path, img_path: Path, result: Dict):
    output_dir.mkdir(parents=True, exist_ok=True)
    out_path = output_dir / f"{img_path.stem}_analysis.json"
    out_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    return out_path


def main():
    parser = argparse.ArgumentParser(description="Batch GPT-4o vision analysis with OAuth.")
    parser.add_argument("--images-dir", type=Path, default=DEFAULT_IMAGES_DIR, help="Folder with images.")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR, help="Folder for JSON outputs.")
    parser.add_argument("--model", type=str, default=DEFAULT_MODEL, help="Model name (e.g., gpt-4o).")
    parser.add_argument("--pattern", type=str, default=None, help="Glob filter (e.g., *.jpg).")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of images.")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing outputs.")
    args = parser.parse_args()

    if not args.images_dir.exists():
        print(f"Images directory not found: {args.images_dir}")
        return 1

    client = get_openai_client()
    images = collect_images(args.images_dir, args.pattern, args.limit)
    if not images:
        print("No images found to process.")
        return 0

    print(f"Found {len(images)} image(s). Writing results to: {args.output_dir}")

    processed = 0
    for img in images:
        out_file = args.output_dir / f"{img.stem}_analysis.json"
        if out_file.exists() and not args.overwrite:
            print(f"- Skip (exists): {img.name}")
            continue

        print(f"- Analyzing: {img.name}")
        try:
            result = analyze_image(client, img, args.model)
            save_result(args.output_dir, img, result)
            processed += 1
        except Exception as e:
            err_path = args.output_dir / f"{img.stem}_error.txt"
            err_path.write_text(str(e), encoding="utf-8")
            print(f"  ! Error: {e} (logged to {err_path.name})")

    # Optional index
    index = {
        "model": args.model,
        "images_dir": str(args.images_dir),
        "output_dir": str(args.output_dir),
        "count_found": len(images),
        "count_processed": processed,
        "timestamp_utc": datetime.utcnow().isoformat(),
    }
    (args.output_dir / "index.json").write_text(json.dumps(index, indent=2), encoding="utf-8")

    print(f"Done. Processed {processed}/{len(images)} image(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

