# Agent Skills

This document defines reusable capability areas for agents working on DockPet. Each skill has clear boundaries, inputs, outputs, and constraints.

---

## Skill: macOS Window Management

**Responsibility:** Creating, configuring, and managing the transparent overlay window where the pet is rendered.

**Inputs:**
- Target screen and Dock geometry
- Desired window dimensions and position
- Collection behavior requirements (Spaces, fullscreen)

**Expected Outputs:**
- A transparent, borderless, click-aware NSWindow/NSPanel at the correct screen position
- Correct window level so the pet floats above the desktop but below alerts
- Proper behavior across Spaces transitions

**Related Documentation:**
- [ARCHITECTURE.md](ARCHITECTURE.md) → WindowSystem module
- [docs/MACOS_RESEARCH.md](docs/MACOS_RESEARCH.md) → NSWindow, NSPanel, window levels, Spaces

**When to Activate:** Any task involving window creation, positioning, transparency, window levels, Spaces behavior, or fullscreen handling.

**Must NOT Modify:**
- Pet behavior/state logic
- Sprite rendering internals
- Asset loading
- Dock detection logic (only consumes its output)

---

## Skill: Pixel Sprite Rendering

**Responsibility:** Drawing pixel-art sprites to screen with crisp, unblurred rendering at correct scale.

**Inputs:**
- Sprite image data (from asset pipeline)
- Current animation frame index
- Target render size and position
- Display scale factor (Retina)

**Expected Outputs:**
- Pixel-perfect sprite display at integer scale
- Nearest-neighbor interpolation (no bilinear blur)
- Correct frame timing for animation playback
- Proper Retina handling

**Related Documentation:**
- [ARCHITECTURE.md](ARCHITECTURE.md) → Rendering module
- [docs/ASSET_PIPELINE.md](docs/ASSET_PIPELINE.md) → sprite format, frame ordering, dimensions
- [docs/MACOS_RESEARCH.md](docs/MACOS_RESEARCH.md) → SpriteKit, Core Animation, NSImage rendering

**When to Activate:** Any task involving sprite display, animation playback, scaling, image loading, or rendering quality.

**Must NOT Modify:**
- Window management logic
- Pet behavior/state transitions
- Dock geometry detection
- Asset manifest format (coordinate with Asset Pipeline skill)

---

## Skill: Pet State Machine

**Responsibility:** Managing pet behavioral states and transitions.

**Inputs:**
- Current state
- Elapsed time / timers
- External events (click, boundary hit, mouse proximity)
- Pet type configuration (speed, personality weights)

**Expected Outputs:**
- Current active state (idle, walk, sleep, run, jump, interaction)
- Transition events to drive animation and movement changes
- Deterministic behavior given same inputs (for testing)

**Related Documentation:**
- [ARCHITECTURE.md](ARCHITECTURE.md) → PetEngine module
- [docs/PET_BEHAVIOR.md](docs/PET_BEHAVIOR.md) → state definitions, transitions, randomness
- [PRODUCT.md](PRODUCT.md) → expected pet behaviors

**When to Activate:** Any task involving pet behavior, state transitions, idle timers, random behavior, or personality differences.

**Must NOT Modify:**
- Window management
- Rendering implementation
- Dock detection
- Asset loading
- macOS platform code

---

## Skill: Dock Detection

**Responsibility:** Determining Dock position, orientation, size, and auto-hide state.

**Inputs:**
- NSScreen geometry (frame, visibleFrame)
- System UserDefaults (com.apple.dock where publicly readable)
- Screen change notifications

**Expected Outputs:**
- Dock orientation (bottom, left, right)
- Dock screen-space rectangle (inferred)
- Auto-hide state
- Notification when Dock geometry changes

**Related Documentation:**
- [ARCHITECTURE.md](ARCHITECTURE.md) → DockGeometry module
- [docs/MACOS_RESEARCH.md](docs/MACOS_RESEARCH.md) → NSScreen, visibleFrame, Dock detection

**When to Activate:** Any task involving Dock position detection, screen geometry, multi-monitor layout, or Dock auto-hide.

**Must NOT Modify:**
- Pet behavior logic
- Rendering
- Window creation (only provides geometry data)
- Asset system

---

## Skill: Performance

**Responsibility:** Ensuring the application runs efficiently for hours with minimal resource consumption.

**Inputs:**
- Animation loop design
- Timer/event monitor usage patterns
- Rendering pipeline

**Expected Outputs:**
- CPU usage stays low during idle and animation
- Memory is stable (no leaks, no growth)
- Battery impact is minimal
- Animation remains smooth

**Related Documentation:**
- [ARCHITECTURE.md](ARCHITECTURE.md) → all modules (performance cross-cuts)
- [docs/MACOS_RESEARCH.md](docs/MACOS_RESEARCH.md) → animation timing, CADisplayLink
- [PRODUCT.md](PRODUCT.md) → lightweight requirement

**When to Activate:** Performance profiling, animation timing optimization, reducing polling, fixing memory leaks, or reviewing timer usage.

**Must NOT Modify:**
- Product requirements
- Feature scope
- Asset formats

---

## Skill: Testing

**Responsibility:** Verifying correctness of behavior logic, geometry, rendering, and platform integration.

**Inputs:**
- Architecture module boundaries
- State machine definitions
- Geometry calculations
- Asset manifest format

**Expected Outputs:**
- Unit tests for domain logic (state machine, movement, geometry)
- Integration tests for platform behavior (window positioning, display changes)
- Manual test checklists for macOS-specific scenarios
- All tests runnable without a real Dock or pixel art assets

**Related Documentation:**
- [docs/TESTING_STRATEGY.md](docs/TESTING_STRATEGY.md)
- [ARCHITECTURE.md](ARCHITECTURE.md) → testability per module

**When to Activate:** Writing tests, reviewing test coverage, defining test fixtures, or verifying a milestone's definition of done.

**Must NOT Modify:**
- Production code behavior (tests observe, not change)
- Asset files
- Documentation files (except test documentation)
