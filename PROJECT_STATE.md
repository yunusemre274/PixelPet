# Current Project State

**Milestones:** ROADMAP.md M0–M14 are DONE; subsequent 64×64 artwork/behavior enhancements are recorded in ADR-017–019.
**Latest stable work:** 2026-10-15 — Baby Yoda with a stable component model, hood/saber/training actions and sleep.

## Working

- Native macOS 14+ Swift/AppKit menu bar agent; transparent, non-activating NSPanel with no Dock/Cmd+Tab presence.
- Public Dock geometry inference for bottom/left/right, auto-hide, multiple monitors and manual display selection.
- Crisp nearest-neighbor rendering of ten 64×64 pets: BabyYoda, Cat, Dog, Parrot, Rabbit, Turtle, Dinosaur, Hamster, CristianoRonaldo, LionelMessi.
- Fixed cycle: **10s walk → 5s signature → 10s sleep → repeat**.
- Walking starts immediately at launch/pet selection; edge collisions reverse without losing distance or interrupting walking.
- Available travel area spans the screen edge above/beside the Dock. Walking pace is at least span / 10s, including wide displays; activity settings still determine base speed.
- Walking frames advance only when the panel actually travels. Geometry/scale changes clamp position into valid bounds.
- Signatures play once over five seconds, without looping back to the beginning:
  - Baby Yoda: green body, large solid black eyes, gray tunic; raise hood → draw/ignite green saber → solo training. Separate training frames and closed-eye breathing sleep also supplied.
  - Ronaldo: SIU → silver European cup lift and held finish.
  - Messi: visible ball skill with travel → goal celebration → World Cup lift ending overhead.
  - Turtle: shell retreat; other animals retain their existing signature actions.
  - Cat: coherent walking model with small pixel bob, crouch/paw poses with native yarn overlay, consistent curled-up sleep.
- Footballer rest uses quiet/closed-eye source poses plus native sleep marks; original palettes preserved.
- Per-pixel click handling, optional native Pop sound and transparent-region pass-through.
- Click reaction pauses the phase for one second, then resumes its remaining timer, sprite progress and direction.
- Hide/show preserves phase and playback. OS sleep/debugger gaps over one second pause simulation without teleporting.
- Pet choice, size (1×/2×/3×), activity, sound and display preferences persist in UserDefaults.

## Architecture and Optimization

- `PetStateMachine` and `PetMovement` remain pure Foundation domain logic.
- `PetCoordinator` integrates domain, geometry, AppKit panel and rendering using a single CADisplayLink.
- State updates split elapsed time across phase boundaries; ordinary 5Hz callbacks retain their full 0.2s.
- `SpriteView` caches CGImages and has no independent repeating animation timer. Small props use native Core Graphics.
- Requested refresh rates: walk 60–120Hz; translating skill 30–60Hz; stationary skill/sleep 5–10Hz; interaction 10–30Hz.
- Active-pet-only frame caching evicts previous pet assets on switching. No new runtime dependencies or private APIs.
- `Assets/NewPetDesign/` source sheets are unchanged. `scripts/slice_sprites.py` reproducibly extracts/reflects existing poses and scales by nearest neighbor.
- Baby Yoda is generated from one immutable set of body parts by `scripts/generate_baby_yoda.py`; other pet/source assets are unaffected.
- Significant choices: ADR-004/007 (rendering/clock), ADR-017/018 (assets/cycle), ADR-019 (synchronization).

## Validation

- **54 Swift tests across 11 suites pass** with `swift test`; **4 asset tests pass** with `python3 -m unittest discover -s Tests/AssetTests -v`.
- New regressions cover launch travel, 20 exact cycles at 5Hz, time remainders, wide/narrow bounds, both screen halves across successive walks, reflection, clicks, signature travel/playback, switching and hide/show.
- Native renderer snapshots inspected for BabyYoda, Cat, Messi, Ronaldo and Turtle across walk/skill/sleep transitions.
- All ten manifests have five-second one-shot signatures; every frame is 64×64 RGBA. Slicer idempotence and unchanged source sheets checked.
- Release `.app` built with `./scripts/build_app.sh --release`; strict ad-hoc signature verification passes.
- Runtime physical-footprint target: **10–30MB** (`vmmap -summary`, not RSS). Previous nine-pet baseline at 3× size after 17s: **16.1–23.5MB**, highest recorded peak **24.3MB** (Messi). Separate 2× Messi sample: 17.0MB, peak 17.9MB.
- BabyYoda release physical footprint: 1× **14.1MB** (peak 14.2MB), 2× **14.9MB** (peak 15.1MB), 3× **16.2–16.3MB** (peak **17.4MB**). The 3× sample stayed at 16.3MB through two complete cycles (52s).
- Follow-up 3× Messi sample after a complete 25s cycle: 22.0MB, peak 22.7MB.
- These are short release samples after loading walk, signature and sleep assets; a long-duration leak audit has not been repeated for this change.

## Known Limitations / Future Work

- Dock bounds are inferred from screen geometry; no exact Dock-icon rectangle is queried.
- Cat source artwork has one suitable side-facing walk pose; a small native bob preserves the model instead of alternating unrelated silhouettes.
- Feeding, drag repositioning and additional fetch/taunt variants remain optional future work.
- Benign `_NSDetectedLayoutRecursion` warning can originate from macOS NSStatusItem.

## Key Files

- Engine: `DockPet/PetEngine/{PetCoordinator,PetStateMachine,PetMovement}.swift`
- Rendering/assets: `DockPet/Rendering/SpriteView.swift`, `DockPet/Assets/{PetManifest,PetAssetLoader}.swift`
- Sprites: `Assets/Pets/`, `Assets/NewPetDesign/`, `scripts/{slice_sprites,generate_baby_yoda}.py`; preview: `build/previews/BabyYoda.gif`
- Regressions: `Tests/DockPetTests/{PetCycleRegressionTests,PetEngineTests}.swift`, `Tests/AssetTests/test_baby_yoda.py`
- Build: `scripts/build_app.sh`, `scripts/create_dmg.sh`; current release: `build/DockPet.app`
