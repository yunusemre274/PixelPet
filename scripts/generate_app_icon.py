#!/usr/bin/env python3
"""
DockPet App Icon Generator
Generates a retro macOS AppIcon.icns featuring the pixel-art pet.
Uses standard macOS iconutil tool to build the multi-resolution .icns package.
"""

import os
import shutil
import subprocess
from pathlib import Path
from PIL import Image, ImageDraw

def create_base_icon(size=1024):
    """Creates a beautiful retro pixel-art macOS app icon at 1024x1024."""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # 1. Background rounded rect (macOS squircle style)
    margin = size * 0.08
    corner_radius = size * 0.22
    rect = [margin, margin, size - margin, size - margin]

    # Gradient-like layered retro border & backdrop
    # Deep slate / space gray backdrop
    draw.rounded_rectangle(rect, radius=corner_radius, fill=(30, 32, 42, 255))

    # Inner soft inset border
    inner_margin = margin + (size * 0.02)
    inner_radius = corner_radius * 0.88
    draw.rounded_rectangle(
        [inner_margin, inner_margin, size - inner_margin, size - inner_margin],
        radius=inner_radius,
        fill=(42, 45, 60, 255),
        outline=(90, 100, 130, 255),
        width=int(size * 0.015)
    )

    # 2. Load Cat idle frame 0 and upscale with NEAREST neighbor
    cat_frame_path = Path(__file__).resolve().parent.parent / "Assets" / "Pets" / "Cat" / "interaction" / "frame_01.png"
    if not cat_frame_path.exists():
        cat_frame_path = Path(__file__).resolve().parent.parent / "Assets" / "Pets" / "Cat" / "idle" / "frame_00.png"

    if cat_frame_path.exists():
        pet_img = Image.open(cat_frame_path).convert("RGBA")
        # Scale 32x32 pet up to ~600x600 using NEAREST neighbor for crisp retro pixel art
        pet_size = int(size * 0.62)
        scaled_pet = pet_img.resize((pet_size, pet_size), Image.Resampling.NEAREST)

        # Center pet inside squircle
        offset_x = int((size - pet_size) / 2)
        offset_y = int((size - pet_size) / 2 + (size * 0.02))
        img.paste(scaled_pet, (offset_x, offset_y), scaled_pet)

    return img

def generate_icns(output_icns_path: Path):
    """Generates the full .icns bundle with all required Apple icon resolutions."""
    base_img = create_base_icon(1024)

    temp_iconset = output_icns_path.parent / "AppIcon.iconset"
    temp_iconset.mkdir(parents=True, exist_ok=True)

    icon_specs = [
        ("icon_16x16.png", 16),
        ("icon_16x16@2x.png", 32),
        ("icon_32x32.png", 32),
        ("icon_32x32@2x.png", 64),
        ("icon_128x128.png", 128),
        ("icon_128x128@2x.png", 256),
        ("icon_256x256.png", 256),
        ("icon_256x256@2x.png", 512),
        ("icon_512x512.png", 512),
        ("icon_512x512@2x.png", 1024),
    ]

    for filename, s in icon_specs:
        resized = base_img.resize((s, s), Image.Resampling.LANCZOS)
        resized.save(temp_iconset / filename, "PNG")

    # Run iconutil
    output_icns_path.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["iconutil", "-c", "icns", str(temp_iconset), "-o", str(output_icns_path)],
        check=True
    )

    # Clean up temp iconset
    shutil.rmtree(temp_iconset)
    print(f"[✓] Successfully generated {output_icns_path}")

def main():
    project_root = Path(__file__).resolve().parent.parent
    output_path = project_root / "DockPet" / "Resources" / "AppIcon.icns"
    generate_icns(output_path)

if __name__ == "__main__":
    main()
