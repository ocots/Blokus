/**
 * Blokus Controls
 * Handles piece selection, rotation, and keyboard shortcuts
 * @module controls
 */

import { PIECES, getPiece, getOrientationCount, getAllPieceTypes, PieceType } from './pieces.js';
import { PLAYER_COLORS } from './board.js';

/**
 * Controls class manages piece selection and manipulation
 */
export class Controls {
    /**
     * @param {Object} board - Board instance
     */
    constructor(board) {
        this._board = board;
        this._selectedPieceType = null;
        this._currentOrientation = 0;
        this._game = null;

        this._container = document.getElementById('pieces-container');
        this._previewCanvas = document.getElementById('piece-preview');
        this._previewCtx = this._previewCanvas.getContext('2d');

        this._setupButtons();
        this._setupKeyboard();
    }

    /**
     * Set game reference (Dependency Injection)
     * @param {Object} game
     */
    setGame(game) {
        this._game = game;
    }

    /**
     * Render available pieces for a player
     * @param {number} playerId
     * @param {Set<string>} remainingPieces
     */
    renderPieces(playerId, remainingPieces) {
        this._container.innerHTML = '';
        const color = PLAYER_COLORS[playerId];

        for (const type of getAllPieceTypes()) {
            const available = remainingPieces.has(type);
            const pieceDiv = document.createElement('div');
            pieceDiv.className = `piece-item ${available ? '' : 'used'}`;
            pieceDiv.dataset.pieceType = type;

            const canvas = document.createElement('canvas');
            canvas.width = 80;
            canvas.height = 80;
            pieceDiv.appendChild(canvas);

            this._drawPieceOnCanvas(canvas, getPiece(type, 0), color, available);

            if (available) {
                pieceDiv.addEventListener('click', () => this.selectPiece(type));
            }

            this._container.appendChild(pieceDiv);
        }
    }

    /**
     * Draw a piece on a canvas
     * @param {HTMLCanvasElement} canvas
     * @param {Object} piece
     * @param {string} color
     * @param {boolean} available
     * @private
     */
    _drawPieceOnCanvas(canvas, piece, color, available = true) {
        const ctx = canvas.getContext('2d');
        const bbox = piece.getBoundingBox();
        const cellSize = Math.min(
            (canvas.width - 8) / Math.max(bbox.width, bbox.height),
            16
        );

        const offsetX = (canvas.width - bbox.width * cellSize) / 2;
        const offsetY = (canvas.height - bbox.height * cellSize) / 2;

        ctx.clearRect(0, 0, canvas.width, canvas.height);

        ctx.fillStyle = available ? color : '#666666';
        ctx.globalAlpha = available ? 1 : 0.3;

        for (const [r, c] of piece.coords) {
            const x = offsetX + c * cellSize;
            const y = offsetY + r * cellSize;
            ctx.fillRect(x + 1, y + 1, cellSize - 2, cellSize - 2);
        }

        ctx.globalAlpha = 1;
    }

    /**
     * Select a piece
     * @param {string} type
     */
    selectPiece(type) {
        // Deselect previous
        const prev = this._container.querySelector('.selected');
        if (prev) prev.classList.remove('selected');

        if (this._selectedPieceType === type) {
            // Toggle off
            this._selectedPieceType = null;
            this._currentOrientation = 0;
            this._board.clearHover();
            this._renderPreview(null);
            return;
        }

        this._selectedPieceType = type;
        this._currentOrientation = 0;

        // Highlight selected
        const item = this._container.querySelector(`[data-piece-type="${type}"]`);
        if (item) item.classList.add('selected');

        // Update board hover
        const piece = getPiece(type, this._currentOrientation);
        this._board.setHoverPiece(piece);

        // Update preview
        this._renderPreview(piece);
    }

    /**
     * Rotate selected piece
     */
    rotate() {
        if (!this._selectedPieceType) return;

        const count = getOrientationCount(this._selectedPieceType);
        this._currentOrientation = (this._currentOrientation + 1) % count;

        const piece = getPiece(this._selectedPieceType, this._currentOrientation);
        // Use updateHoverPiece to keep position visible after rotation
        this._board.updateHoverPiece(piece);
        this._renderPreview(piece);
    }

    /**
     * Flip selected piece (find flipped orientation)
     */
    flip() {
        if (!this._selectedPieceType) return;

        // Advance by 4 to get flipped version (if exists)
        const count = getOrientationCount(this._selectedPieceType);
        if (count > 4) {
            this._currentOrientation = (this._currentOrientation + 4) % count;
        } else {
            // For pieces with <= 4 orientations, try next
            this._currentOrientation = (this._currentOrientation + 1) % count;
        }

        const piece = getPiece(this._selectedPieceType, this._currentOrientation);
        // Use updateHoverPiece to keep position visible after flip
        this._board.updateHoverPiece(piece);
        this._renderPreview(piece);
    }

    /**
     * Clear selection after piece is placed
     */
    clearSelection() {
        if (this._selectedPieceType) {
            const item = this._container.querySelector(`[data-piece-type="${this._selectedPieceType}"]`);
            if (item) item.classList.remove('selected');
        }

        this._selectedPieceType = null;
        this._currentOrientation = 0;
        this._board.clearHover();
        this._renderPreview(null);
    }

    /**
     * Render the preview canvas (crisp, no blur)
     * @param {Object|null} piece
     * @private
     */
    _renderPreview(piece) {
        const ctx = this._previewCtx;
        const canvasWidth = this._previewCanvas.width;
        const canvasHeight = this._previewCanvas.height;

        ctx.clearRect(0, 0, canvasWidth, canvasHeight);

        if (!piece || !this._game) return;

        const color = PLAYER_COLORS[this._game.currentPlayer];
        const bbox = piece.getBoundingBox();

        // Use integer cell size to avoid subpixel blur
        const maxCellWidth = Math.floor((canvasWidth - 16) / Math.max(bbox.width, 1));
        const maxCellHeight = Math.floor((canvasHeight - 16) / Math.max(bbox.height, 1));
        const cellSize = Math.min(maxCellWidth, maxCellHeight, 20);

        // Use integer offsets to avoid subpixel blur
        const offsetX = Math.floor((canvasWidth - bbox.width * cellSize) / 2);
        const offsetY = Math.floor((canvasHeight - bbox.height * cellSize) / 2);

        ctx.fillStyle = color;
        for (const [r, c] of piece.coords) {
            const x = offsetX + c * cellSize;
            const y = offsetY + r * cellSize;
            ctx.fillRect(x + 1, y + 1, cellSize - 2, cellSize - 2);
        }

        // Draw highlight
        ctx.fillStyle = 'rgba(255, 255, 255, 0.2)';
        for (const [r, c] of piece.coords) {
            const x = offsetX + c * cellSize;
            const y = offsetY + r * cellSize;
            ctx.fillRect(x + 1, y + 1, cellSize - 2, 3);
        }
    }

    /**
     * Setup control buttons
     * @private
     */
    _setupButtons() {
        document.getElementById('btn-rotate').addEventListener('click', () => this.rotate());
        document.getElementById('btn-flip').addEventListener('click', () => this.flip());
        document.getElementById('btn-pass').addEventListener('click', () => {
            if (this._game) this._game.passTurn();
        });
        document.getElementById('btn-new-game').addEventListener('click', () => {
            if (this._game) this._game.reset();
            document.getElementById('game-over-modal').classList.add('hidden');
        });
    }

    /**
     * Setup keyboard shortcuts
     * @private
     */
    _setupKeyboard() {
        document.addEventListener('keydown', (e) => {
            switch (e.key.toLowerCase()) {
                case 'r':
                    this.rotate();
                    break;
                case 's':
                    this.flip();
                    break;
                case 'escape':
                    this.clearSelection();
                    break;
                case ' ':
                    e.preventDefault();
                    if (this._game) this._game.passTurn();
                    break;
            }
        });
    }

    /**
     * Get currently selected piece
     * @returns {Object|null}
     */
    getSelectedPiece() {
        if (!this._selectedPieceType) return null;
        return getPiece(this._selectedPieceType, this._currentOrientation);
    }
}
