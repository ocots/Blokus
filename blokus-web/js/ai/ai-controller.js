/**
 * AI Controller
 * 
 * Single Responsibility: Orchestrate AI turns
 * Follows DIP: Depends on AIStrategy abstraction, not concrete implementations
 * 
 * @module ai/ai-controller
 */

import { PlayerState } from '../state/player-state.js';

/**
 * AI Controller
 * Orchestrates AI player turns using injected strategy
 */
export class AIController {
    /**
     * Create AI controller
     * @param {AIStrategy} aiStrategy - AI strategy instance (dependency injection)
     */
    constructor(aiStrategy) {
        this._strategy = aiStrategy;
        this._isExecuting = false;
    }

    /**
     * Set fast mode (kept for compatibility, does nothing now as everything is fast)
     * @param {boolean} enabled
     */
    setFastMode(enabled) {
        // No-op
    }

    /**
     * Execute AI turn
     * @param {Object} gameContext - Game state and methods
     * @param {PlayerStateMachine} playerState - Player state machine
     * @returns {Promise<void>}
     */
    async executeTurn(gameContext, playerState) {
        if (this._isExecuting) {
            console.warn('AI turn already executing');
            return;
        }

        try {
            this._isExecuting = true;
            
            // Transition to thinking state
            playerState.startAIThinking();
            
            console.log(`🤖 AI Player ${gameContext.playerId} thinking...`);
            
            // Transition to playing state
            playerState.startAIPlaying();
            
            // Get move from strategy (OCP: any strategy works)
            let move = null;
            try {
                move = await this._strategy.getMove(gameContext);
            } catch (e) {
                console.error("Strategy error:", e);
                move = null;
            }
            
            if (move) {
                console.log(`🤖 AI plays: ${move.piece.type} at (${move.row}, ${move.col})`);

                // playMove can return boolean (local) or Promise (API)
                const result = gameContext.playMove(move.piece, move.row, move.col);
                if (result instanceof Promise) {
                    await result;
                }
            } else {
                console.log(`🤖 AI Player ${gameContext.playerId} has no valid moves, passing...`);
                // passTurn can return boolean (local) or Promise (API)
                const result = gameContext.passTurn();
                if (result instanceof Promise) {
                    await result;
                }
            }

            // Deactivate player
            playerState.deactivate();
            
        } catch (error) {
            console.error('🤖 AI turn failed:', error);
            
            // Fallback: pass turn
            try {
                const passResult = gameContext.passTurn();
                if (passResult instanceof Promise) {
                    await passResult;
                }
                playerState.deactivate();
            } catch (passError) {
                console.error('🤖 Failed to pass turn:', passError);
            }
        } finally {
            this._isExecuting = false;
        }
    }

    /**
     * Check if AI is currently executing a turn
     * @returns {boolean}
     */
    get isExecuting() {
        return this._isExecuting;
    }
}
