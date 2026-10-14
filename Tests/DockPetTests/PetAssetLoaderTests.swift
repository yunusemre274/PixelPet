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
        #expect(manifest?.spriteSize.width == 64)
        #expect(manifest?.spriteSize.height == 64)
        #expect(manifest?.animations["idle"] != nil)
        #expect(manifest?.animations["walk"] != nil)
        #expect(manifest?.animations["special"] != nil)
    }

    @Test("Discovers CristianoRonaldo and LionelMessi")
    func discoverNewPets() {
        let loader = PetAssetLoader(assetsDirectory: assetsDir)
        let pets = loader.discoverPets()

        #expect(pets.contains("CristianoRonaldo"))
        #expect(pets.contains("LionelMessi"))
    }

    @Test("Loads frames for idle animation")
    func loadIdleFrames() {
        let loader = PetAssetLoader(assetsDirectory: assetsDir)
        let frames = loader.loadFrames(for: "Cat", animation: "idle")

        #expect(frames != nil)
        #expect(frames?.count == 4)
    }

    @Test("Loads frames for walk animation")
    func loadWalkFrames() {
        let loader = PetAssetLoader(assetsDirectory: assetsDir)
        let frames = loader.loadFrames(for: "Cat", animation: "walk")

        #expect(frames != nil)
        #expect(frames?.count == 4)
    }

    @Test("Loads frames for interaction animation")
    func loadInteractionFrames() {
        let loader = PetAssetLoader(assetsDirectory: assetsDir)
        let frames = loader.loadFrames(for: "Cat", animation: "interaction")

        #expect(frames != nil)
        #expect(frames?.count == 4)
    }

    @Test("Loads frames for special animation")
    func loadSpecialFrames() {
        let loader = PetAssetLoader(assetsDirectory: assetsDir)
        let ronaldoFrames = loader.loadFrames(for: "CristianoRonaldo", animation: "special")
        let messiFrames = loader.loadFrames(for: "LionelMessi", animation: "special")
        let turtleFrames = loader.loadFrames(for: "Turtle", animation: "special")

        #expect(ronaldoFrames != nil && ronaldoFrames?.count == 12)
        #expect(messiFrames != nil && messiFrames?.count == 16)
        #expect(turtleFrames != nil && turtleFrames?.count == 8)
    }

    @Test("Falls back to idle for missing animation state")
    func fallbackMissingAnimation() {
        let loader = PetAssetLoader(assetsDirectory: assetsDir)
        // 'jump' animation is not defined, should fall back to 'idle'
        let frames = loader.loadFrames(for: "Cat", animation: "jump")

        #expect(frames != nil)
        #expect(frames?.count == 4) // idle has 4 frames
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
