#!/usr/bin/env python3
"""List image files in the user's iCloud Drive image folder."""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path


DEFAULT_ICLOUD_IMAGE_DIR = Path.home() / "Library/Mobile Documents/com~apple~CloudDocs/画像"
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".heic", ".tif", ".tiff"}


def _dimensions(path: Path) -> tuple[int | None, int | None]:
    try:
        result = subprocess.run(
            ["sips", "-g", "pixelWidth", "-g", "pixelHeight", str(path)],
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return None, None

    width = None
    height = None
    for line in result.stdout.splitlines():
        stripped = line.strip()
        if stripped.startswith("pixelWidth:"):
            width = int(stripped.split(":", 1)[1].strip())
        elif stripped.startswith("pixelHeight:"):
            height = int(stripped.split(":", 1)[1].strip())
    return width, height


def list_images(root: Path, limit: int) -> list[dict[str, object]]:
    if not root.exists():
        raise SystemExit(f"Image folder not found: {root}")

    files = [path for path in root.iterdir() if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS]
    files.sort(key=lambda path: path.stat().st_mtime, reverse=True)

    rows = []
    for path in files[:limit]:
        stat = path.stat()
        width, height = _dimensions(path)
        rows.append(
            {
                "path": str(path),
                "name": path.name,
                "bytes": stat.st_size,
                "modified_unix": int(stat.st_mtime),
                "pixelWidth": width,
                "pixelHeight": height,
            }
        )
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description="List images from the iCloud Drive image folder.")
    parser.add_argument("--root", type=Path, default=DEFAULT_ICLOUD_IMAGE_DIR, help="Image folder to scan.")
    parser.add_argument("--limit", type=int, default=20, help="Maximum number of images to return.")
    parser.add_argument("--json", action="store_true", help="Print JSON instead of a text table.")
    args = parser.parse_args()

    rows = list_images(args.root, args.limit)
    if args.json:
        print(json.dumps(rows, ensure_ascii=False, indent=2))
        return

    for row in rows:
        dimensions = "unknown"
        if row["pixelWidth"] and row["pixelHeight"]:
            dimensions = f"{row['pixelWidth']}x{row['pixelHeight']}"
        print(f"{row['path']}\t{dimensions}\t{row['bytes']} bytes")


if __name__ == "__main__":
    main()
