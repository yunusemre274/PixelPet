import Foundation

/// Represents the position of the macOS Dock on screen.
enum DockOrientation: String, CustomStringConvertible {
    case bottom
    case left
    case right

    var description: String { rawValue }
}

/// Contains computed information about the Dock's position and dimensions,
/// inferred from NSScreen geometry (frame vs visibleFrame).
///
/// This module has NO AppKit dependency beyond the data it receives.
/// Use `DockGeometry.detect(screenFrame:visibleFrame:)` to compute from NSScreen values.
struct DockInfo: Equatable {
    let orientation: DockOrientation
    let screenFrame: CGRect
    let visibleFrame: CGRect
    let dockThickness: CGFloat
}

/// Pure geometry module for detecting Dock position and computing pet placement.
///
/// All methods are static and side-effect-free. The module infers Dock orientation
/// from the difference between `NSScreen.frame` and `NSScreen.visibleFrame`.
/// No private APIs are used.
///
/// Validated approach: ADR-005 (geometry inference).
enum DockGeometry {

    /// Detects Dock orientation and thickness from screen geometry.
    ///
    /// The Dock occupies the gap between `screenFrame` and `visibleFrame`.
    /// - Bottom Dock: `visibleFrame.origin.y > screenFrame.origin.y`
    /// - Left Dock: `visibleFrame.origin.x > screenFrame.origin.x`
    /// - Right Dock: `visibleFrame.maxX < screenFrame.maxX`
    ///
    /// When no Dock gap is detected (e.g., auto-hide), defaults to `.bottom` with thickness 0.
    static func detect(screenFrame: CGRect, visibleFrame: CGRect) -> DockInfo {
        let bottomGap = visibleFrame.origin.y - screenFrame.origin.y
        let leftGap = visibleFrame.origin.x - screenFrame.origin.x
        let rightGap = screenFrame.maxX - visibleFrame.maxX

        // Also account for menu bar gap at top
        // The menu bar subtracts from the top, so we don't count that as Dock

        // Pick the largest non-menu-bar gap as the Dock side
        // Menu bar is always at the top, so topGap is NOT the Dock
        if bottomGap > leftGap && bottomGap > rightGap && bottomGap > 0 {
            return DockInfo(
                orientation: .bottom,
                screenFrame: screenFrame,
                visibleFrame: visibleFrame,
                dockThickness: bottomGap
            )
        } else if leftGap > rightGap && leftGap > 0 {
            return DockInfo(
                orientation: .left,
                screenFrame: screenFrame,
                visibleFrame: visibleFrame,
                dockThickness: leftGap
            )
        } else if rightGap > 0 {
            return DockInfo(
                orientation: .right,
                screenFrame: screenFrame,
                visibleFrame: visibleFrame,
                dockThickness: rightGap
            )
        } else {
            // No visible Dock gap (auto-hide or no Dock visible)
            // Default to bottom with zero thickness
            return DockInfo(
                orientation: .bottom,
                screenFrame: screenFrame,
                visibleFrame: visibleFrame,
                dockThickness: 0
            )
        }
    }

    /// Computes the frame for the pet window given Dock info and pet size.
    ///
    /// The pet is positioned:
    /// - **Bottom Dock**: centered horizontally, just above the Dock top edge
    /// - **Left Dock**: centered vertically, just to the right of the Dock
    /// - **Right Dock**: centered vertically, just to the left of the Dock
    ///
    /// - Parameters:
    ///   - dockInfo: The detected Dock geometry.
    ///   - petSize: The display size of the pet in points.
    ///   - margin: Points of clearance between the pet and the Dock edge. Default: 4.
    /// - Returns: The frame rect for the pet window in screen coordinates.
    static func petFrame(
        dockInfo: DockInfo,
        petSize: CGSize,
        margin: CGFloat = 4
    ) -> CGRect {
        let screen = dockInfo.screenFrame
        let dockTop = dockInfo.dockThickness

        switch dockInfo.orientation {
        case .bottom:
            // Pet sits centered horizontally, just above the Dock
            let x = screen.midX - petSize.width / 2
            let y = screen.origin.y + dockTop + margin
            return CGRect(x: x, y: y, width: petSize.width, height: petSize.height)

        case .left:
            // Pet sits centered vertically, just to the right of the Dock
            let x = screen.origin.x + dockTop + margin
            let y = screen.midY - petSize.height / 2
            return CGRect(x: x, y: y, width: petSize.width, height: petSize.height)

        case .right:
            // Pet sits centered vertically, just to the left of the Dock
            let x = screen.maxX - dockTop - margin - petSize.width
            let y = screen.midY - petSize.height / 2
            return CGRect(x: x, y: y, width: petSize.width, height: petSize.height)
        }
    }

    /// Returns the horizontal movement bounds for the pet along the Dock edge.
    ///
    /// - Parameters:
    ///   - dockInfo: The detected Dock geometry.
    ///   - petSize: The display size of the pet in points.
    ///   - inset: Points of padding from the screen edges. Default: 8.
    /// - Returns: A `ClosedRange<CGFloat>` of valid X positions (bottom Dock)
    ///   or Y positions (left/right Dock) for the pet's origin.
    static func movementBounds(
        dockInfo: DockInfo,
        petSize: CGSize,
        inset: CGFloat = 8
    ) -> ClosedRange<CGFloat> {
        let screen = dockInfo.screenFrame

        switch dockInfo.orientation {
        case .bottom:
            let minX = screen.origin.x + inset
            let maxX = screen.maxX - petSize.width - inset
            return minX ... max(minX, maxX)

        case .left, .right:
            let minY = screen.origin.y + inset
            let maxY = screen.maxY - petSize.height - inset
            return minY ... max(minY, maxY)
        }
    }
}
