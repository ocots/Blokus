/**
 * Tests for pieces.js module
 */

import { 
    describe, test, assert, assertEqual, assertNotEqual 
} from './test-framework.js';

import { 
    PieceType, Piece, PIECES, 
    getPiece, getOrientationCount, getAllPieceTypes,
    normalizeCoords, rotate90, flipHorizontal
} from '../js/pieces.js';

// ============================================================================
// PIECE DEFINITIONS TESTS
// ============================================================================

describe('PieceType', () => {
    test('all 21 pieces are defined', () => {
        const types = getAllPieceTypes();
        assertEqual(types.length, 21, 'Should have 21 piece types');
    });
    
    test('PieceType is frozen', () => {
        assert(Object.isFrozen(PieceType), 'PieceType should be frozen');
    });
});

describe('Piece sizes', () => {
    test('monomino has 1 square', () => {
        assertEqual(getPiece(PieceType.I1).size, 1, 'I1 should have 1 square');
    });
    
    test('domino has 2 squares', () => {
        assertEqual(getPiece(PieceType.I2).size, 2, 'I2 should have 2 squares');
    });
    
    test('triminoes have 3 squares', () => {
        assertEqual(getPiece(PieceType.I3).size, 3, 'I3 should have 3 squares');
        assertEqual(getPiece(PieceType.L3).size, 3, 'L3 should have 3 squares');
    });
    
    test('tetrominoes have 4 squares', () => {
        for (const type of [PieceType.I4, PieceType.L4, PieceType.T4, PieceType.O4, PieceType.S4]) {
            assertEqual(getPiece(type).size, 4, `${type} should have 4 squares`);
        }
    });
    
    test('pentominoes have 5 squares', () => {
        const pentominoes = [
            PieceType.F, PieceType.I5, PieceType.L5, PieceType.N, PieceType.P,
            PieceType.T5, PieceType.U, PieceType.V, PieceType.W, PieceType.X, 
            PieceType.Y, PieceType.Z
        ];
        for (const type of pentominoes) {
            assertEqual(getPiece(type).size, 5, `${type} should have 5 squares`);
        }
    });
    
    test('total squares per player is 89', () => {
        let total = 0;
        for (const type of getAllPieceTypes()) {
            total += getPiece(type).size;
        }
        assertEqual(total, 89, 'Total squares should be 89');
    });
});

// ============================================================================
// ORIENTATION TESTS
// ============================================================================

describe('Piece orientations', () => {
    test('monomino has 1 orientation', () => {
        assertEqual(getOrientationCount(PieceType.I1), 1, 'I1 should have 1 orientation');
    });
    
    test('domino has 2 orientations', () => {
        assertEqual(getOrientationCount(PieceType.I2), 2, 'I2 should have 2 orientations');
    });
    
    test('square (O4) has 1 orientation', () => {
        assertEqual(getOrientationCount(PieceType.O4), 1, 'O4 should have 1 orientation');
    });
    
    test('X pentomino has 1 orientation', () => {
        assertEqual(getOrientationCount(PieceType.X), 1, 'X should have 1 orientation');
    });
    
    test('asymmetric pieces have 8 orientations', () => {
        for (const type of [PieceType.F, PieceType.N, PieceType.Y]) {
            assertEqual(getOrientationCount(type), 8, `${type} should have 8 orientations`);
        }
    });
    
    test('all orientations are unique', () => {
        for (const type of getAllPieceTypes()) {
            const orientations = PIECES[type];
            const seen = new Set();
            for (const piece of orientations) {
                const key = JSON.stringify([...piece.coords].sort());
                assert(!seen.has(key), `${type} should have unique orientations`);
                seen.add(key);
            }
        }
    });
});

// ============================================================================
// TRANSFORMATION TESTS
// ============================================================================

describe('Coordinate transformations', () => {
    test('normalizeCoords shifts to origin', () => {
        const coords = [[2, 3], [2, 4], [3, 3]];
        const normalized = normalizeCoords(coords);
        assertEqual(normalized, [[0, 0], [0, 1], [1, 0]], 'Should normalize to origin');
    });
    
    test('rotate90 rotates clockwise', () => {
        // Horizontal line -> vertical line
        const coords = [[0, 0], [0, 1], [0, 2]];
        const rotated = rotate90(coords);
        assertEqual(rotated.length, 3, 'Should have same number of cells');
        // Check it's now vertical
        const cols = new Set(rotated.map(c => c[1]));
        assertEqual(cols.size, 1, 'After rotation, all should have same column');
    });
    
    test('four rotations return to original', () => {
        const original = [[0, 0], [0, 1], [1, 0]];
        let current = normalizeCoords(original);
        for (let i = 0; i < 4; i++) {
            current = rotate90(current);
        }
        const originalKey = JSON.stringify(normalizeCoords(original).sort());
        const currentKey = JSON.stringify(current.sort());
        assertEqual(currentKey, originalKey, '4 rotations should return to original');
    });
    
    test('flipHorizontal mirrors piece', () => {
        const coords = [[0, 0], [0, 1], [1, 0]];
        const flipped = flipHorizontal(coords);
        // Should be mirrored
        assertNotEqual(
            JSON.stringify(flipped.sort()), 
            JSON.stringify(coords.sort()),
            'Flipped should be different from original'
        );
    });
});

// ============================================================================
// PIECE METHODS TESTS
// ============================================================================

describe('Piece methods', () => {
    test('getBoundingBox returns correct dimensions', () => {
        const piece = getPiece(PieceType.I5, 0);
        const bbox = piece.getBoundingBox();
        // I5 is either 5x1 or 1x5 depending on orientation
        assert(
            (bbox.height === 5 && bbox.width === 1) || (bbox.height === 1 && bbox.width === 5),
            'I5 should be 5x1 or 1x5'
        );
    });
    
    test('translate moves coordinates by offset', () => {
        const piece = getPiece(PieceType.I1);
        const translated = piece.translate(5, 3);
        assertEqual(translated[0][0], 5, 'Row should be offset');
        assertEqual(translated[0][1], 3, 'Col should be offset');
    });
    
    test('getCorners returns diagonal positions', () => {
        const piece = getPiece(PieceType.I1);
        const corners = piece.getCorners();
        assertEqual(corners.length, 4, 'Monomino should have 4 corners');
    });
    
    test('getEdges returns adjacent positions', () => {
        const piece = getPiece(PieceType.I1);
        const edges = piece.getEdges();
        assertEqual(edges.length, 4, 'Monomino should have 4 edges');
    });
    
    test('corners are not edge-adjacent', () => {
        for (const type of getAllPieceTypes()) {
            const piece = getPiece(type);
            const corners = piece.getCorners();
            for (const [cr, cc] of corners) {
                for (const [pr, pc] of piece.coords) {
                    const dist = Math.abs(cr - pr) + Math.abs(cc - pc);
                    assert(dist > 1, `Corner should not be edge-adjacent in ${type}`);
                }
            }
        }
    });
});

// ============================================================================
// IMMUTABILITY TESTS
// ============================================================================

describe('Immutability', () => {
    test('PIECES is frozen', () => {
        assert(Object.isFrozen(PIECES), 'PIECES should be frozen');
    });
    
    test('Piece.coords is frozen', () => {
        const piece = getPiece(PieceType.I1);
        assert(Object.isFrozen(piece.coords), 'Piece.coords should be frozen');
    });
});

export function runPiecesTests() {
    console.log('\n🧪 Running pieces.js tests...');
}
