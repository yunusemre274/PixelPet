import AppKit

/// Manages the pet panel lifecycle, asset loading, display selection, and coordination.
///
/// Uses DockGeometry for multi-monitor & orientation positioning (M2/M9),
/// SpriteView for rendering (M3), PetCoordinator for behavior (M4/M5),
/// PetAssetLoader for assets (M6).
final class PetWindowController {

    /// Display size of the pet in points (default, overridden by manifest).
    private var petDisplaySize = NSSize(width: 64, height: 64)

    private var panel: PetPanel?
    private var spriteView: SpriteView?
    private(set) var coordinator: PetCoordinator?
    let assetLoader: PetAssetLoader

    /// Current Dock info — updated on screen change notifications.
    private(set) var currentDockInfo: DockInfo?

    /// Name of the currently loaded pet.
    private(set) var currentPetName: String?

    /// Currently selected display preference: "auto" or screen name.
    private(set) var selectedDisplay: String = UserDefaults.standard.string(forKey: "SelectedDisplay") ?? "auto"

    init() {
        let assetsDir = Self.resolveAssetsDirectory()
        self.assetLoader = PetAssetLoader(assetsDirectory: assetsDir)
    }

    // MARK: - Public

    /// Shows the pet panel. Creates it if needed and starts animation.
    func showPet() {
        if panel == nil {
            createPanel()
        }

        if currentPetName == nil {
            let savedPet = UserDefaults.standard.string(forKey: "SelectedPet") ?? "Cat"
            loadPet(named: savedPet)
        }

        panel?.orderFront(nil)
        coordinator?.start()
        print("[DockPet] Pet panel shown")
    }

    /// Hides the pet panel and pauses animation.
    func hidePet() {
        coordinator?.stop()
        panel?.orderOut(nil)
        print("[DockPet] Pet panel hidden")
    }

    /// Loads and displays a specific pet type.
    func loadPet(named petName: String) {
        if panel == nil {
            createPanel()
        }

        coordinator?.loadPet(named: petName)
        currentPetName = petName

        // Update position with the new pet's display size
        if let dockInfo = currentDockInfo {
            coordinator?.updateDockInfo(dockInfo)
        }
    }

    /// Returns available pet names by scanning the assets directory.
    func availablePets() -> [String] {
        assetLoader.discoverPets()
    }

    /// Selects a display target and repositions the pet.
    func selectDisplay(_ displayIdentifier: String) {
        selectedDisplay = displayIdentifier
        UserDefaults.standard.set(displayIdentifier, forKey: "SelectedDisplay")
        repositionPet()
    }

    /// Returns available displays for the menu bar menu.
    func availableDisplays() -> [(id: String, name: String)] {
        var result: [(id: String, name: String)] = [("auto", "Auto (Follow Dock)")]
        for screen in NSScreen.screens {
            result.append((id: screen.localizedName, name: screen.localizedName))
        }
        return result
    }

    /// Manually triggers repositioning (e.g. after display change).
    func repositionPet() {
        let newDockInfo = detectDock()
        currentDockInfo = newDockInfo
        coordinator?.updateDockInfo(newDockInfo)
        print("[DockPet] Repositioned: Dock=\(newDockInfo.orientation), autoHide=\(newDockInfo.isAutoHide)")
    }

    // MARK: - Customization

    var petScale: Int {
        coordinator?.userScale ?? {
            let saved = UserDefaults.standard.integer(forKey: "PetScale")
            return saved > 0 ? saved : 2
        }()
    }

    func setPetScale(_ scale: Int) {
        coordinator?.setScale(scale)
    }

    var activityLevel: String {
        coordinator?.activityLevel.rawValue ?? UserDefaults.standard.string(forKey: "ActivityLevel") ?? "Normal"
    }

    func setActivityLevel(_ level: String) {
        if let activity = PetCoordinator.ActivityLevel(rawValue: level) {
            coordinator?.setActivityLevel(activity)
        }
    }

    var isSoundEnabled: Bool {
        get { coordinator?.isSoundEnabled ?? true }
        set { coordinator?.isSoundEnabled = newValue }
    }

    // MARK: - Panel Setup

    private func createPanel() {
        let dockInfo = detectDock()
        currentDockInfo = dockInfo

        let savedScale = petScale
        let initialPetSize = CGSize(width: 32 * savedScale, height: 32 * savedScale)

        let frame = DockGeometry.petFrame(
            dockInfo: dockInfo,
            petSize: initialPetSize
        )

        let petPanel = PetPanel(contentRect: frame)
        let view = SpriteView(frame: NSRect(origin: .zero, size: frame.size))
        petPanel.contentView = view

        // Create coordinator
        let petCoordinator = PetCoordinator(
            panel: petPanel,
            spriteView: view,
            assetLoader: assetLoader
        )
        petCoordinator.updateDockInfo(dockInfo)

        self.spriteView = view
        self.panel = petPanel
        self.coordinator = petCoordinator

        print("[DockPet] Dock: \(dockInfo.orientation), thickness: \(dockInfo.dockThickness)pt, autoHide: \(dockInfo.isAutoHide)")

        // Listen for screen geometry changes
        NotificationCenter.default.addObserver(
            self,
            selector: #selector(screenParametersChanged),
            name: NSApplication.didChangeScreenParametersNotification,
            object: nil
        )
    }

    // MARK: - Assets Directory

    static func resolveAssetsDirectory() -> URL {
        let candidates = [
            // Inside .app bundle: Contents/Resources/Assets/Pets
            Bundle.main.resourceURL?.appendingPathComponent("Assets/Pets"),
            Bundle.main.bundleURL.appendingPathComponent("Contents/Resources/Assets/Pets"),
            // Development: relative to current directory
            URL(fileURLWithPath: FileManager.default.currentDirectoryPath)
                .appendingPathComponent("Assets/Pets"),
            // Next to executable in build/
            Bundle.main.executableURL?.deletingLastPathComponent().deletingLastPathComponent()
                .appendingPathComponent("Resources/Assets/Pets"),
            Bundle.main.executableURL?.deletingLastPathComponent()
                .appendingPathComponent("Assets/Pets")
        ].compactMap { $0 }

        for candidate in candidates {
            if FileManager.default.fileExists(atPath: candidate.path) {
                print("[DockPet] Found assets directory: \(candidate.path)")
                return candidate
            }
        }

        // Fallback to project root path
        let fallback = URL(fileURLWithPath: FileManager.default.currentDirectoryPath)
            .appendingPathComponent("Assets/Pets")
        print("[DockPet] Fallback assets directory: \(fallback.path)")
        return fallback
    }

    // MARK: - Dock & Screen Detection

    private func detectDock() -> DockInfo {
        let screenGeometries = NSScreen.screens.map { screen in
            ScreenGeometry(
                id: screen.localizedName,
                name: screen.localizedName,
                frame: screen.frame,
                visibleFrame: screen.visibleFrame
            )
        }

        let targetScreen: ScreenGeometry?
        if selectedDisplay == "auto" {
            targetScreen = DockGeometry.findDockScreen(among: screenGeometries)
        } else {
            targetScreen = screenGeometries.first(where: { $0.name == selectedDisplay || $0.id == selectedDisplay })
                ?? DockGeometry.findDockScreen(among: screenGeometries)
        }

        guard let target = targetScreen else {
            return DockInfo(
                orientation: .bottom,
                screenFrame: CGRect(x: 0, y: 0, width: 1440, height: 900),
                visibleFrame: CGRect(x: 0, y: 0, width: 1440, height: 900),
                dockThickness: 0,
                isAutoHide: false
            )
        }

        return DockGeometry.detect(
            screenFrame: target.frame,
            visibleFrame: target.visibleFrame
        )
    }

    @objc private func screenParametersChanged() {
        repositionPet()
    }

    deinit {
        NotificationCenter.default.removeObserver(self)
    }
}
