/**
 * AI Strategy Interface
 * 
 * Defines the contract for AI strategies (OCP + DIP)
 * All AI implementations must implement getMove()
 * 
 * @module ai/ai-strategy
 */

/**
 * AI Strategy base class (interface)
 * Follows Strategy Pattern for extensibility
 * 
 * @interface
 */
export class AIStrategy {
    /**
     * Get next move for AI player
     * 
     * @param {Object} gameContext - Game state and methods
     * @param {number} gameContext.playerId - Current player ID
     * @param {Array} gameContext.players - All players
     * @param {Object} gameContext.board - Board instance
     * @param {Function} gameContext.isFirstMove - Check if first move
     * @param {Function} gameContext.hasValidMove - Check if has valid moves
     * @param {Function} gameContext.getPieces - Get pieces for type
     * @param {Function} gameContext.getPiece - Get specific piece
     * @returns {Promise<{piece, row, col}|null>} Move or null if no valid move
     */
    async getMove(gameContext) {
        throw new Error('getMove() must be implemented by subclass');
    }
}
