/**
 * @jest-environment jsdom
 */

import { jest, describe, test, expect, beforeEach } from '@jest/globals';
import { SetupManager } from '../js/setup.js';

describe('SetupManager', () => {
    let setupManager;
    let onStartGame;

    beforeEach(() => {
        // Mock DOM
        document.body.innerHTML = `
            <div id="setup-modal" class="modal"></div>
            <div id="players-config"></div>
            <button class="toggle-btn" data-players="2"></button>
            <button class="toggle-btn" data-players="3"></button>
            <button class="toggle-btn active" data-players="4"></button>
            <select id="start-player-select">
                <option value="random">Aléatoire</option>
            </select>
            <button id="btn-start-game"></button>
        `;

        onStartGame = jest.fn();
        setupManager = new SetupManager(onStartGame);
    });

    test('should initialize with default 4 players', () => {
        expect(setupManager.playerCount).toBe(4);
    });

    test('should handle 3 players selection by creating 4th SHARED player', () => {
        // Toggle to 3 players
        setupManager.setPlayerCount(3);

        // Mock config row inputs to simulate empty (default) inputs
        // setPlayerCount calls renderPlayerInputs which creates DOM elements.
        // We rely on SetupManager internal logic.

        // Trigger Start Game
        setupManager.startGame();

        expect(onStartGame).toHaveBeenCalled();
        const config = onStartGame.mock.calls[0][0];

        expect(config.playerCount).toBe(4); // Should force 4
        expect(config.players.length).toBe(4);
        expect(config.players[3].type).toBe('SHARED');
        expect(config.players[3].name).toContain('Neutre');
    });

    test('should handle 2 players', () => {
        setupManager.setPlayerCount(2);
        setupManager.startGame();

        const config = onStartGame.mock.calls[0][0];
        expect(config.playerCount).toBe(2);
        expect(config.players.length).toBe(2);
    });
});
