#!/usr/bin/env python3
"""
Advanced Sprite Sheet Slicer & 64x64 Pixel-Art Renderer for DockPet
===================================================================
Slices 256×256 sprite sheets (8×8 grid of 32×32 frames) from Assets/NewPetDesign/
and renders them as pixel-perfect 64×64 frames (2× nearest-neighbor scaling)
with exact state-to-animation mapping for all 9 pet types.

Supported Pets & Signature Special Animations:
  - Lionel Messi: Goal celebration slide + World Cup trophy lift (16 frames)
  - Cristiano Ronaldo: SIU celebration spin/land + Champions League trophy lift (12 frames)
  - Turtle: Retreating into protective shell and peeking out (8 frames)
  - Cat: Batting and playing with fish toy (8 frames)
  - Dog: Dancing on hind legs with joyful hearts (8 frames)
  - Hamster: Eating sunflower seeds and stuffing cheek pouches (8 frames)
  - Dinosaur: Stomping and breathing fire roar (8 frames)
  - Parrot: Flapping wings and singing musical notes (8 frames)
  - Rabbit: Happily munching on a fresh carrot (8 frames)
"""

import json
import os
import sys
from pathlib import Path
from PIL import Image

SPRITE_SHEET_DIR = Path("Assets/NewPetDesign")
OUTPUT_DIR = Path("Assets/Pets")
CELL_SRC_SIZE = 32
TARGET_SIZE = 64  # Upscaled 2x nearest-neighbor for 64x64 pixel art

# Precise row & cell coordinate mappings for each pet
# Format: { anim_name: [ (row, col), ... ] }
PET_ANIMATION_MAPS = {
    "LionelMessi": {
        "idle": [(0, c) for c in range(8)],
        "walk": [(2, c) for c in range(8)],
        "interaction": [(3, c) for c in range(8)],
        # Special: Goal celebration (Row 6) + World Cup kiss & lift (Row 5)
        "special": [(6, c) for c in range(8)] + [(5, c) for c in range(8)],
        "sleep": [(0, 0), (0, 1), (0, 2), (0, 3)],  # Will apply sleeping effect if needed
    },
    "CristianoRonaldo": {
        "idle": [(0, c) for c in range(8)],
        "walk": [(1, c) for c in range(8)],
        "interaction": [(5, c) for c in range(8)],
        # Special: SIU jump & land (Row 6) + Champions Trophy lift (Row 4, cols 0-3)
        "special": [(6, c) for c in range(8)] + [(4, c) for c in range(4)],
        "sleep": [(0, 0), (0, 1), (0, 2), (0, 3)],
    },
    "Turtle": {
        "idle": [(1, c) for c in range(4)],
        "walk": [(0, c) for c in range(8)],
        "sleep": [(3, c) for c in range(8)],
        "interaction": [(7, c) for c in range(8)],
        # Special: Retreating into shell and peeking out (Row 2)
        "special": [(2, c) for c in range(8)],
    },
    "Dog": {
        "idle": [(2, c) for c in range(4)],
        "walk": [(0, c) for c in range(4)],
        "sleep": [(0, c) for c in range(4, 8)],
        "interaction": [(6, c) for c in range(4, 8)],
        # Special: Back legs dancing and jumping with hearts (Row 6, all 8)
        "special": [(6, c) for c in range(8)],
    },
    "Cat": {
        "idle": [(0, c) for c in range(4)],
        "walk": [(3, c) for c in range(4)],
        "sleep": [(5, c) for c in range(4, 8)],
        "interaction": [(5, c) for c in range(4)],  # Cardboard box popup
        # Special: Playing with fish skeleton (Row 7)
        "special": [(7, c) for c in range(8)],
    },
    "Hamster": {
        "idle": [(0, c) for c in range(4)],
        "walk": [(2, c) for c in range(8)],
        "sleep": [(1, c) for c in range(8)],
        "interaction": [(3, c) for c in range(8)],
        # Special: Eating sunflower seeds & stuffing cheek pouches (Row 4)
        "special": [(4, c) for c in range(8)],
    },
    "Dinosaur": {
        "idle": [(0, c) for c in range(8)],
        "walk": [(2, c) for c in range(8)],
        "sleep": [(1, c) for c in range(8)],
        "interaction": [(3, c) for c in range(8)],
        # Special: Stomping and fire roar (Row 4)
        "special": [(4, c) for c in range(8)],
    },
    "Parrot": {
        "idle": [(0, c) for c in range(8)],
        "walk": [(2, c) for c in range(8)],
        "sleep": [(1, c) for c in range(8)],
        "interaction": [(3, c) for c in range(8)],
        # Special: Flapping wings and flying (Row 5)
        "special": [(5, c) for c in range(8)],
    },
    "Rabbit": {
        "idle": [(0, c) for c in range(8)],
        "walk": [(2, c) for c in range(8)],
        "sleep": [(1, c) for c in range(8)],
        "interaction": [(3, c) for c in range(8)],
        # Special: Eating carrot (Row 4)
        "special": [(4, c) for c in range(8)],
    },
}

FILENAME_MAP = {
    "Cat": "Cat.png",
    "CristianoRonaldo": "CristianoRonaldo.png",
    "Dinosaur": "Dinasour.png",
    "Dog": "Dog.png",
    "Hamster": "Hamster.png",
    "LionelMessi": "LionelMessi.png",
    "Parrot": "Parrot.png",
    "Rabbit": "Rabbit.png",
    "Turtle": "Turtle.png",
}

def create_manifest(pet_name: str, anim_counts: dict) -> dict:
    # Set FPS appropriately depending on frame count
    special_fps = 6.0 if anim_counts.get("special", 8) <= 8 else 8.0
    return {
        "name": pet_name,
        "version": 2,
        "spriteSize": {"width": 64, "height": 64},
        "scale": 1,
        "anchorY": 0,
        "animations": {
            "idle": {"fps": 4.0, "loop": True},
            "walk": {"fps": 8.0, "loop": True},
            "sleep": {"fps": 2.0, "loop": True},
            "interaction": {"fps": 6.0, "loop": False},
            "special": {"fps": special_fps, "loop": False},
        },
        "movement": {
            "walkSpeed": 30.0,
            "runSpeed": 60.0,
        },
    }

def process_pet(pet_name: str, filename: str) -> bool:
    sheet_path = SPRITE_SHEET_DIR / filename
    if not sheet_path.exists():
        print(f"ERROR: {sheet_path} not found")
        return False

    img = Image.open(sheet_path).convert("RGBA")
    mapping = PET_ANIMATION_MAPS.get(pet_name)
    if not mapping:
        print(f"ERROR: No animation map for {pet_name}")
        return False

    pet_dir = OUTPUT_DIR / pet_name
    pet_dir.mkdir(parents=True, exist_ok=True)

    anim_counts = {}

    for anim_name, coords in mapping.items():
        anim_dir = pet_dir / anim_name
        # Remove any existing frames in the directory
        if anim_dir.exists():
            for old_file in anim_dir.glob("*.png"):
                old_file.unlink()
        anim_dir.mkdir(parents=True, exist_ok=True)

        anim_counts[anim_name] = len(coords)

        for idx, (row, col) in enumerate(coords):
            x1 = col * CELL_SRC_SIZE
            y1 = row * CELL_SRC_SIZE
            x2 = x1 + CELL_SRC_SIZE
            y2 = y1 + CELL_SRC_SIZE

            cell = img.crop((x1, y1, x2, y2))

            # If sleep animation for pets without dedicated sleep row (Messi, Ronaldo),
            # darken slightly to simulate sleep
            if anim_name == "sleep" and pet_name in ("LionelMessi", "CristianoRonaldo"):
                r, g, b, a = cell.split()
                from PIL import ImageEnhance
                darkened = ImageEnhance.Brightness(cell).enhance(0.7)
                dr, dg, db, _ = darkened.split()
                cell = Image.merge("RGBA", (dr, dg, db, a))

            # Upscale 2x using NEAREST neighbor for 100% crisp 64x64 pixel art
            scaled = cell.resize((TARGET_SIZE, TARGET_SIZE), Image.NEAREST)

            frame_path = anim_dir / f"frame_{idx:02d}.png"
            scaled.save(frame_path, "PNG", optimize=True)

    # Write manifest.json
    manifest = create_manifest(pet_name, anim_counts)
    with open(pet_dir / "manifest.json", "w") as f:
        json.dump(manifest, f, indent=2)

    counts_str = ", ".join(f"{k}: {v}f" for k, v in anim_counts.items())
    print(f"  ✓ {pet_name}: {counts_str}")
    return True

def main():
    print("=" * 60)
    print("DockPet Slicer & 64x64 Pixel Art Renderer")
    print("=" * 60)

    success = 0
    for pet_name, filename in FILENAME_MAP.items():
        if process_pet(pet_name, filename):
            success += 1

    print(f"\nCompleted: {success}/{len(FILENAME_MAP)} pets processed successfully into 64x64 pixel art.")

if __name__ == "__main__":
    main()
