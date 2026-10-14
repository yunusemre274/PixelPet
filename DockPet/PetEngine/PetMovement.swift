import Foundation

/// Computes pet position over time within given movement bounds.
/// Pure domain logic — no AppKit dependency.
///
/// Features:
/// - Smooth traversal across the entire Dock width
/// - Automatic turnaround at screen boundaries
/// - Intelligent direction choice toward the larger open Dock area
final class PetMovement {

    /// Current horizontal position (in points, relative to movement bounds).
    private(set) var positionX: CGFloat = 0

    /// Current movement direction.
    private(set) var direction: PetDirection = .right

    /// Movement speed in points per second (default 110 pt/s for full Dock coverage).
    var speed: CGFloat = 110.0

    /// Whether the pet is currently moving.
    var isMoving: Bool = false

    /// Random number generator (injectable for testing).
    private var rng: any RandomNumberGenerator

    init(rng: any RandomNumberGenerator = SystemRandomNumberGenerator()) {
        self.rng = rng
    }

    /// Sets the initial position.
    func setPosition(_ x: CGFloat) {
        positionX = x
    }

    /// Sets the movement direction explicitly.
    func setDirection(_ newDirection: PetDirection) {
        direction = newDirection
    }

    /// Starts movement, orienting toward the larger open region of the Dock.
    func startMoving(bounds: ClosedRange<CGFloat>? = nil) {
        isMoving = true
        if let bounds {
            let mid = (bounds.lowerBound + bounds.upperBound) / 2.0
            // Walk toward the center/other side of the Dock to maximize traversal
            direction = (positionX >= mid) ? .left : .right
        }
    }

    /// Stops movement.
    func stopMoving() {
        isMoving = false
    }

    /// Advances position by `deltaTime` seconds within the given bounds.
    ///
    /// - Parameters:
    ///   - deltaTime: Seconds elapsed since last update.
    ///   - bounds: Valid range for `positionX` (min...max).
    /// - Returns: `true` if the pet hit a boundary and turned around.
    @discardableResult
    func update(deltaTime: TimeInterval, bounds: ClosedRange<CGFloat>) -> Bool {
        guard isMoving else { return false }

        let delta = speed * CGFloat(deltaTime) * (direction == .right ? 1 : -1)
        positionX += delta

        // Boundary clamping and automatic turnaround
        if positionX <= bounds.lowerBound {
            positionX = bounds.lowerBound
            direction = .right
            return true
        } else if positionX >= bounds.upperBound {
            positionX = bounds.upperBound
            direction = .left
            return true
        }

        return false
    }
}
