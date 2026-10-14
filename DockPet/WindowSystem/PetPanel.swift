import AppKit

/// A transparent, borderless, non-activating panel for displaying the pet.
///
/// Key behaviors:
/// - Does not appear in Mission Control or Cmd+Tab
/// - Does not steal focus from the user's active application
/// - Remains visible when other applications are active
/// - Has no title bar, border, or shadow
///
/// Based on verified macOS research (docs/MACOS_RESEARCH.md §2, §7).
final class PetPanel: NSPanel {

    init(contentRect: NSRect) {
        super.init(
            contentRect: contentRect,
            styleMask: [.borderless, .nonactivatingPanel],
            backing: .buffered,
            defer: false
        )

        // Transparency: no opaque background, clear color, no shadow
        isOpaque = false
        backgroundColor = .clear
        hasShadow = false

        // Stay visible when app is not active
        // NSPanel defaults hidesOnDeactivate to true — must override
        hidesOnDeactivate = false

        // Float above normal windows but below system UI
        level = .floating

        // Spaces behavior: appear on all Spaces, don't move during Mission Control
        collectionBehavior = [
            .canJoinAllSpaces,
            .fullScreenAuxiliary,
            .stationary,
            .ignoresCycle
        ]

        // Do not become key or main window — prevents focus stealing
        // (canBecomeKey and canBecomeMain are overridden below)
    }

    /// Prevent the panel from becoming the key window.
    /// This ensures it never steals keyboard focus.
    override var canBecomeKey: Bool { false }

    /// Prevent the panel from becoming the main window.
    override var canBecomeMain: Bool { false }
}
