
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
    getPlayerCorners() { return [[0, 0]]; }
    init() { }
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
            <div id="game-over-modal" class="hidden">
                <div id="final-scores"></div>
            </div>
        `;

        board = new MockBoard();
        controls = new MockControls();
        config = {
            playerCount: 4,
            players: [
                { name: 'P1', type: 'human', id: 0, remainingPieces: new Set(['I1']) },
                { name: 'P2', type: 'human', id: 1, remainingPieces: new Set(['I1']) },
                { name: 'P3', type: 'human', id: 2, remainingPieces: new Set(['I1']) },
                { name: 'P4', type: 'human', id: 3, remainingPieces: new Set(['I1']) }
            ],
            settings: { colorblindMode: false }
        };

        game = new Game(board, controls, config);
    });

    test('should initialize with correct players', () => {
        expect(game.numPlayers).toBe(4);
        expect(game._players[0].type).toBe('human');
        expect(game._players[3].type).toBe('human');
    });

    test('should cycle through players correctly', () => {
        // Initial state: Player 0
        expect(game.currentPlayer).toBe(0);

        // P1 plays
        game.playMove({ type: 'I1', orientationIndex: 0 }, 0, 0);
        expect(game.currentPlayer).toBe(1);

        // P2 plays
        game.playMove({ type: 'I1', orientationIndex: 0 }, 0, 0);
        expect(game.currentPlayer).toBe(2);

        // P3 plays
        game.playMove({ type: 'I1', orientationIndex: 0 }, 0, 0);
        expect(game.currentPlayer).toBe(3);

        // P4 plays
        game.playMove({ type: 'I1', orientationIndex: 0 }, 0, 0);
        expect(game.currentPlayer).toBe(0); // Back to P1
    });
});
