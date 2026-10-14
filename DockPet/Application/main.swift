import AppKit

/// Application entry point.
/// Configures NSApplication as an accessory (no Dock icon) and runs the event loop.
let app = NSApplication.shared
app.setActivationPolicy(.accessory)

let delegate = AppDelegate()
app.delegate = delegate
app.run()
