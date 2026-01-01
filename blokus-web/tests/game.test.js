
/**
 * @jest-environment jsdom
 */

import { jest, describe, test, expect, beforeEach } from '@jest/globals';
import { Game } from '../js/game.js';

// Mock dependencies
class MockBoard {
    setGame(g) { }
    reset() { }
    render() { }
    isValidPlacement() { return true; }
    placePiece() { }
    setColorblindMode() { }
    getPlayerCorners() { return []; }
}

class MockControls {
    setGame(g) { }
    clearSelection() { }
    renderPieces() { }
}

describe('Game Logic', () => {
    let game;
    let board;
    let controls;
    let config;

    beforeEach(() => {
        // Prepare DOM for UI updates
        document.body.innerHTML = `
            <div id="current-player" class="player-badge"></div>
            <div id="score-0" class="score-value"></div>
            <div id="name-0" class="score-label"></div>
            <div id="score-1" class="score-value"></div>
            <div id="name-1" class="score-label"></div>
            <div id="score-2" class="score-value"></div>
            <div id="name-2" class="score-label"></div>
            <div id="score-3" class="score-value"></div>
            <div id="name-3" class="score-label"></div>
        `;

        board = new MockBoard();
        controls = new MockControls();
        config = {
            playerCount: 4,
            players: [
                { name: 'P1', type: 'human', id: 0, remainingPieces: new Set() },
                { name: 'P2', type: 'human', id: 1, remainingPieces: new Set() },
                { name: 'P3', type: 'human', id: 2, remainingPieces: new Set() },
                { name: 'Shared', type: 'SHARED', id: 3, remainingPieces: new Set() }
            ],
            settings: { colorblindMode: false }
        };

        game = new Game(board, controls, config);
    });

    test('should initialize with correct players', () => {
        expect(game.numPlayers).toBe(4);
        expect(game._players[3].type).toBe('SHARED');
    });

    test('should rotate shared controller index on shared turn', () => {
        // Initial state: Player 0
        expect(game.currentPlayer).toBe(0);
        expect(game._sharedTurnControllerIndex).toBe(0);

        // P1 plays
        game.playMove({ type: 'I1', orientationIndex: 0 }, 0, 0);
        expect(game.currentPlayer).toBe(1);

        // P2 plays
        game.playMove({ type: 'I1', orientationIndex: 0 }, 0, 0);
        expect(game.currentPlayer).toBe(2);

        // P3 plays
        game.playMove({ type: 'I1', orientationIndex: 0 }, 0, 0);
        expect(game.currentPlayer).toBe(3); // Shared Turn

        // UI Check: Controller 0 (P1)
        const badge = document.getElementById('current-player');
        expect(badge.textContent).toContain('Joué par P1');

        // Shared plays (Controlled by P1)
        game.playMove({ type: 'I1', orientationIndex: 0 }, 0, 0);

        // Next should be P1 again (0)
        expect(game.currentPlayer).toBe(0);

        // Check Controller Index rotated
        expect(game._sharedTurnControllerIndex).toBe(1);

        // Fast forward to next Shared turn
        game.playMove({ type: 'I1' }, 0, 0); // P1
        game.playMove({ type: 'I1' }, 0, 0); // P2
        game.playMove({ type: 'I1' }, 0, 0); // P3

        expect(game.currentPlayer).toBe(3);
        // UI Check: Controller 1 (P2)
        expect(badge.textContent).toContain('Joué par P2');
    });
});
