# macOS Research

Verified research on macOS APIs relevant to DockPet. Each finding is categorized:

- **VERIFIED** — confirmed in official Apple documentation
- **EXPERIMENTALLY_VERIFY** — likely works, needs testing on target macOS version
- **AVOID** — deprecated, private, or problematic
- **UNKNOWN** — could not confirm

---

## 1. Transparent Borderless Windows

**Status:** VERIFIED

To create a fully transparent, borderless window:

```swift
let window = NSWindow(
    contentRect: rect,
    styleMask: [.borderless],
    backing: .buffered,
    defer: false
)
window.isOpaque = false
window.backgroundColor = .clear
window.hasShadow = false
```

- `styleMask: [.borderless]` — removes title bar and frame
- `isOpaque = false` — tells WindowServer the window has transparency
- `backgroundColor = .clear` — makes the window background transparent
- `hasShadow = false` — **important**: even clear windows draw a faint shadow by default

**Docs:**
- [NSWindow](https://developer.apple.com/documentation/appkit/nswindow)
- [NSWindow.StyleMask](https://developer.apple.com/documentation/appkit/nswindow/stylemask-swift.struct)

---

## 2. NSPanel vs NSWindow

**Status:** VERIFIED

`NSPanel` is a subclass of `NSWindow` designed for utility/floating panels. **Recommended for DockPet** because:

- `.nonactivatingPanel` style mask — clicking does not steal focus from other apps
- `becomesKeyOnlyIfNeeded = true` — panel stays non-key unless a text field requires it
- `isFloatingPanel = true` — auto-sets level to `.floating`
- `hidesOnDeactivate` — **defaults to `true` on NSPanel**. **Must set to `false`** or the pet disappears when the user clicks another app.

**Docs:**
- [NSPanel](https://developer.apple.com/documentation/appkit/nspanel)

---

## 3. Window Levels

**Status:** VERIFIED

Window levels establish stacking order:

| Level | Raw Value | Use |
|-------|-----------|-----|
| `.normal` | 0 | Standard windows |
| `.floating` | 3 | Utility panels, palettes |
| `.modalPanel` | 8 | Modal dialogs |
| `.mainMenu` | 24 | Menu bar |
| `.statusBar` | 25 | Status bar items |
| `.popUpMenu` | 101 | Context menus |
| `.screenSaver` | 1000 | Screen saver |

**Recommendation:** Use `.floating` for the pet. Adjust higher only if the pet is hidden behind too many windows.

**Docs:** [NSWindow.Level](https://developer.apple.com/documentation/appkit/nswindow/level)

---

## 4. NSScreen Geometry

**Status:** VERIFIED

### `frame` vs `visibleFrame`

- `frame` — entire physical display bounds in points
- `visibleFrame` — usable area excluding menu bar and Dock

Example (bottom Dock):
```
frame:        (0, 0, 1470, 956)
visibleFrame: (0, 66, 1470, 857)
```
Bottom inset (66pt) = Dock thickness. Top inset (33pt) = menu bar.

### Multi-Monitor

- `NSScreen.screens` — array of all active screens. Index 0 is primary.
- `NSScreen.main` — screen with current key window. **Can be nil in agent apps.**
- Listen for `NSApplication.didChangeScreenParametersNotification` for changes.

**Docs:**
- [NSScreen](https://developer.apple.com/documentation/appkit/nsscreen)
- [NSScreen.visibleFrame](https://developer.apple.com/documentation/appkit/nsscreen/1388369-visibleframe)

---

## 5. Dock Position Detection

**Status:** VERIFIED (geometry inference), AVOID (private APIs)

### No public Dock API exists.

**Recommended approach:** Infer from `frame` vs `visibleFrame`:

```swift
let frame = screen.frame
let visible = screen.visibleFrame

let bottomInset = visible.origin.y - frame.origin.y
let leftInset = visible.origin.x - frame.origin.x
let rightInset = (frame.maxX) - (visible.maxX)
let topInset = (frame.maxY) - (visible.maxY)  // menu bar

// Largest non-menu-bar inset indicates Dock position
```

### `com.apple.dock` UserDefaults

**Status:** EXPERIMENTALLY_VERIFY (works outside sandbox), AVOID (inside App Sandbox)

Keys: `orientation` ("bottom"/"left"/"right"), `autohide` (bool), `tilesize` (float).

**Warning:** Sandboxed apps cannot read other apps' UserDefaults. The geometry approach is sandbox-safe.

### Private APIs (`CoreDock`)

**Status:** AVOID — undocumented, may break between macOS versions.

---

## 6. Dock Auto-Hide

**Status:** VERIFIED

- When Dock is auto-hidden, `visibleFrame` expands to match `frame` (minus menu bar).
- macOS maintains a 1–4pt invisible trigger band at the Dock edge.
- Toggling auto-hide posts `NSApplication.didChangeScreenParametersNotification`.
- Re-query `visibleFrame` in the notification handler.

**Consequence:** When auto-hidden, we cannot determine Dock thickness from geometry alone. Fallback options:

1. Read `UserDefaults` for `autohide` key (EXPERIMENTALLY_VERIFY, fails in sandbox)
2. Use a sensible default thickness
3. Position pet at screen edge regardless

**Deferred to M9.**

---

## 7. Click-Through and Hit Testing

**Status:** VERIFIED

### Two approaches:

**Option A: Tight Sprite Window (Recommended)**

Size the NSPanel to match the sprite bounds (e.g., 64×64pt). Move the window frame as the pet moves. Clicks outside the window pass through automatically.

**Option B: Full-Screen Overlay**

Use `ignoresMouseEvents` toggling based on cursor position. More complex, less reliable.

**Recommendation:** Option A. Simpler, no permission issues, native click-through.

**Docs:** [NSWindow.ignoresMouseEvents](https://developer.apple.com/documentation/appkit/nswindow/1419735-ignoresmouseevents)

---

## 8. Mouse Event Handling

**Status:** VERIFIED

| API | Scope | Permissions |
|-----|-------|-------------|
| `NSEvent.mouseLocation` | Global cursor position | None |
| `NSEvent.addLocalMonitorForEvents` | Events in own app | None |
| `NSEvent.addGlobalMonitorForEvents` | Events in other apps | Accessibility |
| `NSTrackingArea` | Hover detection on a view | None |

**Recommendation:** Use `NSTrackingArea` with `.activeAlways` for hover detection and local event monitors for clicks. Avoid global monitors to skip Accessibility permission.

**Docs:**
- [NSTrackingArea](https://developer.apple.com/documentation/appkit/nstrackingarea)
- [NSEvent monitors](https://developer.apple.com/documentation/appkit/nsevent/1535472-addglobalmonitorforevents)

---

## 9. Spaces and Fullscreen

**Status:** VERIFIED

Configure `collectionBehavior` for persistent floating overlay:

```swift
panel.collectionBehavior = [
    .canJoinAllSpaces,        // appear on all Spaces
    .fullScreenAuxiliary,     // visible over fullscreen apps
    .stationary,              // don't move during Mission Control
    .ignoresCycle             // exclude from Cmd+` cycling
]
```

- `.canJoinAllSpaces` — pet visible on every Space
- `.fullScreenAuxiliary` — **critical**: without this, pet hides when any app goes fullscreen
- `.stationary` — pet stays anchored during Exposé/Mission Control
- `.ignoresCycle` — pet window excluded from window switching

**Docs:** [NSWindow.CollectionBehavior](https://developer.apple.com/documentation/appkit/nswindow/collectionbehavior)

---

## 10. SpriteKit in Transparent Window

**Status:** VERIFIED

- `SKView.allowsTransparency = true` + `scene.backgroundColor = .clear` works
- `SKTexture.filteringMode = .nearest` for pixel art
- **Downside:** SpriteKit runs a continuous Metal render loop (60/120Hz) even when idle. Significant battery impact unless manually paused with `isPaused = true`.

**Docs:**
- [SKView.allowsTransparency](https://developer.apple.com/documentation/spritekit/skview/1519707-allowstransparency)
- [SKTextureFilteringMode](https://developer.apple.com/documentation/spritekit/sktexturefilteringmode)

---

## 11. Core Animation for Pixel Art

**Status:** VERIFIED

- `CALayer.magnificationFilter = .nearest` for crisp pixel scaling
- `CALayer.minificationFilter = .nearest`
- Frame cycling: assign `CGImage` to `layer.contents` or use `CAKeyframeAnimation(keyPath: "contents")` with `calculationMode = .discrete`
- **Extremely low overhead** — composited by WindowServer, ~0% idle CPU

**Comparison:**

| | Core Animation | SpriteKit |
|---|---|---|
| Idle CPU | ~0% | Moderate-high |
| Battery | Negligible | Noticeable |
| Complexity | Simple | Heavyweight |
| Pixel art | `.nearest` filter | `.nearest` filter |

**Recommendation:** Core Animation is strongly preferred for a background desktop pet.

**Docs:**
- [CALayer.magnificationFilter](https://developer.apple.com/documentation/quartzcore/calayer/1410769-magnificationfilter)
- [CAKeyframeAnimation](https://developer.apple.com/documentation/quartzcore/cakeyframeanimation)

---

## 12. Image Rendering and Retina

**Status:** VERIFIED

### Nearest-Neighbor in Custom Drawing

```swift
NSGraphicsContext.current?.imageInterpolation = .none
image.draw(in: bounds)
```

### Nearest-Neighbor in Layer-Backed Views

```swift
view.wantsLayer = true
view.layer?.magnificationFilter = .nearest
```

### Retina Handling

- macOS uses points, not pixels. On Retina (2x), a 32×32pt view = 64×64 physical pixels.
- A 16×16 pixel sprite in a 64×64pt view = 8× integer scale. With nearest-neighbor, each sprite pixel becomes a crisp 8×8 block.
- Use `NSScreen.backingScaleFactor` to compute actual pixel dimensions.

**Docs:** [NSScreen.backingScaleFactor](https://developer.apple.com/documentation/appkit/nsscreen/1388385-backingscalefactor)

---

## 13. Menu Bar Agent App (LSUIElement)

**Status:** VERIFIED

Set `LSUIElement = true` in Info.plist (key: "Application is agent (UI element)"):

- No Dock icon
- No Cmd+Tab entry
- Can still show NSStatusItem (menu bar icon) and windows/panels

Programmatic equivalent: `NSApplication.shared.setActivationPolicy(.accessory)`

**AVOID `LSBackgroundOnly`** — creates a daemon with no window server connection. Cannot show windows.

**Docs:** [LSUIElement](https://developer.apple.com/documentation/bundleresources/information_property_list/lsuielement)

---

## 14. Animation Timing

**Status:** VERIFIED

| Mechanism | When to Use | Status |
|-----------|-------------|--------|
| `CADisplayLink` (macOS 14+) | Display-synced rendering | VERIFIED |
| `CVDisplayLink` | Legacy display sync | AVOID (deprecated) |
| `DispatchSourceTimer` | Low-frequency sprite ticking (6-10 Hz) | VERIFIED |
| `Timer` with tolerance | Simple periodic updates | VERIFIED |
| `NSAnimationContext` | Smooth window movement | VERIFIED |

**For DockPet:**
- **Sprite frame cycling** (4-8 FPS): `DispatchSourceTimer` at 6-10Hz with tolerance for CPU coalescing
- **Window movement** (pet walking): `NSAnimationContext.runAnimationGroup` — handled by GPU compositor, no CPU per frame
- **State machine updates**: `DispatchSourceTimer` (same timer or separate low-frequency timer)

`CADisplayLink` is available macOS 14+ via `NSView.displayLink(target:selector:)`. Good for smooth animation but overkill for 6 FPS sprite cycling.

**Docs:**
- [CADisplayLink](https://developer.apple.com/documentation/quartzcore/cadisplaylink)
- [NSAnimationContext](https://developer.apple.com/documentation/appkit/nsanimationcontext)

---

## 15. Permissions Summary

| Feature | Permission Required |
|---------|-------------------|
| Transparent floating window | None |
| NSPanel non-activating | None |
| Menu bar icon | None |
| NSTrackingArea | None |
| NSEvent.mouseLocation | None |
| Local event monitors | None |
| **Global event monitors** | **Accessibility** |
| **Screen recording** | **Screen Recording** |
| UserDefaults (own app) | None |
| UserDefaults (com.apple.dock) | None (unsandboxed) / **Blocked (sandboxed)** |

**Recommendation:** MVP requires NO special permissions. Avoid global event monitors initially.
