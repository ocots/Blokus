/**
 * Blokus - Main Entry Point
 * Initializes the game when page loads
 * @module main
 */

import { Board } from './board.js';
import { Controls } from './controls.js';
import { Game } from './game.js';
import { SetupManager } from './setup.js';
import { AppStateManager, APP_STATE } from './state.js';
import * as api from './api.js';

/** @type {Game|null} */
let game = null;
/** @type {AppStateManager} */
let stateManager = null;

/**
 * Get the game instance (for testing/debugging)
 * @returns {Game|null}
 */
export function getGame() {
    return game;
}

/**
 * Initialize the application
 */
/**
 * Initialize the application
 */
async function initApp() {
    console.log('🎮 Initializing Blokus App...');

    // Initialize State Manager
    stateManager = new AppStateManager();

    // Use event delegation for buttons (works even if DOM updates)
    document.body.addEventListener('click', (e) => {
        // Fullscreen button
        if (e.target.id === 'btn-fullscreen' || e.target.closest('#btn-fullscreen')) {
            if (!document.fullscreenElement) {
                document.documentElement.requestFullscreen().catch(err => {
                    console.error(`Error attempting to enable fullscreen: ${err.message}`);
                });
            } else {
                if (document.exitFullscreen) {
                    document.exitFullscreen();
                }
            }
        }

        // Quit button
        if (e.target.id === 'btn-quit' || e.target.closest('#btn-quit')) {
            if (confirm('Voulez-vous vraiment quitter et effacer la sauvegarde ?')) {
                if (game) game.clearSave();
                window.location.reload();
            }
        }

        // Return to menu button (from game over modal)
        if (e.target.id === 'btn-return-menu' || e.target.closest('#btn-return-menu')) {
            const gameOverModal = document.getElementById('game-over-modal');
            gameOverModal.classList.add('hidden');

            // Clear game state
            if (game) {
                game.clearSave();
                game = null;
            }

            // Return to setup
            stateManager.transitionTo(APP_STATE.SETUP);
        }

        // Test game over button (for testing)
        if (e.target.id === 'btn-test-gameover' || e.target.closest('#btn-test-gameover')) {
            if (game && !game.isGameOver) {
                // Force all players to pass
                game._players.forEach(p => p.hasPassed = true);
                game._gameOver = true;
                game._showGameOver();
            }
        }
    });

    // Check for saved game
    const savedData = localStorage.getItem('blokus_save');
    if (savedData) {
        try {
            console.log('📂 Found saved game, attempting to resume...');
            // Transition directly to GAME
            stateManager.transitionTo(APP_STATE.GAME, {
                onStartGame: () => resumeGame(savedData)
            });
            return; // Skip Setup
        } catch (e) {
            console.warn('Invalid save data, clearing:', e);
            localStorage.removeItem('blokus_save');
        }
    }

    // Normal Start: Go to Setup
    stateManager.transitionTo(APP_STATE.SETUP);

    // Check API availability first
    let isApiAvailable = false;
    try {
        isApiAvailable = await api.isServerAvailable();
        if (isApiAvailable) {
            console.log('🌐 API server detected at', api.getBaseUrl());
        } else {
            console.log('📴 API server not available, using local mode');
        }
    } catch (err) {
        console.log('📴 API check failed, using local mode:', err.message);
    }

    // Initialize Setup Manager
    new SetupManager((config) => {
        stateManager.transitionTo(APP_STATE.GAME, {
            onStartGame: () => launchGame(config, isApiAvailable)
        });
    });
}

/**
 * Resume game from local storage
 * @param {string} json - Saved game JSON
 */
async function resumeGame(json) {
    const data = JSON.parse(json);
    console.log('🔄 Resuming game...', data.config);

    // Create board
    const board = new Board('game-board');

    // Create controls
    const controls = new Controls(board);

    // Create game instance (always local for resumed games)
    game = new Game(board, controls, data.config, null);

    // Restore state
    const success = game.deserialize(json);

    if (success) {
        console.log('✅ Game successfully resumed');
    } else {
        console.error('❌ Failed to resume game');
        alert('Erreur lors du chargement de la sauvegarde.');
        localStorage.removeItem('blokus_save');
        window.location.reload();
    }
}

/**
 * Launch the game with provided configuration
 * @param {Object} config - Game configuration from Setup
 * @param {boolean} isApiAvailable - Whether API is available
 */
async function launchGame(config, isApiAvailable) {
    console.log('🚀 Launching Game with config:', config);

    // Apply "Start Player" logic: Reorder config.players if necessary
    // If Start Player is not 0, we rotate the players array so that the chosen player is at index 0 (Blue)
    if (config.startPlayer > 0 && config.players) {
        const rotation = config.startPlayer; // number of positions to shift
        const players = [...config.players];

        // Rotating logic: [0, 1, 2, 3] -> startPlayer=1 -> [1, 2, 3, 0]
        // But wait, the Setup UI has fixed colors.
        // Row 0 is Blue. Row 1 is Green.
        // If I say "Row 1 (Green) starts", I want that PERSON to be Blue.
        // So I take the config of Row 1 and move it to Index 0.
        // Yes, rotate:
        const reorderedPlayers = [];
        for (let i = 0; i < config.playerCount; i++) {
            reorderedPlayers.push(players[(i + rotation) % config.playerCount]);
        }

        // Reassign reordered players to config, but keep IDs logic consistent locally if needed?
        // Game engine assigns ID 0..3 based on array index.
        // So ID 0 will be the player in reorderedPlayers[0].
        config.players = reorderedPlayers;
        config.startPlayer = 0; // Reset to 0 since we rotated
        console.log('🔄 Players reordered for start player:', config.players);
    }

    // Create board
    const board = new Board('game-board');

    // Create controls
    const controls = new Controls(board);

    // Create game instance
    const useApiClient = isApiAvailable ? api : null;
    game = new Game(board, controls, config, useApiClient);

    // If using API, initialize from server
    if (useApiClient) {
        try {
            // Need to tell API to create a new game with specific player count
            // Note: API implementation currently ignores player names/types, only cares about count
            await api.createGame(config.playerCount);

            // Sync initial state
            await game.initFromApi();
            console.log('✅ Blokus ready (API mode)');
        } catch (err) {
            console.error('❌ API init failed:', err);
            console.log('↩️ Falling back to local mode');
            // Re-create game without API client
            game = new Game(board, controls, config, null);
        }
    } else {
        console.log('✅ Blokus ready (local mode)');
    }

    // Initial render
    board.render();
}

// Start when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initApp);
} else {
    initApp();
}
