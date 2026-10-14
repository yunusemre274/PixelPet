# Testing Strategy

Testing is designed before implementation. The architecture maximizes logic that can be tested without UI automation.

---

## Testing Principles

1. **Domain logic is pure** — PetEngine (state machine, movement, behavior) has zero AppKit dependencies and is fully unit-testable
2. **Platform code is thin** — WindowSystem, Rendering, and Interaction are thin wrappers around macOS APIs with minimal logic
3. **Deterministic randomness** — all random behavior accepts a seeded `RandomSource` for reproducible tests
4. **Injected time** — all timers accept `deltaTime` instead of using real clocks
5. **Protocol boundaries** — modules communicate through protocols, enabling mock injection

---

## Unit Tests

Unit tests run in XCTest without any macOS UI. They must be fast and deterministic.

### State Machine Tests

| Test | Verifies |
|------|----------|
| Initial state is `idle` | State machine starts correctly |
| Idle → walking after timer | Timer-based transition works |
| Walking → idle after timer | Return transition works |
| Walking → idle on boundary hit | Event-based transition works |
| Any → interaction on click | Click event triggers reaction |
| Interaction → idle on animation complete | One-shot completion works |
| State duration within configured range | Random duration is bounded |
| Weighted transitions respect probabilities | Over many iterations, distribution matches weights |
| Deterministic with seeded random | Same seed produces same sequence |

### Movement Tests

| Test | Verifies |
|------|----------|
| Position updates by speed × deltaTime | Basic movement math |
| Position clamped to bounds | Boundary enforcement |
| Direction reverses at boundary | Turnaround logic |
| Speed matches current state (walk vs run) | State-speed mapping |
| Zero speed during idle/sleep | Stationary states don't move |
| Direction flip updates correctly | Left/right tracking |

### Geometry Tests

| Test | Verifies |
|------|----------|
| Dock orientation from frame/visibleFrame diff (bottom) | Bottom Dock detection |
| Dock orientation from frame/visibleFrame diff (left) | Left Dock detection |
| Dock orientation from frame/visibleFrame diff (right) | Right Dock detection |
| Dock thickness calculation | Inset math |
| Pet region calculation for bottom Dock | Placement math |
| Pet region calculation for left Dock | Placement math |
| Pet region calculation for right Dock | Placement math |
| Auto-hide detection (visibleFrame ≈ frame) | Edge case handling |

### Asset Loading Tests

| Test | Verifies |
|------|----------|
| Valid manifest.json decodes correctly | JSON parsing |
| Missing optional fields use defaults | Default values |
| Invalid JSON produces error | Error handling |
| Available pets discovered from directory listing | Pet discovery |
| Frame files loaded in correct order | Alphabetical sorting |
| Missing animation state triggers fallback | Fallback chain |
| Missing `idle` state produces error | Required state validation |

### Settings Tests

| Test | Verifies |
|------|----------|
| Selected pet saves to UserDefaults | Persistence write |
| Selected pet loads from UserDefaults | Persistence read |
| Missing UserDefaults returns default pet | First-launch behavior |

---

## Integration Tests

Integration tests may require a running macOS window server (Xcode test host) but should not require real pixel art or a visible Dock.

### Window Tests

| Test | Verifies |
|------|----------|
| Pet window is transparent | `isOpaque`, `backgroundColor` |
| Pet window is borderless | `styleMask` |
| Pet window has no shadow | `hasShadow` |
| Pet window level is correct | `.floating` level |
| Pet window is non-activating | Does not steal focus |
| Window repositions on geometry change | Notification handling |

### Rendering Tests

| Test | Verifies |
|------|----------|
| Sprite renders with nearest-neighbor | No blur (visual/layer check) |
| Animation cycles frames at correct FPS | Frame timing |
| Direction flip renders correctly | Horizontal mirror |

---

## Manual macOS Tests

These require a human tester on a real Mac. Each should be a checklist item verified during milestone reviews.

### Dock Configuration Matrix

| # | Dock Position | Auto-Hide | Monitors | Expected |
|---|---------------|-----------|----------|----------|
| 1 | Bottom | Off | Single | Pet above Dock ✓ |
| 2 | Bottom | On | Single | Pet at screen bottom ✓ |
| 3 | Left | Off | Single | Pet beside left Dock ✓ |
| 4 | Right | Off | Single | Pet beside right Dock ✓ |
| 5 | Left | On | Single | Pet at screen left ✓ |
| 6 | Right | On | Single | Pet at screen right ✓ |
| 7 | Bottom | Off | Dual | Pet on Dock screen ✓ |
| 8 | Bottom | Off | Dual | Pet not on non-Dock screen ✓ |

### Display Tests

| # | Scenario | Expected |
|---|----------|----------|
| 1 | Retina display | Sprites crisp, no blur |
| 2 | Non-Retina display | Sprites crisp, correctly sized |
| 3 | Display attach (hot-plug) | Pet repositions or stays visible |
| 4 | Display detach (hot-unplug) | Pet moves to remaining display |

### Spaces / Fullscreen Tests

| # | Scenario | Expected |
|---|----------|----------|
| 1 | Switch to different Space | Pet visible on new Space |
| 2 | Enter fullscreen app | Pet visible (or gracefully hidden) |
| 3 | Exit fullscreen app | Pet visible and correctly positioned |
| 4 | Mission Control activated | Pet stays stationary |
| 5 | Exposé activated | Pet stays stationary |

### Interaction Tests

| # | Scenario | Expected |
|---|----------|----------|
| 1 | Click on pet | Pet reacts |
| 2 | Click next to pet | Click passes to desktop/app behind |
| 3 | Click on menu bar icon | Menu appears |
| 4 | Select Quit | App terminates cleanly |
| 5 | Select different pet | Pet sprite changes |

### Stability Tests

| # | Scenario | Expected |
|---|----------|----------|
| 1 | Run for 1 hour | No memory growth |
| 2 | Run for 1 hour | CPU < 1% during idle |
| 3 | Sleep/wake Mac | Pet recovers correctly |
| 4 | Fast user switching | Pet still visible on return |
| 5 | Change Dock size (System Settings) | Pet repositions |
| 6 | Change Dock magnification | No crash |

---

## Test Infrastructure

### Test Fixtures

- **MockRandomSource** — seeded random for deterministic tests
- **MockScreenGeometry** — configurable frame/visibleFrame for Dock detection tests
- **TestPetAssets** — minimal valid manifest + placeholder frame for asset loading tests

### Test Targets

```
DockPetTests/          ← Unit tests (no UI)
DockPetUITests/        ← Integration tests (requires window server)
```

### When to Write Tests

| Milestone | Tests Required |
|-----------|---------------|
| M2 | Geometry unit tests |
| M3 | Scaling unit tests |
| M4 | Movement unit tests |
| M5 | State machine unit tests |
| M6 | Asset loading unit tests |
| M7 | Hit test unit tests |
| M8 | Settings unit tests |
| M9 | Extended geometry tests |
| M10 | Performance benchmarks |
