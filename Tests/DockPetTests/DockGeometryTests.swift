import Testing
import CoreGraphics
@testable import DockPet

// MARK: - Dock Detection Tests

@Suite("DockGeometry Detection")
struct DockDetectionTests {

    @Test("Detects bottom Dock from screen geometry")
    func detectBottomDock() {
        let screen = CGRect(x: 0, y: 0, width: 1440, height: 900)
        let visible = CGRect(x: 0, y: 70, width: 1440, height: 795)
        // Menu bar takes ~35pt from top, Dock takes 70pt from bottom

        let info = DockGeometry.detect(screenFrame: screen, visibleFrame: visible)

        #expect(info.orientation == .bottom)
        #expect(info.dockThickness == 70)
    }

    @Test("Detects left Dock from screen geometry")
    func detectLeftDock() {
        let screen = CGRect(x: 0, y: 0, width: 1440, height: 900)
        let visible = CGRect(x: 70, y: 0, width: 1370, height: 865)
        // Dock on left takes 70pt, menu bar takes 35pt from top

        let info = DockGeometry.detect(screenFrame: screen, visibleFrame: visible)

        #expect(info.orientation == .left)
        #expect(info.dockThickness == 70)
    }

    @Test("Detects right Dock from screen geometry")
    func detectRightDock() {
        let screen = CGRect(x: 0, y: 0, width: 1440, height: 900)
        let visible = CGRect(x: 0, y: 0, width: 1370, height: 865)
        // Dock on right takes 70pt from right

        let info = DockGeometry.detect(screenFrame: screen, visibleFrame: visible)

        #expect(info.orientation == .right)
        #expect(info.dockThickness == 70)
    }

    @Test("Defaults to bottom when no Dock gap (auto-hide)")
    func detectAutoHideDock() {
        let screen = CGRect(x: 0, y: 0, width: 1440, height: 900)
        // With auto-hide, visibleFrame only loses the menu bar
        let visible = CGRect(x: 0, y: 0, width: 1440, height: 865)

        let info = DockGeometry.detect(screenFrame: screen, visibleFrame: visible)

        // Menu bar takes top 35pt, no bottom/left/right gap → default bottom
        #expect(info.orientation == .bottom)
        #expect(info.dockThickness == 0)
    }

    @Test("Handles secondary display offset")
    func detectSecondaryDisplay() {
        // Secondary display to the right, with its own bottom Dock
        let screen = CGRect(x: 1440, y: 0, width: 1920, height: 1080)
        let visible = CGRect(x: 1440, y: 65, width: 1920, height: 1015)

        let info = DockGeometry.detect(screenFrame: screen, visibleFrame: visible)

        #expect(info.orientation == .bottom)
        #expect(info.dockThickness == 65)
    }
}

// MARK: - Pet Frame Tests

@Suite("DockGeometry Pet Placement")
struct DockPetFrameTests {

    let petSize = CGSize(width: 64, height: 64)

    @Test("Pet placed above bottom Dock, centered horizontally")
    func petFrameBottomDock() {
        let info = DockInfo(
            orientation: .bottom,
            screenFrame: CGRect(x: 0, y: 0, width: 1440, height: 900),
            visibleFrame: CGRect(x: 0, y: 70, width: 1440, height: 795),
            dockThickness: 70
        )

        let frame = DockGeometry.petFrame(dockInfo: info, petSize: petSize, margin: 4)

        #expect(frame.origin.y == 74)  // Dock top (70) + margin (4)
        #expect(frame.midX == 720)     // Centered on 1440
        #expect(frame.width == 64)
        #expect(frame.height == 64)
    }

    @Test("Pet placed to right of left Dock, centered vertically")
    func petFrameLeftDock() {
        let info = DockInfo(
            orientation: .left,
            screenFrame: CGRect(x: 0, y: 0, width: 1440, height: 900),
            visibleFrame: CGRect(x: 70, y: 0, width: 1370, height: 865),
            dockThickness: 70
        )

        let frame = DockGeometry.petFrame(dockInfo: info, petSize: petSize, margin: 4)

        #expect(frame.origin.x == 74)   // Dock right edge (70) + margin (4)
        #expect(frame.midY == 450)       // Centered on 900
    }

    @Test("Pet placed to left of right Dock, centered vertically")
    func petFrameRightDock() {
        let info = DockInfo(
            orientation: .right,
            screenFrame: CGRect(x: 0, y: 0, width: 1440, height: 900),
            visibleFrame: CGRect(x: 0, y: 0, width: 1370, height: 865),
            dockThickness: 70
        )

        let frame = DockGeometry.petFrame(dockInfo: info, petSize: petSize, margin: 4)

        // Pet right edge should be at (1440 - 70 - 4) = 1366
        #expect(frame.origin.x == 1302)  // 1440 - 70 - 4 - 64
        #expect(frame.midY == 450)
    }

    @Test("Pet with zero Dock thickness (auto-hide)")
    func petFrameAutoHideDock() {
        let info = DockInfo(
            orientation: .bottom,
            screenFrame: CGRect(x: 0, y: 0, width: 1440, height: 900),
            visibleFrame: CGRect(x: 0, y: 0, width: 1440, height: 865),
            dockThickness: 0
        )

        let frame = DockGeometry.petFrame(dockInfo: info, petSize: petSize, margin: 4)

        #expect(frame.origin.y == 4)  // 0 + 0 + 4
    }
}

// MARK: - Movement Bounds Tests

@Suite("DockGeometry Movement Bounds")
struct DockMovementBoundsTests {

    let petSize = CGSize(width: 64, height: 64)

    @Test("Horizontal bounds for bottom Dock")
    func movementBoundsBottom() {
        let info = DockInfo(
            orientation: .bottom,
            screenFrame: CGRect(x: 0, y: 0, width: 1440, height: 900),
            visibleFrame: CGRect(x: 0, y: 70, width: 1440, height: 795),
            dockThickness: 70
        )

        let bounds = DockGeometry.movementBounds(dockInfo: info, petSize: petSize, inset: 8)

        #expect(bounds.lowerBound == 8)
        #expect(bounds.upperBound == 1368)  // 1440 - 64 - 8
    }

    @Test("Vertical bounds for left Dock")
    func movementBoundsLeft() {
        let info = DockInfo(
            orientation: .left,
            screenFrame: CGRect(x: 0, y: 0, width: 1440, height: 900),
            visibleFrame: CGRect(x: 70, y: 0, width: 1370, height: 865),
            dockThickness: 70
        )

        let bounds = DockGeometry.movementBounds(dockInfo: info, petSize: petSize, inset: 8)

        #expect(bounds.lowerBound == 8)
        #expect(bounds.upperBound == 828)  // 900 - 64 - 8
    }
}

// MARK: - Multi-Monitor Tests (M9)

@Suite("DockGeometry Multi-Monitor Tests")
struct DockMultiMonitorTests {

    let primaryScreen = ScreenGeometry(
        id: "primary",
        name: "Built-in Retina Display",
        frame: CGRect(x: 0, y: 0, width: 1470, height: 956),
        visibleFrame: CGRect(x: 0, y: 65, width: 1470, height: 858) // 65pt dock
    )

    let secondaryScreen = ScreenGeometry(
        id: "secondary",
        name: "External 4K Display",
        frame: CGRect(x: 1470, y: -124, width: 1920, height: 1080),
        visibleFrame: CGRect(x: 1470, y: -124, width: 1920, height: 1080) // no dock gap
    )

    @Test("Finds screen containing Dock gap among multiple screens")
    func findDockScreenWithGap() {
        let screens = [secondaryScreen, primaryScreen] // secondary listed first

        let dockScreen = DockGeometry.findDockScreen(among: screens)

        #expect(dockScreen?.id == "primary")
        #expect(dockScreen?.name == "Built-in Retina Display")
    }

    @Test("Finds left-docked screen among multiple screens")
    func findLeftDockScreen() {
        let leftDockScreen = ScreenGeometry(
            id: "leftDock",
            name: "Side Monitor",
            frame: CGRect(x: 0, y: 0, width: 1920, height: 1080),
            visibleFrame: CGRect(x: 75, y: 0, width: 1845, height: 1045) // 75pt left dock
        )
        let otherScreen = ScreenGeometry(
            id: "other",
            name: "Other Monitor",
            frame: CGRect(x: 1920, y: 0, width: 1920, height: 1080),
            visibleFrame: CGRect(x: 1920, y: 0, width: 1920, height: 1045) // only menu bar
        )

        let dockScreen = DockGeometry.findDockScreen(among: [otherScreen, leftDockScreen])

        #expect(dockScreen?.id == "leftDock")
    }

    @Test("Falls back to primary display (origin 0,0) when all docks are auto-hidden")
    func fallbackToPrimaryOnAutoHide() {
        let autoHidePrimary = ScreenGeometry(
            id: "primary",
            name: "Primary Display",
            frame: CGRect(x: 0, y: 0, width: 1470, height: 956),
            visibleFrame: CGRect(x: 0, y: 0, width: 1470, height: 920) // no bottom dock gap
        )
        let autoHideSecondary = ScreenGeometry(
            id: "secondary",
            name: "Secondary Display",
            frame: CGRect(x: 1470, y: 0, width: 1920, height: 1080),
            visibleFrame: CGRect(x: 1470, y: 0, width: 1920, height: 1080)
        )

        let dockScreen = DockGeometry.findDockScreen(among: [autoHideSecondary, autoHidePrimary])

        #expect(dockScreen?.id == "primary")
    }
}

