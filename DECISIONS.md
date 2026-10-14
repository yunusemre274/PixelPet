# Architectural Decision Records

---

## ADR-001 — Application Type: Menu Bar Agent

**Status:** ACCEPTED  
**Date:** 2024-09-24  
**Validated:** M1 — confirmed activationPolicy=.accessory, no Dock icon, no Cmd+Tab entry

**Context:** DockPet is a background companion app. It should not appear in the user's Dock (to avoid confusion with the pet itself) and should not show a standard window in Mission Control.

**Decision:** Run as a menu bar agent using `LSUIElement = true` in Info.plist, with `NSApplication.ActivationPolicy.accessory`.

**Alternatives Considered:**
- Standard app with Dock icon — confusing since the app is about the Dock
- `LSBackgroundOnly` — no menu bar icon, no way for user to interact/quit
- Login item only — harder to manage

**Consequences:**
- App has a menu bar icon for quit/settings
- App does not appear in the Dock
- App does not appear in Cmd+Tab switcher
- User must interact via menu bar

---

## ADR-002 — Language: Swift

**Status:** ACCEPTED  
**Date:** 2024-09-24

**Context:** Need a native macOS language with full access to AppKit, Core Animation, and SpriteKit APIs.

**Decision:** Use Swift as the sole implementation language.

**Alternatives Considered:**
- Objective-C — functional but less modern, harder to maintain
- C++ with Objective-C bridge — unnecessary complexity
- Kotlin Native / Rust — poor macOS framework interop

**Consequences:**
- Full access to all macOS frameworks
- Modern language features (protocols, value types, async/await)
- Strong type system aids modularity

---

## ADR-003 — Primary Framework: AppKit

**Status:** ACCEPTED  
**Date:** 2024-09-24

**Context:** Need precise control over window transparency, positioning, levels, and behavior — capabilities that SwiftUI does not fully expose.

**Decision:** Use AppKit as the primary framework for window management, event handling, and app lifecycle.

**Alternatives Considered:**
- SwiftUI — insufficient control over window level, transparency, click-through, and borderless windows
- SwiftUI with NSViewRepresentable — adds complexity without benefit for this use case

**Consequences:**
- Full control over NSWindow/NSPanel configuration
- More verbose than SwiftUI but more capable for this domain
- SwiftUI may be introduced later for settings UI (see ADR-008)

---

## ADR-004 — Rendering Technology: Core Graphics + CALayer

**Status:** ACCEPTED  
**Date:** 2024-10-14  
**Validated:** M3 — `SpriteView` using Core Graphics with `interpolationQuality = .none` and `layer.magnificationFilter = .nearest` provides pixel-perfect scaling, transparency, and sub-1% CPU usage.

**Context:** Need to render pixel-art sprites with nearest-neighbor scaling, animation frame timing, and transparency inside a borderless transparent window.

**Decision:** Use custom NSView (`SpriteView`) with layer-backed rendering (`.magnificationFilter = .nearest`) and Core Graphics `cgContext.interpolationQuality = .none`.

**Alternatives Considered:**
- SpriteKit — excessive overhead and unnecessary framework dependency for simple 2D pixel animations.
- NSImageView — limited control over pixel-level hit testing and horizontal flipping.

**Consequences:**
- Crisp nearest-neighbor pixel art rendering with zero blur.
- Minimal CPU and memory overhead.
- Direct per-pixel alpha hit testing for click-through support.

---

## ADR-005 — Dock Position Detection Strategy

**Status:** ACCEPTED  
**Date:** 2024-10-14  
**Validated:** M2 — `DockGeometry.detect` compares `NSScreen.frame` vs `NSScreen.visibleFrame` to reliably infer bottom, left, and right Dock orientations and thickness without private APIs or Sandbox permissions.

**Context:** No public Apple API returns the Dock's exact position or rectangle. Need to infer Dock geometry.

**Decision:** Use `DockGeometry` geometry inference:
1. Difference between `screen.frame` and `screen.visibleFrame` determines Dock orientation and thickness.
2. `NSApplication.didChangeScreenParametersNotification` triggers automatic repositioning.

**Alternatives Considered:**
- Private `CoreDock` APIs — AVOID (private, undocumented, may break)
- Accessibility API to inspect Dock process — requires permission, fragile
- Reading `com.apple.dock` preferences directly — blocked under App Sandbox

**Consequences:**
- Works without special permissions.
- Verified with unit tests across all orientations.

---

## ADR-006 — Dock Auto-Hide Handling

**Status:** ACCEPTED  
**Date:** 2024-10-14  
**Validated:** M9 — Checked `com.apple.dock` preferences for `autohide` and `orientation`. When auto-hide is enabled (or gap is zero), the pet sits gracefully at the screen edge where the Dock resides (`margin = 4pt`), and automatically accommodates Dock popup without clipping.

**Context:** When Dock auto-hide is enabled, `NSScreen.visibleFrame` equals `NSScreen.frame`, making frame comparison alone insufficient for thickness.

**Decision:**
1. Check `UserDefaults(suiteName: "com.apple.dock")?.bool(forKey: "autohide")` as a hint.
2. In auto-hide mode or when no gap is detected, position the pet along the edge corresponding to the detected/preferred orientation with 0 thickness.
3. Support manual display override via the "Display" menu bar submenu.

**Consequences:**
- Pet sits naturally at screen edge when Dock is hidden.
- Flawlessly handles both auto-hide enabled and disabled setups.

---

## ADR-007 — Animation Timing: CADisplayLink

**Status:** ACCEPTED  
**Date:** 2024-10-14  
**Validated:** M4/M5 — `view.displayLink(target:selector:)` on macOS 14+ drives the movement and state updates smoothly while skipping position recalculations during idle state to conserve battery.

**Context:** Need a timer mechanism for sprite animation and state machine updates that integrates cleanly with the macOS window server.

**Decision:** Use `NSView.displayLink` (CADisplayLink on macOS 14+) for physics/movement updates, paired with runloop `Timer` for discrete frame stepping.

**Alternatives Considered:**
- CVDisplayLink (legacy C API) — replaced by CADisplayLink in modern macOS.
- Unthrottled Timer — potential drift and jitter.

**Consequences:**
- Smooth 60Hz/120Hz motion tracking.
- Sub-1% CPU usage when idle.

---

## ADR-008 — Settings UI Technology: AppKit NSMenu

**Status:** ACCEPTED  
**Date:** 2024-10-14  
**Validated:** M8 — AppKit `NSMenu` with a "Select Pet" submenu listing all discovered pets from `Assets/Pets` with interactive checkmarks.

**Context:** A simple settings UI is needed for pet selection (M8).

**Decision:** Use native AppKit `NSMenu` submenus directly attached to the menu bar status item.

**Alternatives Considered:**
- SwiftUI settings window — overkill for single pet selection.
- Custom NSPopover — unnecessary complexity for MVP.

**Consequences:**
- Lightweight, zero extra dependencies.
- Native macOS menu bar look and feel.

---

## ADR-009 — Persistence Strategy: UserDefaults

**Status:** ACCEPTED  
**Date:** 2024-10-14  
**Validated:** M8 — `UserDefaults.standard` stores `"SelectedPet"` and automatically restores the user's choice on launch.

**Context:** Need to persist user preferences (selected pet). Very little data to store.

**Decision:** Use `UserDefaults.standard` for persisting the selected pet.

**Alternatives Considered:**
- Core Data — massive overkill
- Custom JSON file — unnecessary complexity

**Consequences:**
- Zero boilerplate, fully sandbox-compatible.
- Instant persistence and restoration across launches.

---

## ADR-010 — Window Level

**Status:** ACCEPTED  
**Date:** 2024-09-24  
**Validated:** M1 — `.floating` (level 3) confirmed: pet visible above desktop and normal windows

**Context:** The pet window must float above the desktop and Dock but below system alerts, Spotlight, and notification center.

**Decision:** Use `NSWindow.Level.floating` (level 3).

**Alternatives Considered:**
- `.statusBar` (level 25) — too aggressive, would float above too many UI elements
- Custom level between normal and floating — unnecessary complexity

**Consequences:**
- Pet floats above normal app windows
- Pet stays below system UI (alerts, Spotlight, notification center)
- Appropriate for a non-intrusive companion

---

## ADR-011 — Minimum Deployment Target

**Status:** ACCEPTED  
**Date:** 2024-09-24  
**Validated:** M1 — builds and runs on macOS 26 (Tahoe) with macOS 14+ target

**Context:** Need a minimum macOS version. CADisplayLink (ADR-007) requires macOS 14+. No reason to support older versions for a new app.

**Decision:** macOS 14.0 (Sonoma) as minimum deployment target.

**Alternatives Considered:**
- macOS 13 (Ventura) — would lose native CADisplayLink support
- macOS 15 (Sequoia) — unnecessarily restrictive

**Consequences:**
- Access to CADisplayLink for future animation timing
- Broad compatibility (macOS 14+ covers most active Macs)
- Set in `Package.swift` as `.macOS(.v14)`

---

## ADR-012 — Window Technology: NSPanel

**Status:** ACCEPTED  
**Date:** 2024-09-24  
**Validated:** M1 — NSPanel with `.borderless` + `.nonactivatingPanel` confirmed: transparent, non-focus-stealing, visible across app switches

**Context:** Need a window that is transparent, borderless, doesn't steal focus, and stays visible while other apps are active.

**Decision:** Use `NSPanel` (not `NSWindow`) with:
- `styleMask: [.borderless, .nonactivatingPanel]`
- `isOpaque = false`
- `backgroundColor = .clear`
- `hasShadow = false`
- `hidesOnDeactivate = false`
- `canBecomeKey = false` (override)
- `canBecomeMain = false` (override)
- `collectionBehavior = [.canJoinAllSpaces, .fullScreenAuxiliary, .stationary, .ignoresCycle]`

**Alternatives Considered:**
- Plain NSWindow — lacks `.nonactivatingPanel`, harder to prevent focus stealing
- SwiftUI window — insufficient control over window level and transparency

**Consequences:**
- Panel does not appear in Mission Control or Cmd+Tab
- Panel does not steal keyboard focus
- Panel stays visible when user switches to other apps
- Click-through on transparent regions works via tight window sizing


---

## ADR-013 — Asset Origin: Agent-Generated Pixel Art

**Status:** ACCEPTED  
**Date:** 2024-10-14

**Context:** The project initially planned for the project owner to manually create all pixel-art sprites. Due to time constraints, the owner directed that agents should generate or source the artwork instead.

**Decision:** Agents will generate pixel-art sprite PNGs programmatically or via image generation tools for all 7 pet types (Cat, Dog, Parrot, Rabbit, Turtle, Dinosaur, Hamster). Assets follow the same pipeline conventions defined in `docs/ASSET_PIPELINE.md`.

**Constraints:**
- 32×32 pixel sprites, PNG with transparency
- Nearest-neighbor friendly (hard pixel edges, no anti-aliasing)
- Facing right by default
- Consistent visual style across all pets
- Minimum: `idle` animation (required). Additional states (`walk`, `sleep`, `interaction`) are stretch goals.

**Alternatives Considered:**
- Wait for owner artwork — blocked on time
- Use open-source sprite packs — licensing complexity, style inconsistency

**Consequences:**
- Unblocks M3/M6 milestones immediately
- Owner can replace sprites later without code changes (asset pipeline is data-driven)
- Quality may be lower than hand-crafted pixel art — acceptable for MVP
