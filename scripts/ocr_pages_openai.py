#!/usr/bin/env python3
"""Convert page images from the BYN manual into raw LaTeX fragments.

This is a helper for generating first-draft OCR/AI fragments only. The output
must be reviewed against the original PDF/page image before it becomes final
LaTeX source.

Requirements:
  - OPENAI_API_KEY in the environment
  - requests installed in the active Python environment

Example:
  OPENAI_API_KEY=... python scripts/ocr_pages_openai.py \
    --input-dir scratch/ocr-input \
    --output-dir scratch/generated-pages \
    --archive-dir source/pages \
    --move-processed
"""

from __future__ import annotations

import argparse
import base64
import os
import shutil
import sys
import time
from pathlib import Path

import requests

PROMPT = """This page belongs to a radiation-safety manual in Spanish.
Convert the visible text to LaTeX fragment form.

Rules:
- Return only LaTeX content, without Markdown fences.
- Do not include documentclass, packages, begin{document}, or end{document}.
- Preserve the original meaning, order, numbering, units, tables, and formulas.
- Correct obvious OCR spelling/accent errors only when unambiguous.
- Add LaTeX comments for uncertain readings instead of inventing text.
"""

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-dir", type=Path, default=Path("scratch/ocr-input"))
    parser.add_argument("--output-dir", type=Path, default=Path("scratch/generated-pages"))
    parser.add_argument("--archive-dir", type=Path, default=Path("source/pages"))
    parser.add_argument("--model", default="gpt-4o")
    parser.add_argument("--max-tokens", type=int, default=1500)
    parser.add_argument("--sleep", type=float, default=30.0, help="Seconds to wait between API calls")
    parser.add_argument("--move-processed", action="store_true", help="Move processed images to --archive-dir")
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def encode_image(path: Path) -> str:
    return base64.b64encode(path.read_bytes()).decode("utf-8")


def iter_images(input_dir: Path) -> list[Path]:
    if not input_dir.exists():
        return []
    return sorted(
        path
        for path in input_dir.rglob("*")
        if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS
    )


def convert_image(path: Path, *, api_key: str, model: str, max_tokens: int) -> str:
    mime = "image/jpeg" if path.suffix.lower() in {".jpg", ".jpeg"} else f"image/{path.suffix.lower().lstrip('.')}"
    payload = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": PROMPT},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:{mime};base64,{encode_image(path)}",
                        },
                    },
                ],
            }
        ],
        "max_tokens": max_tokens,
    }
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }
    response = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers=headers,
        json=payload,
        timeout=120,
    )
    response.raise_for_status()
    data = response.json()
    return data["choices"][0]["message"]["content"].strip() + "\n"


def main() -> int:
    args = parse_args()
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key and not args.dry_run:
        print("error: OPENAI_API_KEY is not set", file=sys.stderr)
        return 2

    images = iter_images(args.input_dir)
    if not images:
        print(f"No images found in {args.input_dir}")
        return 0

    args.output_dir.mkdir(parents=True, exist_ok=True)
    if args.move_processed:
        args.archive_dir.mkdir(parents=True, exist_ok=True)

    for index, image_path in enumerate(images, start=1):
        output_path = args.output_dir / f"{image_path.name}.tex"
        print(f"[{index}/{len(images)}] {image_path} -> {output_path}")

        if args.dry_run:
            continue

        latex = convert_image(
            image_path,
            api_key=api_key or "",
            model=args.model,
            max_tokens=args.max_tokens,
        )
        output_path.write_text(latex, encoding="utf-8")

        if args.move_processed:
            destination = args.archive_dir / image_path.name
            shutil.move(str(image_path), str(destination))

        if index < len(images) and args.sleep > 0:
            time.sleep(args.sleep)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
