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

    // MARK: - Customization & Settings

    enum ActivityLevel: String, CaseIterable {
        case calm = "Calm"
        case normal = "Normal"
        case energetic = "Energetic"
    }

    private(set) var userScale: Int = {
        let saved = UserDefaults.standard.integer(forKey: "PetScale")
        return saved > 0 ? saved : 2
    }()

    private(set) var activityLevel: ActivityLevel = {
        let saved = UserDefaults.standard.string(forKey: "ActivityLevel") ?? "Normal"
        return ActivityLevel(rawValue: saved) ?? .normal
    }()

    var isSoundEnabled: Bool {
        get {
            if UserDefaults.standard.object(forKey: "SoundEffectsEnabled") == nil {
                return true
            }
            return UserDefaults.standard.bool(forKey: "SoundEffectsEnabled")
        }
        set {
            UserDefaults.standard.set(newValue, forKey: "SoundEffectsEnabled")
        }
    }

    /// Computed display size based on base sprite size and userScale.
    var currentPetDisplaySize: CGSize {
        let baseWidth = manifest?.spriteSize.width ?? 64
        let baseHeight = manifest?.spriteSize.height ?? 64
        return CGSize(width: CGFloat(baseWidth * userScale), height: CGFloat(baseHeight * userScale))
    }

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

    /// Sets the pet display scale multiplier (1x, 2x, 3x) and updates panel geometry.
    func setScale(_ scale: Int) {
        guard scale >= 1 && scale <= 4 else { return }
        userScale = scale
        UserDefaults.standard.set(scale, forKey: "PetScale")
        let size = currentPetDisplaySize
        panel.setContentSize(size)
        if let dockInfo {
            updatePanelPosition(dockInfo: dockInfo, petSize: size)
        }
        print("[PetCoordinator] Scale set to \(scale)x (\(size.width)×\(size.height))")
    }

    /// Sets the pet activity level (calm, normal, energetic) and updates physics & timers.
    func setActivityLevel(_ level: ActivityLevel) {
        self.activityLevel = level
        UserDefaults.standard.set(level.rawValue, forKey: "ActivityLevel")
        applyActivityLevel()
        print("[PetCoordinator] Activity level set to \(level.rawValue)")
    }

    private func applyActivityLevel() {
        let baseSpeed = CGFloat(manifest?.movement?.walkSpeed ?? 30.0)
        switch activityLevel {
        case .calm:
            stateMachine.idleDurationRange = 4.0...10.0
            stateMachine.walkDurationRange = 2.0...5.0
            movement.speed = baseSpeed * 0.75
        case .normal:
            stateMachine.idleDurationRange = 2.0...6.0
            stateMachine.walkDurationRange = 3.0...8.0
            movement.speed = baseSpeed
        case .energetic:
            stateMachine.idleDurationRange = 1.0...3.0
            stateMachine.walkDurationRange = 4.0...10.0
            movement.speed = baseSpeed * 1.4
        }
    }

    /// Loads a pet by name and starts its animation and movement.
    func loadPet(named petName: String) {
        // Clear cache for previous pet to reduce memory
        if let previousPet = currentPetName, previousPet != petName {
            assetLoader.clearCache(for: previousPet)
        }

        guard let manifest = assetLoader.loadManifest(for: petName) else {
            print("[PetCoordinator] Failed to load manifest for \(petName)")
            return
        }

        self.manifest = manifest
        self.currentPetName = petName

        // Apply activity settings (movement speed and state durations)
        applyActivityLevel()

        // Resize panel to match user scale display size
        let displaySize = currentPetDisplaySize
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

        print("[PetCoordinator] Loaded pet: \(petName) (\(manifest.spriteSize.width)×\(manifest.spriteSize.height) @\(userScale)x)")
    }

    /// Updates the Dock geometry context (called when screen or display changes).
    func updateDockInfo(_ dockInfo: DockInfo) {
        let changedOrientation = (self.dockInfo?.orientation != dockInfo.orientation)
        let changedScreen = (self.dockInfo?.screenFrame != dockInfo.screenFrame)
        let isFirst = (self.dockInfo == nil)
        self.dockInfo = dockInfo

        let petSize = currentPetDisplaySize
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
        // Start throttled (5-10Hz) when idle to save CPU & battery
        link.preferredFrameRateRange = CAFrameRateRange(minimum: 5, maximum: 10, preferred: 5)
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

        // Sprite click → state machine event + audio feedback
        spriteView.onClicked = { [weak self] in
            guard let self else { return }
            print("[PetCoordinator] Pet was clicked!")
            if self.isSoundEnabled {
                NSSound(named: "Pop")?.play()
            }
            self.stateMachine.handleEvent(.clicked)
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
            let petSize = currentPetDisplaySize
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
            // Ramp up to high refresh rate (60-120Hz) for fluid animation
            displayLink?.preferredFrameRateRange = CAFrameRateRange(minimum: 60, maximum: 120, preferred: 60)
            movement.startMoving()
        case .idle, .sleeping, .interaction, .specialAnimation:
            // Throttle to 5-10Hz when stationary to save energy
            displayLink?.preferredFrameRateRange = CAFrameRateRange(minimum: 5, maximum: 10, preferred: 5)
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
        case .specialAnimation: return "special"
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
