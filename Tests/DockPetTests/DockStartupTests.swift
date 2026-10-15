import AppKit
import Foundation
import Testing
@testable import DockPet

@Suite("Custom Dock startup geometry")
struct DockStartupTests {
    private let screen = CGRect(x: 0, y: 0, width: 1440, height: 900)

    @Test("A custom visible Dock height wins over tile-size estimates", arguments: [24.0, 48.0, 96.0])
    func actualDockHeight(height: Double) {
        let info = DockGeometry.detect(screenFrame: screen,
            visibleFrame: CGRect(x: 0, y: height, width: 1440, height: 865 - height),
            preferences: DockPreferences(orientation: .bottom, tileSize: 120))
        #expect(info.dockThickness == CGFloat(height))
        let frame = DockGeometry.petFrame(dockInfo: info, petSize: CGSize(width: 192, height: 192), anchorOffset: 6)
        #expect(frame.minY + 6 == CGFloat(height) + 4)
    }

    @Test("Startup without a reserved frame uses the user's custom tile size and side")
    func startupFallback() {
        let info = DockGeometry.detect(screenFrame: screen, visibleFrame: screen,
            preferences: DockPreferences(orientation: .left, tileSize: 26))
        #expect(info.orientation == .left)
        #expect(info.dockThickness == 26)
        #expect(DockGeometry.petFrame(dockInfo: info, petSize: CGSize(width: 64, height: 64)).minX == 30)
    }

    @Test("Hidden Dock remains on the screen edge rather than using a visible-height estimate")
    func hiddenDock() {
        let info = DockGeometry.detect(screenFrame: screen, visibleFrame: screen,
            preferences: DockPreferences(orientation: .right, isAutoHide: true, tileSize: 72))
        #expect(info.orientation == .right)
        #expect(info.dockThickness == 0)
    }

    @Test("Invalid tile sizes cannot produce invalid window geometry", arguments: [Double.nan, .infinity, -1, 0])
    func invalidFallback(size: Double) {
        let info = DockGeometry.detect(screenFrame: screen, visibleFrame: screen,
            preferences: DockPreferences(orientation: .bottom, tileSize: size))
        #expect(info.dockThickness == 0)
    }

    @Test("Foot anchor remains Dock-relative on an offset secondary display")
    func offsetDisplay() {
        let screen = CGRect(x: 1470, y: -124, width: 1920, height: 1080)
        let info = DockGeometry.detect(screenFrame: screen,
            visibleFrame: CGRect(x: 1470, y: -100, width: 1920, height: 1020), checkDefaults: false)
        let frame = DockGeometry.petFrame(dockInfo: info, petSize: CGSize(width: 128, height: 128), anchorOffset: 4)
        #expect(frame.minY + 4 == -96)
    }
}

@Suite("Baby Yoda integration", .serialized)
@MainActor
struct BabyYodaIntegrationTests {
    private func withPet(_ test: (PetCoordinator, SpriteView, PetPanel) -> Void) {
        let defaults = UserDefaults.standard
        let saved = defaults.object(forKey: "PetScale")
        defer {
            if let saved { defaults.set(saved, forKey: "PetScale") }
            else { defaults.removeObject(forKey: "PetScale") }
        }
        defaults.set(3, forKey: "PetScale")
        let panel = PetPanel(contentRect: CGRect(x: 0, y: 0, width: 192, height: 192))
        let view = SpriteView(frame: CGRect(x: 0, y: 0, width: 192, height: 192))
        panel.contentView = view
        let assets = URL(fileURLWithPath: FileManager.default.currentDirectoryPath).appendingPathComponent("Assets/Pets")
        let loader = PetAssetLoader(assetsDirectory: assets)
        #expect(loader.discoverPets().contains("BabyYoda"))
        let coordinator = PetCoordinator(panel: panel, spriteView: view, assetLoader: loader)
        coordinator.updateDockInfo(info(height: 24))
        coordinator.loadPet(named: "BabyYoda")
        test(coordinator, view, panel)
        coordinator.stop()
    }

    private func info(height: CGFloat) -> DockInfo {
        DockGeometry.detect(screenFrame: CGRect(x: 0, y: 0, width: 1440, height: 900),
            visibleFrame: CGRect(x: 0, y: height, width: 1440, height: 865 - height), checkDefaults: false)
    }

    @Test("Baby Yoda loads, anchors his feet and completes the hood/saber/training/sleep cycle")
    func completeCycle() {
        withPet { coordinator, view, panel in
            #expect(coordinator.manifest?.resolvedAnchorY == 2)
            #expect(panel.frame.minY + 6 == 28)
            #expect(coordinator.movement.isMoving)
            coordinator.advance(deltaTime: 10)
            #expect(coordinator.stateMachine.state == .specialAnimation)
            #expect(view.frames.count == 20)
            coordinator.advance(deltaTime: 3)
            #expect(view.currentFrameIndex == 12) // First training frame after dressing/ignition.
            coordinator.advance(deltaTime: 2)
            #expect(coordinator.stateMachine.state == .sleeping)
            #expect(view.frames.count == 4)
            #expect(!coordinator.movement.isMoving)
            coordinator.advance(deltaTime: 10)
            #expect(coordinator.stateMachine.state == .walking)
            #expect(coordinator.movement.isMoving)
        }
    }

    @Test("Dock shrink and pet resize re-anchor feet without restarting the walking phase")
    func dockResize() {
        withPet { coordinator, _, panel in
            coordinator.advance(deltaTime: 2)
            let x = panel.frame.minX
            let direction = coordinator.movement.direction
            coordinator.updateDockInfo(info(height: 90))
            #expect(panel.frame.minY + 6 == 94)
            coordinator.updateDockInfo(info(height: 24))
            #expect(panel.frame.minY + 6 == 28)
            #expect(panel.frame.minX == x)
            #expect(coordinator.movement.direction == direction)
            #expect(coordinator.stateMachine.stateTimer == 8)
            coordinator.setScale(1)
            #expect(panel.frame.minY + 2 == 28)
            coordinator.setScale(2)
            #expect(panel.frame.minY + 4 == 28)
        }
    }
}
