/**
 * AI Animator
 * 
 * Provides visual feedback for AI actions
 * - Hover animations for pieces being considered
 * - Rotation animations
 * - Thinking indicators
 * 
 * @module ai/ai-animator
 */

/**
 * AI Animator class
 * Handles visual animations for AI player actions
 */
export class AIAnimator {
    /**
     * Create AI animator
     * @param {Object} board - Board instance
     * @param {Object} controls - Controls instance
     */
    constructor(board, controls) {
        this._board = board;
        this._controls = controls;
        this._isAnimating = false;
        this._animationFrame = null;
    }

    /**
     * Animate AI thinking about a move
     * Shows piece hovering and rotating
     * @param {Object} piece - Piece to animate
     * @param {number} row - Row position
     * @param {number} col - Column position
     * @param {number} duration - Animation duration in ms
     * @returns {Promise<void>}
     */
    async animateThinking(piece, row, col, duration = 500) {
        if (!piece || row === undefined || col === undefined) {
            return;
        }

        this._isAnimating = true;

        return new Promise((resolve) => {
            // Show piece preview
            this._controls.setSelectedPiece(piece);
            this._board.showPreview(piece, row, col);

            // Wait for duration
            setTimeout(() => {
                // Clear preview
                this._board.clearPreview();
                this._controls.clearSelection();
                this._isAnimating = false;
                resolve();
            }, duration);
        });
    }

    /**
     * Animate piece rotation
     * @param {Object} piece - Piece to rotate
     * @param {number} rotations - Number of 90° rotations
     * @param {number} duration - Duration per rotation in ms
     * @returns {Promise<void>}
     */
    async animateRotation(piece, rotations = 1, duration = 200) {
        if (!piece) return;

        this._isAnimating = true;

        for (let i = 0; i < rotations; i++) {
            await this._sleep(duration);
            // Trigger rotation visual update
            this._board.render();
        }

        this._isAnimating = false;
    }

    /**
     * Show thinking indicator on board
     * @param {number} playerId - Player ID
     */
    showThinkingIndicator(playerId) {
        // Add visual indicator that AI is thinking
        const indicator = document.createElement('div');
        indicator.id = `ai-thinking-${playerId}`;
        indicator.className = 'ai-thinking-indicator';
        indicator.textContent = '🤖 Réflexion...';
        indicator.style.cssText = `
            position: absolute;
            top: 10px;
            right: 10px;
            padding: 8px 16px;
            background: rgba(0, 0, 0, 0.8);
            color: white;
            border-radius: 4px;
            font-size: 14px;
            z-index: 1000;
            animation: pulse 1.5s ease-in-out infinite;
        `;

        // Add to board container
        const boardContainer = document.querySelector('.board-container') || document.body;
        boardContainer.appendChild(indicator);
    }

    /**
     * Hide thinking indicator
     * @param {number} playerId - Player ID
     */
    hideThinkingIndicator(playerId) {
        const indicator = document.getElementById(`ai-thinking-${playerId}`);
        if (indicator) {
            indicator.remove();
        }
    }

    /**
     * Animate piece placement
     * Shows a smooth transition when AI places a piece
     * @param {Object} piece - Piece being placed
     * @param {number} row - Row position
     * @param {number} col - Column position
     * @returns {Promise<void>}
     */
    async animatePlacement(piece, row, col) {
        if (!piece) return;

        this._isAnimating = true;

        // Show brief highlight
        this._board.highlightCells(piece, row, col);

        await this._sleep(300);

        // Clear highlight
        this._board.clearHighlight();
        this._isAnimating = false;
    }

    /**
     * Animate AI considering multiple moves
     * Quickly shows several potential moves
     * @param {Array<{piece, row, col}>} moves - Array of potential moves
     * @param {number} delayPerMove - Delay between showing moves in ms
     * @returns {Promise<void>}
     */
    async animateConsideringMoves(moves, delayPerMove = 150) {
        if (!moves || moves.length === 0) return;

        this._isAnimating = true;

        for (const move of moves) {
            await this.animateThinking(move.piece, move.row, move.col, delayPerMove);
        }

        this._isAnimating = false;
    }

    /**
     * Check if currently animating
     * @returns {boolean}
     */
    get isAnimating() {
        return this._isAnimating;
    }

    /**
     * Cancel current animation
     */
    cancel() {
        if (this._animationFrame) {
            cancelAnimationFrame(this._animationFrame);
            this._animationFrame = null;
        }
        this._board.clearPreview();
        this._controls.clearSelection();
        this._isAnimating = false;
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
}

/**
 * Add CSS animation for thinking indicator
 * This should be called once when the app initializes
 */
export function initAIAnimationStyles() {
    if (document.getElementById('ai-animation-styles')) {
        return; // Already initialized
    }

    const style = document.createElement('style');
    style.id = 'ai-animation-styles';
    style.textContent = `
        @keyframes pulse {
            0%, 100% {
                opacity: 1;
                transform: scale(1);
            }
            50% {
                opacity: 0.7;
                transform: scale(1.05);
            }
        }

        .ai-thinking-indicator {
            animation: pulse 1.5s ease-in-out infinite;
        }

        .ai-piece-preview {
            opacity: 0.6;
            transition: opacity 0.2s ease;
        }

        .ai-piece-preview:hover {
            opacity: 0.8;
        }
    `;
    document.head.appendChild(style);
}
