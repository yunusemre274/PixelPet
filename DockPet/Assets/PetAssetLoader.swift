import AppKit

/// Loads pet assets from disk following the asset pipeline conventions.
///
/// Scans `Assets/Pets/` for pet folders, each containing a `manifest.json`
/// and animation frame PNGs organized in subfolders.
///
/// See docs/ASSET_PIPELINE.md for the full specification.
final class PetAssetLoader {

    /// Known animation state names in fallback priority order.
    /// Used when a requested animation is missing.
    private static let fallbackChain: [String: [String]] = [
        "walk": ["idle"],
        "run": ["walk", "idle"],
        "sleep": ["idle"],
        "jump": ["idle"],
        "interaction": ["idle"]
    ]

    /// The base directory containing pet asset folders.
    private let assetsDirectory: URL

    /// Cache of loaded frames per pet+animation.
    private var frameCache: [String: [String: [NSImage]]] = [:]

    init(assetsDirectory: URL) {
        self.assetsDirectory = assetsDirectory
    }

    // MARK: - Discovery

    /// Discovers all available pet types by scanning the assets directory.
    /// Returns pet folder names that contain a valid `manifest.json`.
    func discoverPets() -> [String] {
        guard let contents = try? FileManager.default.contentsOfDirectory(
            at: assetsDirectory,
            includingPropertiesForKeys: [.isDirectoryKey],
            options: [.skipsHiddenFiles]
        ) else {
            print("[AssetLoader] Cannot read assets directory: \(assetsDirectory.path)")
            return []
        }

        return contents
            .filter { url in
                var isDir: ObjCBool = false
                return FileManager.default.fileExists(atPath: url.path, isDirectory: &isDir)
                    && isDir.boolValue
                    && FileManager.default.fileExists(atPath: url.appendingPathComponent("manifest.json").path)
            }
            .map(\.lastPathComponent)
            .sorted()
    }

    // MARK: - Manifest Loading

    /// Loads and decodes the manifest for a specific pet type.
    func loadManifest(for petName: String) -> PetManifest? {
        let manifestURL = assetsDirectory
            .appendingPathComponent(petName)
            .appendingPathComponent("manifest.json")

        guard let data = try? Data(contentsOf: manifestURL) else {
            print("[AssetLoader] Cannot read manifest: \(manifestURL.path)")
            return nil
        }

        do {
            return try JSONDecoder().decode(PetManifest.self, from: data)
        } catch {
            print("[AssetLoader] Invalid manifest for \(petName): \(error)")
            return nil
        }
    }

    // MARK: - Frame Loading

    /// Loads animation frames for a specific pet and animation state.
    /// Applies fallback chain if the requested animation is missing.
    ///
    /// Returns an array of NSImage frames, or nil if no frames are available
    /// (including after exhausting fallbacks).
    func loadFrames(for petName: String, animation: String) -> [NSImage]? {
        // Check cache first
        if let cached = frameCache[petName]?[animation] {
            return cached
        }

        // Try the requested animation
        if let frames = loadFramesFromDisk(petName: petName, animation: animation), !frames.isEmpty {
            cacheFrames(frames, petName: petName, animation: animation)
            return frames
        }

        // Try fallback chain
        if let fallbacks = Self.fallbackChain[animation] {
            for fallback in fallbacks {
                if let frames = loadFramesFromDisk(petName: petName, animation: fallback), !frames.isEmpty {
                    cacheFrames(frames, petName: petName, animation: animation)
                    return frames
                }
            }
        }

        print("[AssetLoader] No frames found for \(petName)/\(animation) (including fallbacks)")
        return nil
    }

    // MARK: - Private

    private func loadFramesFromDisk(petName: String, animation: String) -> [NSImage]? {
        let animDir = assetsDirectory
            .appendingPathComponent(petName)
            .appendingPathComponent(animation)

        guard FileManager.default.fileExists(atPath: animDir.path) else { return nil }

        guard let files = try? FileManager.default.contentsOfDirectory(
            at: animDir,
            includingPropertiesForKeys: nil,
            options: [.skipsHiddenFiles]
        ) else { return nil }

        // Filter for frame_XX.png files and sort by name
        let framePNGs = files
            .filter { $0.pathExtension.lowercased() == "png" && $0.lastPathComponent.hasPrefix("frame_") }
            .sorted { $0.lastPathComponent < $1.lastPathComponent }

        let images = framePNGs.compactMap { url -> NSImage? in
            guard let image = NSImage(contentsOf: url) else {
                print("[AssetLoader] Failed to load image: \(url.lastPathComponent)")
                return nil
            }
            // Mark the image as template-free to preserve exact pixel colors
            image.isTemplate = false
            return image
        }

        return images.isEmpty ? nil : images
    }

    private func cacheFrames(_ frames: [NSImage], petName: String, animation: String) {
        if frameCache[petName] == nil {
            frameCache[petName] = [:]
        }
        frameCache[petName]?[animation] = frames
    }

    /// Clears the frame cache for all or a specific pet.
    func clearCache(for petName: String? = nil) {
        if let petName {
            frameCache.removeValue(forKey: petName)
        } else {
            frameCache.removeAll()
        }
    }
}
