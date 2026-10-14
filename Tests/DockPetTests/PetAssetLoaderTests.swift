import Testing
import Foundation
@testable import DockPet

@Suite("PetAssetLoader Tests")
struct PetAssetLoaderTests {

    let assetsDir = URL(fileURLWithPath: FileManager.default.currentDirectoryPath).appendingPathComponent("Assets/Pets")

    @Test("Discovers all 7 pets in Assets directory")
    func discoverPets() {
        let loader = PetAssetLoader(assetsDirectory: assetsDir)
        let pets = loader.discoverPets()

        #expect(pets.contains("Cat"))
        #expect(pets.contains("Dog"))
        #expect(pets.contains("Parrot"))
        #expect(pets.contains("Rabbit"))
        #expect(pets.contains("Turtle"))
        #expect(pets.contains("Dinosaur"))
        #expect(pets.contains("Hamster"))
        #expect(pets.count >= 7)
    }

    @Test("Loads valid manifest for Cat")
    func loadCatManifest() {
        let loader = PetAssetLoader(assetsDirectory: assetsDir)
        let manifest = loader.loadManifest(for: "Cat")

        #expect(manifest != nil)
        #expect(manifest?.name == "Cat")
        #expect(manifest?.spriteSize.width == 32)
        #expect(manifest?.spriteSize.height == 32)
        #expect(manifest?.animations["idle"] != nil)
        #expect(manifest?.animations["walk"] != nil)
    }

    @Test("Loads frames for idle animation")
    func loadIdleFrames() {
        let loader = PetAssetLoader(assetsDirectory: assetsDir)
        let frames = loader.loadFrames(for: "Cat", animation: "idle")

        #expect(frames != nil)
        #expect(frames?.count == 3)
    }

    @Test("Loads frames for walk animation")
    func loadWalkFrames() {
        let loader = PetAssetLoader(assetsDirectory: assetsDir)
        let frames = loader.loadFrames(for: "Cat", animation: "walk")

        #expect(frames != nil)
        #expect(frames?.count == 4)
    }

    @Test("Falls back to idle for missing animation state")
    func fallbackMissingAnimation() {
        let loader = PetAssetLoader(assetsDirectory: assetsDir)
        // 'interaction' animation folder does not exist for Cat, should fall back to 'idle'
        let frames = loader.loadFrames(for: "Cat", animation: "interaction")

        #expect(frames != nil)
        #expect(frames?.count == 3) // idle has 3 frames
    }

    @Test("Frame caching returns cached instances")
    func frameCaching() {
        let loader = PetAssetLoader(assetsDirectory: assetsDir)
        let first = loader.loadFrames(for: "Cat", animation: "idle")
        let second = loader.loadFrames(for: "Cat", animation: "idle")

        #expect(first?.count == second?.count)
        #expect(first?.first === second?.first)
    }
}
