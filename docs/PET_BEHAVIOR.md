# Pet Behavior System

The implemented engine separates state (`PetStateMachine`), position (`PetMovement`), rendering (`SpriteView`), and their AppKit integration (`PetCoordinator`). See ADR-018 and ADR-019 in `DECISIONS.md`.

## Continuous cycle

| Phase | Duration | Position | Sprite playback |
|-------|----------|----------|-----------------|
| `walking` | 10 seconds | Travels along the full screen edge beside the Dock; reflects at boundaries | Walk loop, advancing only when the panel travels |
| `specialAnimation` | 5 seconds | Stationary, except leading `movingFrames` configured in the manifest | Signature sequence plays once across the whole phase |
| `sleeping` | 10 seconds | Stationary | Sleep/rest loop |

The cycle repeats every 25 seconds of active application time. Loading a pet begins a fresh walking phase immediately, including movement and the appropriate refresh rate. Screen geometry and scale changes clamp position to the new valid bounds.

A boundary turns the pet around without interrupting walking. Motion preserves the distance beyond the boundary rather than losing a frame of travel. On load or display changes, the pet heads toward the larger open region. After sleep it preserves its last heading, so repeated midpoint walks visit both halves of wide displays. Speed is the greater of its activity-adjusted base speed and the available span / 10 seconds. The first walk starts from the current/center position; successive walks cover the remaining edge. Activity changes do not alter cycle durations.

## Signature actions and artwork

- Ronaldo: SIU sequence, then silver European cup lift and a final held pose.
- Messi: visible ball skill while translating, goal celebration, World Cup lift ending overhead.
- Turtle: retreat into the shell, followed by a resting pose.
- Cat: consistent side-facing walking model with a small pixel bob; crouching/paw poses with a native yarn-ball overlay; one curled-up sleeping silhouette.
- Other pets retain their existing signature sequences (dog celebration, parrot wings, rabbit carrot, dinosaur roar, hamster seeds).

Source sheets in `Assets/NewPetDesign/` stay unchanged. The slicer selects existing poses. Footballer rest uses closed-eye/quiet source poses with native sleep marks, preserving the original palette. Special sequences never restart halfway through the five-second phase.

## Click and visibility behavior

A click temporarily enters `interaction` for one second, stops travel and plays the reaction. The remaining phase duration and sprite progress are preserved, then resumed; repeated clicks during the reaction are ignored. Interaction pauses the normal cycle, adding the reaction's duration to that repetition. An animation-completion event cannot shorten a signature phase.

Hide stops playback and invalidates the display link. Show restores the same phase and sprite progress. Gaps greater than one second between display callbacks (OS sleep/debugger stalls) pause the simulation instead of teleporting the pet. Normal low-frequency sleep callbacks retain their full elapsed time.

`idle` remains available for compatibility and displays a static pose; it is not part of the automatic cycle. The implementation has no `running`, `sitting`, or `jumping` states.

## One update clock

`PetCoordinator` drives state, movement and sprite progression from one CADisplayLink. The state machine splits a tick across phase boundaries and preserves leftover time, avoiding cumulative drift. `SpriteView` owns no repeating timer and changes its displayed frame only when the index changes.

| Mode | Requested display-link range | Preferred |
|------|------------------------------|-----------|
| Walking | 60–120 Hz | 60 Hz |
| Translating skill | 30–60 Hz | 30 Hz |
| Stationary skill | 5–10 Hz | 10 Hz |
| Sleep | 5–10 Hz | 5 Hz |
| Interaction / idle | 10–30 Hz | 15 Hz |

These are requested rates; macOS may choose a supported refresh rate. Frame playback uses elapsed time rather than counting callbacks. Only the active pet's frames are cached, and runtime props use Core Graphics without extra bitmap sequences or dependencies.

## Verification

Pure logic tests inject elapsed time without real timers. Coordinator regressions exercise launch movement, full cycles, low-frequency sleep ticks, wide/narrow bounds, skill translation, one-shot playback, clicks, switching pets and hide/show. Runtime release measurements use `vmmap -summary` physical footprint; RSS is recorded separately and is not the same memory metric.
