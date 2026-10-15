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

    @Test("Initial state is walking")
    func initialState() {
        let sm = PetStateMachine()
        #expect(sm.state == .walking)
        #expect(sm.stateTimer == 10.0)
    }

    @Test("Walking transitions to specialAnimation on timerExpired after 10s")
    func walkingToSkillOnTimer() {
        let sm = PetStateMachine()
        #expect(sm.state == .walking)

        sm.handleEvent(.timerExpired)
        #expect(sm.state == .specialAnimation)
        #expect(sm.stateTimer == 5.0)
    }

    @Test("Walking continues without stopping on boundary hit")
    func walkingContinuesOnBoundary() {
        let sm = PetStateMachine()
        #expect(sm.state == .walking)

        sm.handleEvent(.hitBoundary)
        #expect(sm.state == .walking) // Stays in walking state!
    }

    @Test("SpecialAnimation transitions to sleeping on timerExpired after 5s")
    func skillToSleeping() {
        let sm = PetStateMachine(initialState: .specialAnimation)
        #expect(sm.state == .specialAnimation)

        sm.handleEvent(.timerExpired)
        #expect(sm.state == .sleeping)
        #expect(sm.stateTimer == 10.0)
    }

    @Test("Sleeping transitions to walking on timerExpired after 10s")
    func sleepingToWalking() {
        let sm = PetStateMachine(initialState: .sleeping)
        #expect(sm.state == .sleeping)

        sm.handleEvent(.timerExpired)
        #expect(sm.state == .walking)
        #expect(sm.stateTimer == 10.0)
    }

    @Test("Complete 10s walk -> 5s skill -> 10s sleep cycle repeats")
    func fullCycleLoop() {
        let sm = PetStateMachine()
        #expect(sm.state == .walking)

        // 10 seconds of walking
        sm.update(deltaTime: 10.1)
        #expect(sm.state == .specialAnimation)

        // 5 seconds of skill
        sm.update(deltaTime: 5.1)
        #expect(sm.state == .sleeping)

        // 10 seconds of sleep
        sm.update(deltaTime: 10.1)
        #expect(sm.state == .walking)
    }

    @Test("Click transitions to interaction and resumes cycle")
    func clickInteraction() {
        let sm = PetStateMachine()
        #expect(sm.state == .walking)

        sm.handleEvent(.clicked)
        #expect(sm.state == .interaction)

        sm.handleEvent(.animationComplete)
        #expect(sm.state == .walking)
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
        movement.setDirection(.right)

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

        movement.setDirection(.right)

        let hitBoundary = movement.update(deltaTime: 1.0, bounds: bounds)

        #expect(hitBoundary == true)
        #expect(movement.positionX == 460)
        #expect(movement.direction == .left)
    }

    @Test("Reverses direction at lower boundary")
    func reversesAtLowerBoundary() {
        let movement = PetMovement()
        movement.setPosition(20)
        movement.speed = 50.0
        movement.startMoving()

        movement.setDirection(.left)

        let hitBoundary = movement.update(deltaTime: 1.0, bounds: bounds)

        #expect(hitBoundary == true)
        #expect(movement.positionX == 50)
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
        #expect(coordinator.currentPetDisplaySize == CGSize(width: 64, height: 64))

        coordinator.setScale(2)
        #expect(coordinator.userScale == 2)
        #expect(coordinator.currentPetDisplaySize == CGSize(width: 128, height: 128))

        coordinator.setScale(3)
        #expect(coordinator.userScale == 3)
        #expect(coordinator.currentPetDisplaySize == CGSize(width: 192, height: 192))
    }

    @Test("Activity level updates state durations and speed")
    func activityLevelChangesPhysics() {
        let panel = PetPanel(contentRect: NSRect(x: 0, y: 0, width: 64, height: 64))
        let view = SpriteView(frame: NSRect(x: 0, y: 0, width: 64, height: 64))
        let loader = PetAssetLoader(assetsDirectory: assetsDir)
        let coordinator = PetCoordinator(panel: panel, spriteView: view, assetLoader: loader)
        coordinator.loadPet(named: "Cat")

        let baseSpeed = CGFloat(coordinator.manifest?.movement?.walkSpeed ?? 110.0)

        coordinator.setActivityLevel(.calm)
        #expect(coordinator.movement.speed == baseSpeed * 0.75)

        coordinator.setActivityLevel(.energetic)
        #expect(coordinator.movement.speed == baseSpeed * 1.35)

        coordinator.setActivityLevel(.normal)
        #expect(coordinator.movement.speed == baseSpeed)
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
