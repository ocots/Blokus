/**
 * Application State Management
 */

export const APP_STATE = {
    INTRO: 'INTRO',
    SETUP: 'SETUP',
    GAME: 'GAME',
    GAME_OVER: 'GAME_OVER'
};

export class AppStateManager {
    constructor() {
        this.currentState = APP_STATE.INTRO;
        this.elements = {
            intro: document.getElementById('intro-screen'), // Potential future screen
            setup: document.getElementById('setup-modal'),
            game: document.getElementById('game-container'),
            gameOver: document.getElementById('game-over-modal') // Potential future
        };
    }

    /**
     * Transition to a new state
     * @param {string} newState 
     * @param {Object} context - Optional data to pass to the new state
     */
    transitionTo(newState, context = {}) {
        console.log(`Transitioning from ${this.currentState} to ${newState}`);
        this.currentState = newState;
        this._updateDisplay();
        this._handleStateLogic(newState, context);
    }

    /**
     * Update DOM visibility based on state
     * @private
     */
    _updateDisplay() {
        // Simple visibility logic: Hide all, Show relevant
        // Note: Currently setup-modal is overlay, game is always background.
        // We refine this:
        
        switch (this.currentState) {
            case APP_STATE.INTRO:
                // If we had an intro screen
                break;
            case APP_STATE.SETUP:
                if (this.elements.setup) this.elements.setup.style.display = 'flex';
                // Game might be visible in background or hidden
                break;
            case APP_STATE.GAME:
                if (this.elements.setup) this.elements.setup.style.display = 'none';
                if (this.elements.game) this.elements.game.style.display = 'block';
                break;
            case APP_STATE.GAME_OVER:
                // Show game over overlay
                break;
        }
    }

    /**
     * Execute specific logic for the new state
     * @private
     */
    _handleStateLogic(state, context) {
        switch (state) {
            case APP_STATE.GAME:
                if (context.onStartGame) {
                    context.onStartGame();
                }
                break;
        }
    }
}
