import AppKit

/// Manages application lifecycle and menu bar status item.
/// Owns the PetWindowController and provides menu bar controls for Show/Hide,
/// Pet Selection, Multi-Monitor Display Selection, and Quit.
class AppDelegate: NSObject, NSApplicationDelegate {

    private var statusItem: NSStatusItem?
    private var petWindowController: PetWindowController?
    private var petMenuItems: [NSMenuItem] = []
    private var displayMenuItems: [NSMenuItem] = []
    private var displaysSubmenu: NSMenu?

    func applicationDidFinishLaunching(_ notification: Notification) {
        print("[DockPet] Application started")

        setupPetWindow()
        setupMenuBar()

        // Listen for screen changes to update display menu
        NotificationCenter.default.addObserver(
            self,
            selector: #selector(screensChanged),
            name: NSApplication.didChangeScreenParametersNotification,
            object: nil
        )
    }

    func applicationWillTerminate(_ notification: Notification) {
        print("[DockPet] Application terminating")
        NotificationCenter.default.removeObserver(self)
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

        // Displays Submenu (M9)
        let dispSubmenu = NSMenu()
        self.displaysSubmenu = dispSubmenu
        populateDisplayMenu(dispSubmenu)

        let displaySelectMenuItem = NSMenuItem(title: "Display", action: nil, keyEquivalent: "")
        displaySelectMenuItem.submenu = dispSubmenu
        menu.addItem(displaySelectMenuItem)

        menu.addItem(NSMenuItem.separator())
        menu.addItem(NSMenuItem(title: "Quit DockPet", action: #selector(quitApp), keyEquivalent: "q"))

        statusItem?.menu = menu
    }

    private func populateDisplayMenu(_ menu: NSMenu) {
        menu.removeAllItems()
        displayMenuItems.removeAll()

        let currentDisplay = petWindowController?.selectedDisplay ?? "auto"
        let displays = petWindowController?.availableDisplays() ?? [("auto", "Auto (Follow Dock)")]

        for (id, name) in displays {
            let item = NSMenuItem(title: name, action: #selector(selectDisplay(_:)), keyEquivalent: "")
            item.representedObject = id
            item.state = (id == currentDisplay) ? .on : .off
            menu.addItem(item)
            displayMenuItems.append(item)
        }
    }

    private func updatePetMenuCheckmarks(selectedPet: String) {
        for item in petMenuItems {
            if let petName = item.representedObject as? String {
                item.state = (petName == selectedPet) ? .on : .off
            }
        }
    }

    private func updateDisplayMenuCheckmarks(selectedDisplay: String) {
        for item in displayMenuItems {
            if let displayId = item.representedObject as? String {
                item.state = (displayId == selectedDisplay) ? .on : .off
            }
        }
    }

    @objc private func screensChanged() {
        if let menu = displaysSubmenu {
            populateDisplayMenu(menu)
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

    @objc private func selectDisplay(_ sender: NSMenuItem) {
        guard let displayId = sender.representedObject as? String else { return }
        print("[DockPet] Selected display: \(displayId)")

        petWindowController?.selectDisplay(displayId)
        updateDisplayMenuCheckmarks(selectedDisplay: displayId)
    }

    @objc private func quitApp() {
        NSApplication.shared.terminate(nil)
    }
}
