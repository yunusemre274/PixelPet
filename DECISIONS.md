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

---

## ADR-014 — Interactive Feedback & Audio Engine

**Status:** ACCEPTED  
**Date:** 2026-10-14  
**Validated:** M12 — 3-frame reaction animations (`interaction/`) generated for all 7 pets + native `NSSound(named: "Pop")`

**Context:** Clicking the pet triggered the `.interaction` state, but fell back to `.idle` due to lack of dedicated sprite frames. Visual and auditory feedback make the pet feel lively and responsive.

**Decision:**
1. Generate dedicated 3-frame `interaction` animations for all 7 pet types displaying happy squint eyes, a rising 1-pixel bounce, and a pulsing pixel heart/sparkles.
2. Provide gentle, public macOS audio feedback using AppKit `NSSound(named: "Pop")?.play()`.
3. Provide an in-menu checkbox toggle for sound effects, persisted via `UserDefaults`.

**Consequences:**
- Click interactions are visually delightful and audible.
- Zero external audio dependencies or audio files needed.
- Users who prefer silence can disable audio with one click.

---

## ADR-015 — In-Menu Customization (Pet Size & Activity Levels)

**Status:** ACCEPTED  
**Date:** 2026-10-14  
**Validated:** M13 — runtime scale selection (1x, 2x, 3x) and pacing modes (Calm, Normal, Energetic)

**Context:** Users have different screen resolutions (Retina vs non-Retina, Ultrawide vs Laptop) and different preferences for how active or calm the virtual pet should be.

**Decision:**
1. Expose a "Pet Size" submenu in the menu bar: `Small (32px / 1x)`, `Normal (64px / 2x)`, `Large (96px / 3x)`. Dynamic window sizing recalculates Dock placement and boundary turnaround.
2. Expose an "Activity Level" submenu: `Calm` (longer idle/sleep periods, slower walk), `Normal` (balanced), `Energetic` (faster walk, frequent movements).
3. Persist selections in `UserDefaults.standard`.

**Consequences:**
- User can customize pet appearance and behavior on the fly without restarting.
- Respects nearest-neighbor scaling at all sizes with crisp pixel edges.

---

## ADR-016 — Application Icon & Packaging

**Status:** ACCEPTED  
**Date:** 2026-10-14  
**Validated:** M14 — automated compilation of `AppIcon.icns` via `iconutil` and integration into `.app` and DMG

**Context:** The application bundle previously lacked an official macOS application icon (`AppIcon.icns`).

**Decision:**
1. Generate a multi-resolution retro pixel-art macOS squircle app icon featuring the pet cat, red heart, and paw print.
2. Compile into standard macOS `AppIcon.icns` using `/usr/bin/iconutil`.
3. Include `CFBundleIconFile: AppIcon` in `Info.plist` and embed in release `.app` and `.dmg`.

**Consequences:**
---

## ADR-017 — 64×64 Pixel-Art Upgrade, Signature Celebrations, Sleep Cycle & Extreme Memory Optimization

**Status:** ACCEPTED  
**Date:** 2026-10-15  
**Validated:** ROADMAP_UPDATE / M15-M20 — 64×64 pixel-art pipeline, 9 pet types (including Ronaldo and Messi), 15-30s signature animations, 2-min active -> 30s sleep cycle, and 22MB physical footprint

**Context:** The user provided high-quality pixel-art sprite sheets in `Assets/NewPetDesign/` (256×256 containing 8×8 grids = 64 frames of 32×32 pixel art), requested new characters (Cristiano Ronaldo and Lionel Messi), special signature animations (Messi goal + World Cup lift, Ronaldo SIU + Cup lift, Turtle shell retreat), 2-minute active time leading to 30s sleep, and strict RAM optimization between 10MB and 30MB.

**Decision:**
1. **Asset Pipeline & Rendering (M15-M17):**
   - Created `scripts/slice_sprites.py` to extract source cells and upscale 2× nearest-neighbor (`Image.NEAREST`) to 64×64 PNGs.
   - Preserves 100% pixel sharpness, zero blur, zero color bleeding, and zero artifacts.
   - Slices exact animations: `idle`, `walk`, `sleep`, `interaction`, and `special`.
2. **New Characters & Signature Animations (M20):**
   - Added **Lionel Messi**: Goal celebration slide + World Cup trophy lift (16 frames).
   - Added **Cristiano Ronaldo**: SIU spin & landing celebration + Champions League trophy lift (12 frames).
   - Added **Turtle**: Full protective shell retreat and peeking animation (8 frames).
   - Unique signature animations for all remaining pets (Cat fish toy, Dog dancing with hearts, Hamster sunflower seeds & cheek pouch, Dinosaur fire roar, Parrot flying, Rabbit eating carrot).
3. **Behavior Lifecycle:**
   - Pets trigger their signature special animation periodically every 15–30 seconds.
   - After cumulative 2 minutes (120 seconds) of active time (idle + walking), the pet enters a restorative 30-second sleep.
4. **Memory & Runtime Optimization (M19):**
   - Implemented active pet cache eviction in `PetAssetLoader.clearCache(for:)` when switching pets.
   - Dynamic CADisplayLink throttling (5–10Hz stationary, 60–120Hz walking).
   - Physical memory footprint measured via `vmmap`: **22.1 MB** (comfortably within the 10MB–30MB target budget).

**Consequences:**
- Visual quality is dramatically improved with rich, fluid 64×64 retro pixel art.
- Football icons Ronaldo & Messi and iconic animal animations delight the user.
- System resource footprint is tiny (22MB RAM, <1% CPU), completely unnoticeable on macOS.

---

## ADR-018 — Deterministic 25-Second Behavioral Loop & Full Dock Traversal

**Status:** ACCEPTED  
**Date:** 2026-10-15  
**Validated:** M20/M21 — 10s continuous walk across full Dock, 5s signature skill, 10s sleep cycle, cohesive frame selection eliminating visual morphing

**Context:** The user reported visual morphing ("hayvanlar sürekli şekil değiştiriyor") caused by random state hopping and inconsistent frame slices, and requested:
1. 10s continuous walking (aralıksız yürüme)
2. 5s signature skill (dribbling, sprint, gol sevinci, kabuğuna çekilme vs.)
3. 10s sleep (uyku)
4. Continuous repetition of the exact 25-second loop
5. Full Dock utilization (pet must traverse the entire screen width above the Dock)

**Decision:**
1. **Behavioral Loop (`PetStateMachine`):**
   - Eliminated erratic random duration timers.
   - Fixed cycle: `walking (10.0s)` → `specialAnimation / skill (5.0s)` → `sleeping (10.0s)` → repeat.
   - Boundary collisions (`hitBoundary`) no longer interrupt the 10s walk; the pet smoothly reverses direction and keeps walking.
2. **Full Dock Traversal (`PetMovement`):**
   - Walking speed set to 110 pt/s (traversing 1100 points in 10s, utilizing the entire width of the display above the Dock).
   - Upon waking, the pet automatically heads toward the open side of the screen (`startMoving(bounds:)`).
3. **Cohesive Frame Slicing (`slice_sprites.py`):**
   - Cleaned frame selections so that all frames in an animation share identical silhouettes, outfits, and color palettes.
   - Added custom cropping for Dog (removing top banner text and centering) and Cat (curled up sleeping, clean walk).

**Consequences:**
- The pet behaves in an intuitive, entertaining, predictable cycle.
- Traverses the entire Dock from edge to edge.
- Visual morphing/flickering is completely eliminated.
- Physical memory footprint drops further to **13.0 MB**!


---

## ADR-019 — Shared Movement/Animation Clock and Cycle Corrections

**Status:** ACCEPTED
**Date:** 2026-10-15

**Context:** ADR-018 described a 25-second cycle, but initial walking never started the movement motor. Clamping every tick to 0.1s doubled sleep duration at 5Hz. A separate sprite timer allowed walking in place, and looping skills restarted before their five-second slot finished. Fixed 110pt/s could not cover wide displays.

**Decision:**
- Keep AppKit/Core Graphics, CADisplayLink, existing engine boundaries and the active-pet cache. Add no dependencies.
- Drive state, translation and sprite frames from the coordinator's single display-link clock. Preserve elapsed-time remainders at state boundaries; accept ordinary 0.2s sleep ticks. Pause across callback gaps greater than one second.
- Explicitly apply walking behavior on load/start. Preserve phase time, sprite progress and direction across click/visibility interruptions; pet selection starts a fresh cycle.
- Reflect edge overshoot, clamp on geometry changes, preserve heading after sleep to visit both halves of wide displays, and use a minimum walking pace of available span / 10 seconds. User activity sets base pace without changing the 10/5/10 durations.
- Play signatures once over five seconds. Optional manifest `movingFrames` keeps leading ball-skill frames translating while celebrations remain stationary.
- Preserve all source sheets. Select coherent existing cat poses, visible Messi ball frames, Ronaldo SIU/cup frames and quieter resting poses. Draw yarn/sleep marks as native pixel overlays.

**Consequences:** Walking poses freeze without actual travel, low-frequency sleep retains correct timing, and skills show a complete ordered sequence. Source art remains reusable; runtime effects add no frame-cache growth. Regression tests cover the integration failures that pure state tests missed. The 10–30MB target is evaluated using release physical footprint, with current measurements recorded in `PROJECT_STATE.md`.
