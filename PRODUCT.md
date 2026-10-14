# Product Definition

## Vision

A small pixel-art virtual companion that lives around the macOS Dock — walking, idling, sleeping, and reacting to your mouse. Lightweight, charming, and native.

## Core Experience

The application should feel:

- **Lightweight** — barely noticeable on CPU/battery
- **Charming** — personality through pixel-art animation
- **Non-intrusive** — never blocks work, never demands attention
- **Responsive** — smooth animation, instant interaction
- **Native** — behaves like a proper macOS citizen
- **Playful** — surprising micro-behaviors that reward attention

## Supported Pets

| Pet | Notes |
|-----|-------|
| Cat | — |
| Dog | — |
| Parrot | — |
| Rabbit | — |
| Turtle | Slower movement speed |
| Dinosaur | — |
| Hamster | — |

All artwork is created manually by the project owner. The application provides a [data-driven asset pipeline](docs/ASSET_PIPELINE.md) so sprites can be dropped into folders without modifying code.

---

## MVP (Minimum Viable Product)

The MVP is intentionally small. Scope creep is the enemy.

### MVP Requirements

1. Application launches as a menu bar app (no Dock icon for itself)
2. A transparent pet window appears near the bottom of the screen, above the Dock
3. One placeholder pet renders correctly (can be a simple colored rectangle initially)
4. Pet moves horizontally when Dock is at bottom position
5. Idle and walk animation states exist and transition correctly
6. Pet stays within valid screen/Dock boundaries
7. Basic click interaction (e.g., pet reacts when clicked)
8. User can quit the app cleanly from the menu bar
9. Asset system supports replacing placeholder graphics with real pixel art later

### MVP Explicitly Does NOT Include

- Multiple pet selection UI
- Settings panel
- All 7 pets fully animated
- Left/right Dock support
- Multi-monitor support
- Dock auto-hide support
- Personality system
- Sound effects
- Persistence of pet state

---

## Future Ideas

These are possibilities for post-MVP milestones. They are NOT commitments.

### Behaviors
- Walking, standing, sitting, sleeping, running, jumping
- Idle micro-animations (tail wag, ear twitch, blinking)
- Reacting to mouse movement (following cursor, startled)
- Reacting to clicks (happy bounce, wave)
- Randomly changing direction
- Moving along the full Dock width
- Interacting with Dock boundaries (bumping, turning around)

### Personality
- Different pets have different behavior probabilities
- Speed varies by pet type
- Preferred activities differ (cat sleeps more, dog runs more)

### Platform
- Support Dock at bottom / left / right
- Support Dock auto-hide
- Support multiple monitors
- Support Spaces and fullscreen apps
- Settings UI for pet selection, behavior tuning
- Multiple pets simultaneously

### Distribution
- Code signing and notarization
- DMG or App Store distribution
- Auto-update mechanism
