import Foundation

/// Represents the current behavioral state of the pet.
/// See docs/PET_BEHAVIOR.md for the full state machine specification.
enum PetState: String, CaseIterable {
    case walking
    case specialAnimation // 5s skill (dribbling, SIU, World Cup lift, shell retreat, etc.)
    case sleeping
    case interaction
    case idle
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

/// State machine implementing the requested continuous behavior cycle:
///
/// **Cycle:**
/// 1. 10 seconds continuous walking (`walking`) — traverses the Dock, reverses at edges without stopping
/// 2. 5 seconds signature skill (`specialAnimation`) — dribbling, SIU, World Cup, shell retreat, etc.
/// 3. 10 seconds sleep (`sleeping`) — rests peacefully
/// 4. Repeat cycle: 10s walk → 5s skill → 10s sleep → 10s walk...
///
/// Click interaction temporarily triggers a reaction, then resumes the cycle.
final class PetStateMachine {

    /// Current pet state.
    private(set) var state: PetState = .walking

    /// Callback fired on every state change: (oldState, newState).
    var onStateChanged: ((PetState, PetState) -> Void)?

    /// Time remaining in the current state before auto-transition.
    private(set) var stateTimer: TimeInterval = 10.0

    /// State that was active before an interaction interrupt.
    private var interruptedState: PetState = .walking

    // MARK: - Exact Durations (As Requested)

    /// 10 seconds continuous walk.
    var walkDuration: TimeInterval = 10.0

    /// 5 seconds signature skill animation.
    var skillDuration: TimeInterval = 5.0

    /// 10 seconds sleep.
    var sleepDuration: TimeInterval = 10.0

    /// Duration of click interaction reaction.
    var interactionDuration: TimeInterval = 1.0

    // MARK: - Init

    init(initialState: PetState = .walking) {
        self.state = initialState
        switch initialState {
        case .walking: self.stateTimer = walkDuration
        case .specialAnimation: self.stateTimer = skillDuration
        case .sleeping: self.stateTimer = sleepDuration
        case .interaction: self.stateTimer = interactionDuration
        case .idle: self.stateTimer = 1.0
        }
    }

    /// Resets internal timers to match configured values.
    func resetTimers() {
        switch state {
        case .walking: stateTimer = walkDuration
        case .specialAnimation: stateTimer = skillDuration
        case .sleeping: stateTimer = sleepDuration
        case .interaction: stateTimer = interactionDuration
        case .idle: stateTimer = 1.0
        }
    }

    // MARK: - Update

    /// Advances the state timer by `deltaTime`. Transitions when expired.
    func update(deltaTime: TimeInterval) {
        stateTimer -= deltaTime

        if stateTimer <= 0 {
            handleEvent(.timerExpired)
        }
    }

    // MARK: - Events

    /// Handles an external event that may trigger a state transition.
    func handleEvent(_ event: PetEvent) {
        let oldState = state

        switch (state, event) {
        case (.walking, .timerExpired):
            // 10s walk finished → 5s skill
            transition(to: .specialAnimation)

        case (.walking, .hitBoundary):
            // Reaching the Dock boundary does NOT stop the walk; the pet simply turns around
            break

        case (.specialAnimation, .timerExpired), (.specialAnimation, .animationComplete):
            // 5s skill finished → 10s sleep
            transition(to: .sleeping)

        case (.sleeping, .timerExpired):
            // 10s sleep finished → 10s walk (cycle repeats)
            transition(to: .walking)

        case (.idle, .timerExpired):
            transition(to: .walking)

        case (.walking, .clicked), (.specialAnimation, .clicked), (.sleeping, .clicked), (.idle, .clicked):
            // Click interrupt: save current state and show reaction
            interruptedState = state
            transition(to: .interaction)

        case (.interaction, .timerExpired), (.interaction, .animationComplete):
            // Return to interrupted state or continue walking
            let resumeState = (interruptedState == .interaction) ? .walking : interruptedState
            transition(to: resumeState)

        default:
            break
        }

        if state != oldState {
            onStateChanged?(oldState, state)
        }
    }

    // MARK: - Transition

    private func transition(to newState: PetState) {
        state = newState

        switch newState {
        case .walking:
            stateTimer = walkDuration
        case .specialAnimation:
            stateTimer = skillDuration
        case .sleeping:
            stateTimer = sleepDuration
        case .interaction:
            stateTimer = interactionDuration
        case .idle:
            stateTimer = 1.0
        }
    }
}
