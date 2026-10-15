import Foundation

/// Describes a single pet's metadata and animation configuration.
/// Decoded from `manifest.json` in each pet's asset folder.
///
/// See docs/ASSET_PIPELINE.md for the full specification.
struct PetManifest: Codable, Equatable {
    let name: String
    let version: Int
    let spriteSize: SpriteSize
    let scale: Int
    let anchorY: Int?
    let animations: [String: AnimationConfig]
    let movement: MovementConfig?

    struct SpriteSize: Codable, Equatable {
        let width: Int
        let height: Int
    }

    struct AnimationConfig: Codable, Equatable {
        let fps: Double
        let loop: Bool
        /// Leading frames that travel during a signature animation (e.g. dribbling).
        var movingFrames: Int? = nil
    }

    struct MovementConfig: Codable, Equatable {
        let walkSpeed: Double?
        let runSpeed: Double?
    }

    /// Resolved anchor Y offset in pixels (defaults to 0).
    var resolvedAnchorY: Int { anchorY ?? 0 }

    /// Display size in points: spriteSize × scale.
    var displaySize: CGSize {
        CGSize(
            width: CGFloat(spriteSize.width * scale),
            height: CGFloat(spriteSize.height * scale)
        )
    }
}
