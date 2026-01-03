/**
 * AI Controller
 * 
 * Orchestrates AI player turns by getting a move from a strategy
 * and playing it after a configurable delay.
 * 
 * @module ai/ai-controller
 */

import { PlayerState } from '../state/player-state.js';
import { logger } from '../logger.js';

/**
 * AI Controller
 * Orchestrates AI player turns using injected strategy
 */
export class AIController {
    /**
     * Create AI controller
     * @param {AIStrategy} aiStrategy - AI strategy instance
     * @param {Object} options - Configuration options
     */
    constructor(aiStrategy, options = {}) {
        this._strategy = aiStrategy;
        this._isExecuting = false;
        this._thinkDelay = options.fastMode ? 0 : (options.thinkDelay || 500);
        console.log(`🤖 AIController initialized with thinkDelay=${this._thinkDelay}ms (fastMode=${options.fastMode})`);
    }

    /**
     * Set fast mode
     * @param {boolean} enabled
     */
    setFastMode(enabled) {
        this._thinkDelay = enabled ? 0 : 500;
    }

    /**
     * Execute AI turn
     * @param {Object} gameContext - Game state and methods
     * @param {PlayerStateMachine} playerState - Player state machine
     * @returns {Promise<void>}
     */
    async executeTurn(gameContext, playerState) {
        if (this._isExecuting) return;

        try {
            this._isExecuting = true;
            
            // Transition to thinking state
            playerState.startAIThinking();
            
            logger.debug(`🤖 AI Player ${gameContext.playerId} calculating... (thinkDelay=${this._thinkDelay}ms)`);

            // Get move from strategy
            const move = await this._strategy.getMove(gameContext);

            // Optional "thinking" delay for UX (unless fast mode)
            if (this._thinkDelay > 0) {
                await new Promise(resolve => setTimeout(resolve, this._thinkDelay));
            }

            // Transition to playing state
            playerState.startAIPlaying();

            if (move) {
                logger.debug(`🤖 AI plays: ${move.piece.type} at (${move.row}, ${move.col})`);
                const result = gameContext.playMove(move.piece, move.row, move.col);
                if (result instanceof Promise) {
                    await result;
                }
            } else {
                logger.debug(`🤖 AI Player ${gameContext.playerId} passing...`);
                const result = gameContext.passTurn();
                if (result instanceof Promise) {
                    await result;
                }
            }
        } catch (error) {
            console.error('🤖 AI turn failed:', error);
            // Fallback: try to pass turn so game doesn't hang
            try {
                const passResult = gameContext.passTurn();
                if (passResult instanceof Promise) {
                    await passResult;
                }
            } catch (passError) {
                console.error('🤖 Fallback pass failed:', passError);
            }
        } finally {
            this._isExecuting = false;
            // Deactivate player state
            playerState.deactivate();
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
