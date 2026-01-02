/**
 * Player State Machine
 * 
 * Manages player states and valid transitions
 * Follows state machine pattern for clear state management
 * 
 * @module state/player-state
 */

import { StateMachine } from '../utils/state-machine.js';

/**
 * Player state enumeration
 * @enum {string}
 */
export const PlayerState = {
    IDLE: 'idle',           // Waiting for turn
    ACTIVE: 'active',       // Human player's turn
    AI_THINKING: 'thinking', // AI is thinking
    AI_PLAYING: 'playing',  // AI is executing move
    PASSED: 'passed',       // Player has passed
    FINISHED: 'finished'    // Player finished (no pieces)
};

/**
 * Valid state transitions
 * Defines which states can transition to which other states
 */
const PLAYER_TRANSITIONS = {
    [PlayerState.IDLE]: [PlayerState.ACTIVE, PlayerState.AI_THINKING],
    [PlayerState.ACTIVE]: [PlayerState.IDLE, PlayerState.PASSED, PlayerState.FINISHED],
    [PlayerState.AI_THINKING]: [PlayerState.AI_PLAYING, PlayerState.PASSED],
    [PlayerState.AI_PLAYING]: [PlayerState.IDLE, PlayerState.FINISHED],
    [PlayerState.PASSED]: [PlayerState.FINISHED],
    [PlayerState.FINISHED]: []
};

/**
 * Player State Machine
 * Extends generic StateMachine with player-specific methods
 */
export class PlayerStateMachine extends StateMachine {
    constructor() {
        super(PlayerState.IDLE, PLAYER_TRANSITIONS);
    }

    /**
     * Activate player (human player's turn)
     */
    activate() {
        this.transitionTo(PlayerState.ACTIVE);
    }

    /**
     * Start AI thinking phase
     */
    startAIThinking() {
        this.transitionTo(PlayerState.AI_THINKING);
    }

    /**
     * Start AI playing phase
     */
    startAIPlaying() {
        this.transitionTo(PlayerState.AI_PLAYING);
    }

    /**
     * Mark player as passed
     */
    pass() {
        this.transitionTo(PlayerState.PASSED);
    }

    /**
     * Mark player as finished
     */
    finish() {
        this.transitionTo(PlayerState.FINISHED);
    }

    /**
     * Deactivate player (return to idle)
     */
    deactivate() {
        this.transitionTo(PlayerState.IDLE);
    }

    /**
     * Check if player is in an active state (can interact)
     * @returns {boolean}
     */
    isActive() {
        return this.state === PlayerState.ACTIVE;
    }

    /**
     * Check if player is AI and currently thinking/playing
     * @returns {boolean}
     */
    isAIActive() {
        return this.state === PlayerState.AI_THINKING || 
               this.state === PlayerState.AI_PLAYING;
    }

    /**
     * Check if player is done (passed or finished)
     * @returns {boolean}
     */
    isDone() {
        return this.state === PlayerState.PASSED || 
               this.state === PlayerState.FINISHED;
    }
}
