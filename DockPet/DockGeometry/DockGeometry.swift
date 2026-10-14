import Foundation

/// Represents the position of the macOS Dock on screen.
enum DockOrientation: String, CustomStringConvertible, CaseIterable {
    case bottom
    case left
    case right

    var description: String { rawValue }
}

/// Contains computed information about the Dock's position and dimensions,
/// inferred from NSScreen geometry (frame vs visibleFrame) and system preferences.
///
/// This module has NO AppKit dependency beyond the data it receives.
struct DockInfo: Equatable {
    let orientation: DockOrientation
    let screenFrame: CGRect
    let visibleFrame: CGRect
    let dockThickness: CGFloat
    let isAutoHide: Bool

    init(
        orientation: DockOrientation,
        screenFrame: CGRect,
        visibleFrame: CGRect,
        dockThickness: CGFloat,
        isAutoHide: Bool = false
    ) {
        self.orientation = orientation
        self.screenFrame = screenFrame
        self.visibleFrame = visibleFrame
        self.dockThickness = dockThickness
        self.isAutoHide = isAutoHide
    }
}

/// Structure representing a screen with its identity and geometry for multi-monitor support.
struct ScreenGeometry: Equatable {
    let id: String
    let name: String
    let frame: CGRect
    let visibleFrame: CGRect
}

/// Pure geometry module for detecting Dock position, multi-monitor displays, and pet placement.
///
/// All methods are static and side-effect-free.
enum DockGeometry {

    /// Detects Dock orientation, thickness, and auto-hide status.
    ///
    /// - Parameters:
    ///   - screenFrame: Full frame of the screen.
    ///   - visibleFrame: Usable area of the screen excluding Dock and menu bar.
    ///   - checkDefaults: Whether to check `com.apple.dock` defaults for auto-hide. Default: true.
    static func detect(
        screenFrame: CGRect,
        visibleFrame: CGRect,
        checkDefaults: Bool = true
    ) -> DockInfo {
        let bottomGap = visibleFrame.origin.y - screenFrame.origin.y
        let leftGap = visibleFrame.origin.x - screenFrame.origin.x
        let rightGap = screenFrame.maxX - visibleFrame.maxX

        // Check com.apple.dock defaults for auto-hide and orientation fallback
        var isAutoHide = false
        var defaultsOrientation: DockOrientation? = nil

        if checkDefaults, let dockDefaults = UserDefaults(suiteName: "com.apple.dock") {
            isAutoHide = dockDefaults.bool(forKey: "autohide")
            if let orientStr = dockDefaults.string(forKey: "orientation") {
                defaultsOrientation = DockOrientation(rawValue: orientStr)
            }
        }

        // Determine orientation by the largest gap between screenFrame and visibleFrame
        if bottomGap > leftGap && bottomGap > rightGap && bottomGap > 0 {
            return DockInfo(
                orientation: .bottom,
                screenFrame: screenFrame,
                visibleFrame: visibleFrame,
                dockThickness: bottomGap,
                isAutoHide: isAutoHide
            )
        } else if leftGap > rightGap && leftGap > 0 {
            return DockInfo(
                orientation: .left,
                screenFrame: screenFrame,
                visibleFrame: visibleFrame,
                dockThickness: leftGap,
                isAutoHide: isAutoHide
            )
        } else if rightGap > 0 {
            return DockInfo(
                orientation: .right,
                screenFrame: screenFrame,
                visibleFrame: visibleFrame,
                dockThickness: rightGap,
                isAutoHide: isAutoHide
            )
        } else {
            // No visible Dock gap (Dock auto-hidden or on another display)
            let fallbackOrientation = defaultsOrientation ?? .bottom
            return DockInfo(
                orientation: fallbackOrientation,
                screenFrame: screenFrame,
                visibleFrame: visibleFrame,
                dockThickness: 0,
                isAutoHide: isAutoHide
            )
        }
    }

    /// Finds the screen containing the Dock among all connected displays.
    ///
    /// The Dock screen is identified by the presence of a Dock gap (bottom, left, or right)
    /// between `frame` and `visibleFrame`. If no screen has a detectable Dock gap
    /// (e.g. auto-hide is active), it defaults to the primary screen (origin 0,0).
    static func findDockScreen(among screens: [ScreenGeometry]) -> ScreenGeometry? {
        guard !screens.isEmpty else { return nil }

        // First pass: find the screen with an actual Dock gap
        for screen in screens {
            let info = detect(screenFrame: screen.frame, visibleFrame: screen.visibleFrame, checkDefaults: false)
            if info.dockThickness > 0 {
                return screen
            }
        }

        // Second pass: if auto-hide or no gap detected, return primary display (origin 0,0) or first
        if let primary = screens.first(where: { $0.frame.origin == .zero }) {
            return primary
        }

        return screens.first
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
            let x = screen.midX - petSize.width / 2
            let y = screen.origin.y + dockTop + margin
            return CGRect(x: x, y: y, width: petSize.width, height: petSize.height)

        case .left:
            let x = screen.origin.x + dockTop + margin
            let y = screen.midY - petSize.height / 2
            return CGRect(x: x, y: y, width: petSize.width, height: petSize.height)

        case .right:
            let x = screen.maxX - dockTop - margin - petSize.width
            let y = screen.midY - petSize.height / 2
            return CGRect(x: x, y: y, width: petSize.width, height: petSize.height)
        }
    }

    /// Returns the movement bounds for the pet along the Dock edge.
    ///
    /// - Parameters:
    ///   - dockInfo: The detected Dock geometry.
    ///   - petSize: The display size of the pet in points.
    ///   - inset: Points of padding from the screen edges. Default: 8.
    /// - Returns: A `ClosedRange<CGFloat>` of valid coordinates along the movement axis
    ///   (X for bottom Dock, Y for left/right Dock).
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
