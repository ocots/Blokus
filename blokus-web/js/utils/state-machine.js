/**
 * Generic State Machine
 * 
 * Follows OCP: Extensible without modification
 * Provides clear state transitions with validation
 * 
 * @module utils/state-machine
 */

/**
 * Generic State Machine class
 * Manages state transitions with validation and event listeners
 */
export class StateMachine {
    /**
     * Create a state machine
     * @param {string} initialState - Initial state
     * @param {Object} validTransitions - Map of valid transitions {state: [allowedStates]}
     */
    constructor(initialState, validTransitions) {
        this._currentState = initialState;
        this._validTransitions = validTransitions;
        this._listeners = [];
    }

    /**
     * Get current state
     * @returns {string}
     */
    get state() {
        return this._currentState;
    }

    /**
     * Check if transition to new state is valid
     * @param {string} newState - Target state
     * @returns {boolean}
     */
    canTransitionTo(newState) {
        const allowed = this._validTransitions[this._currentState];
        return allowed && allowed.includes(newState);
    }

    /**
     * Transition to new state
     * @param {string} newState - Target state
     * @throws {Error} If transition is invalid
     */
    transitionTo(newState) {
        if (!this.canTransitionTo(newState)) {
            throw new Error(
                `Invalid transition: ${this._currentState} -> ${newState}`
            );
        }

        const oldState = this._currentState;
        this._currentState = newState;
        
        this._notifyListeners(oldState, newState);
    }

    /**
     * Register a transition listener
     * @param {Function} callback - Called with (oldState, newState)
     */
    onTransition(callback) {
        this._listeners.push(callback);
    }

    /**
     * Notify all listeners of state transition
     * @param {string} oldState - Previous state
     * @param {string} newState - New state
     * @private
     */
    _notifyListeners(oldState, newState) {
        this._listeners.forEach(cb => cb(oldState, newState));
    }
}
