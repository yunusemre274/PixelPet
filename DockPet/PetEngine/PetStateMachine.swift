import Foundation

/// Represents the current behavioral state of the pet.
/// See docs/PET_BEHAVIOR.md for the full state machine specification.
enum PetState: String, CaseIterable {
    case idle
    case walking
    case sleeping
    case interaction
}

/// Events that can trigger state transitions.
enum PetEvent {
    case timerExpired
    case clicked
    case animationComplete
    case hitBoundary
}

/// Direction the pet is facing/moving.
enum PetDirection {
    case left
    case right
}

/// Pure state machine for pet behavior. No AppKit dependency.
///
/// Manages state transitions and timing. The state machine is fully
/// deterministic when given a fixed random seed, making it unit-testable.
///
/// Transition graph (MVP):
/// ```
/// idle → walking (timer)
/// walking → idle (timer or boundary)
/// idle → interaction (clicked)
/// interaction → idle (animation complete)
/// idle → sleeping (long idle timer)
/// sleeping → idle (timer or clicked)
/// ```
final class PetStateMachine {

    /// Current pet state.
    private(set) var state: PetState = .idle

    /// Callback fired on every state change: (oldState, newState).
    var onStateChanged: ((PetState, PetState) -> Void)?

    /// Time remaining in the current state before auto-transition.
    private var stateTimer: TimeInterval = 0

    /// How long the pet has been continuously idle (for sleep transition).
    private var idleDuration: TimeInterval = 0

    /// Random number generator (injectable for testing).
    private var rng: any RandomNumberGenerator

    // MARK: - Configuration

    /// Idle duration range in seconds before transitioning to walk.
    var idleDurationRange: ClosedRange<TimeInterval> = 2.0...6.0

    /// Walk duration range in seconds before transitioning back to idle.
    var walkDurationRange: ClosedRange<TimeInterval> = 3.0...8.0

    /// Interaction animation duration in seconds.
    var interactionDuration: TimeInterval = 0.8

    /// Sleep duration range in seconds.
    var sleepDurationRange: ClosedRange<TimeInterval> = 5.0...15.0

    /// How long the pet must be idle before it falls asleep.
    var sleepThreshold: TimeInterval = 20.0

    // MARK: - Init

    init(rng: any RandomNumberGenerator = SystemRandomNumberGenerator()) {
        self.rng = rng
        self.stateTimer = randomDuration(from: idleDurationRange)
    }

    // MARK: - Update

    /// Advances the state machine by `deltaTime` seconds.
    /// May trigger state transitions if timers expire.
    func update(deltaTime: TimeInterval) {
        stateTimer -= deltaTime

        if state == .idle {
            idleDuration += deltaTime
        }

        if stateTimer <= 0 {
            handleEvent(.timerExpired)
        }
    }

    // MARK: - Events

    /// Handles an external event that may trigger a state transition.
    func handleEvent(_ event: PetEvent) {
        let oldState = state

        switch (state, event) {
        case (.idle, .timerExpired):
            if idleDuration >= sleepThreshold {
                transition(to: .sleeping)
            } else {
                transition(to: .walking)
            }

        case (.walking, .timerExpired), (.walking, .hitBoundary):
            transition(to: .idle)

        case (.idle, .clicked), (.walking, .clicked):
            transition(to: .interaction)

        case (.interaction, .timerExpired), (.interaction, .animationComplete):
            transition(to: .idle)

        case (.sleeping, .timerExpired), (.sleeping, .clicked):
            transition(to: .idle)

        default:
            break
        }

        if state != oldState {
            onStateChanged?(oldState, state)
        }
    }

    // MARK: - Private

    private func transition(to newState: PetState) {
        state = newState
        idleDuration = 0

        switch newState {
        case .idle:
            stateTimer = randomDuration(from: idleDurationRange)
        case .walking:
            stateTimer = randomDuration(from: walkDurationRange)
        case .sleeping:
            stateTimer = randomDuration(from: sleepDurationRange)
        case .interaction:
            stateTimer = interactionDuration
        }
    }

    private func randomDuration(from range: ClosedRange<TimeInterval>) -> TimeInterval {
        TimeInterval.random(in: range, using: &rng)
    }
}
