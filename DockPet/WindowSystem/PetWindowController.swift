import AppKit

/// Manages the pet panel lifecycle, asset loading, and coordination.
///
/// Uses DockGeometry for positioning (M2), SpriteView for rendering (M3),
/// PetCoordinator for behavior (M4/M5), PetAssetLoader for assets (M6).
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

    // MARK: - Panel Setup

    private func createPanel() {
        let dockInfo = detectDock()
        currentDockInfo = dockInfo

        let frame = DockGeometry.petFrame(
            dockInfo: dockInfo,
            petSize: CGSize(width: petDisplaySize.width, height: petDisplaySize.height)
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

        print("[DockPet] Dock: \(dockInfo.orientation), thickness: \(dockInfo.dockThickness)pt")

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

    // MARK: - Dock Detection

    private func detectDock() -> DockInfo {
        guard let screen = NSScreen.main ?? NSScreen.screens.first else {
            return DockInfo(
                orientation: .bottom,
                screenFrame: CGRect(x: 0, y: 0, width: 1440, height: 900),
                visibleFrame: CGRect(x: 0, y: 0, width: 1440, height: 900),
                dockThickness: 0
            )
        }

        return DockGeometry.detect(
            screenFrame: screen.frame,
            visibleFrame: screen.visibleFrame
        )
    }

    @objc private func screenParametersChanged() {
        let newDockInfo = detectDock()
        currentDockInfo = newDockInfo
        coordinator?.updateDockInfo(newDockInfo)
        print("[DockPet] Repositioned: Dock=\(newDockInfo.orientation)")
    }

    deinit {
        NotificationCenter.default.removeObserver(self)
    }
}
