# DockPet 🐾

A native macOS desktop application where a pixel-art virtual pet lives around the macOS Dock.

## Project Status

**Status:** Implemented native macOS app; roadmap milestones M0–M14 are complete.

Ten 64×64 pets follow a repeating **10s walk → 5s signature action → 10s sleep** cycle. Movement covers the full screen edge above/beside the Dock, with automatic turnaround. See [PROJECT_STATE.md](PROJECT_STATE.md) for current validation and [DECISIONS.md](DECISIONS.md) for later behavior and rendering decisions.

Build and launch on macOS 14+ with Xcode's Swift toolchain:

```sh
swift test
./scripts/build_app.sh --release
open build/DockPet.app
```

## What Is DockPet?

DockPet places a small, animated pixel-art companion on your screen — walking, idling, and interacting near the macOS Dock. It uses a transparent native window positioned relative to the Dock, so the pet appears to live on top of your desktop environment.

The application is:
- **Lightweight** — minimal CPU/memory footprint
- **Native** — built with Swift and AppKit, no web runtimes
- **Charming** — pixel-art sprites with personality
- **Non-intrusive** — sits quietly near the Dock, never blocks your work

## Supported Pets

| Pet | Status |
|-----|--------|
| Baby Yoda | Gray hood, green lightsaber, solo training, sleep |
| Cat | Walking, yarn play, sleep |
| Dog | Walking, celebration, sleep |
| Parrot | Walking, wing flapping, sleep |
| Rabbit | Hopping, carrot snack, sleep |
| Turtle | Walking, shell retreat, sleep |
| Dinosaur | Walking, roar, sleep |
| Hamster | Walking, seeds, sleep |
| Cristiano Ronaldo | Walking, SIU → silver European cup lift, rest |
| Lionel Messi | Walking, visible ball skill → goal celebration → World Cup lift, rest |

Original pet artwork is supplied by the project owner; Baby Yoda uses a deterministic pixel-art generator. The application defines a clean [asset pipeline](docs/ASSET_PIPELINE.md) so sprites can be dropped into predefined folders.

## Architecture Overview

DockPet is built around modular, testable components:

- **WindowSystem** — transparent native window management
- **DockGeometry** — Dock position/size detection
- **PetEngine** — state machine, movement, and behavior
- **Rendering** — pixel-perfect sprite display
- **Assets** — data-driven sprite loading
- **Interaction** — mouse/click handling

See [ARCHITECTURE.md](ARCHITECTURE.md) for full details.

## Development Philosophy

1. **Documentation first** — design before code
2. **Incremental milestones** — each independently verifiable
3. **Native macOS only** — no Electron, Tauri, or web views
4. **No private APIs** — only public, maintainable Apple APIs
5. **Testable domain logic** — behavior logic separated from platform code
6. **Asset pipeline** — artists never touch Swift code

## Documentation

| Document | Purpose |
|----------|---------|
| [GEMINI.md](GEMINI.md) | Agent context router (keep small) |
| [AGENTS.md](AGENTS.md) | Agent operating rules |
| [PRODUCT.md](PRODUCT.md) | Product vision and MVP |
| [ROADMAP.md](ROADMAP.md) | Staged milestone plan |
| [ARCHITECTURE.md](ARCHITECTURE.md) | Technical architecture |
| [DECISIONS.md](DECISIONS.md) | Architectural decision records |
| [PROJECT_STATE.md](PROJECT_STATE.md) | Compressed current state |
| [TOKEN_REDUCE.md](TOKEN_REDUCE.md) | Context efficiency protocol |
| [SKILLS.md](SKILLS.md) | Agent skill definitions |
| [docs/ASSET_PIPELINE.md](docs/ASSET_PIPELINE.md) | Sprite asset conventions |
| [docs/PET_BEHAVIOR.md](docs/PET_BEHAVIOR.md) | Behavior and state system |
| [docs/MACOS_RESEARCH.md](docs/MACOS_RESEARCH.md) | macOS API research |
| [docs/TESTING_STRATEGY.md](docs/TESTING_STRATEGY.md) | Testing approach |

## Getting Started (Future Contributors)

1. Read [GEMINI.md](GEMINI.md) for the routing table
2. Read [PROJECT_STATE.md](PROJECT_STATE.md) for current status
3. Read documentation relevant to your task
4. Follow rules in [AGENTS.md](AGENTS.md)
5. Follow context protocol in [TOKEN_REDUCE.md](TOKEN_REDUCE.md)

## License

TBD
