/**
 * Local AI Strategy
 * 
 * Simple random AI that runs locally (no API calls)
 * Follows Strategy Pattern - can be replaced with other strategies
 * 
 * @module ai/local-ai-strategy
 */

import { AIStrategy } from './ai-strategy.js';

/**
 * Local Random AI Strategy
 * Tries pieces in random order until finding a valid move
 */
export class LocalAIStrategy extends AIStrategy {
    /**
     * Get next move for AI player
     * @param {Object} gameContext - Game state and methods
     * @returns {Promise<{piece, row, col}|null>}
     */
    async getMove(gameContext) {
        const { playerId, players, board, isFirstMove, getPieces } = gameContext;
        
        if (!gameContext.hasValidMove(playerId)) {
            return null; // No valid move
        }

        const player = players[playerId];
        const pieces = Array.from(player.remainingPieces);
        
        // Shuffle pieces for randomness
        this._shuffle(pieces);
        
        // Try each piece
        for (const type of pieces) {
            for (const piece of getPieces(type)) {
                const corners = board.getPlayerCorners(playerId);
                
                // Shuffle corners for randomness
                this._shuffle(corners);
                
                for (const [cr, cc] of corners) {
                    for (const [pr, pc] of piece.coords) {
                        const row = cr - pr;
                        const col = cc - pc;
                        
                        if (board.isValidPlacement(piece, row, col, playerId, isFirstMove(playerId))) {
                            // Found valid move!
                            return { piece, row, col };
                        }
                    }
                }
            }
        }
        
        return null; // No valid move found
    }

    /**
     * Shuffle array in place (Fisher-Yates algorithm)
     * @param {Array} array - Array to shuffle
     * @private
     */
    _shuffle(array) {
        for (let i = array.length - 1; i > 0; i--) {
            const j = Math.floor(Math.random() * (i + 1));
            [array[i], array[j]] = [array[j], array[i]];
        }
    }
}
