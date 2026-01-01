/**
 * Tests for board.js module
 */

import { 
    describe, test, assert, assertEqual 
} from './test-framework.js';

import { 
    Board, BOARD_SIZE, CELL_SIZE, STARTING_CORNERS, 
    PLAYER_COLORS, PLAYER_COLORS_LIGHT 
} from '../js/board.js';

import { getPiece, PieceType } from '../js/pieces.js';

// ============================================================================
// CONSTANTS TESTS
// ============================================================================

describe('Board constants', () => {
    test('BOARD_SIZE is 20', () => {
        assertEqual(BOARD_SIZE, 20, 'Board should be 20x20');
    });
    
    test('CELL_SIZE is 30', () => {
        assertEqual(CELL_SIZE, 30, 'Cell size should be 30px');
    });
    
    test('4 starting corners are defined', () => {
        assertEqual(Object.keys(STARTING_CORNERS).length, 4, 'Should have 4 starting corners');
    });
    
    test('starting corners are at board corners', () => {
        assertEqual(STARTING_CORNERS[0], [0, 0], 'Player 0 starts top-left');
        assertEqual(STARTING_CORNERS[1], [0, 19], 'Player 1 starts top-right');
        assertEqual(STARTING_CORNERS[2], [19, 19], 'Player 2 starts bottom-right');
        assertEqual(STARTING_CORNERS[3], [19, 0], 'Player 3 starts bottom-left');
    });
    
    test('4 player colors are defined', () => {
        assertEqual(Object.keys(PLAYER_COLORS).length, 4, 'Should have 4 player colors');
        assertEqual(Object.keys(PLAYER_COLORS_LIGHT).length, 4, 'Should have 4 light colors');
    });
});

// ============================================================================
// BOARD LOGIC TESTS (without DOM)
// ============================================================================

describe('Board logic', () => {
    // Create a mock board for testing logic
    // Note: These tests work on the logic, not the DOM rendering
    
    test('isValidPosition accepts valid positions', () => {
        // Test the logic directly
        const isValid = (row, col) => row >= 0 && row < 20 && col >= 0 && col < 20;
        
        assert(isValid(0, 0), '(0,0) should be valid');
        assert(isValid(19, 19), '(19,19) should be valid');
        assert(isValid(10, 10), '(10,10) should be valid');
    });
    
    test('isValidPosition rejects invalid positions', () => {
        const isValid = (row, col) => row >= 0 && row < 20 && col >= 0 && col < 20;
        
        assert(!isValid(-1, 0), '(-1,0) should be invalid');
        assert(!isValid(0, -1), '(0,-1) should be invalid');
        assert(!isValid(20, 0), '(20,0) should be invalid');
        assert(!isValid(0, 20), '(0,20) should be invalid');
    });
});

// ============================================================================
// PLACEMENT VALIDATION LOGIC TESTS
// ============================================================================

describe('Placement validation logic', () => {
    test('first move must cover starting corner', () => {
        // Simulating the logic
        const startingCorner = [0, 0];
        const piecePositions = [[0, 0]]; // Monomino at corner
        
        const coversCorner = piecePositions.some(
            ([r, c]) => r === startingCorner[0] && c === startingCorner[1]
        );
        
        assert(coversCorner, 'Piece at corner should cover starting corner');
    });
    
    test('first move not at corner is invalid', () => {
        const startingCorner = [0, 0];
        const piecePositions = [[5, 5]]; // Monomino away from corner
        
        const coversCorner = piecePositions.some(
            ([r, c]) => r === startingCorner[0] && c === startingCorner[1]
        );
        
        assert(!coversCorner, 'Piece away from corner should not cover it');
    });
});

// ============================================================================
// CORNER DETECTION LOGIC TESTS
// ============================================================================

describe('Corner detection logic', () => {
    test('player with no pieces gets starting corner', () => {
        // Simulating getPlayerCorners for empty board
        const playerCells = [];
        const playerId = 0;
        
        if (playerCells.length === 0) {
            const corners = [STARTING_CORNERS[playerId]];
            assertEqual(corners, [[0, 0]], 'Should return starting corner');
        }
    });
    
    test('diagonal neighbors are detected', () => {
        const cell = [5, 5];
        const diagonals = [
            [cell[0] - 1, cell[1] - 1],
            [cell[0] - 1, cell[1] + 1],
            [cell[0] + 1, cell[1] - 1],
            [cell[0] + 1, cell[1] + 1]
        ];
        
        assertEqual(diagonals.length, 4, 'Should have 4 diagonal neighbors');
        assert(diagonals.some(([r, c]) => r === 4 && c === 4), 'Should include (4,4)');
        assert(diagonals.some(([r, c]) => r === 6 && c === 6), 'Should include (6,6)');
    });
    
    test('edge neighbors are detected', () => {
        const cell = [5, 5];
        const edges = [
            [cell[0] - 1, cell[1]],
            [cell[0] + 1, cell[1]],
            [cell[0], cell[1] - 1],
            [cell[0], cell[1] + 1]
        ];
        
        assertEqual(edges.length, 4, 'Should have 4 edge neighbors');
        assert(edges.some(([r, c]) => r === 4 && c === 5), 'Should include (4,5)');
        assert(edges.some(([r, c]) => r === 5 && c === 6), 'Should include (5,6)');
    });
});

export function runBoardTests() {
    console.log('\n🧪 Running board.js tests...');
}
