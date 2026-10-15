#!/usr/bin/env python3
"""
Advanced Sprite Sheet Slicer & 64x64 Pixel-Art Renderer for DockPet
===================================================================
Produces uniform, cohesive, non-morphing 64×64 pixel-art animation frames
for all 9 pet types:
  - Lionel Messi: Running walk, visible ball skill + Goal celebration + World Cup lift, Rest
  - Cristiano Ronaldo: Running walk, SIU celebration + European cup lift, Rest
  - Turtle: 4-leg walk, skill (Retreat into shell), Sleep with zzz
  - Dog: 4-leg walk, skill (Dancing on hind legs with hearts), Sleep curled up
  - Cat: Consistent walking pose, crouch/paw poses with native yarn effect, Sleep curled up
  - Hamster: Running walk, skill (Eating sunflower seeds & cheek pouch), Sleep with zzz
  - Dinosaur: Stomping walk, skill (Roaring fire stomp), Sleep with zzz
  - Parrot: 2-leg walk, skill (Flying & flapping wings), Sleep with zzz
  - Rabbit: Hopping walk, skill (Eating crunchy carrot), Sleep with zzz
"""

import json
import os
import sys
from pathlib import Path
from PIL import Image

SPRITE_SHEET_DIR = Path("Assets/NewPetDesign")
OUTPUT_DIR = Path("Assets/Pets")
TARGET_SIZE = 64

def create_manifest(pet_name: str, anim_counts: dict) -> dict:
    manifest = {
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
            "special": {"fps": anim_counts["special"] / 5.0, "loop": False},
        },
        "movement": {
            "walkSpeed": 110.0,
            "runSpeed": 160.0,
        },
    }
    if pet_name == "LionelMessi":
        manifest["animations"]["special"]["movingFrames"] = 8
    return manifest

def save_scaled_frame(img_cell: Image.Image, output_path: Path):
    """Upscales 32x32 cell to 64x64 using nearest neighbor, ensuring RGBA mode."""
    if img_cell.mode != "RGBA":
        img_cell = img_cell.convert("RGBA")
    scaled = img_cell.resize((TARGET_SIZE, TARGET_SIZE), Image.NEAREST)
    scaled.save(output_path, "PNG", optimize=True)

def process_standard_pet(pet_name: str, filename: str, mapping: dict):
    sheet_path = SPRITE_SHEET_DIR / filename
    img = Image.open(sheet_path).convert("RGBA")
    pet_dir = OUTPUT_DIR / pet_name
    pet_dir.mkdir(parents=True, exist_ok=True)

    anim_counts = {}

    for anim_name, coords in mapping.items():
        anim_dir = pet_dir / anim_name
        anim_dir.mkdir(parents=True, exist_ok=True)
        for old in anim_dir.glob("*.png"):
            old.unlink()

        anim_counts[anim_name] = len(coords)

        for idx, (row, col) in enumerate(coords):
            x1 = col * 32
            y1 = row * 32
            cell = img.crop((x1, y1, x1 + 32, y1 + 32))

            save_scaled_frame(cell, anim_dir / f"frame_{idx:02d}.png")

    manifest = create_manifest(pet_name, anim_counts)
    with open(pet_dir / "manifest.json", "w") as f:
        json.dump(manifest, f, indent=2)

    counts_str = ", ".join(f"{k}: {v}f" for k, v in anim_counts.items())
    print(f"  ✓ {pet_name}: {counts_str}")

def process_dog():
    pet_name = "Dog"
    sheet_path = SPRITE_SHEET_DIR / "Dog.png"
    img = Image.open(sheet_path).convert("RGBA")
    pet_dir = OUTPUT_DIR / pet_name
    pet_dir.mkdir(parents=True, exist_ok=True)

    # Walk: 4 frames at y=19..45, x=0..128
    walk_dir = pet_dir / "walk"
    walk_dir.mkdir(parents=True, exist_ok=True)
    for old in walk_dir.glob("*.png"): old.unlink()
    for c in range(4):
        cell = img.crop((c * 32, 19, (c + 1) * 32, 45))
        frame = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
        frame.paste(cell, (0, 6))
        save_scaled_frame(frame, walk_dir / f"frame_{c:02d}.png")

    # Idle: 2 frames from walk
    idle_dir = pet_dir / "idle"
    idle_dir.mkdir(parents=True, exist_ok=True)
    for old in idle_dir.glob("*.png"): old.unlink()
    for c in range(4):
        src_c = c % 2
        cell = img.crop((src_c * 32, 19, (src_c + 1) * 32, 45))
        frame = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
        frame.paste(cell, (0, 6))
        save_scaled_frame(frame, idle_dir / f"frame_{c:02d}.png")

    # Sleep: 4 frames at y=19..45, x=128..256
    sleep_dir = pet_dir / "sleep"
    sleep_dir.mkdir(parents=True, exist_ok=True)
    for old in sleep_dir.glob("*.png"): old.unlink()
    for c in range(4):
        cell = img.crop((128 + c * 32, 19, 128 + (c + 1) * 32, 45))
        frame = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
        frame.paste(cell, (0, 6))
        save_scaled_frame(frame, sleep_dir / f"frame_{c:02d}.png")

    # Special (Skill): 8 frames at y=198..242
    special_dir = pet_dir / "special"
    special_dir.mkdir(parents=True, exist_ok=True)
    for old in special_dir.glob("*.png"): old.unlink()
    for c in range(8):
        cell = img.crop((c * 32, 198, (c + 1) * 32, 242)) # 32x44
        frame = Image.new("RGBA", (44, 44), (0, 0, 0, 0))
        frame.paste(cell, (6, 0))
        scaled = frame.resize((TARGET_SIZE, TARGET_SIZE), Image.NEAREST)
        scaled.save(special_dir / f"frame_{c:02d}.png", "PNG", optimize=True)

    # Interaction
    inter_dir = pet_dir / "interaction"
    inter_dir.mkdir(parents=True, exist_ok=True)
    for old in inter_dir.glob("*.png"): old.unlink()
    for c in range(4):
        cell = img.crop(((4 + c) * 32, 198, (5 + c) * 32, 242))
        frame = Image.new("RGBA", (44, 44), (0, 0, 0, 0))
        frame.paste(cell, (6, 0))
        scaled = frame.resize((TARGET_SIZE, TARGET_SIZE), Image.NEAREST)
        scaled.save(inter_dir / f"frame_{c:02d}.png", "PNG", optimize=True)

    manifest = create_manifest(pet_name, {"idle": 4, "walk": 4, "sleep": 4, "interaction": 4, "special": 8})
    with open(pet_dir / "manifest.json", "w") as f:
        json.dump(manifest, f, indent=2)
    print("  ✓ Dog: idle: 4f, walk: 4f, sleep: 4f, interaction: 4f, special: 8f")

def process_cat():
    pet_name = "Cat"
    sheet_path = SPRITE_SHEET_DIR / "Cat.png"
    img = Image.open(sheet_path).convert("RGBA")
    pet_dir = OUTPUT_DIR / pet_name
    pet_dir.mkdir(parents=True, exist_ok=True)

    # Walk: one consistent side-on model; the renderer adds a small stride bob.
    walk_coords = [(6, 5)] * 4
    walk_dir = pet_dir / "walk"
    walk_dir.mkdir(parents=True, exist_ok=True)
    for old in walk_dir.glob("*.png"): old.unlink()
    for idx, (r, c) in enumerate(walk_coords):
        cell = img.crop((c * 32, r * 32, (c + 1) * 32, (r + 1) * 32))
        save_scaled_frame(cell.transpose(Image.Transpose.FLIP_LEFT_RIGHT), walk_dir / f"frame_{idx:02d}.png")

    # Idle: gentle sitting & blinking (Row 0 col 0, col 2, col 0, col 1)
    idle_coords = [(0, 0), (0, 2), (0, 0), (0, 1)]
    idle_dir = pet_dir / "idle"
    idle_dir.mkdir(parents=True, exist_ok=True)
    for old in idle_dir.glob("*.png"): old.unlink()
    for idx, (r, c) in enumerate(idle_coords):
        cell = img.crop((c * 32, r * 32, (c + 1) * 32, (r + 1) * 32))
        save_scaled_frame(cell, idle_dir / f"frame_{idx:02d}.png")

    # Sleep: keep one curled-up silhouette with z (Row 5 col 4).
    sleep_coords = [(5, 4)] * 4
    sleep_dir = pet_dir / "sleep"
    sleep_dir.mkdir(parents=True, exist_ok=True)
    for old in sleep_dir.glob("*.png"): old.unlink()
    for idx, (r, c) in enumerate(sleep_coords):
        cell = img.crop((c * 32, r * 32, (c + 1) * 32, (r + 1) * 32))
        save_scaled_frame(cell, sleep_dir / f"frame_{idx:02d}.png")

    # Special: coherent crouch/paw poses; yarn is a native pixel overlay.
    special_coords = [(2, 0), (5, 7)] * 4
    special_dir = pet_dir / "special"
    special_dir.mkdir(parents=True, exist_ok=True)
    for old in special_dir.glob("*.png"): old.unlink()
    for idx, (r, c) in enumerate(special_coords):
        cell = img.crop((c * 32, r * 32, (c + 1) * 32, (r + 1) * 32))
        save_scaled_frame(cell, special_dir / f"frame_{idx:02d}.png")

    # Interaction
    inter_coords = [(0, 1), (0, 2), (5, 2), (0, 0)]
    inter_dir = pet_dir / "interaction"
    inter_dir.mkdir(parents=True, exist_ok=True)
    for old in inter_dir.glob("*.png"): old.unlink()
    for idx, (r, c) in enumerate(inter_coords):
        cell = img.crop((c * 32, r * 32, (c + 1) * 32, (r + 1) * 32))
        save_scaled_frame(cell, inter_dir / f"frame_{idx:02d}.png")

    manifest = create_manifest(pet_name, {"idle": 4, "walk": 4, "sleep": 4, "interaction": 4, "special": 8})
    with open(pet_dir / "manifest.json", "w") as f:
        json.dump(manifest, f, indent=2)
    print("  ✓ Cat: idle: 4f, walk: 4f, sleep: 4f, interaction: 4f, special: 8f")

def main():
    print("=" * 60)
    print("DockPet Unified Slicer & Cohesive Pixel Art Pipeline")
    print("=" * 60)

    # 1. Cristiano Ronaldo: 8 walk, 4 rest, 20 skill frames (SIU + cup lift/hold).
    process_standard_pet("CristianoRonaldo", "CristianoRonaldo.png", {
        "idle": [(0, c) for c in range(8)],
        "walk": [(1, c) for c in range(8)],
        "sleep": [(7, 7)] * 4,
        "interaction": [(5, c) for c in range(8)],
        # Skill: SIU (8f), then silver European cup lift with a final hold (12f).
        "special": [(6, c) for c in range(8)] + [(4, c) for c in [0, 1, 2, 3, 3, 3, 3, 3, 3, 3, 3, 3]],
    })

    # 2. Lionel Messi: 8 walk, 4 rest, 24 skill frames (ball + celebration + World Cup).
    process_standard_pet("LionelMessi", "LionelMessi.png", {
        "idle": [(0, c) for c in range(8)],
        "walk": [(2, c) for c in range(8)],
        "sleep": [(3, 0)] * 4,
        "interaction": [(3, c) for c in range(8)],
        # Skill: visible ball (8f), goal celebration (8f), World Cup ending overhead (8f).
        "special": [(1, c) for c in range(8)] + [(6, c) for c in range(8)] + [(5, c) for c in [2, 3, 4, 5, 6, 0, 1, 7]],
    })

    # 3. Turtle: 8 frames walk on 4 legs, 8 frames sleep with zzz, 8 frames skill (shell retreat)
    process_standard_pet("Turtle", "Turtle.png", {
        "idle": [(1, c) for c in range(4)],
        "walk": [(0, c) for c in range(8)],
        "sleep": [(3, c) for c in range(8)],
        "interaction": [(7, c) for c in range(8)],
        "special": [(2, c) for c in range(8)], # Retract into shell
    })

    # 4. Dinosaur: 8 frames stomping walk, 8 frames sleep, 8 frames skill (fire roar)
    process_standard_pet("Dinosaur", "Dinasour.png", {
        "idle": [(0, c) for c in range(8)],
        "walk": [(2, c) for c in range(8)],
        "sleep": [(1, c) for c in range(8)],
        "interaction": [(3, c) for c in range(8)],
        "special": [(4, c) for c in range(8)],
    })

    # 5. Hamster: 8 frames running walk, 8 frames sleep, 8 frames skill (chewing seeds)
    process_standard_pet("Hamster", "Hamster.png", {
        "idle": [(0, c) for c in range(4)],
        "walk": [(2, c) for c in range(8)],
        "sleep": [(1, c) for c in range(8)],
        "interaction": [(3, c) for c in range(8)],
        "special": [(4, c) for c in range(8)],
    })

    # 6. Parrot: 8 frames walking, 8 frames sleep, 8 frames skill (flying & flapping)
    process_standard_pet("Parrot", "Parrot.png", {
        "idle": [(0, c) for c in range(8)],
        "walk": [(2, c) for c in range(8)],
        "sleep": [(1, c) for c in range(8)],
        "interaction": [(3, c) for c in range(8)],
        "special": [(5, c) for c in range(8)],
    })

    # 7. Rabbit: 8 frames hopping walk, 8 frames sleep, 8 frames skill (eating carrot)
    process_standard_pet("Rabbit", "Rabbit.png", {
        "idle": [(0, c) for c in range(8)],
        "walk": [(2, c) for c in range(8)],
        "sleep": [(1, c) for c in range(8)],
        "interaction": [(3, c) for c in range(8)],
        "special": [(4, c) for c in range(8)],
    })

    # 8. Dog: Clean crop walk, sleep, and heart dancing skill
    process_dog()

    # 9. Cat: Coherent ginger cat walk, sleep with z, and paw/yarn skill.
    process_cat()

    print("\nAll 9 pets successfully processed with cohesive, non-morphing animations.")

if __name__ == "__main__":
    main()
