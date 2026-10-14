import Testing
import Foundation
import CoreGraphics
@testable import DockPet

// MARK: - Mock RNG for Deterministic Testing

struct SeededRNG: RandomNumberGenerator {
    private var state: UInt64

    init(seed: UInt64 = 42) {
        self.state = seed
    }

    mutating func next() -> UInt64 {
        state = state &* 6364136223846793005 &+ 1442695040888963407
        return state
    }
}

// MARK: - Pet Manifest Tests

@Suite("PetManifest Tests")
struct PetManifestTests {

    @Test("Decodes valid JSON manifest")
    func decodeValidManifest() throws {
        let json = """
        {
          "name": "Cat",
          "version": 1,
          "spriteSize": { "width": 32, "height": 32 },
          "scale": 2,
          "anchorY": 0,
          "animations": {
            "idle": { "fps": 4, "loop": true },
            "walk": { "fps": 6, "loop": true },
            "sleep": { "fps": 2, "loop": true }
          },
          "movement": {
            "walkSpeed": 30.0,
            "runSpeed": 60.0
          }
        }
        """

        let data = try #require(json.data(using: .utf8))
        let manifest = try JSONDecoder().decode(PetManifest.self, from: data)

        #expect(manifest.name == "Cat")
        #expect(manifest.version == 1)
        #expect(manifest.spriteSize.width == 32)
        #expect(manifest.spriteSize.height == 32)
        #expect(manifest.scale == 2)
        #expect(manifest.resolvedAnchorY == 0)
        #expect(manifest.displaySize == CGSize(width: 64, height: 64))
        #expect(manifest.animations["idle"]?.fps == 4)
        #expect(manifest.animations["walk"]?.loop == true)
        #expect(manifest.movement?.walkSpeed == 30.0)
    }

    @Test("Uses default anchorY when omitted")
    func defaultAnchorY() throws {
        let json = """
        {
          "name": "Dog",
          "version": 1,
          "spriteSize": { "width": 48, "height": 48 },
          "scale": 3,
          "animations": {
            "idle": { "fps": 5, "loop": true }
          }
        }
        """

        let data = try #require(json.data(using: .utf8))
        let manifest = try JSONDecoder().decode(PetManifest.self, from: data)

        #expect(manifest.anchorY == nil)
        #expect(manifest.resolvedAnchorY == 0)
        #expect(manifest.displaySize == CGSize(width: 144, height: 144))
    }
}

// MARK: - Pet State Machine Tests

@Suite("PetStateMachine Tests")
struct PetStateMachineTests {

    @Test("Initial state is idle")
    func initialState() {
        let rng = SeededRNG(seed: 123)
        let sm = PetStateMachine(rng: rng)
        #expect(sm.state == .idle)
    }

    @Test("Idle transitions to walking on timerExpired")
    func idleToWalking() {
        let rng = SeededRNG(seed: 123)
        let sm = PetStateMachine(rng: rng)

        var transitioned = false
        sm.onStateChanged = { oldState, newState in
            if oldState == .idle && newState == .walking {
                transitioned = true
            }
        }

        sm.handleEvent(.timerExpired)

        #expect(sm.state == .walking)
        #expect(transitioned)
    }

    @Test("Walking transitions to idle on timerExpired")
    func walkingToIdleOnTimer() {
        let rng = SeededRNG(seed: 123)
        let sm = PetStateMachine(rng: rng)

        sm.handleEvent(.timerExpired) // idle -> walking
        #expect(sm.state == .walking)

        sm.handleEvent(.timerExpired) // walking -> idle
        #expect(sm.state == .idle)
    }

    @Test("Walking transitions to idle on boundary hit")
    func walkingToIdleOnBoundary() {
        let rng = SeededRNG(seed: 123)
        let sm = PetStateMachine(rng: rng)

        sm.handleEvent(.timerExpired) // idle -> walking
        #expect(sm.state == .walking)

        sm.handleEvent(.hitBoundary) // walking -> idle
        #expect(sm.state == .idle)
    }

    @Test("Click transitions to interaction")
    func clickInteraction() {
        let rng = SeededRNG(seed: 123)
        let sm = PetStateMachine(rng: rng)

        sm.handleEvent(.clicked)
        #expect(sm.state == .interaction)

        sm.handleEvent(.animationComplete)
        #expect(sm.state == .idle)
    }

    @Test("Update advances state timer and triggers transition")
    func updateTrigger() {
        let rng = SeededRNG(seed: 123)
        let sm = PetStateMachine(rng: rng)
        sm.idleDurationRange = 1.0...1.0 // fixed 1.0s timer

        // Re-init with fixed range
        let smFixed = PetStateMachine(rng: rng)
        smFixed.idleDurationRange = 1.0...1.0

        // Advance by 10 seconds to ensure timer fires
        smFixed.update(deltaTime: 10.0)
        #expect(smFixed.state == .walking)
    }
}

// MARK: - Pet Movement Tests

@Suite("PetMovement Tests")
struct PetMovementTests {

    let bounds: ClosedRange<CGFloat> = 10...500

    @Test("Initial state is stopped at origin")
    func initialMovementState() {
        let movement = PetMovement()
        #expect(movement.positionX == 0)
        #expect(movement.isMoving == false)
    }

    @Test("setPosition updates horizontal position")
    func setPosition() {
        let movement = PetMovement()
        movement.setPosition(150)
        #expect(movement.positionX == 150)
    }

    @Test("Movement stays stationary when stopped")
    func stationaryWhenStopped() {
        let movement = PetMovement()
        movement.setPosition(100)
        movement.speed = 50.0

        let hitBoundary = movement.update(deltaTime: 1.0, bounds: bounds)

        #expect(movement.positionX == 100)
        #expect(hitBoundary == false)
    }

    @Test("Movement updates position when moving right")
    func movesRight() {
        let movement = PetMovement()
        movement.setPosition(100)
        movement.speed = 50.0
        movement.startMoving()

        // Force direction right
        while movement.direction != .right {
            movement.startMoving()
        }

        let hitBoundary = movement.update(deltaTime: 1.0, bounds: bounds)

        #expect(movement.positionX == 150)
        #expect(hitBoundary == false)
    }

    @Test("Reverses direction at upper boundary")
    func reversesAtUpperBoundary() {
        let movement = PetMovement()
        movement.setPosition(490)
        movement.speed = 50.0
        movement.startMoving()

        while movement.direction != .right {
            movement.startMoving()
        }

        let hitBoundary = movement.update(deltaTime: 1.0, bounds: bounds)

        #expect(hitBoundary == true)
        #expect(movement.positionX == 500)
        #expect(movement.direction == .left)
    }

    @Test("Reverses direction at lower boundary")
    func reversesAtLowerBoundary() {
        let movement = PetMovement()
        movement.setPosition(20)
        movement.speed = 50.0
        movement.startMoving()

        while movement.direction != .left {
            movement.startMoving()
        }

        let hitBoundary = movement.update(deltaTime: 1.0, bounds: bounds)

        #expect(hitBoundary == true)
        #expect(movement.positionX == 10)
        #expect(movement.direction == .right)
    }
}

// MARK: - Pet Customization Tests

@Suite("PetCustomization Tests")
@MainActor
struct PetCustomizationTests {

    let assetsDir = URL(fileURLWithPath: FileManager.default.currentDirectoryPath).appendingPathComponent("Assets/Pets")

    @Test("PetCoordinator scale updates display size")
    func scaleChangesDisplaySize() {
        let panel = PetPanel(contentRect: NSRect(x: 0, y: 0, width: 64, height: 64))
        let view = SpriteView(frame: NSRect(x: 0, y: 0, width: 64, height: 64))
        let loader = PetAssetLoader(assetsDirectory: assetsDir)
        let coordinator = PetCoordinator(panel: panel, spriteView: view, assetLoader: loader)
        coordinator.loadPet(named: "Cat")

        coordinator.setScale(1)
        #expect(coordinator.userScale == 1)
        #expect(coordinator.currentPetDisplaySize == CGSize(width: 32, height: 32))

        coordinator.setScale(2)
        #expect(coordinator.userScale == 2)
        #expect(coordinator.currentPetDisplaySize == CGSize(width: 64, height: 64))

        coordinator.setScale(3)
        #expect(coordinator.userScale == 3)
        #expect(coordinator.currentPetDisplaySize == CGSize(width: 96, height: 96))
    }

    @Test("Activity level updates state durations and speed")
    func activityLevelChangesPhysics() {
        let panel = PetPanel(contentRect: NSRect(x: 0, y: 0, width: 64, height: 64))
        let view = SpriteView(frame: NSRect(x: 0, y: 0, width: 64, height: 64))
        let loader = PetAssetLoader(assetsDirectory: assetsDir)
        let coordinator = PetCoordinator(panel: panel, spriteView: view, assetLoader: loader)
        coordinator.loadPet(named: "Cat")

        coordinator.setActivityLevel(.calm)
        #expect(coordinator.stateMachine.idleDurationRange == 4.0...10.0)
        #expect(coordinator.stateMachine.walkDurationRange == 2.0...5.0)

        coordinator.setActivityLevel(.energetic)
        #expect(coordinator.stateMachine.idleDurationRange == 1.0...3.0)
        #expect(coordinator.stateMachine.walkDurationRange == 4.0...10.0)

        coordinator.setActivityLevel(.normal)
        #expect(coordinator.stateMachine.idleDurationRange == 2.0...6.0)
        #expect(coordinator.stateMachine.walkDurationRange == 3.0...8.0)
    }

    @Test("Sound setting toggle can be enabled and disabled")
    func soundSettingToggle() {
        let panel = PetPanel(contentRect: NSRect(x: 0, y: 0, width: 64, height: 64))
        let view = SpriteView(frame: NSRect(x: 0, y: 0, width: 64, height: 64))
        let loader = PetAssetLoader(assetsDirectory: assetsDir)
        let coordinator = PetCoordinator(panel: panel, spriteView: view, assetLoader: loader)

        coordinator.isSoundEnabled = true
        #expect(coordinator.isSoundEnabled == true)

        coordinator.isSoundEnabled = false
        #expect(coordinator.isSoundEnabled == false)

        coordinator.isSoundEnabled = true
        #expect(coordinator.isSoundEnabled == true)
    }
}
