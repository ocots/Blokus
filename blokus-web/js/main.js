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
import { logger } from './logger.js';
import * as api from './api.js';
import { ReplayManager } from './replay.js';
import { VERSION, logVersion } from './version.js';

/** @type {Game|null} */
let game = null;
/** @type {AppStateManager} */
let stateManager = null;
/** @type {ReplayManager|null} */
let replayManager = null;

/**
 * Get the game instance (for testing/debugging)
 * @returns {Game|null}
 */
export function getGame() {
    return game;
}

// Expose getGame globally for console debugging
window.getGame = getGame;

/**
 * Initialize the application
 */
async function initApp() {
    // Log version info first
    logVersion();
    console.log(`${VERSION.getLogPrefix()} 🎮 Initializing Blokus App...`);

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
        /* if (e.target.id === 'btn-test-gameover' || e.target.closest('#btn-test-gameover')) {
            if (game && !game.isGameOver) {
                // Force all players to pass
                game._players.forEach(p => p.hasPassed = true);
                game._gameOver = true;
                game._showGameOver();
            }
        } */
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
        const apiData = await api.isServerAvailable();
        if (apiData) {
            isApiAvailable = true;
            console.log(`${VERSION.getLogPrefix()} 🌐 API server detected at ${api.getBaseUrl()}`);
            if (apiData.pid) {
                console.log(`${VERSION.getLogPrefix()} 🆔 Backend PID: ${apiData.pid} | Started: ${apiData.started_at}`);
            }
        } else {
            console.log(`${VERSION.getLogPrefix()} 📴 API server not available, using local mode`);
        }
    } catch (err) {
        console.log(`${VERSION.getLogPrefix()} 📴 API check failed, using local mode: ${err.message}`);
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
    console.log(`${VERSION.getLogPrefix()} 🔄 Resuming game...`, data.config);

    // Create board
    const board = new Board('game-board');

    // Create controls
    const controls = new Controls(board);

    // Create game instance (always local for resumed games)
    game = new Game(board, controls, data.config, null);

    // Update global reference for console debugging
    window.getGame = getGame;

    // Restore state
    const success = game.deserialize(json);

    if (success) {
        console.log(`${VERSION.getLogPrefix()} ✅ Game successfully resumed`);

        // Initialize replay (cleanup old one)
        if (replayManager) replayManager.destroy();
        replayManager = new ReplayManager('replay-board', game);
        game.onGameOver((history) => {
            replayManager.init(history);
        });
    } else {
        console.error(`${VERSION.getLogPrefix()} ❌ Failed to resume game`);
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
    console.log(`${VERSION.getLogPrefix()} 🚀 Launching Game with config:`, config);

    // Remove player rotation logic - backend now handles starting player
    // The startPlayer value is passed directly to the backend
    console.log(`${VERSION.getLogPrefix()} 📋 Starting player will be: ${config.startPlayer}`);

    // Create board
    const board = new Board('game-board');

    // Create controls
    const controls = new Controls(board);

    // Create game instance
    const useApiClient = isApiAvailable ? api : null;
    game = new Game(board, controls, config, useApiClient);

    // Update global reference for console debugging
    window.getGame = getGame;

    // If using API, initialize from server
    if (useApiClient) {
        try {
            // Need to tell API to create a new game with specific player count
            // Note: API implementation currently ignores player names/types, only cares about count
            // Pass config values, including startPlayer, players array, and mode options
            logger.api('CALLING api.createGame with:', {
                count: config.playerCount,
                start: config.startPlayer,
                players: config.players,
                opts: { twoPlayerMode: config.twoPlayerMode }
            });

            await api.createGame(
                config.playerCount,
                config.startPlayer,
                config.players,
                {
                    twoPlayerMode: config.twoPlayerMode,
                    settings: config.settings
                }
            );

            // Sync initial state
            await game.initFromApi();
            console.log(`${VERSION.getLogPrefix()} ✅ Blokus ready (API mode)`);
        } catch (err) {
            console.error('❌ API init failed:', err);
            console.log('↩️ Falling back to local mode');
            // Re-create game without API client
            game = new Game(board, controls, config, null);
            // Update reference again after fallback
            window.getGame = getGame;
        }
    } else {
        console.log(`${VERSION.getLogPrefix()} ✅ Blokus ready (local mode)`);
    }

    // Initial render
    board.render();

    // Initialize replay (cleanup old one)
    if (replayManager) replayManager.destroy();
    replayManager = new ReplayManager('replay-board', game);
    game.onGameOver((history) => {
        replayManager.init(history);
    });

    // Auto-save immediately to enable reload-resume
    game.save();
}

// Start when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initApp);
} else {
    initApp();
}
