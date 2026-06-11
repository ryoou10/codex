#!/usr/bin/env python3
"""Compose an imagegen handoff spec from structured condition JSON."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


FIELD_DEFAULTS = {
    "use_case": "stylized-concept",
    "mode": "generate",
    "asset_type": "preview",
    "reference_roles": "Assign roles after inspecting the provided image files.",
    "primary_request": "Generate a polished image from the reference evidence and conditions.",
    "subject": "Infer the primary subject from the reference image, then strengthen the visual anchor with concrete identity, pose, expression, material, or texture details.",
    "scene": "Choose a coherent setting that supports the subject without stealing focus; include location, time, atmosphere, and surrounding elements.",
    "style": "Choose one compatible primary visual medium and add only reinforcing style modifiers.",
    "composition": "Define camera angle, shot size, aspect ratio, subject placement, depth layers, and focal hierarchy.",
    "lighting_color": "Use a motivated light source, clear contrast, color temperature, dominant palette, and a focal accent color.",
    "quality": "Specify concrete detail, texture, depth of field, edge quality, and finish appropriate to the medium.",
    "text": "none",
    "constraints": "Preserve explicit user constraints and reference-image identity; avoid adding text unless specified.",
}


def _as_text(value: Any, default: str) -> str:
    if value is None:
        return default
    if isinstance(value, str):
        stripped = value.strip()
        return stripped or default
    if isinstance(value, list):
        parts = [str(item).strip() for item in value if str(item).strip()]
        return "; ".join(parts) if parts else default
    return str(value).strip() or default


def _reference_roles(value: Any) -> str:
    if value is None:
        return FIELD_DEFAULTS["reference_roles"]
    if isinstance(value, dict):
        parts = [f"{key}: {role}" for key, role in value.items() if str(key).strip() and str(role).strip()]
        return "; ".join(parts) if parts else FIELD_DEFAULTS["reference_roles"]
    return _as_text(value, FIELD_DEFAULTS["reference_roles"])


def _avoid(value: Any) -> str:
    defaults = [
        "unwanted text",
        "watermark",
        "signature",
        "mismatched style",
        "muddy colors",
        "cluttered focal area",
    ]
    if value is None:
        return "; ".join(defaults)
    if isinstance(value, str):
        extra = [part.strip() for part in value.split(",") if part.strip()]
    elif isinstance(value, list):
        extra = [str(part).strip() for part in value if str(part).strip()]
    else:
        extra = [str(value).strip()]
    merged = []
    for item in extra + defaults:
        if item and item not in merged:
            merged.append(item)
    return "; ".join(merged)


def compose(data: dict[str, Any]) -> str:
    use_case = _as_text(data.get("use_case"), FIELD_DEFAULTS["use_case"])
    mode = _as_text(data.get("mode"), FIELD_DEFAULTS["mode"])
    asset_type = _as_text(data.get("asset_type"), FIELD_DEFAULTS["asset_type"])
    references = _reference_roles(data.get("reference_roles"))
    request = _as_text(data.get("primary_request"), FIELD_DEFAULTS["primary_request"])

    lines = [
        f"Use case: {use_case}",
        f"Mode: {mode}",
        f"Asset type: {asset_type}",
        f"Reference roles: {references}",
        f"Primary request: {request}",
        f"Subject: {_as_text(data.get('subject'), FIELD_DEFAULTS['subject'])}",
        f"Scene/backdrop: {_as_text(data.get('scene'), FIELD_DEFAULTS['scene'])}",
        f"Style/medium: {_as_text(data.get('style'), FIELD_DEFAULTS['style'])}",
        f"Composition/framing: {_as_text(data.get('composition'), FIELD_DEFAULTS['composition'])}",
        f"Lighting/mood: {_as_text(data.get('lighting_color'), FIELD_DEFAULTS['lighting_color'])}",
        f"Color palette: {_as_text(data.get('color_palette'), 'Derive a dominant palette and one accent from the subject, scene, and desired mood.')}",
        f"Materials/textures: {_as_text(data.get('materials_textures'), 'Describe tactile surface detail based on the subject and medium.')}",
        f"Quality/detail: {_as_text(data.get('quality'), FIELD_DEFAULTS['quality'])}",
        f"Text (verbatim): \"{_as_text(data.get('text'), FIELD_DEFAULTS['text'])}\"",
        f"Constraints: {_as_text(data.get('constraints'), FIELD_DEFAULTS['constraints'])}",
        f"Avoid: {_avoid(data.get('avoid'))}",
    ]
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Compose an imagegen handoff spec from JSON conditions.")
    parser.add_argument("input", type=Path, help="Path to a JSON file containing image generation conditions.")
    parser.add_argument("--out", type=Path, help="Optional output path for the generated handoff spec.")
    args = parser.parse_args()

    with args.input.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise SystemExit("Input JSON must contain an object at the top level.")

    output = compose(data)
    if args.out:
        args.out.write_text(output + "\n", encoding="utf-8")
    else:
        print(output)


if __name__ == "__main__":
    main()
