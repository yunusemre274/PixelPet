import AppKit

/// Temporary placeholder view for M1 proof of concept.
/// Draws a simple pixel-art-style creature using Core Graphics.
///
/// This is NOT final artwork. It exists only to verify:
/// 1. Transparency works (clear background is invisible)
/// 2. The placeholder is visible above the Dock
/// 3. Click detection works on the drawn content
/// 4. Nearest-neighbor rendering produces crisp pixels (no blur)
///
/// Will be replaced by the asset pipeline in M3/M6.
final class PlaceholderPetView: NSView {

    /// Tracks whether the placeholder was clicked (simple visual feedback for M1 testing).
    private var isClicked = false

    override init(frame: NSRect) {
        super.init(frame: frame)
        wantsLayer = true
        // Nearest-neighbor so any scaled drawing stays crisp
        layer?.magnificationFilter = .nearest
        layer?.minificationFilter = .nearest
    }

    @available(*, unavailable)
    required init?(coder: NSCoder) {
        fatalError("Not implemented")
    }

    // MARK: - Drawing

    override func draw(_ dirtyRect: NSRect) {
        guard let ctx = NSGraphicsContext.current?.cgContext else { return }

        // Clear the entire view (transparent)
        ctx.clear(bounds)

        // Disable interpolation for crisp pixel art
        ctx.interpolationQuality = .none

        // Draw a simple 8×8 grid pixel creature, scaled to fill the view
        // Each "pixel" in our 8×8 grid maps to (viewWidth/8) × (viewHeight/8) points
        let gridSize = 8
        let pixelW = bounds.width / CGFloat(gridSize)
        let pixelH = bounds.height / CGFloat(gridSize)

        // Simple creature pattern (1 = body, 2 = eye, 0 = transparent)
        // Drawn facing right
        let pattern: [[Int]] = [
            [0, 0, 1, 1, 1, 0, 0, 0],
            [0, 1, 1, 1, 1, 1, 0, 0],
            [0, 1, 2, 1, 2, 1, 0, 0],
            [0, 1, 1, 1, 1, 1, 1, 0],
            [1, 1, 1, 1, 1, 1, 1, 0],
            [0, 1, 1, 1, 1, 1, 0, 0],
            [0, 1, 0, 1, 0, 1, 0, 0],
            [0, 1, 0, 0, 0, 1, 0, 0],
        ]

        // Body color changes on click (simple visual feedback for M1)
        let bodyColor: NSColor = isClicked
            ? NSColor(red: 0.3, green: 0.8, blue: 0.4, alpha: 1.0)   // green flash
            : NSColor(red: 0.6, green: 0.75, blue: 0.95, alpha: 1.0) // soft blue
        let eyeColor = NSColor.white

        for row in 0..<gridSize {
            for col in 0..<gridSize {
                let value = pattern[row][col]
                guard value != 0 else { continue }

                let color = (value == 2) ? eyeColor : bodyColor
                ctx.setFillColor(color.cgColor)

                // Flip Y: row 0 is the top of the creature, but CG origin is bottom-left
                let x = CGFloat(col) * pixelW
                let y = bounds.height - CGFloat(row + 1) * pixelH
                ctx.fill(CGRect(x: x, y: y, width: pixelW, height: pixelH))
            }
        }
    }

    // MARK: - Click Handling

    override func mouseDown(with event: NSEvent) {
        print("[DockPet] Placeholder clicked")

        // Toggle color as simple visual feedback
        isClicked = true
        needsDisplay = true

        // Reset after a short delay
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.3) { [weak self] in
            self?.isClicked = false
            self?.needsDisplay = true
        }
    }

    // MARK: - Hit Testing

    /// Only register clicks on non-transparent pixels.
    /// Since our view is tightly sized to the pet, this is mostly a safety check.
    override func hitTest(_ point: NSPoint) -> NSView? {
        // Convert to view coordinates
        let localPoint = convert(point, from: superview)
        guard bounds.contains(localPoint) else { return nil }

        // Check if this pixel position corresponds to a drawn pixel in our pattern
        let gridSize = 8
        let col = Int(localPoint.x / (bounds.width / CGFloat(gridSize)))
        let row = gridSize - 1 - Int(localPoint.y / (bounds.height / CGFloat(gridSize)))

        let pattern: [[Int]] = [
            [0, 0, 1, 1, 1, 0, 0, 0],
            [0, 1, 1, 1, 1, 1, 0, 0],
            [0, 1, 2, 1, 2, 1, 0, 0],
            [0, 1, 1, 1, 1, 1, 1, 0],
            [1, 1, 1, 1, 1, 1, 1, 0],
            [0, 1, 1, 1, 1, 1, 0, 0],
            [0, 1, 0, 1, 0, 1, 0, 0],
            [0, 1, 0, 0, 0, 1, 0, 0],
        ]

        if row >= 0 && row < gridSize && col >= 0 && col < gridSize && pattern[row][col] != 0 {
            return self
        }

        // Transparent area — pass through
        return nil
    }
}
