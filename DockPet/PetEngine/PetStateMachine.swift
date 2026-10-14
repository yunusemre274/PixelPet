import Foundation

/// Represents the current behavioral state of the pet.
/// See docs/PET_BEHAVIOR.md for the full state machine specification.
enum PetState: String, CaseIterable {
    case idle
    case walking
    case sleeping
    case interaction
    case specialAnimation
}

/// Events that can trigger state transitions.
enum PetEvent {
    case timerExpired
    case clicked
    case animationComplete
    case hitBoundary
    case specialTrigger
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
/// Transition graph:
/// ```
/// idle → walking (timer)
/// walking → idle (timer or boundary)
/// idle → interaction (clicked)
/// walking → interaction (clicked)
/// interaction → idle (animation complete)
/// idle → sleeping (2min cumulative active time)
/// sleeping → idle (timer 30s or clicked)
/// idle → specialAnimation (15-30s periodic trigger)
/// walking → specialAnimation (15-30s periodic trigger)
/// specialAnimation → idle (animation complete)
/// ```
final class PetStateMachine {

    /// Current pet state.
    private(set) var state: PetState = .idle

    /// Callback fired on every state change: (oldState, newState).
    var onStateChanged: ((PetState, PetState) -> Void)?

    /// Time remaining in the current state before auto-transition.
    private var stateTimer: TimeInterval = 0

    /// Cumulative time the pet has been active (idle + walking) since last sleep.
    /// Resets after sleeping.
    private var activeTime: TimeInterval = 0

    /// Time until next special animation trigger.
    private var specialAnimationTimer: TimeInterval = 0

    /// Random number generator (injectable for testing).
    private var rng: any RandomNumberGenerator

    // MARK: - Configuration

    /// Idle duration range in seconds before transitioning to walk.
    var idleDurationRange: ClosedRange<TimeInterval> = 2.0...6.0

    /// Walk duration range in seconds before transitioning back to idle.
    var walkDurationRange: ClosedRange<TimeInterval> = 3.0...8.0

    /// Interaction animation duration in seconds.
    var interactionDuration: TimeInterval = 0.8

    /// Sleep duration in seconds (fixed 30s as per requirement).
    var sleepDuration: TimeInterval = 30.0

    /// How long the pet must be active (cumulative idle+walking) before it sleeps.
    /// Default: 120 seconds (2 minutes).
    var sleepAfterActiveTime: TimeInterval = 120.0

    /// Special animation duration in seconds.
    var specialAnimationDuration: TimeInterval = 2.5

    /// Range for periodic special animation trigger (15-30 seconds).
    var specialAnimationInterval: ClosedRange<TimeInterval> = 15.0...30.0

    // MARK: - Init

    init(rng: any RandomNumberGenerator = SystemRandomNumberGenerator()) {
        self.rng = rng
        self.stateTimer = randomDuration(from: idleDurationRange)
        self.specialAnimationTimer = randomDuration(from: specialAnimationInterval)
    }

    /// Resets internal timers according to current configuration ranges.
    func resetTimers() {
        self.stateTimer = randomDuration(from: idleDurationRange)
        self.specialAnimationTimer = randomDuration(from: specialAnimationInterval)
        self.activeTime = 0
    }

    // MARK: - Update

    /// Advances the state machine by `deltaTime` seconds.
    /// May trigger state transitions if timers expire.
    func update(deltaTime: TimeInterval) {
        stateTimer -= deltaTime

        // Track active time (idle + walking count as "active")
        if state == .idle || state == .walking {
            activeTime += deltaTime

            // Decrement special animation timer only during active states
            specialAnimationTimer -= deltaTime

            // Check if it's time for a special animation
            if specialAnimationTimer <= 0 {
                specialAnimationTimer = randomDuration(from: specialAnimationInterval)
                handleEvent(.specialTrigger)
                return
            }
        }

        // Check if pet should sleep after 2 minutes of activity
        if (state == .idle || state == .walking) && activeTime >= sleepAfterActiveTime {
            let oldState = state
            transition(to: .sleeping)
            if state != oldState {
                onStateChanged?(oldState, state)
            }
            return
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
            transition(to: .walking)

        case (.walking, .timerExpired), (.walking, .hitBoundary):
            transition(to: .idle)

        case (.idle, .clicked), (.walking, .clicked):
            transition(to: .interaction)

        case (.interaction, .timerExpired), (.interaction, .animationComplete):
            transition(to: .idle)

        case (.sleeping, .timerExpired), (.sleeping, .clicked):
            transition(to: .idle)

        case (.idle, .specialTrigger), (.walking, .specialTrigger):
            transition(to: .specialAnimation)

        case (.specialAnimation, .timerExpired), (.specialAnimation, .animationComplete):
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

        switch newState {
        case .idle:
            stateTimer = randomDuration(from: idleDurationRange)
        case .walking:
            stateTimer = randomDuration(from: walkDurationRange)
        case .sleeping:
            stateTimer = sleepDuration
            activeTime = 0  // Reset active time after sleeping
        case .interaction:
            stateTimer = interactionDuration
        case .specialAnimation:
            stateTimer = specialAnimationDuration
        }
    }

    private func randomDuration(from range: ClosedRange<TimeInterval>) -> TimeInterval {
        TimeInterval.random(in: range, using: &rng)
    }
}
