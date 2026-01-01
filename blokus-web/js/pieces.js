/**
 * Blokus Pieces Definitions
 * All 21 polyominoes with their shapes and orientations
 * @module pieces
 */

// Piece types enum
export const PieceType = Object.freeze({
    I1: 'I1',
    I2: 'I2',
    I3: 'I3', L3: 'L3',
    I4: 'I4', L4: 'L4', T4: 'T4', O4: 'O4', S4: 'S4',
    F: 'F', I5: 'I5', L5: 'L5', N: 'N', P: 'P',
    T5: 'T5', U: 'U', V: 'V', W: 'W', X: 'X', Y: 'Y', Z: 'Z'
});

// Base shapes as [row, col] coordinates relative to (0, 0)
const PIECE_SHAPES = Object.freeze({
    [PieceType.I1]: [[0, 0]],
    [PieceType.I2]: [[0, 0], [0, 1]],
    [PieceType.I3]: [[0, 0], [0, 1], [0, 2]],
    [PieceType.L3]: [[0, 0], [0, 1], [1, 0]],
    [PieceType.I4]: [[0, 0], [0, 1], [0, 2], [0, 3]],
    [PieceType.L4]: [[0, 0], [1, 0], [2, 0], [2, 1]],
    [PieceType.T4]: [[0, 1], [1, 0], [1, 1], [1, 2]],
    [PieceType.O4]: [[0, 0], [0, 1], [1, 0], [1, 1]],
    [PieceType.S4]: [[0, 0], [0, 1], [1, 1], [1, 2]],
    [PieceType.F]: [[0, 1], [0, 2], [1, 0], [1, 1], [2, 1]],
    [PieceType.I5]: [[0, 0], [0, 1], [0, 2], [0, 3], [0, 4]],
    [PieceType.L5]: [[0, 0], [1, 0], [2, 0], [3, 0], [3, 1]],
    [PieceType.N]: [[0, 0], [1, 0], [1, 1], [2, 1], [3, 1]],
    [PieceType.P]: [[0, 0], [0, 1], [1, 0], [1, 1], [2, 0]],
    [PieceType.T5]: [[0, 0], [0, 1], [0, 2], [1, 1], [2, 1]],
    [PieceType.U]: [[0, 0], [0, 2], [1, 0], [1, 1], [1, 2]],
    [PieceType.V]: [[0, 0], [1, 0], [2, 0], [2, 1], [2, 2]],
    [PieceType.W]: [[0, 0], [1, 0], [1, 1], [2, 1], [2, 2]],
    [PieceType.X]: [[0, 1], [1, 0], [1, 1], [1, 2], [2, 1]],
    [PieceType.Y]: [[0, 1], [1, 0], [1, 1], [2, 1], [3, 1]],
    [PieceType.Z]: [[0, 0], [0, 1], [1, 1], [2, 1], [2, 2]]
});

/**
 * Normalize coordinates so minimum is at (0, 0)
 * @param {number[][]} coords - Array of [row, col] coordinates
 * @returns {number[][]} Normalized coordinates
 */
export function normalizeCoords(coords) {
    if (coords.length === 0) return [];
    const minRow = Math.min(...coords.map(c => c[0]));
    const minCol = Math.min(...coords.map(c => c[1]));
    return coords.map(([r, c]) => [r - minRow, c - minCol]);
}

/**
 * Rotate coordinates 90 degrees clockwise
 * @param {number[][]} coords - Array of [row, col] coordinates
 * @returns {number[][]} Rotated and normalized coordinates
 */
export function rotate90(coords) {
    const rotated = coords.map(([r, c]) => [c, -r]);
    return normalizeCoords(rotated);
}

/**
 * Flip coordinates horizontally
 * @param {number[][]} coords - Array of [row, col] coordinates
 * @returns {number[][]} Flipped and normalized coordinates
 */
export function flipHorizontal(coords) {
    if (coords.length === 0) return [];
    const maxCol = Math.max(...coords.map(c => c[1]));
    const flipped = coords.map(([r, c]) => [r, maxCol - c]);
    return normalizeCoords(flipped);
}

/**
 * Convert coords to a string key for deduplication
 * @param {number[][]} coords
 * @returns {string}
 */
function coordsToKey(coords) {
    const sorted = [...coords].sort((a, b) => a[0] - b[0] || a[1] - b[1]);
    return JSON.stringify(sorted);
}

/**
 * Generate all unique orientations for a piece
 * @param {number[][]} baseCoords
 * @returns {number[][][]} Array of unique orientations
 */
function generateOrientations(baseCoords) {
    const seen = new Set();
    const orientations = [];

    let current = normalizeCoords(baseCoords);

    // 4 rotations
    for (let i = 0; i < 4; i++) {
        const key = coordsToKey(current);
        if (!seen.has(key)) {
            seen.add(key);
            orientations.push([...current.map(c => [...c])]);
        }
        current = rotate90(current);
    }

    // Flip and 4 more rotations
    current = flipHorizontal(normalizeCoords(baseCoords));
    for (let i = 0; i < 4; i++) {
        const key = coordsToKey(current);
        if (!seen.has(key)) {
            seen.add(key);
            orientations.push([...current.map(c => [...c])]);
        }
        current = rotate90(current);
    }

    return orientations;
}

/**
 * Piece class representing a Blokus piece with a specific orientation
 */
export class Piece {
    /**
     * @param {string} type - Piece type from PieceType enum
     * @param {number[][]} coords - Array of [row, col] coordinates
     * @param {number} orientationIndex - Index of this orientation
     */
    constructor(type, coords, orientationIndex = 0) {
        this.type = type;
        this.coords = Object.freeze(coords.map(c => Object.freeze([...c])));
        this.orientationIndex = orientationIndex;
        Object.freeze(this);
    }

    /** @returns {number} Number of squares in this piece */
    get size() {
        return this.coords.length;
    }

    /**
     * Get bounding box dimensions
     * @returns {{height: number, width: number}}
     */
    getBoundingBox() {
        const maxRow = Math.max(...this.coords.map(c => c[0]));
        const maxCol = Math.max(...this.coords.map(c => c[1]));
        return { height: maxRow + 1, width: maxCol + 1 };
    }

    /**
     * Translate coordinates by offset
     * @param {number} rowOffset
     * @param {number} colOffset
     * @returns {number[][]}
     */
    translate(rowOffset, colOffset) {
        return this.coords.map(([r, c]) => [r + rowOffset, c + colOffset]);
    }

    /**
     * Get corner positions (diagonal neighbors, not edge-adjacent)
     * @returns {number[][]}
     */
    getCorners() {
        const corners = [];
        const coordSet = new Set(this.coords.map(c => `${c[0]},${c[1]}`));

        for (const [r, c] of this.coords) {
            for (const [dr, dc] of [[-1, -1], [-1, 1], [1, -1], [1, 1]]) {
                const nr = r + dr;
                const nc = c + dc;
                const key = `${nr},${nc}`;

                if (coordSet.has(key)) continue;

                // Check not edge-adjacent
                let isEdgeAdj = false;
                for (const [er, ec] of this.coords) {
                    if (Math.abs(nr - er) + Math.abs(nc - ec) === 1) {
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
     * Get edge-adjacent positions
     * @returns {number[][]}
     */
    getEdges() {
        const edges = [];
        const coordSet = new Set(this.coords.map(c => `${c[0]},${c[1]}`));

        for (const [r, c] of this.coords) {
            for (const [dr, dc] of [[-1, 0], [1, 0], [0, -1], [0, 1]]) {
                const nr = r + dr;
                const nc = c + dc;
                const key = `${nr},${nc}`;

                if (!coordSet.has(key)) {
                    edges.push([nr, nc]);
                }
            }
        }

        return edges;
    }
}

// Generate all pieces with all orientations
const _pieces = {};
for (const [type, baseCoords] of Object.entries(PIECE_SHAPES)) {
    const orientations = generateOrientations(baseCoords);
    _pieces[type] = Object.freeze(orientations.map((coords, i) => new Piece(type, coords, i)));
}

/** @type {Readonly<Object.<string, readonly Piece[]>>} */
export const PIECES = Object.freeze(_pieces);

/**
 * Get a piece by type and orientation
 * @param {string} type - Piece type
 * @param {number} orientation - Orientation index (default 0)
 * @returns {Piece}
 */
export function getPiece(type, orientation = 0) {
    const orientations = PIECES[type];
    return orientations[orientation % orientations.length];
}

/**
 * Get number of orientations for a piece type
 * @param {string} type
 * @returns {number}
 */
export function getOrientationCount(type) {
    return PIECES[type].length;
}

/**
 * Get all piece types
 * @returns {string[]}
 */
export function getAllPieceTypes() {
    return Object.keys(PieceType);
}
