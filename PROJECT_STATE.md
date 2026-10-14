# Current Project State

**Current Milestone:** All Milestones (M0 — M21) Completed  
**Status:** ALL MILESTONES DONE — CUSTOM 64×64 PETS, CR7 & MESSI, SIGNATURE ANIMATIONS & EXTREME OPTIMIZATION COMPLETE

## Working

- Transparent NSPanel displays pet directly above the macOS Dock
- Menu bar agent (LSUIElement) — no Dock icon, no Cmd+Tab
- NSPanel: borderless, non-activating, no shadow, stays visible across app switches
- Window level `.floating` — above desktop, below system UI
- Spaces: `.canJoinAllSpaces`, `.fullScreenAuxiliary`, `.stationary`, `.ignoresCycle`
- DockGeometry module: detects bottom, left, and right Dock orientations from screen geometry (M2)
- Multi-Monitor support: automatic Dock display detection and manual display selection via "Display" menu bar submenu (M9)
- Auto-hide support: detects `com.apple.dock` auto-hide flag, places pet gracefully on the screen edge (M9)
- SpriteView: Core Graphics + CALayer with nearest-neighbor rendering (`.magnificationFilter = .nearest`, no blur) (M3/M17)
- **High-Quality 64×64 Pixel-Art Upgraded for 9 Pet Types** (M15/M16/M20, ADR-017):
  - Cat, Dog, Parrot, Rabbit, Turtle, Dinosaur, Hamster
  - **Cristiano Ronaldo**: SIU spin & landing celebration + Champions League trophy lift
  - **Lionel Messi**: Goal celebration slide + World Cup trophy lift
  - **Turtle**: Full protective shell retreat & peek animation
- **Advanced State Machine & Pet Behavior** (M5/M17/M20):
  - States: `idle`, `walking`, `sleeping`, `interaction`, `specialAnimation`
  - Periodic 15–30s signature special animations
  - Active time tracking: after cumulative 2 minutes (120s) of activity (idle+walking), pet enters a 30s restorative sleep
  - Interactive reaction animations with click feedback and native `Pop` sound
- PetMovement: horizontal/vertical movement physics with boundary collision turnaround and orientation-aware direction (M4/M9)
- PetAssetLoader: scans `Assets/Pets/`, decodes `manifest.json`, loads animation frame PNGs with fallback chain and active-pet-only caching (M6/M19)
- Sprite interaction: click-through transparent regions via per-pixel alpha hit testing (M7)
- User Customization & Menu Bar Controls (M13):
  - "Pet Size" submenu: 1× (64px), 2× (128px), 3× (192px)
  - "Activity Level" submenu: Calm, Normal, Energetic
  - Dynamic window resizing, movement bounds recalculation, and Dock geometry adjustment
  - All settings persisted via `UserDefaults` across app launches
- **Extreme Power & Memory Optimization** (M10/M19):
  - Dynamic display link throttling (5-10Hz when idle/sleeping, 60-120Hz during walking)
  - Active-pet cache eviction upon switching pets
  - CPU usage: 0.2% - 0.5% during idle
  - Memory: **22.1 MB physical footprint** (measured via `vmmap -summary`, within 10MB-30MB target budget)
- Packaging & Distribution (M11 & M14):
  - High-resolution retro pixel-art macOS squircle `AppIcon.icns` generated via `scripts/generate_app_icon.py` and `iconutil`
  - Self-contained signed release `.app` bundle via `./scripts/build_app.sh --release`
  - Automated compressed DMG installer creation with drag-and-drop `/Applications` symlink via `./scripts/create_dmg.sh`
- **42 automated unit tests passing across 9 test suites in 0.05s**

## Not Implemented / Future Explorations

- Pet snack / feeding interactions (optional future stretch goal)
- Drag-and-drop pet repositioning (optional future stretch goal)

## Known Issues

- Benign `_NSDetectedLayoutRecursion` warning from NSStatusItem (macOS system internal behavior)

## Important Decisions

| ADR | Topic | Status |
|-----|-------|--------|
| 001 | Menu bar agent (LSUIElement) | **ACCEPTED** (M1 validated) |
| 002 | Language: Swift | ACCEPTED |
| 003 | Primary framework: AppKit | ACCEPTED |
| 004 | Rendering: Core Graphics + CALayer | **ACCEPTED** (M3 validated) |
| 005 | Dock detection: geometry inference | **ACCEPTED** (M2 validated) |
| 006 | Dock auto-hide handling | **ACCEPTED** (M9 validated) |
| 007 | Animation timing: CADisplayLink | **ACCEPTED** (M4/M5/M10 validated) |
| 008 | Settings UI: AppKit NSMenu | **ACCEPTED** (M8 validated) |
| 009 | Persistence: UserDefaults | **ACCEPTED** (M8 validated) |
| 010 | Window level: `.floating` | **ACCEPTED** (M1 validated) |
| 011 | Deployment target: macOS 14+ | **ACCEPTED** (M1 validated) |
| 012 | Window tech: NSPanel | **ACCEPTED** (M1 validated) |
| 013 | Asset Origin: Agent-Generated Pixel Art | **ACCEPTED** (M3/M6 validated) |
| 014 | Interactive Feedback & Audio Engine | **ACCEPTED** (M12 validated) |
| 015 | In-Menu Customization (Size & Activity) | **ACCEPTED** (M13 validated) |
| 016 | Application Icon & Packaging | **ACCEPTED** (M14 validated) |

## Current File/Module Structure

```
PixelPet/
├── Package.swift
├── .gitignore
├── Assets/
│   └── Pets/
│       ├── Cat/ (manifest.json, idle/, walk/, sleep/, interaction/)
│       ├── Dog/
│       ├── Parrot/
│       ├── Rabbit/
│       ├── Turtle/
│       ├── Dinosaur/
│       └── Hamster/
├── DockPet/
│   ├── Application/
│   │   ├── main.swift
│   │   └── AppDelegate.swift
│   ├── Assets/
│   │   ├── PetManifest.swift
│   │   └── PetAssetLoader.swift
│   ├── DockGeometry/
│   │   └── DockGeometry.swift
│   ├── PetEngine/
│   │   ├── PetStateMachine.swift
│   │   ├── PetMovement.swift
│   │   └── PetCoordinator.swift
│   ├── Rendering/
│   │   └── SpriteView.swift
│   ├── WindowSystem/
│   │   ├── PetPanel.swift
│   │   ├── PetWindowController.swift
│   │   └── PlaceholderPetView.swift
│   └── Resources/
│       ├── Info.plist
│       └── AppIcon.icns
├── Tests/
│   └── DockPetTests/
│       ├── DockGeometryTests.swift
│       ├── PetEngineTests.swift
│       └── PetAssetLoaderTests.swift
├── scripts/
│   ├── build_app.sh
│   ├── create_dmg.sh
│   ├── generate_sprites.py
│   └── generate_app_icon.py
├── docs/
└── [Documentation files]
```

## Last Significant Change

Completed M12 (Interactive Reaction Animations & Sound), M13 (Pet Sizing 1x/2x/3x & Activity Level Customization), and M14 (Retro Pixel-Art AppIcon.icns & Release Packaging). 38 tests passing.

