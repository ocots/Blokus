/**
 * Replay Manager
 * Handles visualization of game history (move by move)
 * @module replay
 */

import { Board } from './board.js';
import { getPiece } from './pieces.js';
import { ReplayStateMachine, ReplayState } from './state/replay-state.js';
import { logger } from './logger.js';

export class ReplayManager {
    /**
     * @param {string} canvasId - Canvas ID for the replay board
     * @param {Object} game - Main game instance to get config and history
     */
    constructor(canvasId, game) {
        this._game = game;
        this._board = new Board(canvasId);
        this._stateMachine = new ReplayStateMachine();

        this._history = [];
        this._currentIndex = -1; // -1 means empty board
        this._playbackInterval = null;
        this._speed = 1; // Base speed: 1 move per second (adjustable)

        this._initUI();
        this._setupListeners();
    }

    /**
     * Initialize replay with current game history
     * @param {Array} history - Move history from game
     */
    init(history) {
        this._history = history ? [...history] : []; // Create a shallow copy to prevent external mutations
        this._currentIndex = this._history.length - 1; // Default to final state
        this._stateMachine.reset();

        // Match board size/corners with game
        this._board.init(this._game._board.size, this._game._board.startingCorners);

        this._updateBoard();
        this._updateUI();

        logger.debug(`🎬 Replay initialized with ${this._history.length} moves.`);
    }

    /**
     * Start/Resume playback
     */
    play() {
        if (this._currentIndex >= this._history.length - 1) {
            this._currentIndex = -1; // Restart from beginning
            this._updateBoard(); // IMMEDIATE: clear board before starting timer
        }

        if (this._stateMachine.canTransitionTo(ReplayState.PLAYING)) {
            this._stateMachine.play();
            this._startPlaybackLoop();
        }
    }

    /**
     * Pause playback
     */
    pause() {
        this._stateMachine.pause();
        this._stopPlaybackLoop();
    }

    /**
     * Go to start
     */
    goToStart() {
        this.pause();
        this._currentIndex = -1;
        this._updateBoard();
        this._updateUI();
    }

    /**
     * Go to end
     */
    goToEnd() {
        this.pause();
        this._currentIndex = this._history.length - 1;
        this._updateBoard();
        this._updateUI();
    }

    /**
     * Step forward
     */
    stepForward() {
        this.pause(); // Stop auto-play when stepping manually
        if (this._currentIndex < this._history.length - 1) {
            this._currentIndex++;
            this._updateBoard();
            this._updateUI();
        } else {
            this._stateMachine.finish();
        }
    }

    /**
     * Step backward
     */
    stepBackward() {
        this.pause(); // Force pause mode

        // If we were finished, we need to unlock the state first
        if (this._stateMachine.state === ReplayState.FINISHED) {
            this._stateMachine.pause();
        }

        if (this._currentIndex >= 0) {
            this._currentIndex--;
            this._updateBoard(); // Force re-render from scratch up to new index
            this._updateUI();
        }
    }

    /**
     * Set playback speed
     * @param {number} speed 
     */
    setSpeed(speed) {
        this._speed = parseFloat(speed);
        if (this._stateMachine.state === ReplayState.PLAYING) {
            this._stopPlaybackLoop();
            this._startPlaybackLoop();
        }
    }

    /**
     * Start the playback timer loop
     * @private
     */
    _startPlaybackLoop() {
        this._stopPlaybackLoop();
        const delay = 1000 / this._speed;
        this._playbackInterval = setInterval(() => {
            if (this._currentIndex < this._history.length - 1) {
                this._currentIndex++;
                this._updateBoard();
                this._updateUI();
            } else {
                this.pause();
                this._stateMachine.finish();
                this._updateUI();
            }
        }, delay);
    }

    /**
     * Stop the playback timer loop
     * @private
     */
    _stopPlaybackLoop() {
        if (this._playbackInterval) {
            clearInterval(this._playbackInterval);
            this._playbackInterval = null;
        }
    }

    /**
     * Re-render board based on current history index
     * @private
     */
    _updateBoard() {
        this._board.reset();

        // Re-apply moves up to currentIndex
        for (let i = 0; i <= this._currentIndex; i++) {
            const move = this._history[i];
            const piece = getPiece(move.pieceType, move.orientation);
            this._board.placePiece(piece, move.row, move.col, move.playerId);
        }
    }

    /**
     * Update UI elements (counter, buttons state)
     * @private
     */
    _updateUI() {
        const infoEl = document.getElementById('replay-move-info');
        const countEl = document.getElementById('replay-move-counter');
        const playBtn = document.getElementById('btn-replay-play');
        const prevBtn = document.getElementById('btn-replay-prev');
        const nextBtn = document.getElementById('btn-replay-next');
        const startBtn = document.getElementById('btn-replay-start');
        const endBtn = document.getElementById('btn-replay-end');

        // Text info
        if (this._currentIndex === -1) {
            if (infoEl) infoEl.textContent = 'Début de partie';
        } else if (this._currentIndex >= this._history.length - 1) {
            if (infoEl) infoEl.textContent = 'Fin de partie';
        } else {
            const move = this._history[this._currentIndex];
            const player = this._game._players[move.playerId];

            logger.debug(`Replay UI Update: Move ${this._currentIndex}, PlayerID from move: ${move.playerId}`);
            logger.debug(`Game Players Array Length: ${this._game._players.length}`);
            if (player) {
                logger.debug(`Found Player: ID=${player.id}, Name=${player.name}, Color=${player.color}`);
            } else {
                logger.warn(`Player NOT FOUND for ID ${move.playerId}`);
            }

            // Format player info with color indicator
            const playerName = player ? player.name : `Joueur ${move.playerId + 1}`;

            // Handle dual colors for 2-player standard mode
            // In standard 2p: Red/Blue (0/2) -> Player 0, Yellow/Green (1/3) -> Player 1
            // But here move.playerId is the index in the player array (0 or 1), 
            // wait, move.playerId in history is the turn index or the actual player ID? 
            // Let's check: in game.js, playerId is passed.
            // If it's standard mode, we have 4 colors but 2 players.
            // The move history stores the ACTUAL color index played (0-3) or the player index?
            // Re-checking game.js: "playerId" is pushed. In local mode it's this._currentPlayer.

            let colorHtml = '';

            // Get actual color class for the piece played
            // The move has a 'playerId' which corresponds to the turn's color index usually
            // Visual color depends on turn index usually: 0=Blue, 1=Yellow, 2=Red, 3=Green

            // Let's rely on the player object's color or look up standard colors
            // Standard colors: 0:Blue, 1:Yellow, 2:Red, 3:Green

            // If API mode with Standard 2P, players might be mapped differently, 
            // but the move history likely records the 'seat' or 'color' index that played.
            // Let's assume the move.playerId maps to the standard 4 colors.

            // Now we can trust player.color because it's enforced in Game._init
            let statusColor = '#cccccc'; // Default fallback

            // Check if player exists and has color
            if (player && player.color) {
                const colorMap = {
                    'blue': '#3b82f6',
                    'yellow': '#eab308',
                    'red': '#ef4444',
                    'green': '#22c55e',
                    'violet': '#8b5cf6',
                    'orange': '#f97316'
                };

                if (colorMap[player.color]) {
                    statusColor = colorMap[player.color];
                } else if (player.color.startsWith('#')) {
                    statusColor = player.color;
                }
            } else {
                // Fallback: If player object is missing (e.g. server sync mismatch in 2P Standard)
                // or color is missing, use the standard color corresponding to the move ID.
                // This ensures that even if the player array is truncated to 2, 
                // moves 2 (Red) and 3 (Green) still display correctly.
                const modernColors = ['#3b82f6', '#eab308', '#ef4444', '#22c55e'];
                statusColor = modernColors[move.playerId % 4];
            }

            colorHtml = `<span style="display:inline-block; width:12px; height:12px; border-radius:50%; background-color:${statusColor}; margin-left:8px; border: 1px solid rgba(255,255,255,0.3);"></span>`;

            if (infoEl) infoEl.innerHTML = `Au tour de <strong>${playerName}</strong> ${colorHtml}`;
        }

        if (countEl) {
            const current = this._currentIndex + 1;
            const total = this._history.length;
            countEl.textContent = `Coup ${current} / ${total}`;
        }

        // Button icons/states
        if (playBtn) {
            const isPlaying = this._stateMachine.state === ReplayState.PLAYING;
            playBtn.innerHTML = isPlaying ? '⏸️' : '▶️';
            playBtn.title = isPlaying ? 'Pause' : 'Lecture';
            logger.debug(`Toggle Play Button: isPlaying=${isPlaying}, state=${this._stateMachine.state}`);
        }

        if (prevBtn) prevBtn.disabled = (this._currentIndex === -1);
        if (nextBtn) nextBtn.disabled = (this._currentIndex >= this._history.length - 1);
        if (startBtn) startBtn.disabled = (this._currentIndex === -1);
        if (endBtn) endBtn.disabled = (this._currentIndex >= this._history.length - 1);
    }

    /**
     * Get UI elements and bind events
     * @private
     */
    _initUI() {
        const playBtn = document.getElementById('btn-replay-play');
        const prevBtn = document.getElementById('btn-replay-prev');
        const nextBtn = document.getElementById('btn-replay-next');
        const startBtn = document.getElementById('btn-replay-start');
        const endBtn = document.getElementById('btn-replay-end');
        const speedSelect = document.getElementById('replay-speed');

        playBtn?.addEventListener('click', () => {
            if (this._stateMachine.state === ReplayState.PLAYING) {
                this.pause();
            } else {
                this.play();
            }
        });

        prevBtn?.addEventListener('click', () => this.stepBackward());
        nextBtn?.addEventListener('click', () => this.stepForward());
        startBtn?.addEventListener('click', () => this.goToStart());
        endBtn?.addEventListener('click', () => this.goToEnd());

        speedSelect?.addEventListener('change', (e) => this.setSpeed(e.target.value));
    }

    /**
     * Setup state machine listeners
     * @private
     */
    _setupListeners() {
        this._stateMachine.onTransition((oldState, newState) => {
            logger.debug(`🎞️ Replay: ${oldState} -> ${newState}`);
            this._updateUI();
        });
    }

    /**
     * Clean up event listeners and intervals
     */
    destroy() {
        this._stopPlaybackLoop();

        // Remove listeners by cloning nodes (quickest way for anonymous functions)
        const buttons = [
            'btn-replay-play', 'btn-replay-prev', 'btn-replay-next',
            'btn-replay-start', 'btn-replay-end', 'replay-speed'
        ];

        buttons.forEach(id => {
            const el = document.getElementById(id);
            if (el) {
                const clone = el.cloneNode(true);
                el.parentNode.replaceChild(clone, el);
            }
        });

        logger.debug("🧹 ReplayManager destroyed and cleaned up.");
    }
}
