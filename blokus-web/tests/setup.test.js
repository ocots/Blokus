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

    test('should handle 4 players correctly', () => {
        setupManager.setPlayerCount(4);
        setupManager.startGame();

        expect(onStartGame).toHaveBeenCalled();
        const config = onStartGame.mock.calls[0][0];

        expect(config.playerCount).toBe(4);
        expect(config.players.length).toBe(4);
        expect(config.players[0].type).toBe('human');
    });

    test('should handle 2 players', () => {
        setupManager.setPlayerCount(2);
        setupManager.startGame();

        const config = onStartGame.mock.calls[0][0];
        expect(config.playerCount).toBe(2);
        expect(config.players.length).toBe(2);
    });
});
