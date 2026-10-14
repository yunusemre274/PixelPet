# Current Project State

**Current Milestone:** M9 — Multi-Monitor & Dock Orientations  
**Status:** M1 through M9 DONE

## Working

- Transparent NSPanel displays pet directly above the macOS Dock
- Menu bar agent (LSUIElement) — no Dock icon, no Cmd+Tab
- NSPanel: borderless, non-activating, no shadow, stays visible across app switches
- Window level `.floating` — above desktop, below system UI
- Spaces: `.canJoinAllSpaces`, `.fullScreenAuxiliary`, `.stationary`, `.ignoresCycle`
- DockGeometry module: detects bottom, left, and right Dock orientations from screen geometry (M2)
- Multi-Monitor support: automatic Dock display detection and manual display selection via "Display" menu bar submenu (M9)
- Auto-hide support: detects `com.apple.dock` auto-hide flag, places pet gracefully on the screen edge (M9)
- SpriteView: Core Graphics + CALayer with nearest-neighbor rendering (`.magnificationFilter = .nearest`, no blur) (M3)
- Real pixel-art sprites generated for all 7 pet types: Cat, Dog, Parrot, Rabbit, Turtle, Dinosaur, Hamster (ADR-013)
- Multi-state animations: idle (3 frames), walk (4 frames), sleep (2 frames)
- PetMovement: horizontal/vertical movement physics with boundary collision turnaround and orientation-aware direction (M4/M9)
- PetStateMachine: idle ↔ walk transitions, sleep after prolonged idle, click interaction, deterministic RNG testing (M5)
- PetAssetLoader: scans `Assets/Pets/`, decodes `manifest.json`, loads animation frame PNGs with fallback chain and caching (M6)
- Sprite interaction: click-through transparent regions via per-pixel alpha hit testing, click triggers pet reaction (M7)
- Menu Bar pet selection: "Select Pet" submenu with checkmarks for active pet, persisted across launches via UserDefaults (M8)
- Battery optimization: pauses window frame updates when pet is idle/sleeping
- 34 automated unit tests passing in 0.006s

## Not Implemented

- Performance profiling and automated CPU/memory benchmarks (M10)
- Code signing, notarization, DMG / installer packaging (M11)

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
| 007 | Animation timing: CADisplayLink | **ACCEPTED** (M4/M5 validated) |
| 008 | Settings UI: AppKit NSMenu | **ACCEPTED** (M8 validated) |
| 009 | Persistence: UserDefaults | **ACCEPTED** (M8 validated) |
| 010 | Window level: `.floating` | **ACCEPTED** (M1 validated) |
| 011 | Deployment target: macOS 14+ | **ACCEPTED** (M1 validated) |
| 012 | Window tech: NSPanel | **ACCEPTED** (M1 validated) |
| 013 | Asset Origin: Agent-Generated Pixel Art | **ACCEPTED** (M3/M6 validated) |

## Current File/Module Structure

```
PixelPet/
├── Package.swift
├── .gitignore
├── Assets/
│   └── Pets/
│       ├── Cat/ (manifest.json, idle/, walk/, sleep/)
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
│       └── Info.plist
├── Tests/
│   └── DockPetTests/
│       ├── DockGeometryTests.swift
│       ├── PetEngineTests.swift
│       └── PetAssetLoaderTests.swift
├── scripts/
│   ├── build_app.sh
│   └── generate_sprites.py
├── docs/
└── [Documentation files]
```

## Next Recommended Task

**M10 — Performance / Stability**: Conduct memory leak audit, CPU profiling, and verify power consumption during long-running background execution.

## Last Significant Change

Completed M9: Implemented multi-monitor display detection and menu selection, auto-hide Dock accommodation, and 34 unit tests passing.
