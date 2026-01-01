/**
 * Blokus Game Board
 * Handles rendering and interaction with the 20x20 game board
 * @module board
 */

import { PIECES } from './pieces.js';

export const BOARD_SIZE = 20;
export const CELL_SIZE = 30; // pixels per cell

/** Starting corners for each player */
export const STARTING_CORNERS = Object.freeze({
    0: [0, 0],                           // Top-left
    1: [0, BOARD_SIZE - 1],             // Top-right
    2: [BOARD_SIZE - 1, BOARD_SIZE - 1], // Bottom-right
    3: [BOARD_SIZE - 1, 0]              // Bottom-left
});

/** Player colors matching CSS */
export const PLAYER_COLORS = Object.freeze({
    0: '#3b82f6',  // Blue
    1: '#22c55e',  // Green
    2: '#eab308',  // Yellow
    3: '#ef4444'   // Red
});

export const PLAYER_COLORS_LIGHT = Object.freeze({
    0: '#60a5fa',
    1: '#4ade80',
    2: '#facc15',
    3: '#f87171'
});

/**
 * Board class handles the game board state and rendering
 */
export class Board {
    /**
     * @param {string} canvasId - ID of the canvas element
     */
    constructor(canvasId) {
        this.canvas = document.getElementById(canvasId);
        this.ctx = this.canvas.getContext('2d');
        this.size = BOARD_SIZE;
        this.cellSize = CELL_SIZE;

        // Grid state: 0 = empty, 1-4 = player
        this._grid = this._createEmptyGrid();

        // Hover state
        this._hoverPosition = null;
        this._hoverPiece = null;
        this._hoverValid = false;

        // Game reference (will be set later)
        this._game = null;

        // Bind events
        this._bindEvents();

        // Settings
        this.colorblindMode = false;
    }

    /**
     * Enable/Disable colorblind mode
     * @param {boolean} enabled 
     */
    setColorblindMode(enabled) {
        this.colorblindMode = enabled;
        this.render();
    }

    /**
     * Draw patterns for accessibility
     * @param {CanvasRenderingContext2D} ctx 
     * @param {number} pId - 0-3
     * @param {number} x - Pixel x
     * @param {number} y - Pixel y
     * @param {number} s - Size
     * @private
     */
    _drawPattern(ctx, pId, x, y, s) {
        ctx.fillStyle = 'rgba(255, 255, 255, 0.4)';
        ctx.beginPath();
        const cx = x + s / 2;
        const cy = y + s / 2;
        const r = s / 4;

        if (pId === 0) { // Blue -> Circle
            ctx.arc(cx, cy, r, 0, Math.PI * 2);
            ctx.fill();
        } else if (pId === 1) { // Green -> Square
            ctx.fillRect(cx - r, cy - r, r * 2, r * 2);
        } else if (pId === 2) { // Yellow -> Triangle
            ctx.moveTo(cx, cy - r);
            ctx.lineTo(cx + r, cy + r);
            ctx.lineTo(cx - r, cy + r);
            ctx.fill();
        } else if (pId === 3) { // Red -> X (Cross)
            ctx.strokeStyle = 'rgba(255, 255, 255, 0.6)';
            ctx.lineWidth = 3;
            ctx.moveTo(cx - r, cy - r);
            ctx.lineTo(cx + r, cy + r);
            ctx.moveTo(cx + r, cy - r);
            ctx.lineTo(cx - r, cy + r);
            ctx.stroke();
        }
    }

    /**
     * Create empty grid
     * @returns {number[][]}
     * @private
     */
    _createEmptyGrid() {
        return Array(BOARD_SIZE).fill(null)
            .map(() => Array(BOARD_SIZE).fill(0));
    }

    /**
     * Bind mouse events
     * @private
     */
    _bindEvents() {
        this.canvas.addEventListener('mousemove', this._handleMouseMove.bind(this));
        this.canvas.addEventListener('mouseleave', this._handleMouseLeave.bind(this));
        this.canvas.addEventListener('click', this._handleClick.bind(this));
    }

    /**
     * Set game reference
     * @param {Object} game - Game instance
     */
    setGame(game) {
        this._game = game;
    }

    /**
     * Clear and reset the board
     */
    reset() {
        this._grid = this._createEmptyGrid();
        this._hoverPosition = null;
        this._hoverPiece = null;
        this._hoverValid = false;
        this.render();
    }

    /**
     * Set grid from 2D array (for API sync)
     * @param {number[][]} gridArray - 2D array of cell values (0-4)
     */
    setGridFromArray(gridArray) {
        if (gridArray.length !== BOARD_SIZE || gridArray[0].length !== BOARD_SIZE) {
            console.error('Invalid grid size');
            return;
        }
        this._grid = gridArray.map(row => [...row]); // Deep copy
        this._hoverPosition = null;
        this._hoverPiece = null;
        this._hoverValid = false;
        this.render();
    }

    /**
     * Get a copy of the grid (for read access)
     * @returns {number[][]}
     */
    getGrid() {
        return this._grid.map(row => [...row]);
    }

    /**
     * Check if a position is within board bounds
     * @param {number} row
     * @param {number} col
     * @returns {boolean}
     */
    isValidPosition(row, col) {
        return row >= 0 && row < this.size && col >= 0 && col < this.size;
    }

    /**
     * Check if a cell is empty
     * @param {number} row
     * @param {number} col
     * @returns {boolean}
     */
    isEmpty(row, col) {
        return this.isValidPosition(row, col) && this._grid[row][col] === 0;
    }

    /**
     * Get cells occupied by a player
     * @param {number} playerId
     * @returns {number[][]}
     */
    getPlayerCells(playerId) {
        const cells = [];
        for (let r = 0; r < this.size; r++) {
            for (let c = 0; c < this.size; c++) {
                if (this._grid[r][c] === playerId + 1) {
                    cells.push([r, c]);
                }
            }
        }
        return cells;
    }

    /**
     * Get valid corner positions for a player to connect
     * @param {number} playerId
     * @returns {number[][]}
     */
    getPlayerCorners(playerId) {
        const playerCells = this.getPlayerCells(playerId);

        if (playerCells.length === 0) {
            return [STARTING_CORNERS[playerId]];
        }

        const corners = [];
        const playerSet = new Set(playerCells.map(c => `${c[0]},${c[1]}`));

        for (const [r, c] of playerCells) {
            for (const [dr, dc] of [[-1, -1], [-1, 1], [1, -1], [1, 1]]) {
                const nr = r + dr;
                const nc = c + dc;

                if (!this.isValidPosition(nr, nc)) continue;
                if (!this.isEmpty(nr, nc)) continue;

                // Check not edge-adjacent to player's pieces
                let isEdgeAdj = false;
                for (const [er, ec] of [[-1, 0], [1, 0], [0, -1], [0, 1]]) {
                    if (playerSet.has(`${nr + er},${nc + ec}`)) {
                        isEdgeAdj = true;
                        break;
                    }
                }

                if (!isEdgeAdj) {
                    corners.push([nr, nc]);
                }
            }
        }

        return corners;
    }

    /**
     * Get edge-adjacent positions for a player
     * @param {number} playerId
     * @returns {number[][]}
     */
    getPlayerEdges(playerId) {
        const playerCells = this.getPlayerCells(playerId);
        const edges = new Set();
        const playerSet = new Set(playerCells.map(c => `${c[0]},${c[1]}`));

        for (const [r, c] of playerCells) {
            for (const [dr, dc] of [[-1, 0], [1, 0], [0, -1], [0, 1]]) {
                const nr = r + dr;
                const nc = c + dc;
                if (this.isValidPosition(nr, nc) && !playerSet.has(`${nr},${nc}`)) {
                    edges.add(`${nr},${nc}`);
                }
            }
        }

        return Array.from(edges).map(k => k.split(',').map(Number));
    }

    /**
     * Check if a piece placement is valid
     * @param {Object} piece - Piece object
     * @param {number} row - Top-left row
     * @param {number} col - Top-left col
     * @param {number} playerId
     * @param {boolean} isFirstMove
     * @returns {boolean}
     */
    isValidPlacement(piece, row, col, playerId, isFirstMove = false) {
        const positions = piece.translate(row, col);
        const playerCells = this.getPlayerCells(playerId);

        // Check all cells are valid and empty
        for (const [r, c] of positions) {
            if (!this.isValidPosition(r, c) || !this.isEmpty(r, c)) {
                return false;
            }
        }

        // First move: must cover starting corner
        if (isFirstMove || playerCells.length === 0) {
            const corner = STARTING_CORNERS[playerId];
            const coversCorner = positions.some(([r, c]) => r === corner[0] && c === corner[1]);
            return coversCorner;
        }

        // Must not touch own pieces by edge
        const playerEdges = new Set(this.getPlayerEdges(playerId).map(c => `${c[0]},${c[1]}`));
        for (const [r, c] of positions) {
            if (playerEdges.has(`${r},${c}`)) {
                return false;
            }
        }

        // Must touch own pieces by at least one corner
        const playerCorners = new Set(this.getPlayerCorners(playerId).map(c => `${c[0]},${c[1]}`));
        const touchesCorner = positions.some(([r, c]) => playerCorners.has(`${r},${c}`));
        return touchesCorner;
    }

    /**
     * Place a piece on the board
     * @param {Object} piece
     * @param {number} row
     * @param {number} col
     * @param {number} playerId
     */
    placePiece(piece, row, col, playerId) {
        const positions = piece.translate(row, col);
        for (const [r, c] of positions) {
            this._grid[r][c] = playerId + 1;
        }
        this.render();
    }

    /**
     * Convert mouse position to grid cell
     * @param {MouseEvent} event
     * @returns {number[]}
     * @private
     */
    _mouseToCell(event) {
        const rect = this.canvas.getBoundingClientRect();
        const x = event.clientX - rect.left;
        const y = event.clientY - rect.top;

        const col = Math.floor(x / this.cellSize);
        const row = Math.floor(y / this.cellSize);

        return [row, col];
    }

    /**
     * Handle mouse move for piece preview
     * @param {MouseEvent} event
     * @private
     */
    _handleMouseMove(event) {
        if (!this._hoverPiece || !this._game) return;

        const [row, col] = this._mouseToCell(event);

        // Snap to grid - center piece on cursor
        const bbox = this._hoverPiece.getBoundingBox();
        const snapRow = row - Math.floor(bbox.height / 2);
        const snapCol = col - Math.floor(bbox.width / 2);

        this._hoverPosition = [snapRow, snapCol];
        this._hoverValid = this.isValidPlacement(
            this._hoverPiece,
            snapRow,
            snapCol,
            this._game.currentPlayer,
            this._game.isFirstMove(this._game.currentPlayer)
        );

        this.render();
    }

    /**
     * Handle mouse leave
     * @private
     */
    _handleMouseLeave() {
        this._hoverPosition = null;
        this.render();
    }

    /**
     * Handle click to place piece
     * @private
     */
    _handleClick() {
        if (!this._hoverPiece || !this._hoverPosition || !this._game) return;

        if (this._hoverValid) {
            const [row, col] = this._hoverPosition;
            this._game.playMove(this._hoverPiece, row, col);
        }
    }

    /**
     * Set the piece being hovered (resets position)
     * @param {Object|null} piece
     */
    setHoverPiece(piece) {
        this._hoverPiece = piece;
        this._hoverPosition = null;
        this._hoverValid = false;
        this.render();
    }

    /**
     * Update hover piece without resetting position (for rotation/flip)
     * Keeps the current hover position and recalculates validity
     * @param {Object|null} piece
     */
    updateHoverPiece(piece) {
        this._hoverPiece = piece;

        // Recalculate validity at current position if we have one
        if (this._hoverPosition && this._game && piece) {
            const [snapRow, snapCol] = this._hoverPosition;
            this._hoverValid = this.isValidPlacement(
                piece,
                snapRow,
                snapCol,
                this._game.currentPlayer,
                this._game.isFirstMove(this._game.currentPlayer)
            );
        }

        this.render();
    }

    /**
     * Clear hover state
     */
    clearHover() {
        this._hoverPiece = null;
        this._hoverPosition = null;
        this._hoverValid = false;
        this.render();
    }

    /**
     * Main render function
     */
    render() {
        const ctx = this.ctx;
        const size = this.cellSize;

        // Clear canvas
        ctx.fillStyle = '#e8e4dc';
        ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);

        // Draw grid
        ctx.strokeStyle = '#d0ccc4';
        ctx.lineWidth = 1;

        for (let i = 0; i <= this.size; i++) {
            ctx.beginPath();
            ctx.moveTo(i * size, 0);
            ctx.lineTo(i * size, this.size * size);
            ctx.stroke();

            ctx.beginPath();
            ctx.moveTo(0, i * size);
            ctx.lineTo(this.size * size, i * size);
            ctx.stroke();
        }

        // Draw starting corners
        if (this._game) {
            for (let p = 0; p < 4; p++) {
                if (this.getPlayerCells(p).length === 0) {
                    const [r, c] = STARTING_CORNERS[p];
                    ctx.fillStyle = PLAYER_COLORS_LIGHT[p] + '40';
                    ctx.fillRect(c * size, r * size, size, size);

                    // Corner marker
                    ctx.beginPath();
                    ctx.arc(c * size + size / 2, r * size + size / 2, 4, 0, Math.PI * 2);
                    ctx.fillStyle = PLAYER_COLORS[p];
                    ctx.fill();
                }
            }
        }

        // Draw placed pieces
        for (let r = 0; r < this.size; r++) {
            for (let c = 0; c < this.size; c++) {
                const player = this._grid[r][c];
                if (player > 0) {
                    ctx.fillStyle = PLAYER_COLORS[player - 1];
                    ctx.fillRect(c * size + 1, r * size + 1, size - 2, size - 2);

                    // Colorblind patterns
                    if (this.colorblindMode) {
                        this._drawPattern(ctx, player - 1, c * size, r * size, size);
                    }

                    // Subtle highlight
                    ctx.fillStyle = 'rgba(255, 255, 255, 0.15)';
                    ctx.fillRect(c * size + 1, r * size + 1, size - 2, 3);
                }
            }
        }

        // Draw available corners for current player
        if (this._game && this._hoverPiece) {
            const corners = this.getPlayerCorners(this._game.currentPlayer);
            ctx.fillStyle = 'rgba(255, 255, 255, 0.3)';
            for (const [r, c] of corners) {
                ctx.beginPath();
                ctx.arc(c * size + size / 2, r * size + size / 2, 3, 0, Math.PI * 2);
                ctx.fill();
            }
        }

        // Draw hover preview
        // Always use player color for the piece fill, only border indicates valid/invalid
        if (this._hoverPiece && this._hoverPosition) {
            const [hoverRow, hoverCol] = this._hoverPosition;
            const positions = this._hoverPiece.translate(hoverRow, hoverCol);
            const playerId = this._game ? this._game.currentPlayer : 0;
            const playerColor = PLAYER_COLORS[playerId];

            // Filter to valid positions on board
            const positionsFiltered = positions.filter(([r, c]) => this.isValidPosition(r, c));

            // Draw piece fill with player color (semi-transparent)
            ctx.fillStyle = playerColor + 'B0'; // ~70% opacity
            for (const [r, c] of positionsFiltered) {
                ctx.fillRect(c * size + 1, r * size + 1, size - 2, size - 2);
            }

            // Draw highlight on top
            ctx.fillStyle = 'rgba(255, 255, 255, 0.15)';
            for (const [r, c] of positionsFiltered) {
                ctx.fillRect(c * size + 1, r * size + 1, size - 2, 3);
            }

            // Draw border - GREEN if valid, RED if invalid
            ctx.strokeStyle = this._hoverValid ? '#22c55e' : '#ef4444';
            ctx.lineWidth = 3;
            for (const [r, c] of positionsFiltered) {
                ctx.strokeRect(c * size + 2, r * size + 2, size - 4, size - 4);
            }
        }
    }
}
