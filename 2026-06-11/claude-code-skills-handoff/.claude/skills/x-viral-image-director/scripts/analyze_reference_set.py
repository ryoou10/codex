#!/usr/bin/env python3
"""Analyze reference image sets for X-ready image prompt synthesis."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

from PIL import Image, ImageStat


DEFAULT_ICLOUD_IMAGE_DIR = Path.home() / "Library/Mobile Documents/com~apple~CloudDocs/画像"
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".heic", ".tif", ".tiff"}


def _palette(image: Image.Image, colors: int) -> list[str]:
    small = image.convert("RGB").resize((96, 96))
    quantized = small.quantize(colors=colors).convert("RGB")
    counted = sorted(quantized.getcolors(maxcolors=9216), reverse=True)[:colors]
    return ["#%02x%02x%02x" % color for _, color in counted]


def _entropy(image: Image.Image) -> float:
    gray = image.convert("L").resize((128, 128))
    hist = gray.histogram()
    total = sum(hist)
    return -sum((count / total) * math.log2(count / total) for count in hist if count)


def analyze_image(path: Path, role: str, colors: int) -> dict[str, Any]:
    with Image.open(path) as image:
        rgb = image.convert("RGB")
        stat = ImageStat.Stat(rgb.resize((1, 1)))
        avg = tuple(int(value) for value in stat.mean)
        return {
            "path": str(path),
            "name": path.name,
            "role": role,
            "width": image.width,
            "height": image.height,
            "aspect_ratio": round(image.width / image.height, 4),
            "average_color": "#%02x%02x%02x" % avg,
            "brightness": round(sum(avg) / 3),
            "entropy": round(_entropy(rgb), 2),
            "palette": _palette(rgb, colors),
        }


def collect_icloud(root: Path) -> list[Path]:
    if not root.exists():
        raise SystemExit(f"iCloud image folder not found: {root}")
    paths = [path for path in root.iterdir() if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS]
    return sorted(paths, key=lambda path: path.stat().st_mtime, reverse=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze image references for X image generation prompts.")
    parser.add_argument("paths", nargs="*", type=Path, help="Additional image paths to analyze.")
    parser.add_argument("--icloud", action="store_true", help="Include the default iCloud Drive image folder.")
    parser.add_argument("--icloud-root", type=Path, default=DEFAULT_ICLOUD_IMAGE_DIR, help="iCloud image folder to scan.")
    parser.add_argument("--attachment", action="append", type=Path, default=[], help="Attachment path to analyze as a style/mood reference.")
    parser.add_argument("--colors", type=int, default=8, help="Palette colors per image.")
    parser.add_argument("--json", action="store_true", help="Print JSON output.")
    args = parser.parse_args()

    rows: list[dict[str, Any]] = []
    for path in args.attachment:
        rows.append(analyze_image(path, "style/mood reference", args.colors))
    if args.icloud:
        for path in collect_icloud(args.icloud_root):
            rows.append(analyze_image(path, "iCloud folder reference", args.colors))
    for path in args.paths:
        rows.append(analyze_image(path, "additional reference", args.colors))

    if args.json:
        print(json.dumps(rows, ensure_ascii=False, indent=2))
        return

    for row in rows:
        print(
            f"{row['role']}\t{row['name']}\t{row['width']}x{row['height']}\t"
            f"avg={row['average_color']}\tbrightness={row['brightness']}\t"
            f"entropy={row['entropy']}\tpalette={', '.join(row['palette'])}"
        )


if __name__ == "__main__":
    main()
