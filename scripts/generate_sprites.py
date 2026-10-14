#!/usr/bin/env python3
"""
DockPet Pixel-Art Sprite Generator
Generates 32x32 retro pixel-art PNG sprites with transparency for all 7 pet types:
- Cat
- Dog
- Parrot
- Rabbit
- Turtle
- Dinosaur
- Hamster

Follows DockPet asset pipeline (docs/ASSET_PIPELINE.md):
- Exact 32x32 RGBA PNGs
- Hard pixel edges (no anti-aliasing)
- Transparent background
- Character facing right
- Manifest.json for each pet
- Animations: idle (3 frames), walk (4 frames), sleep (2 frames)
"""

import json
import os
import sys
from pathlib import Path
from PIL import Image

def hex_to_rgba(hex_str, alpha=255):
    hex_str = hex_str.lstrip('#')
    return (int(hex_str[0:2], 16), int(hex_str[2:4], 16), int(hex_str[4:6], 16), alpha)

# ==============================================================================
# PALETTES
# ==============================================================================

PALETTE_CAT = {
    '.': (0, 0, 0, 0),
    'B': hex_to_rgba("#3b1805"), # Outline / deep shadow
    'O': hex_to_rgba("#e6761b"), # Main ginger orange
    'L': hex_to_rgba("#f59336"), # Lighter orange highlight
    'S': hex_to_rgba("#ba5009"), # Stripe / shaded orange
    'W': hex_to_rgba("#fff3de"), # Cream / white muzzle, belly, paws
    'P': hex_to_rgba("#ff92a5"), # Pink nose & inner ear
    'G': hex_to_rgba("#2ecc71"), # Emerald green eye
    'D': hex_to_rgba("#103a1d"), # Pupil
    'H': hex_to_rgba("#ffffff"), # White eye shine
    'Z': hex_to_rgba("#a855f7"), # Purple ZZZ
    'R': hex_to_rgba("#ff2d55"), # Heart rose red
}

PALETTE_DOG = {
    '.': (0, 0, 0, 0),
    'B': hex_to_rgba("#351a08"), # Deep brown outline
    'M': hex_to_rgba("#8c5828"), # Medium golden brown
    'L': hex_to_rgba("#ba7e3c"), # Light brown highlight
    'E': hex_to_rgba("#593111"), # Dark brown floppy ears
    'C': hex_to_rgba("#faebd7"), # Cream snout, belly, paws
    'D': hex_to_rgba("#150e08"), # Dark eye & nose
    'H': hex_to_rgba("#ffffff"), # White eye shine
    'P': hex_to_rgba("#ff7675"), # Tongue / pink
    'Z': hex_to_rgba("#9c27b0"), # Sleep Z
    'R': hex_to_rgba("#ff2d55"), # Heart rose red
}

PALETTE_PARROT = {
    '.': (0, 0, 0, 0),
    'B': hex_to_rgba("#0f3319"), # Deep jungle outline
    'G': hex_to_rgba("#27ae60"), # Parrot green
    'L': hex_to_rgba("#58d68d"), # Light lime highlight
    'R': hex_to_rgba("#e74c3c"), # Scarlet red crown/crest
    'O': hex_to_rgba("#f39c12"), # Orange-yellow cheek
    'A': hex_to_rgba("#2980b9"), # Blue wing
    'C': hex_to_rgba("#3498db"), # Sky blue wing stripe
    'K': hex_to_rgba("#f39c12"), # Golden beak
    'T': hex_to_rgba("#d35400"), # Dark beak tip / claw
    'D': hex_to_rgba("#17202a"), # Eye dark
    'H': hex_to_rgba("#ffffff"), # Eye shine
    'Z': hex_to_rgba("#9c27b0"), # Sleep Z
}

PALETTE_RABBIT = {
    '.': (0, 0, 0, 0),
    'B': hex_to_rgba("#475569"), # Slate outline
    'W': hex_to_rgba("#ffffff"), # White fur
    'S': hex_to_rgba("#e2e8f0"), # Soft shading
    'G': hex_to_rgba("#cbd5e1"), # Deep shading
    'P': hex_to_rgba("#ffb6c1"), # Pink inner ear
    'N': hex_to_rgba("#ff6b81"), # Pink nose
    'D': hex_to_rgba("#3f101f"), # Ruby eye
    'H': hex_to_rgba("#ffffff"), # Eye shine
    'Z': hex_to_rgba("#9c27b0"), # Sleep Z
    'R': hex_to_rgba("#ff2d55"), # Heart rose red
}

PALETTE_TURTLE = {
    '.': (0, 0, 0, 0),
    'B': hex_to_rgba("#13361a"), # Dark shell/skin outline
    'G': hex_to_rgba("#27ae60"), # Green turtle skin
    'L': hex_to_rgba("#58d68d"), # Light skin highlight
    'S': hex_to_rgba("#1e8449"), # Dark forest shell scutes
    'E': hex_to_rgba("#52be80"), # Light emerald scute centers
    'Y': hex_to_rgba("#f1c40f"), # Golden shell rim
    'C': hex_to_rgba("#f9e79f"), # Tan claws
    'D': hex_to_rgba("#141d16"), # Dark eye
    'H': hex_to_rgba("#ffffff"), # Eye shine
    'Z': hex_to_rgba("#9c27b0"), # Sleep Z
    'R': hex_to_rgba("#ff2d55"), # Heart rose red
}

PALETTE_DINOSAUR = {
    '.': (0, 0, 0, 0),
    'B': hex_to_rgba("#2b1040"), # Deep purple outline
    'M': hex_to_rgba("#8e24aa"), # Vibrant dino purple
    'L': hex_to_rgba("#ab47bc"), # Light purple highlight
    'V': hex_to_rgba("#f3e5f5"), # Soft lilac belly
    'K': hex_to_rgba("#00e5ff"), # Cyan dorsal spikes
    'J': hex_to_rgba("#0097a7"), # Cyan shade
    'D': hex_to_rgba("#180926"), # Dark eye
    'H': hex_to_rgba("#ffffff"), # White eye shine & tooth
    'P': hex_to_rgba("#ff80ab"), # Cute pink blush
    'Z': hex_to_rgba("#9c27b0"), # Sleep Z
    'R': hex_to_rgba("#ff2d55"), # Heart rose red
}

PALETTE_HAMSTER = {
    '.': (0, 0, 0, 0),
    'B': hex_to_rgba("#42210b"), # Roasted brown outline
    'O': hex_to_rgba("#e67e22"), # Golden apricot fur
    'L': hex_to_rgba("#f39c12"), # Light golden fur
    'W': hex_to_rgba("#ffffff"), # White belly & cheeks
    'S': hex_to_rgba("#ede8de"), # Shaded white
    'P': hex_to_rgba("#ff9aa2"), # Pink ear/nose/paws
    'D': hex_to_rgba("#1a1007"), # Dark beady eye
    'H': hex_to_rgba("#ffffff"), # Eye glint
    'Z': hex_to_rgba("#9c27b0"), # Sleep Z
    'R': hex_to_rgba("#ff2d55"), # Heart rose red
}

# ==============================================================================
# SPRITE DATA (32x32 ASCII GRIDS)
# ==============================================================================

# --- CAT ---
CAT_FRAMES = {
    "idle": [
        [
            "................................", # 0
            "................................", # 1
            "................................", # 2
            "................................", # 3
            "................................", # 4
            "..................BB......BB....", # 5
            "........BBB......BPB....BPB.....", # 6
            ".......BOOB.....BOPB....BOPB....", # 7
            ".......BOOB.....BOOBBBBBBOOB....", # 8
            "........BOOB...BOOOOOOOOOOOOB...", # 9
            "........BOOB...BOOLLOOOOOLLOB...", # 10
            ".........BOB..BOOOSLOOOOOLOOB...", # 11
            ".........BOB..BOLSSOOOGGHOOOB...", # 12
            ".........BOB..BOOOOOOGDGPOOB....", # 13
            "........BOOB..BOOOOWWWGPOOOB....", # 14
            ".......BOOB...BOOOWWWWWPPOB.....", # 15
            "......BOOB...BBOOOWWWWWWWOB.....", # 16
            "......BOB...BOOOOOOOOOOWOB......", # 17
            ".....BOOB..BOOOOOOOOOOOOB.......", # 18
            ".....BOOB.BOOOOOOOOOOOOOOB......", # 19
            "....BOOB.BOOSSBOOSSBOOOOOOB.....", # 20
            "....BOOB.BOOSB.BOOSB.OOOOOOB....", # 21
            "....BOB.BOOOOOOOOOOOOOOOOOOB....", # 22
            "....BOB.BOWWWWWWWWWWWWWWWWOB....", # 23
            "....BBB.BOWWWWWWWWWWWWWWWWOB....", # 24
            "........BSSBBBSSBB..BOOBBBOB....", # 25
            "........BSSB..BSSB..BOOB..BOB...", # 26
            "........BSSB..BSSB..BOOB..BOB...", # 27
            "........BOOB..BOOB..BOOB..BOB...", # 28
            ".......BWWWB.BWWWB.BWWWB.BWWWB..", # 29
            ".......BBBBB.BBBBB.BBBBB.BBBBB..", # 30
            "................................", # 31
        ],
        [
            "................................", # 0
            "................................", # 1
            "................................", # 2
            "................................", # 3
            "................................", # 4
            "..................BB......BB....", # 5
            ".........BBB.....BPB....BPB.....", # 6
            "........BOOB....BOPB....BOPB....", # 7
            "........BOOB....BOOBBBBBBOOB....", # 8
            ".........BOOB..BOOOOOOOOOOOOB...", # 9
            ".........BOOB..BOOLLOOOOOLLOB...", # 10
            "..........BOB.BOOOSLOOOOOLOOB...", # 11
            "..........BOB.BOLSSOOOGGHOOOB...", # 12
            "..........BOB.BOOOOOOGDGPOOB....", # 13
            ".........BOOB.BOOOOWWWGPOOOB....", # 14
            "........BOOB..BOOOWWWWWPPOB.....", # 15
            ".......BOOB..BBOOOWWWWWWWOB.....", # 16
            "......BOOB..BOOOOOOOOOOWOB......", # 17
            ".....BOOB..BOOOOOOOOOOOOB.......", # 18
            "....BOOB..BOOOOOOOOOOOOOOB......", # 19
            "....BOOB.BOOSSBOOSSBOOOOOOB.....", # 20
            "....BOB..BOOSB.BOOSB.OOOOOOB....", # 21
            "....BOB.BOOOOOOOOOOOOOOOOOOB....", # 22
            "....BBB.BOWWWWWWWWWWWWWWWWOB....", # 23
            "........BOWWWWWWWWWWWWWWWWOB....", # 24
            "........BSSBBBSSBB..BOOBBBOB....", # 25
            "........BSSB..BSSB..BOOB..BOB...", # 26
            "........BSSB..BSSB..BOOB..BOB...", # 27
            "........BOOB..BOOB..BOOB..BOB...", # 28
            ".......BWWWB.BWWWB.BWWWB.BWWWB..", # 29
            ".......BBBBB.BBBBB.BBBBB.BBBBB..", # 30
            "................................", # 31
        ],
        [
            "................................", # 0
            "................................", # 1
            "................................", # 2
            "................................", # 3
            "................................", # 4
            "..................BB......BB....", # 5
            "........BBB......BPB....BPB.....", # 6
            ".......BOOB.....BOPB....BOPB....", # 7
            ".......BOOB.....BOOBBBBBBOOB....", # 8
            "........BOOB...BOOOOOOOOOOOOB...", # 9
            "........BOOB...BOOLLOOOOOLLOB...", # 10
            ".........BOB..BOOOSLOOOOOLOOB...", # 11
            ".........BOB..BOLSSOOOOOOOOOB...", # 12
            ".........BOB..BOOOOOOBBBPOOB....", # 13 eye closed (BBB)
            "........BOOB..BOOOOWWWBBPOOB....", # 14
            ".......BOOB...BOOOWWWWWPPOB.....", # 15
            "......BOOB...BBOOOWWWWWWWOB.....", # 16
            "......BOB...BOOOOOOOOOOWOB......", # 17
            ".....BOOB..BOOOOOOOOOOOOB.......", # 18
            ".....BOOB.BOOOOOOOOOOOOOOB......", # 19
            "....BOOB.BOOSSBOOSSBOOOOOOB.....", # 20
            "....BOOB.BOOSB.BOOSB.OOOOOOB....", # 21
            "....BOB.BOOOOOOOOOOOOOOOOOOB....", # 22
            "....BOB.BOWWWWWWWWWWWWWWWWOB....", # 23
            "....BBB.BOWWWWWWWWWWWWWWWWOB....", # 24
            "........BSSBBBSSBB..BOOBBBOB....", # 25
            "........BSSB..BSSB..BOOB..BOB...", # 26
            "........BSSB..BSSB..BOOB..BOB...", # 27
            "........BOOB..BOOB..BOOB..BOB...", # 28
            ".......BWWWB.BWWWB.BWWWB.BWWWB..", # 29
            ".......BBBBB.BBBBB.BBBBB.BBBBB..", # 30
            "................................", # 31
        ]
    ],
    "walk": [
        [
            "................................", # 0
            "................................", # 1
            "................................", # 2
            "................................", # 3
            "................................", # 4
            "..................BB......BB....", # 5
            "........BBB......BPB....BPB.....", # 6
            ".......BOOB.....BOPB....BOPB....", # 7
            ".......BOOB.....BOOBBBBBBOOB....", # 8
            "........BOOB...BOOOOOOOOOOOOB...", # 9
            "........BOOB...BOOLLOOOOOLLOB...", # 10
            ".........BOB..BOOOSLOOOOOLOOB...", # 11
            ".........BOB..BOLSSOOOGGHOOOB...", # 12
            ".........BOB..BOOOOOOGDGPOOB....", # 13
            "........BOOB..BOOOOWWWGPOOOB....", # 14
            ".......BOOB...BOOOWWWWWPPOB.....", # 15
            "......BOOB...BBOOOWWWWWWWOB.....", # 16
            "......BOB...BOOOOOOOOOOWOB......", # 17
            ".....BOOB..BOOOOOOOOOOOOB.......", # 18
            ".....BOOB.BOOOOOOOOOOOOOOB......", # 19
            "....BOOB.BOOSSBOOSSBOOOOOOB.....", # 20
            "....BOOB.BOOSB.BOOSB.OOOOOOB....", # 21
            "....BOB.BOOOOOOOOOOOOOOOOOOB....", # 22
            "....BOB.BOWWWWWWWWWWWWWWWWOB....", # 23
            "....BBB.BOWWWWWWWWWWWWWWWWOB....", # 24
            ".......BSSB.BBSSBB..BOOB.BB.....", # 25
            "......BSSB...BSSB...BOOB..BOB...", # 26
            "......BSSB....BSSB...BOOB..BOB..", # 27
            ".....BWWWB....BSSB..BOOB..BWWWB.", # 28
            ".....BBBBB...BWWWB..BWWWB..BBBBB", # 29
            ".............BBBBB..BBBBB.......", # 30
            "................................", # 31
        ],
        [
            "................................", # 0
            "................................", # 1
            "................................", # 2
            "................................", # 3
            "..................BB......BB....", # 4 (up 1px)
            "........BBB......BPB....BPB.....", # 5
            ".......BOOB.....BOPB....BOPB....", # 6
            ".......BOOB.....BOOBBBBBBOOB....", # 7
            "........BOOB...BOOOOOOOOOOOOB...", # 8
            "........BOOB...BOOLLOOOOOLLOB...", # 9
            ".........BOB..BOOOSLOOOOOLOOB...", # 10
            ".........BOB..BOLSSOOOGGHOOOB...", # 11
            ".........BOB..BOOOOOOGDGPOOB....", # 12
            "........BOOB..BOOOOWWWGPOOOB....", # 13
            ".......BOOB...BOOOWWWWWPPOB.....", # 14
            "......BOOB...BBOOOWWWWWWWOB.....", # 15
            "......BOB...BOOOOOOOOOOWOB......", # 16
            ".....BOOB..BOOOOOOOOOOOOB.......", # 17
            ".....BOOB.BOOOOOOOOOOOOOOB......", # 18
            "....BOOB.BOOSSBOOSSBOOOOOOB.....", # 19
            "....BOOB.BOOSB.BOOSB.OOOOOOB....", # 20
            "....BOB.BOOOOOOOOOOOOOOOOOOB....", # 21
            "....BOB.BOWWWWWWWWWWWWWWWWOB....", # 22
            "....BBB.BOWWWWWWWWWWWWWWWWOB....", # 23
            "........BSSBBBSSBB..BOOBBBOB....", # 24
            "........BSSB..BSSB..BOOB..BOB...", # 25
            "........BSSB..BSSB..BOOB..BOB...", # 26
            "........BWWWB.BSSB..BOOB.BWWWB..", # 27
            "........BBBBB.BWWWB.BWWWB.BBBB..", # 28
            "..............BBBBB.BBBBB.......", # 29
            "................................", # 30
            "................................", # 31
        ],
        [
            "................................", # 0
            "................................", # 1
            "................................", # 2
            "................................", # 3
            "................................", # 4
            "..................BB......BB....", # 5
            "........BBB......BPB....BPB.....", # 6
            ".......BOOB.....BOPB....BOPB....", # 7
            ".......BOOB.....BOOBBBBBBOOB....", # 8
            "........BOOB...BOOOOOOOOOOOOB...", # 9
            "........BOOB...BOOLLOOOOOLLOB...", # 10
            ".........BOB..BOOOSLOOOOOLOOB...", # 11
            ".........BOB..BOLSSOOOGGHOOOB...", # 12
            ".........BOB..BOOOOOOGDGPOOB....", # 13
            "........BOOB..BOOOOWWWGPOOOB....", # 14
            ".......BOOB...BOOOWWWWWPPOB.....", # 15
            "......BOOB...BBOOOWWWWWWWOB.....", # 16
            "......BOB...BOOOOOOOOOOWOB......", # 17
            ".....BOOB..BOOOOOOOOOOOOB.......", # 18
            ".....BOOB.BOOOOOOOOOOOOOOB......", # 19
            "....BOOB.BOOSSBOOSSBOOOOOOB.....", # 20
            "....BOOB.BOOSB.BOOSB.OOOOOOB....", # 21
            "....BOB.BOOOOOOOOOOOOOOOOOOB....", # 22
            "....BOB.BOWWWWWWWWWWWWWWWWOB....", # 23
            "....BBB.BOWWWWWWWWWWWWWWWWOB....", # 24
            "........BB..BSSBB...BOOB.BSSB...", # 25
            ".......BSSB..BSSB...BOOB..BOB...", # 26
            "......BSSB....BSSB...BOOB..BOB..", # 27
            ".....BWWWB....BOOB...BWWWB..BOB.", # 28
            ".....BBBBB...BWWWB...BBBBB.BWWWB", # 29
            ".............BBBBB.........BBBBB", # 30
            "................................", # 31
        ],
        [
            "................................", # 0
            "................................", # 1
            "................................", # 2
            "................................", # 3
            "..................BB......BB....", # 4 (up 1px)
            "........BBB......BPB....BPB.....", # 5
            ".......BOOB.....BOPB....BOPB....", # 6
            ".......BOOB.....BOOBBBBBBOOB....", # 7
            "........BOOB...BOOOOOOOOOOOOB...", # 8
            "........BOOB...BOOLLOOOOOLLOB...", # 9
            ".........BOB..BOOOSLOOOOOLOOB...", # 10
            ".........BOB..BOLSSOOOGGHOOOB...", # 11
            ".........BOB..BOOOOOOGDGPOOB....", # 12
            "........BOOB..BOOOOWWWGPOOOB....", # 13
            ".......BOOB...BOOOWWWWWPPOB.....", # 14
            "......BOOB...BBOOOWWWWWWWOB.....", # 15
            "......BOB...BOOOOOOOOOOWOB......", # 16
            ".....BOOB..BOOOOOOOOOOOOB.......", # 17
            ".....BOOB.BOOOOOOOOOOOOOOB......", # 18
            "....BOOB.BOOSSBOOSSBOOOOOOB.....", # 19
            "....BOOB.BOOSB.BOOSB.OOOOOOB....", # 20
            "....BOB.BOOOOOOOOOOOOOOOOOOB....", # 21
            "....BOB.BOWWWWWWWWWWWWWWWWOB....", # 22
            "....BBB.BOWWWWWWWWWWWWWWWWOB....", # 23
            "........BSSBBBSSBB..BOOBBBOB....", # 24
            "........BSSB..BSSB..BOOB..BOB...", # 25
            "........BSSB..BSSB..BOOB..BOB...", # 26
            "........BSSB.BWWWB..BWWWB.BOB...", # 27
            ".......BWWWB.BBBBB..BBBBB.BWWWB.", # 28
            ".......BBBBB..............BBBBB.", # 29
            "................................", # 30
            "................................", # 31
        ]
    ],
    "sleep": [
        [
            "................................", # 0
            "................................", # 1
            "................................", # 2
            "................................", # 3
            "................................", # 4
            "................................", # 5
            "................................", # 6
            "................................", # 7
            "................................", # 8
            "................................", # 9
            "................................", # 10
            "................................", # 11
            "......................ZZ........", # 12 'z'
            ".......................Z........", # 13
            "......................ZZ........", # 14
            "...................BB......BB...", # 15
            "..................BPB....BPB....", # 16
            "........BBBB.....BOPB....BOPB...", # 17
            ".......BOOOOB...BOOOOOOOOOOOB...", # 18
            "......BOOSSOOB.BOOOOOOOOOOOOB...", # 19
            ".....BOOSSBOOBBOOOOOOOOOOOOB....", # 20
            "....BOOSB.BOOBBOOOOBBBPOOOB.....", # 21 closed eye
            "....BOOB..BOOBBOOOWWWWWPPOB.....", # 22
            "....BOOB..BOOBBOOOWWWWWWWOB.....", # 23
            "....BOOB.BOOOOOOOOOOOOOOOB......", # 24
            "....BOOB.BOWWWWWWWWWWWWWOB......", # 25
            "....BOOB.BOWWWWWWWWWWWWOB.......", # 26
            ".....BOOB.BOWWWWWWWWWWWOB.......", # 27
            "......BOOB.BWWWWWWWWWWOB........", # 28
            ".......BOOBBBBBBBBBBBBB.........", # 29
            "........BBB.....................", # 30
            "................................", # 31
        ],
        [
            "................................", # 0
            "................................", # 1
            "................................", # 2
            "................................", # 3
            "................................", # 4
            "................................", # 5
            ".......................ZZZ......", # 6 big 'Z'
            ".........................Z......", # 7
            ".......................ZZZ......", # 8
            "................................", # 9
            "....................ZZ..........", # 10 small 'z'
            ".....................Z..........", # 11
            "....................ZZ..........", # 12
            "................................", # 13
            "................................", # 14
            "...................BB......BB...", # 15
            "..................BPB....BPB....", # 16
            "........BBBB.....BOPB....BOPB...", # 17
            ".......BOOOOB...BOOOOOOOOOOOB...", # 18
            "......BOOSSOOB.BOOOOOOOOOOOOB...", # 19
            ".....BOOSSBOOBBOOOOOOOOOOOOB....", # 20
            "....BOOSB.BOOBBOOOOBBBPOOOB.....", # 21
            "....BOOB..BOOBBOOOWWWWWPPOB.....", # 22
            "....BOOB..BOOBBOOOWWWWWWWOB.....", # 23
            "....BOOB.BOOOOOOOOOOOOOOOB......", # 24
            "....BOOB.BOWWWWWWWWWWWWWOB......", # 25
            "....BOOB.BOWWWWWWWWWWWWOB.......", # 26
            ".....BOOB.BOWWWWWWWWWWWOB.......", # 27
            "......BOOB.BWWWWWWWWWWOB........", # 28
            ".......BOOBBBBBBBBBBBBB.........", # 29
            "........BBB.....................", # 30
            "................................", # 31
        ]
    ]
}

# --- DOG ---
DOG_FRAMES = {
    "idle": [
        [
            "................................", # 0
            "................................", # 1
            "................................", # 2
            "................................", # 3
            "................................", # 4
            "................................", # 5
            "...................BBBBBB.......", # 6
            "..................BLLMLLLB......", # 7
            "........BB.......BLLMMMMMLB.....", # 8
            ".......BMLB.....BEELLMMMMMEB....", # 9
            ".......BMLB.....BEEEMMMMMMEEB...", # 10
            "........BMB.....BEEEMMMDMMEEB...", # 11
            "........BMB.....BEEEMMDHMMEEB...", # 12
            "........BMB....BEEEMMMDMMCCB....", # 13
            ".........BB...BEEEMMMCCCCDDB....", # 14
            "..........B..BEEEMMMMCCCCCCB....", # 15
            ".........BB.BEEEMMMMMMCCCCB.....", # 16
            "........BMMBBEEEMMMMMMMMBB......", # 17
            ".......BLLMMMMMMMMMMMMMMB.......", # 18
            "......BLLMMMMMMMMMMMMMMMMB......", # 19
            "......BMMMMMMMMMMMMMMMMMMB......", # 20
            "......BMMMMMMMMMMCCCCCCCCB......", # 21
            "......BMMMMMMMMMCCCCCCCCB.......", # 22
            ".......BMMMMMMMMCCCCCCCCB.......", # 23
            ".......BBBBBBBBBBBBBBBBB........", # 24
            "........BEBBMB....BEBBMB........", # 25
            "........BEBBMB....BEBBMB........", # 26
            "........BEBBMB....BEBBMB........", # 27
            "........BEBBMB....BEBBMB........", # 28
            ".......BCCBCCB...BCCBCCB........", # 29
            ".......BBBBBBB...BBBBBBB........", # 30
            "................................", # 31
        ],
        [
            "................................", # 0
            "................................", # 1
            "................................", # 2
            "................................", # 3
            "................................", # 4
            "................................", # 5
            "...................BBBBBB.......", # 6
            "..........BB......BLLMLLLB......", # 7
            ".........BMLB....BLLMMMMMLB.....", # 8
            ".........BMLB...BEELLMMMMMEB....", # 9
            "..........BMB...BEEEMMMMMMEEB...", # 10
            "..........BMB...BEEEMMMDMMEEB...", # 11
            "..........BMB...BEEEMMDHMMEEB...", # 12
            "...........BB..BEEEMMMDMMCCB....", # 13
            "............B.BEEEMMMCCCCDDB....", # 14
            "...........B.BEEEMMMMCCCCCCB....", # 15
            "..........B.BEEEMMMMMMCCCCB.....", # 16
            "........BMMBBEEEMMMMMMMMBB......", # 17
            ".......BLLMMMMMMMMMMMMMMB.......", # 18
            "......BLLMMMMMMMMMMMMMMMMB......", # 19
            "......BMMMMMMMMMMMMMMMMMMB......", # 20
            "......BMMMMMMMMMMCCCCCCCCB......", # 21
            "......BMMMMMMMMMCCCCCCCCB.......", # 22
            ".......BMMMMMMMMCCCCCCCCB.......", # 23
            ".......BBBBBBBBBBBBBBBBB........", # 24
            "........BEBBMB....BEBBMB........", # 25
            "........BEBBMB....BEBBMB........", # 26
            "........BEBBMB....BEBBMB........", # 27
            "........BEBBMB....BEBBMB........", # 28
            ".......BCCBCCB...BCCBCCB........", # 29
            ".......BBBBBBB...BBBBBBB........", # 30
            "................................", # 31
        ],
        [
            "................................", # 0
            "................................", # 1
            "................................", # 2
            "................................", # 3
            "................................", # 4
            "................................", # 5
            "...................BBBBBB.......", # 6
            "..................BLLMLLLB......", # 7
            "........BB.......BLLMMMMMLB.....", # 8
            ".......BMLB.....BEELLMMMMMEB....", # 9
            ".......BMLB.....BEEEMMMMMMEEB...", # 10
            "........BMB.....BEEEMMMMMMEEB...", # 11
            "........BMB.....BEEEMMBBBMEEB...", # 12 closed eye (BBB)
            "........BMB....BEEEMMMMMMCCB....", # 13
            ".........BB...BEEEMMMCCCCDDB....", # 14
            "..........B..BEEEMMMMCCCCCCB....", # 15
            ".........BB.BEEEMMMMMMCCCCB.....", # 16
            "........BMMBBEEEMMMMMMMMBB......", # 17
            ".......BLLMMMMMMMMMMMMMMB.......", # 18
            "......BLLMMMMMMMMMMMMMMMMB......", # 19
            "......BMMMMMMMMMMMMMMMMMMB......", # 20
            "......BMMMMMMMMMMCCCCCCCCB......", # 21
            "......BMMMMMMMMMCCCCCCCCB.......", # 22
            ".......BMMMMMMMMCCCCCCCCB.......", # 23
            ".......BBBBBBBBBBBBBBBBB........", # 24
            "........BEBBMB....BEBBMB........", # 25
            "........BEBBMB....BEBBMB........", # 26
            "........BEBBMB....BEBBMB........", # 27
            "........BEBBMB....BEBBMB........", # 28
            ".......BCCBCCB...BCCBCCB........", # 29
            ".......BBBBBBB...BBBBBBB........", # 30
            "................................", # 31
        ]
    ],
    "walk": [
        [
            "................................", # 0
            "................................", # 1
            "................................", # 2
            "................................", # 3
            "................................", # 4
            "................................", # 5
            "...................BBBBBB.......", # 6
            "........BB........BLLMLLLB......", # 7
            ".......BMLB......BLLMMMMMLB.....", # 8
            ".......BMLB.....BEELLMMMMMEB....", # 9
            "........BMB.....BEEEMMMMMMEEB...", # 10
            "........BMB.....BEEEMMMDMMEEB...", # 11
            "........BMB.....BEEEMMDHMMEEB...", # 12
            ".........BB....BEEEMMMDMMCCB....", # 13
            "..........B...BEEEMMMCCCCDDB....", # 14
            ".........BB..BEEEMMMMCCCCCCB....", # 15
            "........BMMBBEEEMMMMMMCCCCB.....", # 16
            ".......BLLMMBBMMMMMMMMMMBB......", # 17
            "......BLLMMMMMMMMMMMMMMMB.......", # 18
            "......BMMMMMMMMMMMMMMMMMMB......", # 19
            "......BMMMMMMMMMMCCCCCCCCB......", # 20
            "......BMMMMMMMMMCCCCCCCCB.......", # 21
            ".......BMMMMMMMMCCCCCCCCB.......", # 22
            ".......BBBBBBBBBBBBBBBBB........", # 23
            ".......BEB..BMB....BEB..BMB.....", # 24
            "......BEB....BMB..BEB....BMB....", # 25
            ".....BEB.....BMB...BEB....BMB...", # 26
            "....BCCB.....BCCB.BCCB....BCCB..", # 27
            "....BBBB.....BBBB.BBBB....BBBB..", # 28
            "................................", # 29
            "................................", # 30
            "................................", # 31
        ],
        [
            "................................", # 0
            "................................", # 1
            "................................", # 2
            "................................", # 3
            "................................", # 4
            "...................BBBBBB.......", # 5 (up 1px)
            "..........BB......BLLMLLLB......", # 6
            ".........BMLB....BLLMMMMMLB.....", # 7
            ".........BMLB...BEELLMMMMMEB....", # 8
            "..........BMB...BEEEMMMMMMEEB...", # 9
            "..........BMB...BEEEMMMDMMEEB...", # 10
            "..........BMB...BEEEMMDHMMEEB...", # 11
            "...........BB..BEEEMMMDMMCCB....", # 12
            "............B.BEEEMMMCCCCDDB....", # 13
            "...........B.BEEEMMMMCCCCCCB....", # 14
            "..........B.BEEEMMMMMMCCCCB.....", # 15
            "........BMMBBEEEMMMMMMMMBB......", # 16
            ".......BLLMMMMMMMMMMMMMMB.......", # 17
            "......BLLMMMMMMMMMMMMMMMMB......", # 18
            "......BMMMMMMMMMMMMMMMMMMB......", # 19
            "......BMMMMMMMMMMCCCCCCCCB......", # 20
            "......BMMMMMMMMMCCCCCCCCB.......", # 21
            ".......BMMMMMMMMCCCCCCCCB.......", # 22
            ".......BBBBBBBBBBBBBBBBB........", # 23
            "........BEBBMB....BEBBMB........", # 24
            "........BEBBMB....BEBBMB........", # 25
            "........BEBBMB....BEBBMB........", # 26
            ".......BCCBCCB...BCCBCCB........", # 27
            ".......BBBBBBB...BBBBBBB........", # 28
            "................................", # 29
            "................................", # 30
            "................................", # 31
        ],
        [
            "................................", # 0
            "................................", # 1
            "................................", # 2
            "................................", # 3
            "................................", # 4
            "................................", # 5
            "...................BBBBBB.......", # 6
            "........BB........BLLMLLLB......", # 7
            ".......BMLB......BLLMMMMMLB.....", # 8
            ".......BMLB.....BEELLMMMMMEB....", # 9
            "........BMB.....BEEEMMMMMMEEB...", # 10
            "........BMB.....BEEEMMMDMMEEB...", # 11
            "........BMB.....BEEEMMDHMMEEB...", # 12
            ".........BB....BEEEMMMDMMCCB....", # 13
            "..........B...BEEEMMMCCCCDDB....", # 14
            ".........BB..BEEEMMMMCCCCCCB....", # 15
            "........BMMBBEEEMMMMMMCCCCB.....", # 16
            ".......BLLMMBBMMMMMMMMMMBB......", # 17
            "......BLLMMMMMMMMMMMMMMMB.......", # 18
            "......BMMMMMMMMMMMMMMMMMMB......", # 19
            "......BMMMMMMMMMMCCCCCCCCB......", # 20
            "......BMMMMMMMMMCCCCCCCCB.......", # 21
            ".......BMMMMMMMMCCCCCCCCB.......", # 22
            ".......BBBBBBBBBBBBBBBBB........", # 23
            "........BMB..BEB...BMB..BEB.....", # 24
            ".......BMB....BEB...BMB..BEB....", # 25
            "......BMB......BEB...BMB..BEB...", # 26
            ".....BCCB......BCCB.BCCB..BCCB..", # 27
            ".....BBBB......BBBB.BBBB..BBBB..", # 28
            "................................", # 29
            "................................", # 30
            "................................", # 31
        ],
        [
            "................................", # 0
            "................................", # 1
            "................................", # 2
            "................................", # 3
            "................................", # 4
            "...................BBBBBB.......", # 5 (up 1px)
            "........BB........BLLMLLLB......", # 6
            ".......BMLB......BLLMMMMMLB.....", # 7
            ".......BMLB.....BEELLMMMMMEB....", # 8
            "........BMB.....BEEEMMMMMMEEB...", # 9
            "........BMB.....BEEEMMMDMMEEB...", # 10
            "........BMB.....BEEEMMDHMMEEB...", # 11
            ".........BB....BEEEMMMDMMCCB....", # 12
            "..........B...BEEEMMMCCCCDDB....", # 13
            ".........BB..BEEEMMMMCCCCCCB....", # 14
            "........BMMBBEEEMMMMMMCCCCB.....", # 15
            ".......BLLMMBBMMMMMMMMMMBB......", # 16
            "......BLLMMMMMMMMMMMMMMMB.......", # 17
            "......BMMMMMMMMMMMMMMMMMMB......", # 18
            "......BMMMMMMMMMMCCCCCCCCB......", # 19
            "......BMMMMMMMMMCCCCCCCCB.......", # 20
            ".......BMMMMMMMMCCCCCCCCB.......", # 21
            ".......BBBBBBBBBBBBBBBBB........", # 22
            "........BEBBMB....BEBBMB........", # 23
            "........BEBBMB....BEBBMB........", # 24
            "........BEBBMB....BEBBMB........", # 25
            ".......BCCBCCB...BCCBCCB........", # 26
            ".......BBBBBBB...BBBBBBB........", # 27
            "................................", # 28
            "................................", # 29
            "................................", # 30
            "................................", # 31
        ]
    ],
    "sleep": [
        [
            "................................", # 0
            "................................", # 1
            "................................", # 2
            "................................", # 3
            "................................", # 4
            "................................", # 5
            "................................", # 6
            "................................", # 7
            "................................", # 8
            "................................", # 9
            "................................", # 10
            "......................ZZ........", # 11 'z'
            ".......................Z........", # 12
            "......................ZZ........", # 13
            "................................", # 14
            "..................BBBBBB........", # 15
            "........BB.......BLLMMLLB.......", # 16
            ".......BMLB.....BEELLMMMEEB.....", # 17
            ".......BMMBB...BEEEMMMMMMEEB....", # 18
            "......BLLMMMBBBEEEMMMMMMMMEEB...", # 19
            ".....BLLMMMMMMMEEEMMMBBBMMEEB...", # 20 closed eye
            ".....BMMMMMMMMMMEEEMMCCCCCDDB...", # 21
            "....BMMMMMMMMMMMEEEMCCCCCCDDB...", # 22
            "....BMMMMMMMMMMMMMMMCCCCCCCCB...", # 23
            "....BMMMMMMMMMMMMMMMCCCCCCCCB...", # 24
            ".....BMMMMMMMMMMMMCCCCCCCCB.....", # 25
            ".....BBBBBBBBBBBBBBBBBBBBBB.....", # 26
            "....BCCCB..BCCCB...BCCCB..BCCCB.", # 27
            "....BBBBB..BBBBB...BBBBB..BBBBB.", # 28
            "................................", # 29
            "................................", # 30
            "................................", # 31
        ],
        [
            "................................", # 0
            "................................", # 1
            "................................", # 2
            "................................", # 3
            "................................", # 4
            ".......................ZZZ......", # 5 big 'Z'
            ".........................Z......", # 6
            ".......................ZZZ......", # 7
            "................................", # 8
            "....................ZZ..........", # 9 small 'z'
            ".....................Z..........", # 10
            "....................ZZ..........", # 11
            "................................", # 12
            "................................", # 13
            "................................", # 14
            "..................BBBBBB........", # 15
            "........BB.......BLLMMLLB.......", # 16
            ".......BMLB.....BEELLMMMEEB.....", # 17
            ".......BMMBB...BEEEMMMMMMEEB....", # 18
            "......BLLMMMBBBEEEMMMMMMMMEEB...", # 19
            ".....BLLMMMMMMMEEEMMMBBBMMEEB...", # 20
            ".....BMMMMMMMMMMEEEMMCCCCCDDB...", # 21
            "....BMMMMMMMMMMMEEEMCCCCCCDDB...", # 22
            "....BMMMMMMMMMMMMMMMCCCCCCCCB...", # 23
            "....BMMMMMMMMMMMMMMMCCCCCCCCB...", # 24
            ".....BMMMMMMMMMMMMCCCCCCCCB.....", # 25
            ".....BBBBBBBBBBBBBBBBBBBBBB.....", # 26
            "....BCCCB..BCCCB...BCCCB..BCCCB.", # 27
            "....BBBBB..BBBBB...BBBBB..BBBBB.", # 28
            "................................", # 29
            "................................", # 30
            "................................", # 31
        ]
    ]
}

# --- PARROT ---
PARROT_FRAMES = {
    "idle": [
        [
            "................................", # 0
            "................................", # 1
            "...................RR...........", # 2
            "..................RRR...........", # 3
            ".................RRRRR..........", # 4
            "................BRRRRBB.........", # 5
            "...............BRRRRRRRGB.......", # 6
            "..............BRRRRRRRRGGB......", # 7
            ".............BRRRRRDDHRGGB......", # 8
            ".............BRRRRRDDDOGGB......", # 9
            "............BBRRRRROOOKKKKB.....", # 10
            "...........BGGGBRROOOKKKKKKB....", # 11
            "..........BGGGGGBRROOKKKTKKKB...", # 12
            ".........BGGGGGGGBBOOOKTTTTB....", # 13
            "........BGGGGGGGGGGBB.BTTTB.....", # 14
            "........BGGAAACCGGGGB..BBB......", # 15
            ".......BGAAAAACCCGGGB...........", # 16
            ".......BGAAAAACCCGGGGB..........", # 17
            ".......BGAAAAACCCGGGB...........", # 18
            ".......BGGAAAACCGGGGB...........", # 19
            "......BGBGGGGGGGGGGGB...........", # 20
            ".....BGAB.BGGGGGGGGGB...........", # 21
            "....BGAB...BGGGGGGGB............", # 22
            "...BGAB....BBGGGGGGB............", # 23
            "...BAB......BBBBBB..............", # 24
            "..BAB........BTB.BTB............", # 25
            "..BB.........BTB.BTB............", # 26
            ".............BTTBBTTB...........", # 27
            "............BTTTTBTTTTB.........", # 28
            "............BBBBBBBBBBB.........", # 29
            "................................", # 30
            "................................", # 31
        ],
        [
            "................................", # 0
            "..................RRR...........", # 1
            ".................RRRR...........", # 2
            "................RRRRRR..........", # 3
            "...............BRRRRBB..........", # 4
            "..............BRRRRRRRGB........", # 5
            ".............BRRRRRRRRGGB.......", # 6
            "............BRRRRRDDHRGGB.......", # 7
            "............BRRRRRDDDOGGB.......", # 8
            "...........BBRRRRROOOKKKKB......", # 9
            "..........BGGGBRROOOKKKKKKB.....", # 10
            ".........BGGGGGBRROOKKKTKKKB....", # 11
            "........BGGGGGGGBBOOOKTTTTB.....", # 12
            ".......BGGGGGGGGGGBB.BTTTB......", # 13
            ".......BGGAAACCGGGGB..BBB.......", # 14
            "......BGAAAAACCCGGGB............", # 15
            "......BGAAAAACCCGGGGB...........", # 16
            "......BGAAAAACCCGGGB............", # 17
            "......BGGAAAACCGGGGB............", # 18
            ".....BGBGGGGGGGGGGGB............", # 19
            "....BGAB.BGGGGGGGGGB............", # 20
            "...BGAB...BGGGGGGGB.............", # 21
            "..BGAB....BBGGGGGGB.............", # 22
            "..BAB......BBBBBB...............", # 23
            ".BAB........BTB.BTB.............", # 24
            ".BB.........BTB.BTB.............", # 25
            "............BTTBBTTB............", # 26
            "...........BTTTTBTTTTB..........", # 27
            "...........BBBBBBBBBBB..........", # 28
            "................................", # 29
            "................................", # 30
            "................................", # 31
        ],
        [
            "................................", # 0
            "................................", # 1
            "...................RR...........", # 2
            "..................RRR...........", # 3
            ".................RRRRR..........", # 4
            "................BRRRRBB.........", # 5
            "...............BRRRRRRRGB.......", # 6
            "..............BRRRRRRRRGGB......", # 7
            ".............BRRRRRBBBRGGB......", # 8 eye closed (BBB)
            ".............BRRRRROOOGGB.......", # 9
            "............BBRRRRROOOKKKKB.....", # 10
            "...........BGGGBRROOOKKKKKKB....", # 11
            "..........BGGGGGBRROOKKKTKKKB...", # 12
            ".........BGGGGGGGBBOOOKTTTTB....", # 13
            "........BGGGGGGGGGGBB.BTTTB.....", # 14
            "........BGGAAACCGGGGB..BBB......", # 15
            ".......BGAAAAACCCGGGB...........", # 16
            ".......BGAAAAACCCGGGGB..........", # 17
            ".......BGAAAAACCCGGGB...........", # 18
            ".......BGGAAAACCGGGGB...........", # 19
            "......BGBGGGGGGGGGGGB...........", # 20
            ".....BGAB.BGGGGGGGGGB...........", # 21
            "....BGAB...BGGGGGGGB............", # 22
            "...BGAB....BBGGGGGGB............", # 23
            "...BAB......BBBBBB..............", # 24
            "..BAB........BTB.BTB............", # 25
            "..BB.........BTB.BTB............", # 26
            ".............BTTBBTTB...........", # 27
            "............BTTTTBTTTTB.........", # 28
            "............BBBBBBBBBBB.........", # 29
            "................................", # 30
            "................................", # 31
        ]
    ],
    "walk": [
        [
            "................................", # 0
            "................................", # 1
            "...................RR...........", # 2
            "..................RRR...........", # 3
            ".................RRRRR..........", # 4
            "................BRRRRBB.........", # 5
            "...............BRRRRRRRGB.......", # 6
            "..............BRRRRRRRRGGB......", # 7
            ".............BRRRRRDDHRGGB......", # 8
            ".............BRRRRRDDDOGGB......", # 9
            "............BBRRRRROOOKKKKB.....", # 10
            "...........BGGGBRROOOKKKKKKB....", # 11
            "..........BGGGGGBRROOKKKTKKKB...", # 12
            ".........BGGGGGGGBBOOOKTTTTB....", # 13
            "........BGGGGGGGGGGBB.BTTTB.....", # 14
            "........BGGAAACCGGGGB..BBB......", # 15
            ".......BGAAAAACCCGGGB...........", # 16
            ".......BGAAAAACCCGGGGB..........", # 17
            ".......BGAAAAACCCGGGB...........", # 18
            ".......BGGAAAACCGGGGB...........", # 19
            "......BGBGGGGGGGGGGGB...........", # 20
            ".....BGAB.BGGGGGGGGGB...........", # 21
            "....BGAB...BGGGGGGGB............", # 22
            "...BGAB....BBGGGGGGB............", # 23
            "...BAB......BBBBBB..............", # 24
            "..BAB.......BTB...BTB...........", # 25
            "..BB.......BTB.....BTB..........", # 26
            "..........BTTB.....BTTB.........", # 27
            ".........BTTTTB...BTTTTB........", # 28
            ".........BBBBBB...BBBBBB........", # 29
            "................................", # 30
            "................................", # 31
        ],
        [
            "................................", # 0
            "...................RR...........", # 1 (up 1px)
            "..................RRR...........", # 2
            ".................RRRRR..........", # 3
            "................BRRRRBB.........", # 4
            "...............BRRRRRRRGB.......", # 5
            "..............BRRRRRRRRGGB......", # 6
            ".............BRRRRRDDHRGGB......", # 7
            ".............BRRRRRDDDOGGB......", # 8
            "............BBRRRRROOOKKKKB.....", # 9
            "...........BGGGBRROOOKKKKKKB....", # 10
            "..........BGGGGGBRROOKKKTKKKB...", # 11
            ".........BGGGGGGGBBOOOKTTTTB....", # 12
            "........BGGGGGGGGGGBB.BTTTB.....", # 13
            "........BGGAAACCGGGGB..BBB......", # 14
            ".......BGAAAAACCCGGGB...........", # 15
            ".......BGAAAAACCCGGGGB..........", # 16
            ".......BGAAAAACCCGGGB...........", # 17
            ".......BGGAAAACCGGGGB...........", # 18
            "......BGBGGGGGGGGGGGB...........", # 19
            ".....BGAB.BGGGGGGGGGB...........", # 20
            "....BGAB...BGGGGGGGB............", # 21
            "...BGAB....BBGGGGGGB............", # 22
            "...BAB......BBBBBB..............", # 23
            "..BAB.........BTBBTB............", # 24
            "..BB..........BTBBTB............", # 25
            ".............BTTBBTTB...........", # 26
            "............BTTTTBTTTTB.........", # 27
            "............BBBBBBBBBBB.........", # 28
            "................................", # 29
            "................................", # 30
            "................................", # 31
        ],
        [
            "................................", # 0
            "................................", # 1
            "...................RR...........", # 2
            "..................RRR...........", # 3
            ".................RRRRR..........", # 4
            "................BRRRRBB.........", # 5
            "...............BRRRRRRRGB.......", # 6
            "..............BRRRRRRRRGGB......", # 7
            ".............BRRRRRDDHRGGB......", # 8
            ".............BRRRRRDDDOGGB......", # 9
            "............BBRRRRROOOKKKKB.....", # 10
            "...........BGGGBRROOOKKKKKKB....", # 11
            "..........BGGGGGBRROOKKKTKKKB...", # 12
            ".........BGGGGGGGBBOOOKTTTTB....", # 13
            "........BGGGGGGGGGGBB.BTTTB.....", # 14
            "........BGGAAACCGGGGB..BBB......", # 15
            ".......BGAAAAACCCGGGB...........", # 16
            ".......BGAAAAACCCGGGGB..........", # 17
            ".......BGAAAAACCCGGGB...........", # 18
            ".......BGGAAAACCGGGGB...........", # 19
            "......BGBGGGGGGGGGGGB...........", # 20
            ".....BGAB.BGGGGGGGGGB...........", # 21
            "....BGAB...BGGGGGGGB............", # 22
            "...BGAB....BBGGGGGGB............", # 23
            "...BAB......BBBBBB..............", # 24
            "..BAB........BTB...BTB..........", # 25
            "..BB..........BTB...BTB.........", # 26
            "...............BTTB.BTTB........", # 27
            "..............BTTTTBTTTTB.......", # 28
            "..............BBBBBBBBBBB.......", # 29
            "................................", # 30
            "................................", # 31
        ],
        [
            "................................", # 0
            "...................RR...........", # 1 (up 1px)
            "..................RRR...........", # 2
            ".................RRRRR..........", # 3
            "................BRRRRBB.........", # 4
            "...............BRRRRRRRGB.......", # 5
            "..............BRRRRRRRRGGB......", # 6
            ".............BRRRRRDDHRGGB......", # 7
            ".............BRRRRRDDDOGGB......", # 8
            "............BBRRRRROOOKKKKB.....", # 9
            "...........BGGGBRROOOKKKKKKB....", # 10
            "..........BGGGGGBRROOKKKTKKKB...", # 11
            ".........BGGGGGGGBBOOOKTTTTB....", # 12
            "........BGGGGGGGGGGBB.BTTTB.....", # 13
            "........BGGAAACCGGGGB..BBB......", # 14
            ".......BGAAAAACCCGGGB...........", # 15
            ".......BGAAAAACCCGGGGB..........", # 16
            ".......BGAAAAACCCGGGB...........", # 17
            ".......BGGAAAACCGGGGB...........", # 18
            "......BGBGGGGGGGGGGGB...........", # 19
            ".....BGAB.BGGGGGGGGGB...........", # 20
            "....BGAB...BGGGGGGGB............", # 21
            "...BGAB....BBGGGGGGB............", # 22
            "...BAB......BBBBBB..............", # 23
            "..BAB.........BTBBTB............", # 24
            "..BB..........BTBBTB............", # 25
            ".............BTTBBTTB...........", # 26
            "............BTTTTBTTTTB.........", # 27
            "............BBBBBBBBBBB.........", # 28
            "................................", # 29
            "................................", # 30
            "................................", # 31
        ]
    ],
    "sleep": [
        [
            "................................", # 0
            "................................", # 1
            "................................", # 2
            "................................", # 3
            "................................", # 4
            "................................", # 5
            "................................", # 6
            "................................", # 7
            "................................", # 8
            "................................", # 9
            "................................", # 10
            "......................ZZ........", # 11 'z'
            ".......................Z........", # 12
            "......................ZZ........", # 13
            "................................", # 14
            "..................RRR...........", # 15
            ".................RRRRR..........", # 16
            "................BRRRRBB.........", # 17
            "...............BRRRRRRRGB.......", # 18
            "..............BRRRRRBBBGB.......", # 19 closed eye (BBB)
            ".............BBRRRRROOKKKKB.....", # 20
            "............BGGAAACCGGGGBBB.....", # 21
            "...........BGAAAAACCCGGGB.......", # 22
            "..........BGAAAAACCCGGGGB.......", # 23
            "..........BGGAAAACCGGGGB........", # 24
            ".........BGBGGGGGGGGGGGB........", # 25
            "........BGABBBBBBBBBBB..........", # 26
            ".......BGAB...BTB.BTB...........", # 27
            ".......BAB...BTTBBTTB...........", # 28
            ".......BB...BTTTTBTTTTB.........", # 29
            "............BBBBBBBBBBB.........", # 30
            "................................", # 31
        ],
        [
            "................................", # 0
            "................................", # 1
            "................................", # 2
            "................................", # 3
            ".......................ZZZ......", # 4 big 'Z'
            ".........................Z......", # 5
            ".......................ZZZ......", # 6
            "................................", # 7
            "....................ZZ..........", # 8 small 'z'
            ".....................Z..........", # 9
            "....................ZZ..........", # 10
            "................................", # 11
            "................................", # 12
            "................................", # 13
            "................................", # 14
            "..................RRR...........", # 15
            ".................RRRRR..........", # 16
            "................BRRRRBB.........", # 17
            "...............BRRRRRRRGB.......", # 18
            "..............BRRRRRBBBGB.......", # 19
            ".............BBRRRRROOKKKKB.....", # 20
            "............BGGAAACCGGGGBBB.....", # 21
            "...........BGAAAAACCCGGGB.......", # 22
            "..........BGAAAAACCCGGGGB.......", # 23
            "..........BGGAAAACCGGGGB........", # 24
            ".........BGBGGGGGGGGGGGB........", # 25
            "........BGABBBBBBBBBBB..........", # 26
            ".......BGAB...BTB.BTB...........", # 27
            ".......BAB...BTTBBTTB...........", # 28
            ".......BB...BTTTTBTTTTB.........", # 29
            "............BBBBBBBBBBB.........", # 30
            "................................", # 31
        ]
    ]
}

# --- RABBIT ---
RABBIT_FRAMES = {
    "idle": [
        [
            "................................", # 0
            "................................", # 1
            "................BB....BB........", # 2
            "...............BPB...BPB........", # 3
            "...............BPB...BPB........", # 4
            "..............BWPB..BWPB........", # 5
            "..............BWPB..BWPB........", # 6
            "..............BWPB..BWPB........", # 7
            "..............BWPB..BWPB........", # 8
            "..............BWPB..BWPB........", # 9
            "..............BWPB.BBWPB........", # 10
            ".............BBWBBBWWB..........", # 11
            "............BWWWWWWWWWBB........", # 12
            "...........BWWWWWWWWWWWWBB......", # 13
            "...........BWWWWWWDDHWWWWWB.....", # 14
            "...........BWWWWWWDDDWWWWWB.....", # 15
            "..........BWWWWWWWWWWWWNWB......", # 16
            "..........BWWWWWWWWWWWWWNB......", # 17
            "....BBB...BWWWWWWWWWWWWWWB......", # 18
            "...BWWWB.BBWWWWWWWWWWWWWWB......", # 19
            "..BWWWWWBWWWWWWWWWWWWWWWWB......", # 20
            "..BWWWWWBWWWWWWWWWWWWWWWB.......", # 21
            "...BWWWB.BWWWWWWWWWWWWWWB.......", # 22
            "....BBB..BSSWWWWWWWWWWWWB.......", # 23
            "........BGSGSSBBSSBBWWWB........", # 24
            "........BGSSGB..BGGB.BWB........", # 25
            "........BGSSGB..BGGB.BWB........", # 26
            "........BGSSGB..BGGB.BWB........", # 27
            ".......BWWWWWB.BWWWB.BWWWB......", # 28
            ".......BBBBBBB.BBBBB.BBBBB......", # 29
            "................................", # 30
            "................................", # 31
        ],
        [
            "................................", # 0
            "................................", # 1
            "................BB.....BB.......", # 2
            "...............BPB....BPB.......", # 3
            "...............BPB....BPB.......", # 4
            "..............BWPB...BWPB.......", # 5
            "..............BWPB...BWPB.......", # 6
            "..............BWPB..BWPB........", # 7
            "..............BWPB..BWPB........", # 8
            "..............BWPB..BWPB........", # 9
            "..............BWPB.BBWPB........", # 10
            ".............BBWBBBWWB..........", # 11
            "............BWWWWWWWWWBB........", # 12
            "...........BWWWWWWWWWWWWBB......", # 13
            "...........BWWWWWWDDHWWWWWB.....", # 14
            "...........BWWWWWWDDDWWWWWB.....", # 15
            "..........BWWWWWWWWWWWWNNB......", # 16
            "..........BWWWWWWWWWWWWWNB......", # 17
            "....BBB...BWWWWWWWWWWWWWWB......", # 18
            "...BWWWB.BBWWWWWWWWWWWWWWB......", # 19
            "..BWWWWWBWWWWWWWWWWWWWWWWB......", # 20
            "..BWWWWWBWWWWWWWWWWWWWWWB.......", # 21
            "...BWWWB.BWWWWWWWWWWWWWWB.......", # 22
            "....BBB..BSSWWWWWWWWWWWWB.......", # 23
            "........BGSGSSBBSSBBWWWB........", # 24
            "........BGSSGB..BGGB.BWB........", # 25
            "........BGSSGB..BGGB.BWB........", # 26
            "........BGSSGB..BGGB.BWB........", # 27
            ".......BWWWWWB.BWWWB.BWWWB......", # 28
            ".......BBBBBBB.BBBBB.BBBBB......", # 29
            "................................", # 30
            "................................", # 31
        ],
        [
            "................................", # 0
            "................................", # 1
            "................BB....BB........", # 2
            "...............BPB...BPB........", # 3
            "...............BPB...BPB........", # 4
            "..............BWPB..BWPB........", # 5
            "..............BWPB..BWPB........", # 6
            "..............BWPB..BWPB........", # 7
            "..............BWPB..BWPB........", # 8
            "..............BWPB..BWPB........", # 9
            "..............BWPB.BBWPB........", # 10
            ".............BBWBBBWWB..........", # 11
            "............BWWWWWWWWWBB........", # 12
            "...........BWWWWWWWWWWWWBB......", # 13
            "...........BWWWWWWBBBBWWWWWB....", # 14 blink (BBBB)
            "...........BWWWWWWWWWWWWWWWB....", # 15
            "..........BWWWWWWWWWWWWNWB......", # 16
            "..........BWWWWWWWWWWWWWNB......", # 17
            "....BBB...BWWWWWWWWWWWWWWB......", # 18
            "...BWWWB.BBWWWWWWWWWWWWWWB......", # 19
            "..BWWWWWBWWWWWWWWWWWWWWWWB......", # 20
            "..BWWWWWBWWWWWWWWWWWWWWWB.......", # 21
            "...BWWWB.BWWWWWWWWWWWWWWB.......", # 22
            "....BBB..BSSWWWWWWWWWWWWB.......", # 23
            "........BGSGSSBBSSBBWWWB........", # 24
            "........BGSSGB..BGGB.BWB........", # 25
            "........BGSSGB..BGGB.BWB........", # 26
            "........BGSSGB..BGGB.BWB........", # 27
            ".......BWWWWWB.BWWWB.BWWWB......", # 28
            ".......BBBBBBB.BBBBB.BBBBB......", # 29
            "................................", # 30
            "................................", # 31
        ]
    ],
    "walk": [
        [
            "................................", # 0
            "................................", # 1
            "................................", # 2
            "................................", # 3
            "................BB....BB........", # 4 (crouch)
            "...............BPB...BPB........", # 5
            "...............BPB...BPB........", # 6
            "..............BWPB..BWPB........", # 7
            "..............BWPB..BWPB........", # 8
            "..............BWPB..BWPB........", # 9
            ".............BBWBBBWWB..........", # 10
            "............BWWWWWWWWWBB........", # 11
            "...........BWWWWWWWWWWWWBB......", # 12
            "...........BWWWWWWDDHWWWWWB.....", # 13
            "...........BWWWWWWDDDWWWWWB.....", # 14
            "..........BWWWWWWWWWWWWNWB......", # 15
            "..........BWWWWWWWWWWWWWNB......", # 16
            "....BBB...BWWWWWWWWWWWWWWB......", # 17
            "...BWWWB.BBWWWWWWWWWWWWWWB......", # 18
            "..BWWWWWBWWWWWWWWWWWWWWWWB......", # 19
            "..BWWWWWBWWWWWWWWWWWWWWWB.......", # 20
            "...BWWWB.BWWWWWWWWWWWWWWB.......", # 21
            "....BBB..BSSWWWWWWWWWWWWB.......", # 22
            "........BGSGSSBBSSBBWWWB........", # 23
            "........BGSSGB..BGGB.BWB........", # 24
            ".......BWWWWWB.BWWWB.BWWWB......", # 25
            ".......BBBBBBB.BBBBB.BBBBB......", # 26
            "................................", # 27
            "................................", # 28
            "................................", # 29
            "................................", # 30
            "................................", # 31
        ],
        [
            "...............BB....BB.........", # 0 (airborne leap)
            "..............BPB...BPB.........", # 1
            "..............BPB...BPB.........", # 2
            ".............BWPB..BWPB.........", # 3
            ".............BWPB..BWPB.........", # 4
            ".............BWPB..BWPB.........", # 5
            "............BBWBBBWWB...........", # 6
            "...........BWWWWWWWWWBB.........", # 7
            "..........BWWWWWWWWWWWWBB.......", # 8
            "..........BWWWWWWDDHWWWWWB......", # 9
            "..........BWWWWWWDDDWWWWWB......", # 10
            ".........BWWWWWWWWWWWWNWB.......", # 11
            ".........BWWWWWWWWWWWWWNB.......", # 12
            "...BBB...BWWWWWWWWWWWWWWB.......", # 13
            "..BWWWB.BBWWWWWWWWWWWWWWB.......", # 14
            ".BWWWWWBWWWWWWWWWWWWWWWWB.......", # 15
            ".BWWWWWBWWWWWWWWWWWWWWWB........", # 16
            "..BWWWB.BWWWWWWWWWWWWWWB........", # 17
            "...BBB..BSSWWWWWWWWWWWWB........", # 18
            ".......BGSGSSBBSSBBWWWB.........", # 19
            ".......BGSSGB..BGGB.BWB.........", # 20
            "......BWWWWWB.BWWWB.BWWWB.......", # 21
            "......BBBBBBB.BBBBB.BBBBB.......", # 22
            "................................", # 23
            "................................", # 24
            "................................", # 25
            "................................", # 26
            "................................", # 27
            "................................", # 28
            "................................", # 29
            "................................", # 30
            "................................", # 31
        ],
        [
            "................................", # 0
            "................BB....BB........", # 1 (front landing)
            "...............BPB...BPB........", # 2
            "...............BPB...BPB........", # 3
            "..............BWPB..BWPB........", # 4
            "..............BWPB..BWPB........", # 5
            "..............BWPB..BWPB........", # 6
            "..............BWPB.BBWPB........", # 7
            ".............BBWBBBWWB..........", # 8
            "............BWWWWWWWWWBB........", # 9
            "...........BWWWWWWWWWWWWBB......", # 10
            "...........BWWWWWWDDHWWWWWB.....", # 11
            "...........BWWWWWWDDDWWWWWB.....", # 12
            "..........BWWWWWWWWWWWWNWB......", # 13
            "..........BWWWWWWWWWWWWWNB......", # 14
            "....BBB...BWWWWWWWWWWWWWWB......", # 15
            "...BWWWB.BBWWWWWWWWWWWWWWB......", # 16
            "..BWWWWWBWWWWWWWWWWWWWWWWB......", # 17
            "..BWWWWWBWWWWWWWWWWWWWWWB.......", # 18
            "...BWWWB.BWWWWWWWWWWWWWWB.......", # 19
            "....BBB..BSSWWWWWWWWWWWWB.......", # 20
            "........BGSGSSBBSSBBWWWB........", # 21
            "........BGSSGB...BWB.BWB........", # 22
            ".......BWWWWWB...BWB.BWB........", # 23
            ".......BBBBBBB..BWWWB.BWWWB.....", # 24
            "................BBBBB.BBBBB.....", # 25
            "................................", # 26
            "................................", # 27
            "................................", # 28
            "................................", # 29
            "................................", # 30
            "................................", # 31
        ],
        [
            "................................", # 0
            "................................", # 1
            "................BB....BB........", # 2 (back landing)
            "...............BPB...BPB........", # 3
            "...............BPB...BPB........", # 4
            "..............BWPB..BWPB........", # 5
            "..............BWPB..BWPB........", # 6
            "..............BWPB..BWPB........", # 7
            "..............BWPB..BWPB........", # 8
            "..............BWPB..BWPB........", # 9
            "..............BWPB.BBWPB........", # 10
            ".............BBWBBBWWB..........", # 11
            "............BWWWWWWWWWBB........", # 12
            "...........BWWWWWWWWWWWWBB......", # 13
            "...........BWWWWWWDDHWWWWWB.....", # 14
            "...........BWWWWWWDDDWWWWWB.....", # 15
            "..........BWWWWWWWWWWWWNWB......", # 16
            "..........BWWWWWWWWWWWWWNB......", # 17
            "....BBB...BWWWWWWWWWWWWWWB......", # 18
            "...BWWWB.BBWWWWWWWWWWWWWWB......", # 19
            "..BWWWWWBWWWWWWWWWWWWWWWWB......", # 20
            "..BWWWWWBWWWWWWWWWWWWWWWB.......", # 21
            "...BWWWB.BWWWWWWWWWWWWWWB.......", # 22
            "....BBB..BSSWWWWWWWWWWWWB.......", # 23
            "........BGSGSSBBSSBBWWWB........", # 24
            "........BGSSGB..BGGB.BWB........", # 25
            "........BGSSGB..BGGB.BWB........", # 26
            "........BGSSGB..BGGB.BWB........", # 27
            ".......BWWWWWB.BWWWB.BWWWB......", # 28
            ".......BBBBBBB.BBBBB.BBBBB......", # 29
            "................................", # 30
            "................................", # 31
        ]
    ],
    "sleep": [
        [
            "................................", # 0
            "................................", # 1
            "................................", # 2
            "................................", # 3
            "................................", # 4
            "................................", # 5
            "................................", # 6
            "................................", # 7
            "................................", # 8
            "................................", # 9
            "................................", # 10
            "......................ZZ........", # 11 'z'
            ".......................Z........", # 12
            "......................ZZ........", # 13
            "................................", # 14
            ".........BBBBBBBBBB.............", # 15
            "........BPPBWPBWPBB.............", # 16
            ".......BPPPBWPBWPBWB............", # 17
            "......BBBBBBBBBBBBWB............", # 18
            "....BBB..BWWWWWWWWWWBB..........", # 19
            "...BWWWB.BWWWWWWWWWWWWBB........", # 20
            "..BWWWWWBWWWWWWWWWWWWWWWB.......", # 21
            "..BWWWWWBWWWWWWBBBBWWWWNWB......", # 22
            "...BWWWB.BWWWWWBBBBWWWWWNB......", # 23
            "....BBB..BSSWWWWWWWWWWWWB.......", # 24
            "........BGSGSSBBBBBBWWWB........", # 25
            "........BWWWWWB....BWWWB........", # 26
            "........BBBBBBB....BBBBB........", # 27
            "................................", # 28
            "................................", # 29
            "................................", # 30
            "................................", # 31
        ],
        [
            "................................", # 0
            "................................", # 1
            "................................", # 2
            "................................", # 3
            "................................", # 4
            ".......................ZZZ......", # 5 big 'Z'
            ".........................Z......", # 6
            ".......................ZZZ......", # 7
            "................................", # 8
            "....................ZZ..........", # 9 small 'z'
            ".....................Z..........", # 10
            "....................ZZ..........", # 11
            "................................", # 12
            "................................", # 13
            "................................", # 14
            ".........BBBBBBBBBB.............", # 15
            "........BPPBWPBWPBB.............", # 16
            ".......BPPPBWPBWPBWB............", # 17
            "......BBBBBBBBBBBBWB............", # 18
            "....BBB..BWWWWWWWWWWBB..........", # 19
            "...BWWWB.BWWWWWWWWWWWWBB........", # 20
            "..BWWWWWBWWWWWWWWWWWWWWWB.......", # 21
            "..BWWWWWBWWWWWWBBBBWWWWNWB......", # 22
            "...BWWWB.BWWWWWBBBBWWWWWNB......", # 23
            "....BBB..BSSWWWWWWWWWWWWB.......", # 24
            "........BGSGSSBBBBBBWWWB........", # 25
            "........BWWWWWB....BWWWB........", # 26
            "........BBBBBBB....BBBBB........", # 27
            "................................", # 28
            "................................", # 29
            "................................", # 30
            "................................", # 31
        ]
    ]
}

# --- TURTLE ---
TURTLE_FRAMES = {
    "idle": [
        [
            "................................", # 0
            "................................", # 1
            "................................", # 2
            "................................", # 3
            "................................", # 4
            "................................", # 5
            "................................", # 6
            "................................", # 7
            "................................", # 8
            "................................", # 9
            "................................", # 10
            "................................", # 11
            ".............BBBBBBBBBB.........", # 12
            "...........BBSEESSEESSEBB.......", # 13
            "..........BSEEESSEESSEEESB......", # 14
            ".........BSEEESSEESSEESSEEB.....", # 15
            "........BSBSSSBSBSSSBSBSSSBB....", # 16
            "........BSEESSEESSEESSEESEB.....", # 17
            ".......BSEEESSEESSEESSEEESB.BBB.", # 18
            ".......BSEESSEESSEESSEESSEBBGGLB", # 19
            "..BBB..BSBSSSBSBSSSBSBSSSBGGDDHB", # 20
            ".BGGB..BYYYYYYYYYYYYYYYYYBGGGGGB", # 21
            "BGGGB.BYYYYYYYYYYYYYYYYYYBBGGGGB", # 22
            ".BBB..BBBBBBBBBBBBBBBBBBB..BBBB.", # 23
            "........BGB...BGB...BGB...BGB...", # 24
            "........BGB...BGB...BGB...BGB...", # 25
            ".......BGGB..BGGB..BGGB..BGGB...", # 26
            ".......BCCB..BCCB..BCCB..BCCB...", # 27
            ".......BBBB..BBBB..BBBB..BBBB...", # 28
            "................................", # 29
            "................................", # 30
            "................................", # 31
        ],
        [
            "................................", # 0
            "................................", # 1
            "................................", # 2
            "................................", # 3
            "................................", # 4
            "................................", # 5
            "................................", # 6
            "................................", # 7
            "................................", # 8
            "................................", # 9
            "................................", # 10
            ".............BBBBBBBBBB.........", # 11 (breath up 1px)
            "...........BBSEESSEESSEBB.......", # 12
            "..........BSEEESSEESSEEESB......", # 13
            ".........BSEEESSEESSEESSEEB.....", # 14
            "........BSBSSSBSBSSSBSBSSSBB....", # 15
            "........BSEESSEESSEESSEESEB.....", # 16
            ".......BSEEESSEESSEESSEEESB.BBB.", # 17
            ".......BSEESSEESSEESSEESSEBBGGLB", # 18
            "..BBB..BSBSSSBSBSSSBSBSSSBGGDDHB", # 19
            ".BGGB..BYYYYYYYYYYYYYYYYYBGGGGGB", # 20
            "BGGGB.BYYYYYYYYYYYYYYYYYYBBGGGGB", # 21
            ".BBB..BBBBBBBBBBBBBBBBBBB..BBBB.", # 22
            "........BGB...BGB...BGB...BGB...", # 23
            "........BGB...BGB...BGB...BGB...", # 24
            ".......BGGB..BGGB..BGGB..BGGB...", # 25
            ".......BCCB..BCCB..BCCB..BCCB...", # 26
            ".......BBBB..BBBB..BBBB..BBBB...", # 27
            "................................", # 28
            "................................", # 29
            "................................", # 30
            "................................", # 31
        ],
        [
            "................................", # 0
            "................................", # 1
            "................................", # 2
            "................................", # 3
            "................................", # 4
            "................................", # 5
            "................................", # 6
            "................................", # 7
            "................................", # 8
            "................................", # 9
            "................................", # 10
            "................................", # 11
            ".............BBBBBBBBBB.........", # 12
            "...........BBSEESSEESSEBB.......", # 13
            "..........BSEEESSEESSEEESB......", # 14
            ".........BSEEESSEESSEESSEEB.....", # 15
            "........BSBSSSBSBSSSBSBSSSBB....", # 16
            "........BSEESSEESSEESSEESEB.....", # 17
            ".......BSEEESSEESSEESSEEESB.BBB.", # 18
            ".......BSEESSEESSEESSEESSEBBGGLB", # 19
            "..BBB..BSBSSSBSBSSSBSBSSSBGGBBBB", # 20 eye closed (BBBB)
            ".BGGB..BYYYYYYYYYYYYYYYYYBGGGGGB", # 21
            "BGGGB.BYYYYYYYYYYYYYYYYYYBBGGGGB", # 22
            ".BBB..BBBBBBBBBBBBBBBBBBB..BBBB.", # 23
            "........BGB...BGB...BGB...BGB...", # 24
            "........BGB...BGB...BGB...BGB...", # 25
            ".......BGGB..BGGB..BGGB..BGGB...", # 26
            ".......BCCB..BCCB..BCCB..BCCB...", # 27
            ".......BBBB..BBBB..BBBB..BBBB...", # 28
            "................................", # 29
            "................................", # 30
            "................................", # 31
        ]
    ],
    "walk": [
        [
            "................................", # 0
            "................................", # 1
            "................................", # 2
            "................................", # 3
            "................................", # 4
            "................................", # 5
            "................................", # 6
            "................................", # 7
            "................................", # 8
            "................................", # 9
            "................................", # 10
            "................................", # 11
            ".............BBBBBBBBBB.........", # 12
            "...........BBSEESSEESSEBB.......", # 13
            "..........BSEEESSEESSEEESB......", # 14
            ".........BSEEESSEESSEESSEEB.....", # 15
            "........BSBSSSBSBSSSBSBSSSBB....", # 16
            "........BSEESSEESSEESSEESEB.....", # 17
            ".......BSEEESSEESSEESSEEESB.BBB.", # 18
            ".......BSEESSEESSEESSEESSEBBGGLB", # 19
            "..BBB..BSBSSSBSBSSSBSBSSSBGGDDHB", # 20
            ".BGGB..BYYYYYYYYYYYYYYYYYBGGGGGB", # 21
            "BGGGB.BYYYYYYYYYYYYYYYYYYBBGGGGB", # 22
            ".BBB..BBBBBBBBBBBBBBBBBBB..BBBB.", # 23
            ".......BGB...BGB.....BGB...BGB..", # 24 stride 1
            "......BGGB...BGGB...BGGB...BGGB.", # 25
            ".....BCCB....BCCB...BCCB...BCCB.", # 26
            ".....BBBB....BBBB...BBBB...BBBB.", # 27
            "................................", # 28
            "................................", # 29
            "................................", # 30
            "................................", # 31
        ],
        [
            "................................", # 0
            "................................", # 1
            "................................", # 2
            "................................", # 3
            "................................", # 4
            "................................", # 5
            "................................", # 6
            "................................", # 7
            "................................", # 8
            "................................", # 9
            "................................", # 10
            ".............BBBBBBBBBB.........", # 11 (up 1px)
            "...........BBSEESSEESSEBB.......", # 12
            "..........BSEEESSEESSEEESB......", # 13
            ".........BSEEESSEESSEESSEEB.....", # 14
            "........BSBSSSBSBSSSBSBSSSBB....", # 15
            "........BSEESSEESSEESSEESEB.....", # 16
            ".......BSEEESSEESSEESSEEESB.BBB.", # 17
            ".......BSEESSEESSEESSEESSEBBGGLB", # 18
            "..BBB..BSBSSSBSBSSSBSBSSSBGGDDHB", # 19
            ".BGGB..BYYYYYYYYYYYYYYYYYBGGGGGB", # 20
            "BGGGB.BYYYYYYYYYYYYYYYYYYBBGGGGB", # 21
            ".BBB..BBBBBBBBBBBBBBBBBBB..BBBB.", # 22
            "........BGB...BGB...BGB...BGB...", # 23 passing
            "........BGB...BGB...BGB...BGB...", # 24
            ".......BGGB..BGGB..BGGB..BGGB...", # 25
            ".......BCCB..BCCB..BCCB..BCCB...", # 26
            ".......BBBB..BBBB..BBBB..BBBB...", # 27
            "................................", # 28
            "................................", # 29
            "................................", # 30
            "................................", # 31
        ],
        [
            "................................", # 0
            "................................", # 1
            "................................", # 2
            "................................", # 3
            "................................", # 4
            "................................", # 5
            "................................", # 6
            "................................", # 7
            "................................", # 8
            "................................", # 9
            "................................", # 10
            "................................", # 11
            ".............BBBBBBBBBB.........", # 12
            "...........BBSEESSEESSEBB.......", # 13
            "..........BSEEESSEESSEEESB......", # 14
            ".........BSEEESSEESSEESSEEB.....", # 15
            "........BSBSSSBSBSSSBSBSSSBB....", # 16
            "........BSEESSEESSEESSEESEB.....", # 17
            ".......BSEEESSEESSEESSEEESB.BBB.", # 18
            ".......BSEESSEESSEESSEESSEBBGGLB", # 19
            "..BBB..BSBSSSBSBSSSBSBSSSBGGDDHB", # 20
            ".BGGB..BYYYYYYYYYYYYYYYYYBGGGGGB", # 21
            "BGGGB.BYYYYYYYYYYYYYYYYYYBBGGGGB", # 22
            ".BBB..BBBBBBBBBBBBBBBBBBB..BBBB.", # 23
            "........BGB...BGB...BGB....BGB..", # 24 stride 2
            ".......BGGB...BGGB...BGGB...BGGB", # 25
            ".......BCCB...BCCB...BCCB...BCCB", # 26
            ".......BBBB...BBBB...BBBB...BBBB", # 27
            "................................", # 28
            "................................", # 29
            "................................", # 30
            "................................", # 31
        ],
        [
            "................................", # 0
            "................................", # 1
            "................................", # 2
            "................................", # 3
            "................................", # 4
            "................................", # 5
            "................................", # 6
            "................................", # 7
            "................................", # 8
            "................................", # 9
            "................................", # 10
            ".............BBBBBBBBBB.........", # 11 (up 1px)
            "...........BBSEESSEESSEBB.......", # 12
            "..........BSEEESSEESSEEESB......", # 13
            ".........BSEEESSEESSEESSEEB.....", # 14
            "........BSBSSSBSBSSSBSBSSSBB....", # 15
            "........BSEESSEESSEESSEESEB.....", # 16
            ".......BSEEESSEESSEESSEEESB.BBB.", # 17
            ".......BSEESSEESSEESSEESSEBBGGLB", # 18
            "..BBB..BSBSSSBSBSSSBSBSSSBGGDDHB", # 19
            ".BGGB..BYYYYYYYYYYYYYYYYYBGGGGGB", # 20
            "BGGGB.BYYYYYYYYYYYYYYYYYYBBGGGGB", # 21
            ".BBB..BBBBBBBBBBBBBBBBBBB..BBBB.", # 22
            "........BGB...BGB...BGB...BGB...", # 23 passing 2
            "........BGB...BGB...BGB...BGB...", # 24
            ".......BGGB..BGGB..BGGB..BGGB...", # 25
            ".......BCCB..BCCB..BCCB..BCCB...", # 26
            ".......BBBB..BBBB..BBBB..BBBB...", # 27
            "................................", # 28
            "................................", # 29
            "................................", # 30
            "................................", # 31
        ]
    ],
    "sleep": [
        [
            "................................", # 0
            "................................", # 1
            "................................", # 2
            "................................", # 3
            "................................", # 4
            "................................", # 5
            "................................", # 6
            "................................", # 7
            "................................", # 8
            "................................", # 9
            "................................", # 10
            "................................", # 11
            "......................ZZ........", # 12 'z'
            ".......................Z........", # 13
            "......................ZZ........", # 14
            ".............BBBBBBBBBB.........", # 15
            "...........BBSEESSEESSEBB.......", # 16
            "..........BSEEESSEESSEEESB......", # 17
            ".........BSEEESSEESSEESSEEB.....", # 18
            "........BSBSSSBSBSSSBSBSSSBB....", # 19
            "........BSEESSEESSEESSEESEB.....", # 20
            ".......BSEEESSEESSEESSEEESB.....", # 21
            ".......BSEESSEESSEESSEESSEBBBB..", # 22 head retracted into shell
            "..BBB..BSBSSSBSBSSSBSBSSSBGBBBB.", # 23 eye slit
            ".BGGB..BYYYYYYYYYYYYYYYYYBGGGB..", # 24
            "BGGGB.BYYYYYYYYYYYYYYYYYYBBGGB..", # 25
            ".BBB..BBBBBBBBBBBBBBBBBBBBBBB...", # 26 flippers retracted
            "................................", # 27
            "................................", # 28
            "................................", # 29
            "................................", # 30
            "................................", # 31
        ],
        [
            "................................", # 0
            "................................", # 1
            "................................", # 2
            "................................", # 3
            "................................", # 4
            "................................", # 5
            ".......................ZZZ......", # 6 big 'Z'
            ".........................Z......", # 7
            ".......................ZZZ......", # 8
            "................................", # 9
            "....................ZZ..........", # 10 small 'z'
            ".....................Z..........", # 11
            "....................ZZ..........", # 12
            "................................", # 13
            "................................", # 14
            ".............BBBBBBBBBB.........", # 15
            "...........BBSEESSEESSEBB.......", # 16
            "..........BSEEESSEESSEEESB......", # 17
            ".........BSEEESSEESSEESSEEB.....", # 18
            "........BSBSSSBSBSSSBSBSSSBB....", # 19
            "........BSEESSEESSEESSEESEB.....", # 20
            ".......BSEEESSEESSEESSEEESB.....", # 21
            ".......BSEESSEESSEESSEESSEBBBB..", # 22
            "..BBB..BSBSSSBSBSSSBSBSSSBGBBBB.", # 23
            ".BGGB..BYYYYYYYYYYYYYYYYYBGGGB..", # 24
            "BGGGB.BYYYYYYYYYYYYYYYYYYBBGGB..", # 25
            ".BBB..BBBBBBBBBBBBBBBBBBBBBBB...", # 26
            "................................", # 27
            "................................", # 28
            "................................", # 29
            "................................", # 30
            "................................", # 31
        ]
    ]
}

# --- DINOSAUR ---
DINOSAUR_FRAMES = {
    "idle": [
        [
            "................................", # 0
            "................................", # 1
            "...................KK...........", # 2
            "..................KJJB..........", # 3
            "..................BBBBBBBBB.....", # 4
            ".................BLLMLLLMMMB....", # 5
            "................BLLMMMMMMMMMB...", # 6
            "...............BLLMMMMMMMMMMMB..", # 7
            "..............BLLMMDDHMMMMMMMB..", # 8
            ".....KK......BLLMMDDHHMMMMMMMB..", # 9
            "....KJJB....BLLMMMDDHMMMMMMMMB..", # 10
            "....BBBB...BLLMMMMMMMPPMMMMMB...", # 11
            "..........BLLMMMMMMMMMPPMMMB....", # 12
            ".........BLLMMMMMMMMMMMMMMB.....", # 13
            "...KK...BLLMMMMMMMMMHBBBBB......", # 14
            "..KJJB.BLLMMMMMMMMMBB...........", # 15
            "..BBBBBLLMMVVVVMMMMB.BBB........", # 16
            "......BLLMMVVVVVVMMMBBHHB.......", # 17
            ".....BLLMMVVVVVVVVMMMBBB........", # 18
            ".KK.BLLMMMMVVVVVVVMMB...........", # 19
            "KJJBBLLMMMMMMVVVVVVMB...........", # 20
            "BBBBLLMMMMMMMMVVVVMB............", # 21
            "....BBBBLLMMMMMMMMB.............", # 22
            ".......BBBBBBMMMMMB.............", # 23
            "........BMMMMMBMMMMMB...........", # 24
            "........BMMMMB.BMMMMB...........", # 25
            ".........BMMB...BMMB............", # 26
            ".........BMMB...BMMB............", # 27
            "........BHHHMB.BHHHMB...........", # 28
            "........BBBBBB.BBBBBB...........", # 29
            "................................", # 30
            "................................", # 31
        ],
        [
            "................................", # 0
            "................................", # 1
            "...................KK...........", # 2
            "..................KJJB..........", # 3
            "..................BBBBBBBBB.....", # 4
            ".................BLLMLLLMMMB....", # 5
            "................BLLMMMMMMMMMB...", # 6
            "...............BLLMMMMMMMMMMMB..", # 7
            "..............BLLMMDDHMMMMMMMB..", # 8
            ".....KK......BLLMMDDHHMMMMMMMB..", # 9
            "....KJJB....BLLMMMDDHMMMMMMMMB..", # 10
            "....BBBB...BLLMMMMMMMPPMMMMMB...", # 11
            "..........BLLMMMMMMMMMPPMMMB....", # 12
            ".........BLLMMMMMMMMMMMMMMB.....", # 13
            "...KK...BLLMMMMMMMMMHBBBBB......", # 14
            "..KJJB.BLLMMMMMMMMMBBBBB........", # 15 arms waggle up
            "..BBBBBLLMMVVVVMMMMBBHHB........", # 16
            "......BLLMMVVVVVVMMMBBB.........", # 17
            ".KK..BLLMMVVVVVVVVMMMB..........", # 18 tail tip up
            "KJJBBLLMMMMVVVVVVVMMB...........", # 19
            "BBBBLLMMMMMMVVVVVVMB............", # 20
            "...BBBLLMMMMMMVVVVMB............", # 21
            "....BBBBLLMMMMMMMMB.............", # 22
            ".......BBBBBBMMMMMB.............", # 23
            "........BMMMMMBMMMMMB...........", # 24
            "........BMMMMB.BMMMMB...........", # 25
            ".........BMMB...BMMB............", # 26
            ".........BMMB...BMMB............", # 27
            "........BHHHMB.BHHHMB...........", # 28
            "........BBBBBB.BBBBBB...........", # 29
            "................................", # 30
            "................................", # 31
        ],
        [
            "................................", # 0
            "................................", # 1
            "...................KK...........", # 2
            "..................KJJB..........", # 3
            "..................BBBBBBBBB.....", # 4
            ".................BLLMLLLMMMB....", # 5
            "................BLLMMMMMMMMMB...", # 6
            "...............BLLMMMMMMMMMMMB..", # 7
            "..............BLLMMBBBBMMMMMMB..", # 8 blink (BBBB)
            ".....KK......BLLMMMBBBMMMMMMMB..", # 9
            "....KJJB....BLLMMMMMMMMMMMMMMB..", # 10
            "....BBBB...BLLMMMMMMMPPMMMMMB...", # 11
            "..........BLLMMMMMMMMMPPMMMB....", # 12
            ".........BLLMMMMMMMMMMMMMMB.....", # 13
            "...KK...BLLMMMMMMMMMHBBBBB......", # 14
            "..KJJB.BLLMMMMMMMMMBB...........", # 15
            "..BBBBBLLMMVVVVMMMMB.BBB........", # 16
            "......BLLMMVVVVVVMMMBBHHB.......", # 17
            ".....BLLMMVVVVVVVVMMMBBB........", # 18
            ".KK.BLLMMMMVVVVVVVMMB...........", # 19
            "KJJBBLLMMMMMMVVVVVVMB...........", # 20
            "BBBBLLMMMMMMMMVVVVMB............", # 21
            "....BBBBLLMMMMMMMMB.............", # 22
            ".......BBBBBBMMMMMB.............", # 23
            "........BMMMMMBMMMMMB...........", # 24
            "........BMMMMB.BMMMMB...........", # 25
            ".........BMMB...BMMB............", # 26
            ".........BMMB...BMMB............", # 27
            "........BHHHMB.BHHHMB...........", # 28
            "........BBBBBB.BBBBBB...........", # 29
            "................................", # 30
            "................................", # 31
        ]
    ],
    "walk": [
        [
            "................................", # 0
            "................................", # 1
            "...................KK...........", # 2
            "..................KJJB..........", # 3
            "..................BBBBBBBBB.....", # 4
            ".................BLLMLLLMMMB....", # 5
            "................BLLMMMMMMMMMB...", # 6
            "...............BLLMMMMMMMMMMMB..", # 7
            "..............BLLMMDDHMMMMMMMB..", # 8
            ".....KK......BLLMMDDHHMMMMMMMB..", # 9
            "....KJJB....BLLMMMDDHMMMMMMMMB..", # 10
            "....BBBB...BLLMMMMMMMPPMMMMMB...", # 11
            "..........BLLMMMMMMMMMPPMMMB....", # 12
            ".........BLLMMMMMMMMMMMMMMB.....", # 13
            "...KK...BLLMMMMMMMMMHBBBBB......", # 14
            "..KJJB.BLLMMMMMMMMMBB...........", # 15
            "..BBBBBLLMMVVVVMMMMB.BBB........", # 16
            "......BLLMMVVVVVVMMMBBHHB.......", # 17
            ".....BLLMMVVVVVVVVMMMBBB........", # 18
            ".KK.BLLMMMMVVVVVVVMMB...........", # 19
            "KJJBBLLMMMMMMVVVVVVMB...........", # 20
            "BBBBLLMMMMMMMMVVVVMB............", # 21
            "....BBBBLLMMMMMMMMB.............", # 22
            ".......BBBBBBMMMMMB.............", # 23
            "......BMMMMMB..BMMMMMB..........", # 24 stride 1
            ".....BMMMMB......BMMMMB.........", # 25
            "....BMMB...........BMMB.........", # 26
            "...BMMB.............BMMB........", # 27
            "..BHHHMB...........BHHHMB.......", # 28
            "..BBBBBB...........BBBBBB.......", # 29
            "................................", # 30
            "................................", # 31
        ],
        [
            "................................", # 0
            "...................KK...........", # 1 (up 1px)
            "..................KJJB..........", # 2
            "..................BBBBBBBBB.....", # 3
            ".................BLLMLLLMMMB....", # 4
            "................BLLMMMMMMMMMB...", # 5
            "...............BLLMMMMMMMMMMMB..", # 6
            "..............BLLMMDDHMMMMMMMB..", # 7
            ".....KK......BLLMMDDHHMMMMMMMB..", # 8
            "....KJJB....BLLMMMDDHMMMMMMMMB..", # 9
            "....BBBB...BLLMMMMMMMPPMMMMMB...", # 10
            "..........BLLMMMMMMMMMPPMMMB....", # 11
            ".........BLLMMMMMMMMMMMMMMB.....", # 12
            "...KK...BLLMMMMMMMMMHBBBBB......", # 13
            "..KJJB.BLLMMMMMMMMMBB...........", # 14
            "..BBBBBLLMMVVVVMMMMB.BBB........", # 15
            "......BLLMMVVVVVVMMMBBHHB.......", # 16
            ".....BLLMMVVVVVVVVMMMBBB........", # 17
            ".KK.BLLMMMMVVVVVVVMMB...........", # 18
            "KJJBBLLMMMMMMVVVVVVMB...........", # 19
            "BBBBLLMMMMMMMMVVVVMB............", # 20
            "....BBBBLLMMMMMMMMB.............", # 21
            ".......BBBBBBMMMMMB.............", # 22
            "........BMMMMMBMMMMMB...........", # 23 passing
            "........BMMMMB.BMMMMB...........", # 24
            ".........BMMB...BMMB............", # 25
            ".........BMMB...BMMB............", # 26
            "........BHHHMB.BHHHMB...........", # 27
            "........BBBBBB.BBBBBB...........", # 28
            "................................", # 29
            "................................", # 30
            "................................", # 31
        ],
        [
            "................................", # 0
            "................................", # 1
            "...................KK...........", # 2
            "..................KJJB..........", # 3
            "..................BBBBBBBBB.....", # 4
            ".................BLLMLLLMMMB....", # 5
            "................BLLMMMMMMMMMB...", # 6
            "...............BLLMMMMMMMMMMMB..", # 7
            "..............BLLMMDDHMMMMMMMB..", # 8
            ".....KK......BLLMMDDHHMMMMMMMB..", # 9
            "....KJJB....BLLMMMDDHMMMMMMMMB..", # 10
            "....BBBB...BLLMMMMMMMPPMMMMMB...", # 11
            "..........BLLMMMMMMMMMPPMMMB....", # 12
            ".........BLLMMMMMMMMMMMMMMB.....", # 13
            "...KK...BLLMMMMMMMMMHBBBBB......", # 14
            "..KJJB.BLLMMMMMMMMMBB...........", # 15
            "..BBBBBLLMMVVVVMMMMB.BBB........", # 16
            "......BLLMMVVVVVVMMMBBHHB.......", # 17
            ".....BLLMMVVVVVVVVMMMBBB........", # 18
            ".KK.BLLMMMMVVVVVVVMMB...........", # 19
            "KJJBBLLMMMMMMVVVVVVMB...........", # 20
            "BBBBLLMMMMMMMMVVVVMB............", # 21
            "....BBBBLLMMMMMMMMB.............", # 22
            ".......BBBBBBMMMMMB.............", # 23
            "..........BMMMMMB..BMMMMMB......", # 24 stride 2
            ".........BMMMMB......BMMMMB.....", # 25
            "........BMMB...........BMMB.....", # 26
            ".......BMMB.............BMMB....", # 27
            "......BHHHMB...........BHHHMB...", # 28
            "......BBBBBB...........BBBBBB...", # 29
            "................................", # 30
            "................................", # 31
        ],
        [
            "................................", # 0
            "...................KK...........", # 1 (up 1px)
            "..................KJJB..........", # 2
            "..................BBBBBBBBB.....", # 3
            ".................BLLMLLLMMMB....", # 4
            "................BLLMMMMMMMMMB...", # 5
            "...............BLLMMMMMMMMMMMB..", # 6
            "..............BLLMMDDHMMMMMMMB..", # 7
            ".....KK......BLLMMDDHHMMMMMMMB..", # 8
            "....KJJB....BLLMMMDDHMMMMMMMMB..", # 9
            "....BBBB...BLLMMMMMMMPPMMMMMB...", # 10
            "..........BLLMMMMMMMMMPPMMMB....", # 11
            ".........BLLMMMMMMMMMMMMMMB.....", # 12
            "...KK...BLLMMMMMMMMMHBBBBB......", # 13
            "..KJJB.BLLMMMMMMMMMBB...........", # 14
            "..BBBBBLLMMVVVVMMMMB.BBB........", # 15
            "......BLLMMVVVVVVMMMBBHHB.......", # 16
            ".....BLLMMVVVVVVVVMMMBBB........", # 17
            ".KK.BLLMMMMVVVVVVVMMB...........", # 18
            "KJJBBLLMMMMMMVVVVVVMB...........", # 19
            "BBBBLLMMMMMMMMVVVVMB............", # 20
            "....BBBBLLMMMMMMMMB.............", # 21
            ".......BBBBBBMMMMMB.............", # 22
            "........BMMMMMBMMMMMB...........", # 23 passing 2
            "........BMMMMB.BMMMMB...........", # 24
            ".........BMMB...BMMB............", # 25
            ".........BMMB...BMMB............", # 26
            "........BHHHMB.BHHHMB...........", # 27
            "........BBBBBB.BBBBBB...........", # 28
            "................................", # 29
            "................................", # 30
            "................................", # 31
        ]
    ],
    "sleep": [
        [
            "................................", # 0
            "................................", # 1
            "................................", # 2
            "................................", # 3
            "................................", # 4
            "................................", # 5
            "................................", # 6
            "................................", # 7
            "................................", # 8
            "................................", # 9
            "................................", # 10
            "......................ZZ........", # 11 'z'
            ".......................Z........", # 12
            "......................ZZ........", # 13
            "...................KK...........", # 14
            "..................KJJB..........", # 15
            ".................BBBBBBBBB......", # 16
            "....KK..........BLLMLLLMMMB.....", # 17
            "...KJJB........BLLMMMMMMMMMB....", # 18
            "...BBBBB......BLLMMBBBBMMMMMB...", # 19 closed eye (BBBB)
            ".KK....BLLMMMBBLLMMMMMMMPPMMMB..", # 20
            "KJJB..BLLMMMMMMMMMMMMMMMHBBBBB..", # 21
            "BBBBBLLMMVVVVVVMMMMMMMMMBB......", # 22
            "....BBLLMMVVVVVVVVMMMMMMB.......", # 23
            ".....BBBBBBMMMMMMMMMMMMMB.......", # 24
            ".......BMMMMMBMMMMMMMMMB........", # 25
            "......BHHHMB..BHHHMMMB..........", # 26
            "......BBBBBB..BBBBBB............", # 27
            "................................", # 28
            "................................", # 29
            "................................", # 30
            "................................", # 31
        ],
        [
            "................................", # 0
            "................................", # 1
            "................................", # 2
            "................................", # 3
            "................................", # 4
            ".......................ZZZ......", # 5 big 'Z'
            ".........................Z......", # 6
            ".......................ZZZ......", # 7
            "................................", # 8
            "....................ZZ..........", # 9 small 'z'
            ".....................Z..........", # 10
            "....................ZZ..........", # 11
            "................................", # 12
            "................................", # 13
            "................................", # 14
            "...................KK...........", # 15
            "..................KJJB..........", # 16
            ".................BBBBBBBBB......", # 17
            "....KK..........BLLMLLLMMMB.....", # 18
            "...KJJB........BLLMMMMMMMMMB....", # 19
            "...BBBBB......BLLMMBBBBMMMMMB...", # 20
            ".KK....BLLMMMBBLLMMMMMMMPPMMMB..", # 21
            "KJJB..BLLMMMMMMMMMMMMMMMHBBBBB..", # 22
            "BBBBBLLMMVVVVVVMMMMMMMMMBB......", # 23
            "....BBLLMMVVVVVVVVMMMMMMB.......", # 24
            ".....BBBBBBMMMMMMMMMMMMMB.......", # 25
            ".......BMMMMMBMMMMMMMMMB........", # 26
            "......BHHHMB..BHHHMMMB..........", # 27
            "......BBBBBB..BBBBBB............", # 28
            "................................", # 29
            "................................", # 30
            "................................", # 31
        ]
    ]
}

# --- HAMSTER ---
HAMSTER_FRAMES = {
    "idle": [
        [
            "................................", # 0
            "................................", # 1
            "................................", # 2
            "................................", # 3
            "................................", # 4
            "................................", # 5
            "................................", # 6
            "................................", # 7
            ".............BB.....BB..........", # 8
            "............BPB....BPB..........", # 9
            "...........BOPB...BOPB..........", # 10
            "..........BLLLLBBBBLLBB.........", # 11
            ".........BLLLLLLLLLLLLLB........", # 12
            "........BLLOOOOOOOOOOOLLB.......", # 13
            ".......BLLOOOOOOOOOOOOOLLB......", # 14
            "......BLLOOOOOOOODDHLOOOOB......", # 15
            "......BLOOOOOOOODDDHOOOOOPB.....", # 16
            ".....BLOOOOOOOOODDDHOOOWWWPB....", # 17
            ".....BLOOOOOOOOOOOOOOWWWWWWWB...", # 18
            "....BLOOOOOOOOOOOOOOWWWWWWWWWB..", # 19
            "....BLOOOOOOOOOOOOOWWWWWWWWWWB..", # 20
            "....BLOOOOOOOOOOOOOWWWWWWWWWWB..", # 21
            "....BLOOOOOOOOOOOOOOWWWWWWWWB...", # 22
            ".....BLOOOOOOOOOOOOOOWWWWWWB....", # 23
            ".....BLOOOOOWWWWWWWWWWWWWB......", # 24
            "......BLOOOWWWWWWWWWWWWWB.......", # 25
            ".......BLBBWWWWWWWWWWWB.........", # 26
            ".......BBB.BPPB...BPPB..........", # 27
            "...........BPPB...BPPB..........", # 28
            "...........BBBB...BBBB..........", # 29
            "................................", # 30
            "................................", # 31
        ],
        [
            "................................", # 0
            "................................", # 1
            "................................", # 2
            "................................", # 3
            "................................", # 4
            "................................", # 5
            "................................", # 6
            "................................", # 7
            ".............BB.....BB..........", # 8
            "............BPB....BPB..........", # 9
            "...........BOPB...BOPB..........", # 10
            "..........BLLLLBBBBLLBB.........", # 11
            ".........BLLLLLLLLLLLLLB........", # 12
            "........BLLOOOOOOOOOOOLLB.......", # 13
            ".......BLLOOOOOOOOOOOOOLLB......", # 14
            "......BLLOOOOOOOODDHLOOOOB......", # 15
            "......BLOOOOOOOODDDHOOOOOPB.....", # 16
            ".....BLOOOOOOOOODDDHOOOWWWPB....", # 17
            "....BLOOOOOOOOOOOOOOWWWWWWWWWB..", # 18 (cheeks puff)
            "...BLOOOOOOOOOOOOOOOWWWWWWWWWWB.", # 19
            "...BLOOOOOOOOOOOOOOWWWWWWWWWWWWB", # 20
            "...BLOOOOOOOOOOOOOOWWWWWWWWWWWWB", # 21
            "....BLOOOOOOOOOOOOOOWWWWWWWWB...", # 22
            ".....BLOOOOOOOOOOOOOOWWWWWWB....", # 23
            ".....BLOOOOOWWWWWWWWWWWWWB......", # 24
            "......BLOOOWWWWWWWWWWWWWB.......", # 25
            ".......BLBBWWWWWWWWWWWB.........", # 26
            ".......BBB.BPPB...BPPB..........", # 27
            "...........BPPB...BPPB..........", # 28
            "...........BBBB...BBBB..........", # 29
            "................................", # 30
            "................................", # 31
        ],
        [
            "................................", # 0
            "................................", # 1
            "................................", # 2
            "................................", # 3
            "................................", # 4
            "................................", # 5
            "................................", # 6
            "................................", # 7
            ".............BB.....BB..........", # 8
            "............BPB....BPB..........", # 9
            "...........BOPB...BOPB..........", # 10
            "..........BLLLLBBBBLLBB.........", # 11
            ".........BLLLLLLLLLLLLLB........", # 12
            "........BLLOOOOOOOOOOOLLB.......", # 13
            ".......BLLOOOOOOOOOOOOOLLB......", # 14
            "......BLLOOOOOOOOBBBLOOOOB......", # 15 blink (BBB)
            "......BLOOOOOOOOOBBBHOOOOPB.....", # 16
            ".....BLOOOOOOOOOOOOOOOOWWWPB....", # 17
            ".....BLOOOOOOOOOOOOOOWWWWWWWB...", # 18
            "....BLOOOOOOOOOOOOOOWWWWWWWWWB..", # 19
            "....BLOOOOOOOOOOOOOWWWWWWWWWWB..", # 20
            "....BLOOOOOOOOOOOOOWWWWWWWWWWB..", # 21
            "....BLOOOOOOOOOOOOOOWWWWWWWWB...", # 22
            ".....BLOOOOOOOOOOOOOOWWWWWWB....", # 23
            ".....BLOOOOOWWWWWWWWWWWWWB......", # 24
            "......BLOOOWWWWWWWWWWWWWB.......", # 25
            ".......BLBBWWWWWWWWWWWB.........", # 26
            ".......BBB.BPPB...BPPB..........", # 27
            "...........BPPB...BPPB..........", # 28
            "...........BBBB...BBBB..........", # 29
            "................................", # 30
            "................................", # 31
        ]
    ],
    "walk": [
        [
            "................................", # 0
            "................................", # 1
            "................................", # 2
            "................................", # 3
            "................................", # 4
            "................................", # 5
            "................................", # 6
            "................................", # 7
            ".............BB.....BB..........", # 8
            "............BPB....BPB..........", # 9
            "...........BOPB...BOPB..........", # 10
            "..........BLLLLBBBBLLBB.........", # 11
            ".........BLLLLLLLLLLLLLB........", # 12
            "........BLLOOOOOOOOOOOLLB.......", # 13
            ".......BLLOOOOOOOOOOOOOLLB......", # 14
            "......BLLOOOOOOOODDHLOOOOB......", # 15
            "......BLOOOOOOOODDDHOOOOOPB.....", # 16
            ".....BLOOOOOOOOODDDHOOOWWWPB....", # 17
            ".....BLOOOOOOOOOOOOOOWWWWWWWB...", # 18
            "....BLOOOOOOOOOOOOOOWWWWWWWWWB..", # 19
            "....BLOOOOOOOOOOOOOWWWWWWWWWWB..", # 20
            "....BLOOOOOOOOOOOOOWWWWWWWWWWB..", # 21
            "....BLOOOOOOOOOOOOOOWWWWWWWWB...", # 22
            ".....BLOOOOOOOOOOOOOOWWWWWWB....", # 23
            ".....BLOOOOOWWWWWWWWWWWWWB......", # 24
            "......BLOOOWWWWWWWWWWWWWB.......", # 25
            ".......BLBBWWWWWWWWWWWB.........", # 26
            "......BPPB..BPPB................", # 27
            "......BPPB...BPPB...............", # 28
            "......BBBB...BBBB...............", # 29
            "................................", # 30
            "................................", # 31
        ],
        [
            "................................", # 0
            "................................", # 1
            "................................", # 2
            "................................", # 3
            "................................", # 4
            "................................", # 5
            "................................", # 6
            ".............BB.....BB..........", # 7 (up 1px)
            "............BPB....BPB..........", # 8
            "...........BOPB...BOPB..........", # 9
            "..........BLLLLBBBBLLBB.........", # 10
            ".........BLLLLLLLLLLLLLB........", # 11
            "........BLLOOOOOOOOOOOLLB.......", # 12
            ".......BLLOOOOOOOOOOOOOLLB......", # 13
            "......BLLOOOOOOOODDHLOOOOB......", # 14
            "......BLOOOOOOOODDDHOOOOOPB.....", # 15
            ".....BLOOOOOOOOODDDHOOOWWWPB....", # 16
            ".....BLOOOOOOOOOOOOOOWWWWWWWB...", # 17
            "....BLOOOOOOOOOOOOOOWWWWWWWWWB..", # 18
            "....BLOOOOOOOOOOOOOWWWWWWWWWWB..", # 19
            "....BLOOOOOOOOOOOOOWWWWWWWWWWB..", # 20
            "....BLOOOOOOOOOOOOOOWWWWWWWWB...", # 21
            ".....BLOOOOOOOOOOOOOOWWWWWWB....", # 22
            ".....BLOOOOOWWWWWWWWWWWWWB......", # 23
            "......BLOOOWWWWWWWWWWWWWB.......", # 24
            ".......BLBBWWWWWWWWWWWB.........", # 25
            ".......BBB.BPPB...BPPB..........", # 26
            "...........BPPB...BPPB..........", # 27
            "...........BBBB...BBBB..........", # 28
            "................................", # 29
            "................................", # 30
            "................................", # 31
        ],
        [
            "................................", # 0
            "................................", # 1
            "................................", # 2
            "................................", # 3
            "................................", # 4
            "................................", # 5
            "................................", # 6
            "................................", # 7
            ".............BB.....BB..........", # 8
            "............BPB....BPB..........", # 9
            "...........BOPB...BOPB..........", # 10
            "..........BLLLLBBBBLLBB.........", # 11
            ".........BLLLLLLLLLLLLLB........", # 12
            "........BLLOOOOOOOOOOOLLB.......", # 13
            ".......BLLOOOOOOOOOOOOOLLB......", # 14
            "......BLLOOOOOOOODDHLOOOOB......", # 15
            "......BLOOOOOOOODDDHOOOOOPB.....", # 16
            ".....BLOOOOOOOOODDDHOOOWWWPB....", # 17
            ".....BLOOOOOOOOOOOOOOWWWWWWWB...", # 18
            "....BLOOOOOOOOOOOOOOWWWWWWWWWB..", # 19
            "....BLOOOOOOOOOOOOOWWWWWWWWWWB..", # 20
            "....BLOOOOOOOOOOOOOWWWWWWWWWWB..", # 21
            "....BLOOOOOOOOOOOOOOWWWWWWWWB...", # 22
            ".....BLOOOOOOOOOOOOOOWWWWWWB....", # 23
            ".....BLOOOOOWWWWWWWWWWWWWB......", # 24
            "......BLOOOWWWWWWWWWWWWWB.......", # 25
            ".......BLBBWWWWWWWWWWWB.........", # 26
            "............BPPB..BPPB..........", # 27
            ".............BPPB..BPPB.........", # 28
            ".............BBBB..BBBB.........", # 29
            "................................", # 30
            "................................", # 31
        ],
        [
            "................................", # 0
            "................................", # 1
            "................................", # 2
            "................................", # 3
            "................................", # 4
            "................................", # 5
            "................................", # 6
            ".............BB.....BB..........", # 7 (up 1px)
            "............BPB....BPB..........", # 8
            "...........BOPB...BOPB..........", # 9
            "..........BLLLLBBBBLLBB.........", # 10
            ".........BLLLLLLLLLLLLLB........", # 11
            "........BLLOOOOOOOOOOOLLB.......", # 12
            ".......BLLOOOOOOOOOOOOOLLB......", # 13
            "......BLLOOOOOOOODDHLOOOOB......", # 14
            "......BLOOOOOOOODDDHOOOOOPB.....", # 15
            ".....BLOOOOOOOOODDDHOOOWWWPB....", # 16
            ".....BLOOOOOOOOOOOOOOWWWWWWWB...", # 17
            "....BLOOOOOOOOOOOOOOWWWWWWWWWB..", # 18
            "....BLOOOOOOOOOOOOOWWWWWWWWWWB..", # 19
            "....BLOOOOOOOOOOOOOWWWWWWWWWWB..", # 20
            "....BLOOOOOOOOOOOOOOWWWWWWWWB...", # 21
            ".....BLOOOOOOOOOOOOOOWWWWWWB....", # 22
            ".....BLOOOOOWWWWWWWWWWWWWB......", # 23
            "......BLOOOWWWWWWWWWWWWWB.......", # 24
            ".......BLBBWWWWWWWWWWWB.........", # 25
            ".......BBB.BPPB...BPPB..........", # 26
            "...........BPPB...BPPB..........", # 27
            "...........BBBB...BBBB..........", # 28
            "................................", # 29
            "................................", # 30
            "................................", # 31
        ]
    ],
    "sleep": [
        [
            "................................", # 0
            "................................", # 1
            "................................", # 2
            "................................", # 3
            "................................", # 4
            "................................", # 5
            "................................", # 6
            "................................", # 7
            "................................", # 8
            "................................", # 9
            "................................", # 10
            "......................ZZ........", # 11 'z'
            ".......................Z........", # 12
            "......................ZZ........", # 13
            "................................", # 14
            ".............BB.....BB..........", # 15
            "............BPB....BPB..........", # 16
            "..........BLLLLBBBBLLBB.........", # 17
            ".........BLLLLLLLLLLLLLB........", # 18
            "........BLLOOOOOOOOOOOLLB.......", # 19
            ".......BLLOOOOOOOOBBBLOOOB......", # 20
            "......BLOOOOOOOOOBBBHOOOOPB.....", # 21
            ".....BLOOOOOOOOOOOOOOWWWWWPB....", # 22
            "....BLOOOOOOOOOOOOOOWWWWWWWWWB..", # 23
            "....BLOOOOOOOOOOOOOWWWWWWWWWWB..", # 24
            "....BLOOOOOOOOOOOOOWWWWWWWWWWB..", # 25
            ".....BLOOOOOOOOOOOOOOWWWWWWB....", # 26
            ".....BLOOOOOWWWWWWWWWWWWWB......", # 27
            "......BLOOOWWWWWWWWWWWWWB.......", # 28
            ".......BBBBWWWWWWWWWWWBB........", # 29
            "................................", # 30
            "................................", # 31
        ],
        [
            "................................", # 0
            "................................", # 1
            "................................", # 2
            "................................", # 3
            "................................", # 4
            ".......................ZZZ......", # 5 big 'Z'
            ".........................Z......", # 6
            ".......................ZZZ......", # 7
            "................................", # 8
            "....................ZZ..........", # 9 small 'z'
            ".....................Z..........", # 10
            "....................ZZ..........", # 11
            "................................", # 12
            "................................", # 13
            "................................", # 14
            ".............BB.....BB..........", # 15
            "............BPB....BPB..........", # 16
            "..........BLLLLBBBBLLBB.........", # 17
            ".........BLLLLLLLLLLLLLB........", # 18
            "........BLLOOOOOOOOOOOLLB.......", # 19
            ".......BLLOOOOOOOOBBBLOOOB......", # 20
            "......BLOOOOOOOOOBBBHOOOOPB.....", # 21
            ".....BLOOOOOOOOOOOOOOWWWWWPB....", # 22
            "....BLOOOOOOOOOOOOOOWWWWWWWWWB..", # 23
            "....BLOOOOOOOOOOOOOWWWWWWWWWWB..", # 24
            "....BLOOOOOOOOOOOOOWWWWWWWWWWB..", # 25
            ".....BLOOOOOOOOOOOOOOWWWWWWB....", # 26
            ".....BLOOOOOWWWWWWWWWWWWWB......", # 27
            "......BLOOOWWWWWWWWWWWWWB.......", # 28
            ".......BBBBWWWWWWWWWWWBB........", # 29
            "................................", # 30
            "................................", # 31
        ]
    ]
}

# ==============================================================================
# PET CONFIGURATIONS & GENERATOR
# ==============================================================================

PET_CONFIGS = [
    {
        "name": "Cat",
        "palette": PALETTE_CAT,
        "frames": CAT_FRAMES,
        "walkSpeed": 30.0,
        "runSpeed": 60.0,
    },
    {
        "name": "Dog",
        "palette": PALETTE_DOG,
        "frames": DOG_FRAMES,
        "walkSpeed": 30.0,
        "runSpeed": 60.0,
    },
    {
        "name": "Parrot",
        "palette": PALETTE_PARROT,
        "frames": PARROT_FRAMES,
        "walkSpeed": 30.0,
        "runSpeed": 60.0,
    },
    {
        "name": "Rabbit",
        "palette": PALETTE_RABBIT,
        "frames": RABBIT_FRAMES,
        "walkSpeed": 30.0,
        "runSpeed": 60.0,
    },
    {
        "name": "Turtle",
        "palette": PALETTE_TURTLE,
        "frames": TURTLE_FRAMES,
        "walkSpeed": 20.0,
        "runSpeed": 40.0,
    },
    {
        "name": "Dinosaur",
        "palette": PALETTE_DINOSAUR,
        "frames": DINOSAUR_FRAMES,
        "walkSpeed": 30.0,
        "runSpeed": 60.0,
    },
    {
        "name": "Hamster",
        "palette": PALETTE_HAMSTER,
        "frames": HAMSTER_FRAMES,
        "walkSpeed": 30.0,
        "runSpeed": 60.0,
    },
]

def render_grid_to_image(grid, palette):
    """Render a 32x32 ASCII grid into a PIL RGBA Image using putpixel."""
    assert len(grid) == 32, f"Grid has {len(grid)} rows, expected 32"
    img = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
    for y, row in enumerate(grid):
        assert len(row) == 32, f"Row {y} has {len(row)} cols, expected 32: {row}"
        for x, char in enumerate(row):
            color = palette.get(char, (0, 0, 0, 0))
            if color[3] > 0:
                img.putpixel((x, y), color)
    return img

# ==============================================================================
# INTERACTION ANIMATION HELPERS
# ==============================================================================

HEART_PLACEMENTS = {
    "Cat": (20, 1),
    "Dog": (20, 1),
    "Parrot": (8, 1),
    "Rabbit": (7, 1),
    "Turtle": (22, 6),
    "Dinosaur": (8, 1),
    "Hamster": (18, 2),
}

STAMP_HEART_SMALL = [
    ".R.R.",
    "RRHRR",
    ".RRR.",
    "..R..",
]

STAMP_HEART_FULL = [
    ".RR.RR",
    "RRHRRR",
    ".RRRR.",
    "..RR..",
]

STAMP_HEART_SPARKLE = [
    ".H...H",
    "...H..",
    ".H...H",
]

def overlay_stamp(grid, stamp, start_x, start_y):
    new_grid = [list(row) for row in grid]
    for dy, srow in enumerate(stamp):
        for dx, ch in enumerate(srow):
            if ch != ".":
                x = start_x + dx
                y = start_y + dy
                if 0 <= y < len(new_grid) and 0 <= x < len(new_grid[0]):
                    new_grid[y][x] = ch
    return ["".join(r) for r in new_grid]

def hop_grid(grid):
    return grid[1:] + ["." * 32]

def make_interaction_frames(idle_frames, heart_x, heart_y):
    f0 = overlay_stamp(idle_frames[0], STAMP_HEART_SMALL, heart_x, heart_y + 1)
    f1 = overlay_stamp(hop_grid(idle_frames[0]), STAMP_HEART_FULL, heart_x, heart_y)
    f2 = overlay_stamp(idle_frames[1], STAMP_HEART_SPARKLE, heart_x, max(0, heart_y - 1))
    return [f0, f1, f2]

def create_manifest(pet_name, walk_speed=30.0, run_speed=60.0):
    """Create the manifest dictionary matching DockPet asset pipeline."""
    return {
        "name": pet_name,
        "version": 1,
        "spriteSize": {
            "width": 32,
            "height": 32
        },
        "scale": 2,
        "anchorY": 0,
        "animations": {
            "idle": {
                "fps": 4,
                "loop": True
            },
            "walk": {
                "fps": 6,
                "loop": True
            },
            "sleep": {
                "fps": 2,
                "loop": True
            },
            "interaction": {
                "fps": 4,
                "loop": False
            }
        },
        "movement": {
            "walkSpeed": walk_speed,
            "runSpeed": run_speed
        }
    }

def generate_all_pets(output_base_dir: Path):
    """Generate all pets into the output directory."""
    output_base_dir.mkdir(parents=True, exist_ok=True)
    generated_summary = []

    for pet_cfg in PET_CONFIGS:
        pet_name = pet_cfg["name"]
        palette = pet_cfg["palette"]
        frames_dict = pet_cfg["frames"]
        walk_speed = pet_cfg["walkSpeed"]
        run_speed = pet_cfg["runSpeed"]

        pet_dir = output_base_dir / pet_name
        pet_dir.mkdir(parents=True, exist_ok=True)

        # Write manifest.json
        manifest_path = pet_dir / "manifest.json"
        manifest_data = create_manifest(pet_name, walk_speed, run_speed)
        with open(manifest_path, "w", encoding="utf-8") as mf:
            json.dump(manifest_data, mf, indent=2)

        pet_frames_count = 0

        # Generate interaction frames if not already present
        if "interaction" not in frames_dict and "idle" in frames_dict:
            hx, hy = HEART_PLACEMENTS.get(pet_name, (18, 2))
            frames_dict["interaction"] = make_interaction_frames(frames_dict["idle"], hx, hy)

        # Generate each animation state folder and frames
        for anim_name, frame_list in frames_dict.items():
            anim_dir = pet_dir / anim_name
            anim_dir.mkdir(parents=True, exist_ok=True)

            for f_idx, grid in enumerate(frame_list):
                img = render_grid_to_image(grid, palette)
                frame_filename = f"frame_{f_idx:02d}.png"
                frame_path = anim_dir / frame_filename
                img.save(frame_path, "PNG")
                pet_frames_count += 1

        generated_summary.append((pet_name, pet_frames_count))
        print(f"  [✓] {pet_name:10s}: manifest.json + {pet_frames_count} frames generated")

    return generated_summary

def main():
    # Target directory: /Users/yunusemre/Desktop/PixelPet/Assets/Pets
    project_root = Path(__file__).resolve().parent.parent
    assets_pets_dir = project_root / "Assets" / "Pets"

    print("==================================================")
    print(" DockPet Sprite Generator")
    print(f" Target Directory: {assets_pets_dir}")
    print("==================================================")

    summary = generate_all_pets(assets_pets_dir)

    total_pets = len(summary)
    total_frames = sum(c for _, c in summary)
    print("--------------------------------------------------")
    print(f" Successfully generated {total_pets} pets ({total_frames} frames total)!")
    print("==================================================")

if __name__ == "__main__":
    main()
