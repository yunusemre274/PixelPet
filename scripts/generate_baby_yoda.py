#!/usr/bin/env python3
"""Build Baby Yoda from ONE reusable pixel model; never redraw him per pose.

The head, ears, gray tunic, sleeves and feet are immutable component images.
Only integer component translations, eyelids, hood and saber change. All
frames use the same 32px grid, palette and ground baseline, upscaled to 64px.
Existing pets/source sheets are never touched. Requires the existing Pillow.
"""

import json
import math
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "Assets/Pets/BabyYoda"
PALETTE = {
    "outline": "#20312c", "green": "#8bbf77", "light": "#b1d58c",
    "shade": "#5e925e", "ear": "#6e9a69", "black": "#000000",
    "gray": "#82898c", "grayLight": "#adb3b4", "grayDark": "#565e64",
    "hilt": "#bfc9cc", "blade": "#8aff8b", "core": "#d4ffd2",
    "glow": "#319f59", "sleep": "#b6c9d4",
}


def canvas():
    return Image.new("RGBA", (32, 32), (0, 0, 0, 0))


def polygon(draw, points, color):
    draw.polygon(points, fill=PALETTE[color])


def rect(draw, box, color):
    draw.rectangle(box, fill=PALETTE[color])


def build_model():
    head = canvas()
    d = ImageDraw.Draw(head)
    for points in [
        [(10, 10), (2, 8), (3, 12), (7, 16), (11, 16)],
        [(21, 10), (29, 8), (28, 12), (24, 16), (20, 16)],
    ]:
        polygon(d, points, "outline")
    polygon(d, [(10, 11), (3, 9), (5, 12), (8, 14), (11, 14)], "green")
    polygon(d, [(21, 11), (28, 9), (26, 12), (23, 14), (20, 14)], "green")
    polygon(d, [(5, 10), (10, 12), (10, 14), (7, 12)], "ear")
    polygon(d, [(26, 10), (21, 12), (21, 14), (24, 12)], "ear")
    polygon(d, [(12, 7), (19, 7), (22, 9), (23, 13), (22, 17),
                (19, 20), (12, 20), (9, 17), (8, 13), (9, 10)], "outline")
    polygon(d, [(12, 8), (19, 8), (21, 10), (22, 13), (21, 17),
                (18, 19), (12, 19), (10, 17), (9, 13), (10, 10)], "green")
    rect(d, (12, 8, 18, 9), "light")
    rect(d, (10, 10, 11, 12), "light")
    rect(d, (20, 10, 21, 12), "shade")
    polygon(d, [(10, 17), (12, 19), (18, 19), (21, 17), (19, 18), (12, 18)], "shade")
    # Enormous pure black eyes, deliberately without white highlights.
    polygon(d, [(11, 11), (13, 10), (15, 11), (15, 15), (13, 16), (11, 15)], "black")
    polygon(d, [(17, 11), (19, 10), (21, 11), (21, 15), (19, 16), (17, 15)], "black")
    rect(d, (15, 16, 16, 16), "light")
    rect(d, (14, 18, 17, 18), "outline")
    sleeping_head = head.copy()
    d = ImageDraw.Draw(sleeping_head)
    for x in [11, 17]:
        rect(d, (x, 10, x + 4, 16), "green")
        d.line([(x, 13), (x + 1, 14), (x + 3, 14), (x + 4, 13)], fill=PALETTE["outline"])

    body = canvas()
    d = ImageDraw.Draw(body)
    polygon(d, [(11, 19), (20, 19), (22, 22), (24, 28), (22, 29),
                (9, 29), (7, 28), (9, 22)], "outline")
    polygon(d, [(11, 20), (20, 20), (21, 23), (23, 27), (21, 28),
                (10, 28), (8, 27), (10, 23)], "gray")
    rect(d, (11, 22, 12, 27), "grayLight")
    rect(d, (20, 23, 21, 27), "grayDark")
    rect(d, (14, 23, 15, 28), "grayDark")
    polygon(d, [(9, 20), (12, 19), (16, 21), (19, 19), (22, 20),
                (20, 22), (16, 23), (12, 22)], "grayDark")
    d.line([(10, 20), (12, 20), (16, 22), (19, 20), (21, 20)], fill=PALETTE["grayLight"])

    arms = []
    for x in [7, 22]:
        arm = canvas()
        d = ImageDraw.Draw(arm)
        rect(d, (x, 21, x + 3, 24), "outline")
        rect(d, (x + 1, 21, x + 2, 23), "gray")
        rect(d, (x, 24, x + 3, 25), "shade")
        rect(d, (x + 1, 24, x + 2, 25), "green")
        arms.append(arm)

    feet = []
    for x in [11, 18]:
        foot = canvas()
        d = ImageDraw.Draw(foot)
        rect(d, (x, 29, x + 3, 30), "outline")
        rect(d, (x + 1, 29, x + 2, 30), "green")
        feet.append(foot)

    hood = canvas()
    d = ImageDraw.Draw(hood)
    polygon(d, [(12, 5), (19, 5), (23, 8), (25, 16), (22, 21),
                (9, 21), (6, 16), (8, 8)], "outline")
    polygon(d, [(12, 6), (19, 6), (22, 9), (24, 16), (21, 20),
                (10, 20), (7, 16), (9, 9)], "grayDark")
    d.line([(9, 10), (10, 8), (13, 6), (18, 6), (21, 8)], fill=PALETTE["grayLight"], width=1)
    return head, sleeping_head, body, arms, feet, hood


MODEL = build_model()


def pose(*, stride=0, raised=0, hood=0, saber=None, blade=1, asleep=False, breathe=0, wave=0):
    head, sleeping_head, body, arms, feet, hood_image = MODEL
    image = canvas()
    # Ground stays at row 30 in every pose; the same gray torso never resizes.
    for foot, dx, dy in [(feet[0], -stride, 0), (feet[1], stride, -abs(stride))]:
        image.alpha_composite(foot, (dx, dy))
    image.alpha_composite(body, (0, -breathe))
    if hood:
        image.alpha_composite(hood_image, (0, (1 - hood) * 2 - breathe))
    image.alpha_composite(sleeping_head if asleep else head, (0, -breathe))
    image.alpha_composite(arms[0], (0, -raised - breathe))
    image.alpha_composite(arms[1], (0, -max(raised, wave) - breathe))
    if saber is not None:
        d = ImageDraw.Draw(image)
        pivot = (24, 24 - raised)
        angle = math.radians(saber)
        tip = (round(pivot[0] + math.sin(angle) * 12 * blade),
               round(pivot[1] - math.cos(angle) * 12 * blade))
        if blade > 0:
            d.line([pivot, tip], fill=PALETTE["glow"], width=3)
            d.line([pivot, tip], fill=PALETTE["blade"], width=2)
            d.line([pivot, tip], fill=PALETTE["core"], width=1)
        rect(d, (23, pivot[1], 25, pivot[1] + 3), "outline")
        rect(d, (24, pivot[1], 24, pivot[1] + 2), "hilt")
    if asleep:
        d = ImageDraw.Draw(image)
        x, y = 25, 5 - breathe
        d.line([(x, y), (x + 3, y), (x, y + 3), (x + 3, y + 3)], fill=PALETTE["sleep"])
    return image.resize((64, 64), Image.Resampling.NEAREST)


def animations():
    training = [pose(hood=1, saber=angle, raised=1)
                for angle in [0, 15, 25, 10, -15, -30, -10, 0]]
    dressing = [pose(raised=n) for n in [0, 2, 4, 5]]
    dressing += [pose(hood=1, raised=n) for n in [5, 4, 2, 0]]
    ignition = [pose(hood=1, saber=0, raised=1, blade=n) for n in [0, 0.3, 0.6, 1]]
    return {
        "idle": [pose(), pose(wave=1)],
        "walk": [pose(stride=n) for n in [0, 1, 0, -1]],
        "sleep": [pose(asleep=True, breathe=n) for n in [0, 0, 1, 1]],
        "interaction": [pose(wave=n) for n in [1, 3, 4, 1]],
        "special": dressing + ignition + training,
        "training": training,
    }


def main():
    sequences = animations()
    for name, frames in sequences.items():
        folder = OUTPUT / name
        folder.mkdir(parents=True, exist_ok=True)
        for index, frame in enumerate(frames):
            frame.save(folder / f"frame_{index:02d}.png", optimize=True)
        for stale in folder.glob("frame_*.png"):
            if int(stale.stem.split("_")[1]) >= len(frames):
                stale.unlink()
    manifest = {
        "name": "BabyYoda", "version": 2,
        "spriteSize": {"width": 64, "height": 64}, "scale": 1,
        "anchorY": 2,  # Two transparent output pixels below the feet.
        "animations": {
            name: {"fps": len(frames) / 5 if name == "special" else
                   {"idle": 2, "walk": 6, "sleep": 2, "interaction": 4, "training": 6}[name],
                   "loop": name not in ("special", "interaction")}
            for name, frames in sequences.items()
        },
        "movement": {"walkSpeed": 85.0, "runSpeed": 130.0},
    }
    (OUTPUT / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print("BabyYoda:", ", ".join(f"{name}={len(frames)}" for name, frames in sequences.items()))


if __name__ == "__main__":
    main()
