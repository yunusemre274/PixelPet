# Roadmap

## Status Key

| Status | Meaning |
|--------|---------|
| `NOT_STARTED` | No work begun |
| `IN_PROGRESS` | Actively being worked on |
| `BLOCKED` | Cannot proceed until dependency resolved |
| `DONE` | Definition of done fully satisfied |

---

## M0 — Documentation & Architecture

**Status:** `DONE`

**Objective:** Establish project documentation, architecture design, agent rules, and governance before any implementation.

**Deliverables:**
- README.md
- GEMINI.md, AGENTS.md, SKILLS.md
- PRODUCT.md, ROADMAP.md, ARCHITECTURE.md
- TOKEN_REDUCE.md, DECISIONS.md, PROJECT_STATE.md
- docs/ASSET_PIPELINE.md, docs/PET_BEHAVIOR.md, docs/MACOS_RESEARCH.md, docs/TESTING_STRATEGY.md

**Prerequisites:** None.

**Definition of Done:**
- All documentation files exist and are internally consistent
- Architecture modules are defined with clear boundaries
- macOS research is documented with verification status
- Asset pipeline convention is specified
- Agent workflow and context protocol are defined
- No contradictions between documents

**Risks:** None.

**Tests Required:** Manual review of documentation consistency.

---

## M1 — macOS Window Proof of Concept

**Status:** `DONE`

**Objective:** Prove that a transparent, borderless native macOS window can display a placeholder sprite at a fixed screen position.

**Deliverables:**
- Xcode project scaffolded
- Menu bar app (no Dock icon)
- Transparent NSWindow/NSPanel rendering a colored rectangle or placeholder image
- Window appears above the Dock area
- Window is non-activating and does not steal focus

**Prerequisites:** M0 `DONE`.

**Definition of Done:**
- A transparent window is visible on screen
- The window has no title bar, no background, no shadow
- A placeholder sprite (colored rectangle) renders inside the window
- The window does not appear in Mission Control as a standard window
- The app runs as a menu bar agent (no Dock icon)
- The app can be quit cleanly

**Risks:**
- Window level may need tuning to appear correctly above Dock
- Spaces/fullscreen behavior may need `collectionBehavior` adjustments

**Tests Required:**
- Manual: window appears, is transparent, shows placeholder
- Manual: app has no Dock icon
- Manual: quit works cleanly

---

## M2 — Dock Geometry

**Status:** `DONE`

**Objective:** Detect Dock position (bottom/left/right) and compute the correct pet window placement.

**Deliverables:**
- DockGeometry module
- Dock orientation detection (bottom/left/right)
- Screen `visibleFrame` usage for Dock-relative positioning
- Window repositions when Dock geometry changes

**Prerequisites:** M1 `DONE`.

**Definition of Done:**
- Pet window is positioned just above the Dock (bottom orientation)
- Changing Dock position causes pet to reposition
- Unit tests for geometry calculations pass
- Manual test on bottom Dock position succeeds

**Risks:**
- No public API for exact Dock rect — must infer from `frame` vs `visibleFrame`
- Auto-hide makes `visibleFrame` unreliable (deferred to M9)

**Tests Required:**
- Unit: geometry calculation for bottom/left/right
- Manual: Dock bottom positioning correct
- Manual: Dock position change triggers update

---

## M3 — Sprite Rendering

**Status:** `DONE`

**Objective:** Render a pixel-art sprite with crisp nearest-neighbor scaling, no blur.

**Deliverables:**
- Rendering module
- Nearest-neighbor image scaling
- Correct Retina display handling
- Single static sprite rendered in the pet window

**Prerequisites:** M1 `DONE`.

**Definition of Done:**
- A pixel-art test sprite renders without blur
- Sprite is correctly scaled on Retina and non-Retina displays
- No bilinear interpolation artifacts visible
- Unit tests for scaling math pass

**Risks:**
- Default macOS image rendering uses bilinear filtering — must be explicitly overridden
- SpriteKit vs Core Animation decision affects implementation (see DECISIONS.md)

**Tests Required:**
- Unit: scaling calculations
- Manual: visual inspection on Retina display
- Manual: visual inspection at multiple scale factors

---

## M4 — Pet Movement Engine

**Status:** `DONE`

**Objective:** Pet sprite moves horizontally within valid bounds.

**Deliverables:**
- Movement module
- Horizontal movement with configurable speed
- Boundary detection and turnaround
- Direction-aware sprite facing (flip)

**Prerequisites:** M2 `DONE`, M3 `DONE`.

**Definition of Done:**
- Pet moves left and right within Dock boundaries
- Pet turns around at screen edges
- Movement speed is configurable per pet type
- Sprite faces correct direction
- Unit tests for boundary math pass

**Risks:** None significant.

**Tests Required:**
- Unit: boundary clamping, direction changes
- Manual: visual movement is smooth
- Manual: pet stays within screen bounds

---

## M5 — State Machine

**Status:** `DONE`

**Objective:** Implement the core pet state machine with idle and walk states.

**Deliverables:**
- StateMachine module
- Idle state with random duration
- Walk state with random duration and direction
- Transitions between idle ↔ walk
- Animation frame selection per state

**Prerequisites:** M4 `DONE`.

**Definition of Done:**
- Pet alternates between idle and walking
- State durations are randomized within configured ranges
- State transitions drive correct animation
- State machine is testable without UI
- Unit tests for transitions pass

**Risks:** Timer-based state changes need care to avoid CPU waste.

**Tests Required:**
- Unit: state transitions with deterministic random seed
- Unit: duration ranges respected
- Manual: pet behavior looks natural

---

## M6 — Pet Asset System

**Status:** `DONE`

**Objective:** Implement the data-driven asset pipeline so real pixel art can be dropped into folders.

**Deliverables:**
- Asset loading from manifest.json
- Frame sequence loading per animation state
- Fallback behavior for missing animations
- Placeholder assets for testing

**Prerequisites:** M3 `DONE`, M5 `DONE`.

**Definition of Done:**
- A pet's sprites load from its folder/manifest without code changes
- Missing animation states fall back gracefully
- Adding a new pet type requires only a new asset folder + manifest
- Manifest decoding is unit tested

**Risks:** File naming/ordering conventions must be clear to artists.

**Tests Required:**
- Unit: manifest JSON decoding
- Unit: fallback for missing states
- Manual: drop test sprites into folder, verify they load

---

## M7 — Interaction

**Status:** `DONE`

**Objective:** Pet responds to mouse clicks.

**Deliverables:**
- Click detection on pet sprite
- Pet reaction animation/state on click
- Mouse tracking area for the pet window

**Prerequisites:** M5 `DONE`.

**Definition of Done:**
- Clicking the pet triggers a visible reaction
- Clicking empty window area passes through to desktop
- No unintended focus stealing
- Manual test: click reaction works

**Risks:** Click-through on transparent regions may need `NSView` hit testing.

**Tests Required:**
- Unit: hit test logic
- Manual: click on pet vs click on empty space

---

## M8 — Settings / Pet Selection

**Status:** `DONE`

**Objective:** User can select which pet to display.

**Deliverables:**
- Menu bar menu with pet selection
- Selected pet persists across launches
- Settings stored in UserDefaults

**Prerequisites:** M6 `DONE`, M7 `DONE`.

**Definition of Done:**
- Menu lists available pets (based on discovered asset folders)
- Selecting a pet changes the displayed pet
- Selection persists after quit and relaunch

**Risks:** None significant.

**Tests Required:**
- Unit: UserDefaults read/write
- Manual: pet switching works

---

## M9 — Multi-Monitor & Dock Orientations

**Status:** `NOT_STARTED`

**Objective:** Support Dock at left/right, multi-monitor setups, and Dock auto-hide.

**Deliverables:**
- Left/right Dock positioning
- Multi-monitor Dock screen detection
- Auto-hide detection and handling
- Screen change notification handling

**Prerequisites:** M2 `DONE`, M4 `DONE`.

**Definition of Done:**
- Pet positions correctly for left, right, and bottom Dock
- Pet appears on the correct monitor
- Auto-hide Dock is handled gracefully
- Screen attach/detach is handled
- Manual tests for all orientations pass

**Risks:**
- Auto-hide Dock makes visibleFrame equal to frame — need alternative detection
- Multi-monitor Dock assignment may require monitoring active screen

**Tests Required:**
- Unit: geometry calculations for all orientations
- Manual: all Dock orientations
- Manual: multi-monitor
- Manual: auto-hide on/off

---

## M10 — Performance / Stability

**Status:** `NOT_STARTED`

**Objective:** Optimize for long-running background use.

**Deliverables:**
- CPU profiling and optimization
- Memory leak audit
- Animation timer optimization
- Idle-state power reduction

**Prerequisites:** M5 `DONE`, M7 `DONE`.

**Definition of Done:**
- CPU usage < 1% during idle animation
- No memory growth over 1-hour run
- Instruments profiling shows no hot spots
- Battery impact is negligible

**Risks:** SpriteKit/Core Animation baseline overhead may need measurement.

**Tests Required:**
- Performance: Instruments CPU/memory profile
- Manual: run for 1 hour, check Activity Monitor

---

## M11 — Packaging / Distribution

**Status:** `NOT_STARTED`

**Objective:** Package for distribution.

**Deliverables:**
- Code signing configuration
- Notarization workflow
- DMG or installer creation
- Sandboxing assessment

**Prerequisites:** M10 `DONE`.

**Definition of Done:**
- Signed and notarized .app runs on a clean macOS install
- Gatekeeper does not block the app
- DMG or zip distribution package works

**Risks:**
- Sandboxing may restrict screen-level window placement
- Some macOS APIs may require entitlements

**Tests Required:**
- Manual: install on clean machine
- Manual: Gatekeeper allows launch
