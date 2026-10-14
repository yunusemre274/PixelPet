import AppKit

/// Manages application lifecycle and menu bar status item.
/// Owns the PetWindowController and provides menu bar controls for Show/Hide,
/// Pet Selection, and Quit.
class AppDelegate: NSObject, NSApplicationDelegate {

    private var statusItem: NSStatusItem?
    private var petWindowController: PetWindowController?
    private var petMenuItems: [NSMenuItem] = []

    func applicationDidFinishLaunching(_ notification: Notification) {
        print("[DockPet] Application started")

        setupPetWindow()
        setupMenuBar()
    }

    func applicationWillTerminate(_ notification: Notification) {
        print("[DockPet] Application terminating")
    }

    // MARK: - Menu Bar

    private func setupMenuBar() {
        statusItem = NSStatusBar.system.statusItem(withLength: NSStatusItem.squareLength)

        if let button = statusItem?.button {
            button.title = "🐾"
        }

        let menu = NSMenu()

        menu.addItem(NSMenuItem(title: "Show Pet", action: #selector(showPet), keyEquivalent: ""))
        menu.addItem(NSMenuItem(title: "Hide Pet", action: #selector(hidePet), keyEquivalent: ""))
        menu.addItem(NSMenuItem.separator())

        // Pet Selection Submenu
        let petsSubmenu = NSMenu()
        let availablePets = petWindowController?.availablePets() ?? []
        let currentPet = petWindowController?.currentPetName ?? UserDefaults.standard.string(forKey: "SelectedPet") ?? "Cat"

        petMenuItems.removeAll()
        for petName in availablePets {
            let item = NSMenuItem(title: petName, action: #selector(selectPet(_:)), keyEquivalent: "")
            item.representedObject = petName
            item.state = (petName == currentPet) ? .on : .off
            petsSubmenu.addItem(item)
            petMenuItems.append(item)
        }

        let petSelectMenuItem = NSMenuItem(title: "Select Pet", action: nil, keyEquivalent: "")
        petSelectMenuItem.submenu = petsSubmenu
        menu.addItem(petSelectMenuItem)

        menu.addItem(NSMenuItem.separator())
        menu.addItem(NSMenuItem(title: "Quit DockPet", action: #selector(quitApp), keyEquivalent: "q"))

        statusItem?.menu = menu
    }

    private func updatePetMenuCheckmarks(selectedPet: String) {
        for item in petMenuItems {
            if let petName = item.representedObject as? String {
                item.state = (petName == selectedPet) ? .on : .off
            }
        }
    }

    // MARK: - Pet Window

    private func setupPetWindow() {
        let controller = PetWindowController()
        let savedPet = UserDefaults.standard.string(forKey: "SelectedPet") ?? "Cat"
        controller.loadPet(named: savedPet)
        controller.showPet()
        self.petWindowController = controller
    }

    // MARK: - Actions

    @objc private func showPet() {
        petWindowController?.showPet()
    }

    @objc private func hidePet() {
        petWindowController?.hidePet()
    }

    @objc private func selectPet(_ sender: NSMenuItem) {
        guard let petName = sender.representedObject as? String else { return }
        print("[DockPet] Selected pet: \(petName)")

        petWindowController?.loadPet(named: petName)
        UserDefaults.standard.set(petName, forKey: "SelectedPet")
        updatePetMenuCheckmarks(selectedPet: petName)
    }

    @objc private func quitApp() {
        NSApplication.shared.terminate(nil)
    }
}
