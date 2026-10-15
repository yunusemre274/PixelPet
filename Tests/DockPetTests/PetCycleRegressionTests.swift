import AppKit
import Foundation
import Testing
@testable import DockPet

@Suite("Pet cycle regressions")
struct PetCycleRegressionTests {
    @Test("Low-frequency ticks keep an exact 25-second cycle over many repetitions")
    func cycleDoesNotDrift() {
        let machine = PetStateMachine()
        for _ in 0..<20 {
            for _ in 0..<50 { machine.update(deltaTime: 0.2) }
            #expect(machine.state == .specialAnimation)
            #expect(abs(machine.stateTimer - 5) < 0.000001)
            for _ in 0..<25 { machine.update(deltaTime: 0.2) }
            #expect(machine.state == .sleeping)
            for _ in 0..<50 { machine.update(deltaTime: 0.2) }
            #expect(machine.state == .walking)
            #expect(abs(machine.stateTimer - 10) < 0.000001)
        }
    }

    @Test("A tick crossing phase boundaries preserves all elapsed time")
    func carriesOvershoot() {
        let machine = PetStateMachine()
        var elapsed: TimeInterval = 0
        machine.update(deltaTime: 26.25) { elapsed += $0 }
        #expect(machine.state == .walking)
        #expect(machine.stateTimer == 8.75)
        #expect(elapsed == 26.25)
    }

    @Test("Click resumes the remaining phase instead of restarting its timer")
    func clickPreservesRemainingTime() {
        for state in [PetState.walking, .specialAnimation, .sleeping] {
            let machine = PetStateMachine(initialState: state)
            machine.update(deltaTime: 2.5)
            let remaining = machine.stateTimer
            machine.handleEvent(.clicked)
            machine.update(deltaTime: 1)
            #expect(machine.state == state)
            #expect(machine.stateTimer == remaining)
        }
    }

    @Test("Finishing a sprite sequence cannot shorten the five-second skill")
    func earlyAnimationCompletion() {
        let machine = PetStateMachine(initialState: .specialAnimation)
        machine.handleEvent(.animationComplete)
        #expect(machine.state == .specialAnimation)
        #expect(machine.stateTimer == 5)
    }

    @Test("Traversal covers a wide display and keeps reflected edge distance")
    func wideDisplayTraversal() {
        let movement = PetMovement()
        let bounds: ClosedRange<CGFloat> = -2000...1400
        movement.setPosition(bounds.lowerBound)
        movement.speed = 82.5
        movement.traversalDuration = 10
        movement.startMoving(bounds: bounds)
        movement.update(deltaTime: 10, bounds: bounds)
        #expect(movement.positionX == bounds.upperBound)
        #expect(movement.direction == .left)
        movement.update(deltaTime: 10, bounds: bounds)
        #expect(movement.positionX == bounds.lowerBound)
        #expect(movement.direction == .right)
    }

    @Test("Narrow and zero-width bounds cannot trap or move the pet off-screen")
    func smallBounds() {
        let movement = PetMovement()
        movement.speed = 110
        movement.setPosition(5)
        movement.startMoving()
        movement.update(deltaTime: 1, bounds: 0...10)
        #expect(movement.positionX == 5)
        #expect(movement.direction == .left)
        movement.update(deltaTime: 1, bounds: 3...3)
        #expect(movement.positionX == 3)
    }
}

@Suite("Pet coordinator regressions", .serialized)
@MainActor
struct PetCoordinatorRegressionTests {
    private func withPet(_ name: String = "Cat", screenWidth: CGFloat = 1440,
                         _ test: (PetCoordinator, SpriteView, PetPanel) -> Void) {
        let defaults = UserDefaults.standard
        let keys = ["PetScale", "ActivityLevel"]
        let saved = keys.map { defaults.object(forKey: $0) }
        defer {
            for (key, value) in zip(keys, saved) {
                if let value { defaults.set(value, forKey: key) }
                else { defaults.removeObject(forKey: key) }
            }
        }
        defaults.set(1, forKey: "PetScale")
        defaults.set("Normal", forKey: "ActivityLevel")
        let panel = PetPanel(contentRect: CGRect(x: 0, y: 0, width: 64, height: 64))
        let view = SpriteView(frame: panel.frame)
        panel.contentView = view
        let loader = PetAssetLoader(assetsDirectory: URL(fileURLWithPath: FileManager.default.currentDirectoryPath)
            .appendingPathComponent("Assets/Pets"))
        let coordinator = PetCoordinator(panel: panel, spriteView: view, assetLoader: loader)
        coordinator.updateDockInfo(DockInfo(orientation: .bottom,
            screenFrame: CGRect(x: 0, y: 0, width: screenWidth, height: 900),
            visibleFrame: CGRect(x: 0, y: 70, width: screenWidth, height: 800), dockThickness: 70))
        coordinator.loadPet(named: name)
        test(coordinator, view, panel)
        coordinator.stop()
    }

    @Test("Initial walking immediately translates the panel and advances poses")
    func movesOnLaunch() {
        withPet { coordinator, view, panel in
            #expect(coordinator.movement.isMoving)
            let initial = panel.frame.origin.x
            coordinator.advance(deltaTime: 0.2)
            #expect(panel.frame.origin.x != initial)
            #expect(view.currentFrameIndex == 1)
        }
    }

    @Test("Skill is one-shot, sleep lasts ten seconds, then walking resumes")
    func completeCycle() {
        withPet("CristianoRonaldo") { coordinator, view, panel in
            coordinator.advance(deltaTime: 10)
            #expect(coordinator.stateMachine.state == .specialAnimation)
            let initial = panel.frame.origin.x
            coordinator.advance(deltaTime: 4.9)
            #expect(panel.frame.origin.x == initial)
            #expect(view.currentFrameIndex == 19)
            coordinator.advance(deltaTime: 0.1)
            #expect(coordinator.stateMachine.state == .sleeping)
            for _ in 0..<50 { coordinator.advance(deltaTime: 0.2) }
            #expect(coordinator.stateMachine.state == .walking)
            #expect(coordinator.movement.isMoving)
        }
    }

    @Test("Messi travels with his ball, then stands for celebration and cup lift")
    func dribbleTravel() {
        withPet("LionelMessi") { coordinator, view, panel in
            coordinator.advance(deltaTime: 10)
            let initial = panel.frame.origin.x
            coordinator.advance(deltaTime: 1)
            #expect(panel.frame.origin.x != initial)
            coordinator.advance(deltaTime: 1)
            #expect(view.currentFrameIndex >= 8)
            let celebrating = panel.frame.origin.x
            coordinator.advance(deltaTime: 2.9)
            #expect(panel.frame.origin.x == celebrating)
            #expect(view.currentFrameIndex == 23)
        }
    }

    @Test("Click preserves sprite progress; pet switching restarts a full walk")
    func interruptionAndSwitch() {
        withPet { coordinator, view, _ in
            coordinator.advance(deltaTime: 0.4)
            let frame = view.currentFrameIndex
            coordinator.stateMachine.handleEvent(.clicked)
            coordinator.advance(deltaTime: 1)
            #expect(view.currentFrameIndex == frame)
            #expect(abs(coordinator.stateMachine.stateTimer - 9.6) < 0.000001)
            coordinator.advance(deltaTime: 12)
            coordinator.loadPet(named: "Turtle")
            #expect(coordinator.stateMachine.state == .walking)
            #expect(coordinator.stateMachine.stateTimer == 10)
            #expect(coordinator.movement.isMoving)
        }
    }

    @Test("A pet with no travel space cannot walk in place")
    func blockedWalkIsStatic() {
        withPet(screenWidth: 64) { coordinator, view, _ in
            coordinator.advance(deltaTime: 1)
            #expect(!coordinator.movement.isMoving)
            #expect(view.currentFrameIndex == 0)
        }
    }

    @Test("Successive wide-screen walks visit both edges instead of the same half")
    func coversBothHalves() {
        withPet(screenWidth: 3440) { coordinator, _, panel in
            var minimum = panel.frame.origin.x
            var maximum = minimum
            for _ in 0..<500 {
                coordinator.advance(deltaTime: 0.1)
                minimum = min(minimum, panel.frame.origin.x)
                maximum = max(maximum, panel.frame.origin.x)
            }
            #expect(abs(minimum - 8) < 0.000001)
            #expect(abs(maximum - (3440 - 64 - 8)) < 0.000001)
        }
    }

    @Test("Hide and show resume animation from the same phase")
    func restartPlayback() {
        withPet { coordinator, view, _ in
            coordinator.advance(deltaTime: 0.4)
            let frame = view.currentFrameIndex
            coordinator.stop()
            coordinator.start()
            #expect(view.currentFrameIndex == frame)
            coordinator.advance(deltaTime: 0.2)
            #expect(view.currentFrameIndex != frame)
            coordinator.stateMachine.handleEvent(.clicked)
            coordinator.advance(deltaTime: 0.2)
            let reactionFrame = view.currentFrameIndex
            coordinator.stop()
            coordinator.start()
            #expect(view.currentFrameIndex == reactionFrame)
            coordinator.advance(deltaTime: 0.8)
            #expect(coordinator.stateMachine.state == .walking)
            #expect(abs(coordinator.stateMachine.stateTimer - 9.4) < 0.000001)
        }
    }
}
