import AppKit

/// Coordinates the pet engine (state machine + movement), sprite rendering,
/// and asset loading into a running pet instance.
///
/// PetCoordinator is the integration point between pure domain logic
/// (PetStateMachine, PetMovement) and AppKit rendering (SpriteView, PetPanel).
/// It drives the update loop via a display-link timer.
final class PetCoordinator {

    // MARK: - Domain

    let stateMachine: PetStateMachine
    let movement: PetMovement
    private let assetLoader: PetAssetLoader

    // MARK: - Rendering

    private let spriteView: SpriteView
    private let panel: PetPanel

    // MARK: - State

    private(set) var manifest: PetManifest?
    private(set) var currentPetName: String?
    private var displayLink: CADisplayLink?
    private var lastTimestamp: CFTimeInterval = 0
    private var dockInfo: DockInfo?

    init(panel: PetPanel, spriteView: SpriteView, assetLoader: PetAssetLoader) {
        self.panel = panel
        self.spriteView = spriteView
        self.assetLoader = assetLoader
        self.stateMachine = PetStateMachine()
        self.movement = PetMovement()

        setupCallbacks()
    }

    // MARK: - Public

    /// Loads a pet by name and starts its animation and movement.
    func loadPet(named petName: String) {
        guard let manifest = assetLoader.loadManifest(for: petName) else {
            print("[PetCoordinator] Failed to load manifest for \(petName)")
            return
        }

        self.manifest = manifest
        self.currentPetName = petName

        // Update movement speed from manifest
        movement.speed = CGFloat(manifest.movement?.walkSpeed ?? 30.0)

        // Resize panel to match manifest display size
        let displaySize = manifest.displaySize
        panel.setContentSize(displaySize)

        // Position pet initially if dock info is known
        if let dockInfo {
            let baseFrame = DockGeometry.petFrame(dockInfo: dockInfo, petSize: displaySize)
            let initialPos = (dockInfo.orientation == .bottom) ? baseFrame.origin.x : baseFrame.origin.y
            if movement.positionX == 0 {
                movement.setPosition(initialPos)
            }
            updatePanelPosition(dockInfo: dockInfo, petSize: displaySize)
        }

        // Load and set initial animation
        switchAnimation(to: stateMachine.state)

        print("[PetCoordinator] Loaded pet: \(petName) (\(manifest.spriteSize.width)×\(manifest.spriteSize.height) @\(manifest.scale)x)")
    }

    /// Updates the Dock geometry context (called when screen or display changes).
    func updateDockInfo(_ dockInfo: DockInfo) {
        let changedOrientation = (self.dockInfo?.orientation != dockInfo.orientation)
        let changedScreen = (self.dockInfo?.screenFrame != dockInfo.screenFrame)
        let isFirst = (self.dockInfo == nil)
        self.dockInfo = dockInfo

        let petSize = manifest?.displaySize ?? CGSize(width: 64, height: 64)
        if isFirst || changedOrientation || changedScreen || movement.positionX == 0 {
            let baseFrame = DockGeometry.petFrame(dockInfo: dockInfo, petSize: petSize)
            let initialPos = (dockInfo.orientation == .bottom) ? baseFrame.origin.x : baseFrame.origin.y
            movement.setPosition(initialPos)
        }
        updatePanelPosition(dockInfo: dockInfo, petSize: petSize)
    }

    /// Starts the update loop.
    func start() {
        guard displayLink == nil else { return }

        let link = spriteView.displayLink(target: self, selector: #selector(tick(_:)))
        link.add(to: .main, forMode: .common)
        self.displayLink = link

        print("[PetCoordinator] Update loop started")
    }

    /// Stops the update loop.
    func stop() {
        displayLink?.invalidate()
        displayLink = nil
        spriteView.stopAnimation()
        print("[PetCoordinator] Update loop stopped")
    }

    // MARK: - Setup

    private func setupCallbacks() {
        // State changes → switch animation + movement
        stateMachine.onStateChanged = { [weak self] oldState, newState in
            self?.handleStateChange(from: oldState, to: newState)
        }

        // Sprite click → state machine event
        spriteView.onClicked = { [weak self] in
            print("[PetCoordinator] Pet was clicked!")
            self?.stateMachine.handleEvent(.clicked)
        }
    }

    // MARK: - Update Loop

    @objc private func tick(_ link: CADisplayLink) {
        let timestamp = link.timestamp
        let deltaTime = lastTimestamp > 0 ? timestamp - lastTimestamp : 1.0 / 60.0
        lastTimestamp = timestamp

        // Cap deltaTime to avoid jumps after app sleep
        let dt = min(deltaTime, 0.1)

        // Update state machine
        stateMachine.update(deltaTime: dt)

        // Only update movement & window frame when moving to save CPU/battery
        if movement.isMoving, let dockInfo {
            let petSize = manifest?.displaySize ?? CGSize(width: 64, height: 64)
            let bounds = DockGeometry.movementBounds(dockInfo: dockInfo, petSize: petSize)

            let hitBoundary = movement.update(deltaTime: dt, bounds: bounds)
            if hitBoundary {
                stateMachine.handleEvent(.hitBoundary)
            }

            // Update panel position
            updatePanelPosition(dockInfo: dockInfo, petSize: petSize)
        }

        // Update sprite direction based on movement direction and Dock orientation
        switch dockInfo?.orientation ?? .bottom {
        case .bottom, .left:
            spriteView.isFacingLeft = (movement.direction == .left)
        case .right:
            spriteView.isFacingLeft = (movement.direction == .right)
        }
    }

    // MARK: - State Handling

    private func handleStateChange(from oldState: PetState, to newState: PetState) {
        print("[PetCoordinator] State: \(oldState.rawValue) → \(newState.rawValue)")

        switch newState {
        case .walking:
            movement.startMoving()
        case .idle, .sleeping, .interaction:
            movement.stopMoving()
        }

        switchAnimation(to: newState)
    }

    private func switchAnimation(to state: PetState) {
        guard let petName = currentPetName else { return }

        let animationName = animationKey(for: state)

        guard let frames = assetLoader.loadFrames(for: petName, animation: animationName) else {
            print("[PetCoordinator] No frames for \(animationName)")
            return
        }

        let config = manifest?.animations[animationName]
        let fps = config?.fps ?? 4.0
        let loop = config?.loop ?? true

        spriteView.setAnimation(frames: frames, fps: fps, loop: loop)
    }

    /// Maps PetState to animation folder name.
    private func animationKey(for state: PetState) -> String {
        switch state {
        case .idle: return "idle"
        case .walking: return "walk"
        case .sleeping: return "sleep"
        case .interaction: return "interaction"
        }
    }

    // MARK: - Positioning

    private func updatePanelPosition(dockInfo: DockInfo, petSize: CGSize) {
        var frame = DockGeometry.petFrame(dockInfo: dockInfo, petSize: petSize)

        switch dockInfo.orientation {
        case .bottom:
            frame.origin.x = movement.positionX
        case .left, .right:
            frame.origin.y = movement.positionX
        }

        panel.setFrame(frame, display: true)
    }

    deinit {
        stop()
    }
}
