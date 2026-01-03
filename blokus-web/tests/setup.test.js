/**
 * @jest-environment jsdom
 */

import { jest, describe, test, expect, beforeEach } from '@jest/globals';
import { SetupManager } from '../js/setup.js';
import { SettingsStore } from '../js/settings/SettingsStore.js';
import { LocalStorageObserver } from '../js/settings/LocalStorageObserver.js';

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

            <!-- New elements for mode selection -->
            <div id="two-player-mode-selector" style="display: none;">
                <span class="help-icon">?</span>
                <div class="mode-tooltip">
                    <div class="duo-info"></div>
                    <div class="standard-info"></div>
                </div>
            </div>
            <button class="mode-btn" data-mode="duo"></button>
            <button class="mode-btn" data-mode="standard"></button>
            <input type="checkbox" id="colorblind-mode">
        `;

        // Clear localStorage before each test
        localStorage.clear();

        onStartGame = jest.fn();
        setupManager = new SetupManager(onStartGame);
    });

    test('should initialize with default 4 players', () => {
        expect(setupManager.store.getState().playerCount).toBe(4);
    });

    test('should handle 4 players correctly', () => {
        // Simulate setting 4 players via store
        setupManager.store.update({ playerCount: 4 });
        setupManager.setPlayerCountUI(4); // Force UI update since we don't have full event wiring in test
        setupManager.startGame();

        expect(onStartGame).toHaveBeenCalled();
        const config = onStartGame.mock.calls[0][0];

        expect(config.playerCount).toBe(4);
        expect(config.players.length).toBe(4);
        expect(config.players[0].type).toBe('human');
    });

    test('should handle 2 players', () => {
        setupManager.store.update({ playerCount: 2 });
        setupManager.setPlayerCountUI(2);
        setupManager.startGame();

        const config = onStartGame.mock.calls[0][0];
        expect(config.playerCount).toBe(2);
        expect(config.players.length).toBe(2);
    });

    test('should persist settings', () => {
        jest.useFakeTimers();

        // Change settings
        setupManager.store.update({ playerCount: 2, twoPlayerMode: 'standard' });

        // Check if saved to localStorage (async debounce)
        jest.runAllTimers();

        const key = LocalStorageObserver.STORAGE_KEY;
        const savedRaw = localStorage.getItem(key);
        expect(savedRaw).toBeTruthy();
        const saved = JSON.parse(savedRaw);
        expect(saved.data.playerCount).toBe(2);
        expect(saved.data.twoPlayerMode).toBe('standard');

        jest.useRealTimers();
    });
});
