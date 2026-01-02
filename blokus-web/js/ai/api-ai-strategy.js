/**
 * API AI Strategy
 * 
 * Gets AI moves from backend API
 * Follows Strategy Pattern and DIP (depends on API client abstraction)
 * 
 * @module ai/api-ai-strategy
 */

import { AIStrategy } from './ai-strategy.js';

/**
 * API AI Strategy
 * Delegates move selection to backend API
 */
export class APIAIStrategy extends AIStrategy {
    /**
     * Create API AI strategy
     * @param {Object} apiClient - API client instance (dependency injection)
     */
    constructor(apiClient) {
        super();
        this._apiClient = apiClient;
    }

    /**
     * Get next move from API
     * @param {Object} gameContext - Game state and methods
     * @returns {Promise<{piece, row, col}|null>}
     */
    async getMove(gameContext) {
        try {
            const response = await this._apiClient.getAISuggestedMove();
            
            if (response.success && response.move) {
                const { piece_type, orientation, row, col } = response.move;
                
                // Get piece object from game context
                const piece = gameContext.getPiece(piece_type, orientation);
                
                return { piece, row, col };
            }
            
            return null; // API returned no move
        } catch (error) {
            console.error('API AI strategy failed:', error);
            return null;
        }
    }
}
