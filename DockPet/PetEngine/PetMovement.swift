import Foundation

/// Computes pet position over time within given movement bounds.
/// Pure domain logic — no AppKit dependency.
///
/// The movement engine handles:
/// - Horizontal movement at configurable speed
/// - Direction changes at boundaries
/// - Random direction selection on walk start
final class PetMovement {

    /// Current horizontal position (in points, relative to movement bounds).
    private(set) var positionX: CGFloat = 0

    /// Current movement direction.
    private(set) var direction: PetDirection = .right

    /// Movement speed in points per second.
    var speed: CGFloat = 30.0

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

    /// Starts movement in a random direction.
    func startMoving() {
        isMoving = true
        direction = Bool.random(using: &rng) ? .right : .left
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

        // Boundary clamping and turnaround
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
