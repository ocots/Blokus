/**
 * AI Controller
 * 
 * Single Responsibility: Orchestrate AI turns
 * Follows DIP: Depends on AIStrategy abstraction, not concrete implementations
 * 
 * @module ai/ai-controller
 */

import { PlayerState } from '../state/player-state.js';
import { AIAnimator } from './ai-animator.js';

/**
 * AI Controller
 * Orchestrates AI player turns using injected strategy
 */
export class AIController {
    /**
     * Create AI controller
     * @param {AIStrategy} aiStrategy - AI strategy instance (dependency injection)
     * @param {AIAnimator|null} animator - Optional animator for visual feedback
     */
    constructor(aiStrategy, animator = null) {
        this._strategy = aiStrategy;
        this._animator = animator;
        this._isExecuting = false;
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
            
            // Show thinking indicator if animator available
            if (this._animator) {
                this._animator.showThinkingIndicator(gameContext.playerId);
            }
            
            // Simulate thinking delay (1-3 seconds)
            const delay = 1000 + Math.random() * 2000;
            console.log(`🤖 AI Player ${gameContext.playerId} thinking... (${Math.round(delay)}ms)`);
            await this._sleep(delay);
            
            // Transition to playing state
            playerState.startAIPlaying();
            
            // Get move from strategy (OCP: any strategy works)
            const move = await this._strategy.getMove(gameContext);
            
            if (move) {
                console.log(`🤖 AI plays: ${move.piece.type} at (${move.row}, ${move.col})`);
                
                // Animate piece placement if animator available
                if (this._animator) {
                    await this._animator.animateThinking(move.piece, move.row, move.col, 400);
                }
                
                await gameContext.playMove(move.piece, move.row, move.col);
                
                // Animate placement confirmation
                if (this._animator) {
                    await this._animator.animatePlacement(move.piece, move.row, move.col);
                }
            } else {
                console.log(`🤖 AI Player ${gameContext.playerId} has no valid moves, passing...`);
                await gameContext.passTurn();
            }
            
            // Hide thinking indicator
            if (this._animator) {
                this._animator.hideThinkingIndicator(gameContext.playerId);
            }
            
            // Deactivate player
            playerState.deactivate();
            
        } catch (error) {
            console.error('AI turn failed:', error);
            
            // Hide thinking indicator on error
            if (this._animator) {
                this._animator.hideThinkingIndicator(gameContext.playerId);
            }
            
            // Fallback: pass turn
            try {
                await gameContext.passTurn();
                playerState.deactivate();
            } catch (passError) {
                console.error('Failed to pass turn:', passError);
            }
        } finally {
            this._isExecuting = false;
        }
    }

    /**
     * Sleep for specified milliseconds
     * @param {number} ms - Milliseconds to sleep
     * @returns {Promise<void>}
     * @private
     */
    _sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    /**
     * Check if AI is currently executing a turn
     * @returns {boolean}
     */
    get isExecuting() {
        return this._isExecuting;
    }
}
