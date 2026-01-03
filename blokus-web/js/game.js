/**
 * Blokus Game Manager
 * Handles game state, turns, scoring
 * @module game
 */

import { PIECES, getPiece, getAllPieceTypes, PieceType } from './pieces.js';
import { DUO_STARTING_CORNERS, STARTING_CORNERS } from './board.js';
import { PlayerStateMachine } from './state/player-state.js';
import { AIFactory } from './ai/ai-factory.js';
import { logger } from './logger.js';

/**
 * Game class manages the overall game state.
 * Supports two modes:
 * - Local mode (default): All logic runs in JavaScript
 * - API mode: Delegates to Python backend via injected API client
 */
export class Game {
    /**
     * @param {Object} board - Board instance
     * @param {Object} controls - Controls instance
     * @param {Object|number} config - Configuration object or number of players
     * @param {Object|null} apiClient - Optional API client for server mode
     */
    constructor(board, controls, config = { playerCount: 4 }, apiClient = null) {
        // Handle legacy number argument
        if (typeof config === 'number') {
            config = { playerCount: config };
        }

        this._board = board;
        this._controls = controls;
        this._config = config;
        this._numPlayers = config.playerCount || 4;
        this._apiClient = apiClient;

        this._currentPlayer = 0;
        this._players = [];
        this._moveHistory = [];
        this._gameOver = false;
        this._useApi = apiClient !== null;

        // State machines and AI controllers (SOLID architecture)
        this._playerStates = [];
        this._aiControllers = new Map();

        // Inject game reference into dependencies
        this._board.setGame(this);
        this._controls.setGame(this);

        // Settings
        this._settings = config.settings || {};
        if (this._settings.fastMode === undefined) {
            this._settings.fastMode = true; // Enable fastMode by default for testing
        }
        this._sharedTurnControllerIndex = 0;

        this._init();
    }

    /**
     * Check if game is in API mode
     * @returns {boolean}
     */
    get useApi() {
        return this._useApi;
    }

    /**
     * Get current player ID
     * @returns {number}
     */
    get currentPlayer() {
        return this._currentPlayer;
    }

    /**
     * Get number of players
     * @returns {number}
     */
    get numPlayers() {
        return this._numPlayers;
    }

    /**
     * Check if game is over
     * @returns {boolean}
     */
    get isGameOver() {
        return this._gameOver;
    }

    /**
     * Enable/disable fast mode for AI (skips delays and animations)
     * Can be called from console: getGame().setFastMode(true)
     * @param {boolean} enabled
     */
    setFastMode(enabled) {
        this._settings.fastMode = enabled;
        for (const [playerId, controller] of this._aiControllers) {
            controller.setFastMode(enabled);
        }
        console.log(`🎮 Fast mode ${enabled ? 'enabled' : 'disabled'} for all AI players`);
    }

    /**
     * Initialize game state
     * @private
     */
    _init() {
        // Initialize board based on 2-player mode
        const twoPlayerMode = this._config.twoPlayerMode;
        if (twoPlayerMode === 'duo') {
            // Blokus Duo: 14x14 board
            this._board.init(14, DUO_STARTING_CORNERS);
        } else if (twoPlayerMode === 'standard') {
            // Blokus Standard 2P: 20x20 board, 4 colors
            this._board.init(20, STARTING_CORNERS);
        } else {
            // Default: 20x20 board
            this._board.init(20, STARTING_CORNERS);
        }

        // Initialize players
        this._players = [];

        // Special handling for 2-player Standard mode
        if (this._numPlayers === 2 && twoPlayerMode === 'standard') {
            // Each player controls 2 colors
            // Player 1 controls colors 0 (Blue) and 2 (Yellow)
            // Player 2 controls colors 1 (Green) and 3 (Red)
            for (let colorId = 0; colorId < 4; colorId++) {
                const controllerId = colorId % 2; // 0,2 -> Player 0; 1,3 -> Player 1
                const playerConfig = this._config.players ? this._config.players[controllerId] : null;
                const controllerName = playerConfig ? playerConfig.name : `Joueur ${controllerId + 1}`;

                const colorName = ['Bleu', 'Vert', 'Jaune', 'Rouge'][colorId];
                logger.debug(`🔧 Standard 2P: P${colorId} (${colorName}) -> Config[${controllerId}] Type=${playerConfig?.type}`);

                this._players.push({
                    id: colorId,
                    name: `${controllerName} (${colorName})`,
                    controlledBy: controllerId,
                    color: playerConfig ? playerConfig.color : null,
                    type: playerConfig ? playerConfig.type : 'human',      // CRITICAL: copy type!
                    persona: playerConfig ? playerConfig.persona : null,   // CRITICAL: copy persona!
                    remainingPieces: new Set(getAllPieceTypes()),
                    hasPassed: false,
                    lastPieceWasMonomino: false
                });
            }
            // Override numPlayers for game logic
            this._numPlayers = 4;
        } else {
        // Normal mode
            for (let i = 0; i < this._numPlayers; i++) {
                const playerConfig = this._config.players ? this._config.players[i] : null;
                const name = playerConfig ? (playerConfig.name || `Joueur ${i + 1}`) : `Joueur ${i + 1}`;
                console.log(`Init player ${i}: name="${name}"`, playerConfig);

                this._players.push({
                    id: i,
                    name: name,
                    color: playerConfig ? playerConfig.color : null,
                    type: playerConfig ? playerConfig.type : 'human',
                    persona: playerConfig ? playerConfig.persona : null,
                    remainingPieces: new Set(getAllPieceTypes()),
                    hasPassed: false,
                    lastPieceWasMonomino: false
                });
            }
        }

        this._currentPlayer = this._config.startPlayer || 0;
        this._moveHistory = [];
        this._gameOver = false;

        // Initialize state machines for each player
        this._playerStates = [];
        this._aiControllers.clear();
        
        // AI options (including fastMode from settings)
        const aiOptions = {
            fastMode: this._settings.fastMode ?? false
        };

        for (let i = 0; i < this._numPlayers; i++) {
            const stateMachine = new PlayerStateMachine();
            this._playerStates.push(stateMachine);

            // Setup AI controller if player is AI
            if (this._isAIPlayer(i)) {
                logger.debug(`🤖 Creating AI Controller for P${i}`);
                const aiController = AIFactory.createController(
                    this._useApi, 
                    this._apiClient,
                    this._board,
                    this._controls,
                    aiOptions
                );
                this._aiControllers.set(i, aiController);
            }
        }

        this._updateUI();

        // Apply settings
        if (this._settings.colorblindMode) {
            this._board.setColorblindMode(true);
        }
        
        // Start first turn (will trigger AI if needed)
        // In API mode, we wait for sync before starting (to avoid playing on empty board)
        if (!this._useApi) {
            this._startTurn(this._currentPlayer);
        }
    }

    /**
     * Reset the game
     * @returns {Promise<void>|void}
     */
    reset() {
        this._board.reset();
        this._controls.clearSelection();

        if (this._useApi) {
            return this._apiClient.resetGame().then(state => {
                this._syncFromServerState(state);
            }).catch(err => {
                console.error('API reset failed:', err);
                this._init(); // Fallback to local
            });
        } else {
            this._init();
        }
    }

    /**
     * Initialize game from API (for API mode startup)
     * @returns {Promise<void>}
     */
    async initFromApi() {
        if (!this._useApi) return;


        try {
            // Game is already created by main.js with proper config
            // Just fetch the current state
            const state = await this._apiClient.getGameState();
            this._syncFromServerState(state);
        } catch (err) {
            console.error('API init failed:', err);
            this._useApi = false; // Fallback to local mode
            this._init();
        }
    }

    /**
     * Check if this is a player's first move
     * @param {number} playerId
     * @returns {boolean}
     */
    isFirstMove(playerId) {
        // In local mode, we could trust moveHistory.
        // In API mode, moveHistory is not fully synced.
        // Robust check: If player has full set of pieces (21), it's their first move.
        // Assuming 21 pieces total (standard & duo).
        const player = this._players[playerId];
        if (!player) return true;

        // Use total piece count (21)
        // If remainingPieces is a Set, check size.
        return player.remainingPieces.size === 21; 
    }

    /**
     * Play a move
     * @param {Object} piece
     * @param {number} row
     * @param {number} col
     * @returns {boolean|Promise<boolean>}
     */
    playMove(piece, row, col) {
        const playerId = this._currentPlayer;
        const isFirst = this.isFirstMove(playerId);

        // Check if player is in correct state (for human players)
        if (!this._isAIPlayer(playerId)) {
            const playerState = this._playerStates[playerId];
            if (playerState && !playerState.isActive()) {
                console.warn(`Player ${playerId} is not in ACTIVE state (current: ${playerState.state})`);
                // Force activate if needed (safety fallback)
                if (playerState.canTransitionTo('active')) {
                    playerState.activate();
                }
            }
        }

        // Validate locally first (fast feedback)
        if (!this._board.isValidPlacement(piece, row, col, playerId, isFirst)) {
            return false;
        }

        if (this._useApi) {
            // API mode: Send move to server
            return this._apiClient.playMove(
                playerId,
                piece.type,
                piece.orientationIndex,
                row,
                col
            ).then(response => {
                if (response.success) {
                    this._syncFromServerState(response.game_state);
                    this._controls.clearSelection();
                    return true;
                } else {
                    console.warn('API rejected move:', response.message);
                    return false;
                }
            }).catch(err => {
                console.error('API move failed:', err);
                return false;
            });
        }

        // Local mode: Apply move directly
        this._board.placePiece(piece, row, col, playerId);

        // Update player state
        const player = this._players[playerId];
        player.remainingPieces.delete(piece.type);
        player.lastPieceWasMonomino = (piece.type === PieceType.I1);

        // Record move
        this._moveHistory.push({
            playerId,
            pieceType: piece.type,
            orientation: piece.orientationIndex,
            row,
            col
        });

        // Clear selection
        this._controls.clearSelection();

        // Next turn
        this._nextTurn();

        // 3-Player Logic
        if (this._players[playerId].type === 'shared') {
            this._sharedTurnControllerIndex++;
            this._updateUI();
        }

        return true;
    }

    /**
     * Pass turn (when no valid moves)
     * @returns {boolean|Promise<boolean>}
     */
    passTurn() {
        if (this._useApi) {
            return this._apiClient.passTurn().then(state => {
                this._syncFromServerState(state);
                this._controls.clearSelection();
                return true;
            }).catch(err => {
                console.error('API pass failed:', err);
                return false;
            });
        }

        const player = this._players[this._currentPlayer];

        // Check if player actually has no valid moves
        const hasMove = this._hasValidMove(this._currentPlayer);
        if (hasMove) {
            // Must play if possible
            alert('Vous devez jouer si vous avez un coup valide !');
            return false;
        }

        player.hasPassed = true;
        this._controls.clearSelection();
        this._nextTurn();

        // 3-Player Logic
        if (player.type === 'shared') {
            this._sharedTurnControllerIndex++;
            this._updateUI();
        }
        return true;
    }

    /**
     * Force pass (for debugging)
     */
    forcePass() {
        this._players[this._currentPlayer].hasPassed = true;
        this._controls.clearSelection();
        this._nextTurn();
    }

    /**
     * Synchronize local state from server response (API mode)
     * @param {Object} serverState - State object from API
     * @private
     */
    _syncFromServerState(serverState) {
        // Deactivate all players first to ensure clean state transition
        // This handles cases where local state is out of sync with server
        this._playerStates.forEach(ps => ps.deactivate());

        // Update board grid
        this._board.setGridFromArray(serverState.board);

        // Update players
        const serverPlayers = serverState.players;

        if (this._players.length !== serverPlayers.length) {
            // If mismatch (shouldn't happen on normal start), re-init but try to keep names if possible?
            // Or just logging warning.
            logger.warn(`Sync: Player count mismatch. Local: ${this._players.length}, Server: ${serverPlayers.length}`);
            this._numPlayers = serverPlayers.length;
            this._players = serverPlayers.map(p => ({
                id: p.id,
                name: p.name || `Joueur ${p.id + 1}`, // Fallback
                color: p.color || this._players[p.id]?.color,
                type: p.type || 'human',
                persona: p.persona,
                remainingPieces: new Set(p.pieces_remaining),
                hasPassed: p.has_passed,
                lastPieceWasMonomino: false
            }));

            // Should potentialy re-init AI controllers here if types changed?
            // For now, assume this mismatch path is rare/error recovery.
        } else {
            logger.debug(`Sync: Merging server state for ${serverPlayers.length} players.`);
            // Merge server state into existing player objects to preserve names/colors
            serverPlayers.forEach((p, index) => {
                // Assuming server array order matches ID order 0..3
                const localPlayer = this._players[index];
                if (localPlayer) {
                    localPlayer.remainingPieces = new Set(p.pieces_remaining);
                    localPlayer.hasPassed = p.has_passed;
                    // Reset transient state that server doesn't track strictly or logic differs
                    localPlayer.lastPieceWasMonomino = false;
                }
            });
        }

        // Update current player
        this._currentPlayer = serverState.current_player_id;

        // Update game status
        this._gameOver = serverState.status === 'finished';

        // Calculate scores from API data and update UI
        this._updateUI();

        // Show game over if finished
        if (this._gameOver) {
            this._showGameOver();
        } else {
            // Start next player's turn (both AI and human)
            // Use configurable delay: 0 in fastMode, 100ms otherwise
            const turnDelay = this._settings.fastMode ? 0 : 100;
            logger.debug(`🔄 Sync done. Scheduling _startTurn for P${this._currentPlayer} (delay=${turnDelay}ms)...`);
            if (turnDelay > 0) {
                setTimeout(() => this._startTurn(this._currentPlayer), turnDelay);
            } else {
                this._startTurn(this._currentPlayer);
            }
        }
    }

    /**
     * Check if player has any valid move
     * @param {number} playerId
     * @returns {boolean}
     * @private
     */
    _hasValidMove(playerId) {
        const player = this._players[playerId];
        const isFirst = this.isFirstMove(playerId);

        for (const type of player.remainingPieces) {
            for (const piece of PIECES[type]) {
                // Try positions around corners
                const corners = this._board.getPlayerCorners(playerId);
                for (const [cr, cc] of corners) {
                    for (const [pr, pc] of piece.coords) {
                        const row = cr - pr;
                        const col = cc - pc;
                        if (this._board.isValidPlacement(piece, row, col, playerId, isFirst)) {
                            return true;
                        }
                    }
                }
            }
        }

        return false;
    }

    /**
     * Start a player's turn (new SOLID architecture)
     * @param {number} playerId - Player ID
     * @private
     */
    _startTurn(playerId) {
        logger.debug(`🎬 _startTurn called for P${playerId}. isAI=${this._isAIPlayer(playerId)}`);
        const playerState = this._playerStates[playerId];

        if (this._isAIPlayer(playerId)) {
            // AI player - use AI controller
            const aiController = this._aiControllers.get(playerId);
            const gameContext = this._createGameContext(playerId);
            
            // Don't await here - let AI execute asynchronously
            // The AI will call playMove/passTurn which will trigger _nextTurn
            aiController.executeTurn(gameContext, playerState).catch(err => {
                console.error(`🤖 Unhandled error in AI turn for player ${playerId}:`, err);
            });
        } else {
            // Human player - activate state
            playerState.activate();
        }

        this._updateUI();
    }

    /**
     * Create game context for AI strategies
     * @param {number} playerId - Player ID
     * @returns {Object} Game context
     * @private
     */
    _createGameContext(playerId) {
        return {
            playerId,
            players: this._players,
            board: this._board,
            isFirstMove: (pid) => this.isFirstMove(pid),
            hasValidMove: (pid) => this._hasValidMove(pid),
            getPieces: (type) => PIECES[type],
            getPiece: (type, orientation) => getPiece(type, orientation),
            playMove: (piece, row, col) => this.playMove(piece, row, col),
            passTurn: () => this.passTurn()
        };
    }

    /**
     * Advance to next turn
     * @private
     */
    _nextTurn() {
        // Deactivate current player
        if (this._playerStates[this._currentPlayer]) {
            this._playerStates[this._currentPlayer].deactivate();
        }

        // Check if game over
        if (this._checkGameOver()) {
            this._gameOver = true;
            this._showGameOver();
            return;
        }

        // Find next player who can play
        let attempts = 0;
        while (attempts < this._numPlayers) {
            this._currentPlayer = (this._currentPlayer + 1) % this._numPlayers;
            const player = this._players[this._currentPlayer];

            if (!player.hasPassed) {
                if (player.remainingPieces.size === 0) {
                    player.hasPassed = true;
                } else if (!this._hasValidMove(this._currentPlayer)) {
                    player.hasPassed = true;
                } else {
                    break; // This player can play
                }
            }

            attempts++;
        }

        if (attempts >= this._numPlayers) {
            this._gameOver = true;
            this._showGameOver();
            return;
        }

        this.save();
        
        // Start next turn using new architecture
        this._startTurn(this._currentPlayer);
    }

    /**
     * Check if game is over
     * @returns {boolean}
     * @private
     */
    _checkGameOver() {
        return this._players.every(p => p.hasPassed);
    }

    /**
     * Check if a player is AI
     * @param {number} playerId
     * @returns {boolean}
     * @private
     */
    _isAIPlayer(playerId) {
        // Must check internal player list first as config might be 2P mode expanded to 4P
        if (this._players && this._players[playerId]) {
            return this._players[playerId].type === 'ai';
        }
        // Fallback to config (only if called before init)
        const playerConfig = this._config.players?.[playerId];
        return playerConfig?.type === 'ai';
    }

    /**
     * Get current player configuration
     * @returns {Object|null}
     * @private
     */
    _getCurrentPlayerConfig() {
        return this._config.players?.[this._currentPlayer];
    }

    /**
     * Calculate scores
     * @returns {number[]}
     */
    getScores() {
        return this._players.map(player => {
            let remaining = 0;
            for (const type of player.remainingPieces) {
                remaining += getPiece(type).size;
            }

            let score = -remaining;

            if (player.remainingPieces.size === 0) {
                score += 15; // All pieces placed bonus
                if (player.lastPieceWasMonomino) {
                    score += 5; // Monomino last bonus
                }
            }

            return score;
        });
    }

    /**
     * Get player remaining pieces
     * @param {number} playerId
     * @returns {Set<string>}
     */
    getPlayerPieces(playerId) {
        return new Set(this._players[playerId].remainingPieces);
    }

    /**
     * Update all UI elements
     * @private
     */
    _updateUI() {
        // Update turn indicator
        const currentPlayer = this._players[this._currentPlayer];
        let displayName = currentPlayer.name;

        // 3-Player Logic: Show controller name
        if (currentPlayer.type === 'shared') {
            const controllerId = this._sharedTurnControllerIndex % 3;
            // Ensure controllerId is valid
            const controller = this._players[controllerId];
            if (controller) {
                displayName = `${currentPlayer.name} (Joué par ${controller.name})`;
            }
        }

        const playerBadge = document.getElementById('current-player');
        playerBadge.textContent = displayName;
        playerBadge.className = `player-badge player-${this._currentPlayer}`;

        // Update scores
        const scores = this.getScores();
        for (let i = 0; i < this._numPlayers; i++) {
            const scoreEl = document.getElementById(`score-${i}`);
            const nameEl = document.getElementById(`name-${i}`);

            if (scoreEl) scoreEl.textContent = scores[i];
            if (nameEl) {
                nameEl.textContent = this._players[i].name;
            }

            // Highlight active player
            const scoreItem = scoreEl?.closest('.score-item');
            if (scoreItem) {
                // Show/Hide score items based on playercount
                scoreItem.style.display = 'flex';
                scoreItem.classList.toggle('active', i === this._currentPlayer);
            }
        }

        // Hide unused score items
        for (let i = this._numPlayers; i < 4; i++) {
            const scoreEl = document.getElementById(`score-${i}`);
            const scoreItem = scoreEl?.closest('.score-item');
            if (scoreItem) scoreItem.style.display = 'none';
        }

        // Update pieces panel
        const player = this._players[this._currentPlayer];
        this._controls.renderPieces(this._currentPlayer, player.remainingPieces);

        // Re-render board
        this._board.render();
    }

    /**
     * Show game over modal
     * @private
     */
    _showGameOver() {
        const modal = document.getElementById('game-over-modal');
        const scoresDiv = document.getElementById('final-scores');

        const scores = this.getScores();
        const rankings = [...scores.keys()].sort((a, b) => scores[b] - scores[a]);

        scoresDiv.innerHTML = rankings.map((i, rank) => `
            <div class="final-score-item">
                <span>${rank + 1}. ${this._players[i].name}</span>
                <span>${scores[i]} points</span>
            </div>
        `).join('');

        modal.classList.remove('hidden');
    }

    /**
     * Serialize game state
     */
    serialize() {
        return JSON.stringify({
            version: 1,
            config: this._config,
            currentPlayer: this._currentPlayer,
            players: this._players.map(p => ({
                ...p,
                remainingPieces: Array.from(p.remainingPieces)
            })),
            moveHistory: this._moveHistory,
            gameOver: this._gameOver,
            sharedTurnControllerIndex: this._sharedTurnControllerIndex,
            grid: this._board.getGrid(),
            boardSize: this._board.size,
            startingCorners: this._board.startingCorners
        });
    }

    /**
     * Deserialize and restore game state
     */
    deserialize(json) {
        try {
            const data = JSON.parse(json);

            this._config = data.config;
            this._currentPlayer = data.currentPlayer;
            this._moveHistory = data.moveHistory || [];
            this._gameOver = data.gameOver;
            this._sharedTurnControllerIndex = data.sharedTurnControllerIndex || 0;

            // Restore Players
            this._players = data.players.map(p => ({
                ...p,
                remainingPieces: new Set(p.remainingPieces)
            }));

            // Restore Board size and corners if saved
            if (data.boardSize && data.startingCorners) {
                this._board.init(data.boardSize, data.startingCorners);
            }

            // Restore Board grid
            this._board.setGridFromArray(data.grid);

            // Restore Settings
            if (this._config.isColorblind || (this._config.settings && this._config.settings.colorblindMode)) {
                this._board.setColorblindMode(true);
            }

            this._updateUI();

            if (!this._gameOver) {
                // Ensure controls exist before calling renderPieces
                if (this._controls) {
                    this._controls.renderPieces(this._currentPlayer, this._players[this._currentPlayer].remainingPieces);
                }
            } else {
                this._showGameOver();
            }

            return true;
        } catch (e) {
            console.error('Failed to load save:', e);
            return false;
        }
    }

    /**
     * Save game to local storage
     */
    save() {
        if (this._useApi || this._gameOver) return;
        try {
            localStorage.setItem('blokus_save', this.serialize());
        } catch (e) {
            console.warn('LocalStorage save failed:', e);
        }
    }

    /**
     * Clear saved game
     */
    clearSave() {
        localStorage.removeItem('blokus_save');
    }
}
