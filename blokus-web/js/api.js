/**
 * Blokus API Client
 * 
 * Single Responsibility: Communication with the Python backend API.
 * All HTTP requests to the game server are handled here.
 * 
 * @module api
 */

/**
 * Default API base URL (can be overridden via setBaseUrl)
 * @type {string}
 */
let _baseUrl = 'http://localhost:8000';

/**
 * Configure the API base URL.
 * @param {string} url - The base URL of the API server
 */
export function setBaseUrl(url) {
    _baseUrl = url.replace(/\/$/, ''); // Remove trailing slash
}

/**
 * Get the current API base URL.
 * @returns {string}
 */
export function getBaseUrl() {
    return _baseUrl;
}

/**
 * Generic fetch wrapper with error handling.
 * @param {string} endpoint - API endpoint (e.g., '/game/state')
 * @param {Object} options - Fetch options
 * @returns {Promise<Object>} Parsed JSON response
 * @throws {Error} If request fails
 */
async function _request(endpoint, options = {}) {
    const url = `${_baseUrl}${endpoint}`;
    
    const defaultOptions = {
        headers: {
            'Content-Type': 'application/json',
        },
    };
    
    const mergedOptions = { ...defaultOptions, ...options };
    
    try {
        const response = await fetch(url, mergedOptions);
        
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.detail || `HTTP ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        if (error.name === 'TypeError') {
            throw new Error(`Cannot connect to server at ${_baseUrl}`);
        }
        throw error;
    }
}

/**
 * Create a new game.
 * @param {number} [numPlayers=4] - Number of players (2-4)
 * @param {number} [startPlayer=0] - Starting player index (0 to numPlayers-1)
 * @param {Array} [players=null] - Optional array of player configurations
 * @returns {Promise<Object>} Initial game state
 */
export async function createGame(numPlayers = 4, startPlayer = 0, players = null) {
    const requestBody = { 
        num_players: numPlayers,
        start_player: startPlayer
    };
    
    // Include player configurations if provided
    if (players && players.length > 0) {
        requestBody.players = players;
    }
    
    return _request('/game/new', {
        method: 'POST',
        body: JSON.stringify(requestBody),
    });
}

/**
 * Get current game state.
 * @returns {Promise<Object>} Current game state
 */
export async function getGameState() {
    return _request('/game/state');
}

/**
 * Play a move.
 * @param {number} playerId - Player making the move
 * @param {string} pieceType - Piece type name (e.g., 'I1', 'L3')
 * @param {number} orientation - Orientation index
 * @param {number} row - Row position
 * @param {number} col - Column position
 * @returns {Promise<Object>} Move response with success status and new state
 */
export async function playMove(playerId, pieceType, orientation, row, col) {
    return _request('/game/move', {
        method: 'POST',
        body: JSON.stringify({
            player_id: playerId,
            piece_type: pieceType,
            orientation: orientation,
            row: row,
            col: col,
        }),
    });
}

/**
 * Pass the current player's turn.
 * @returns {Promise<Object>} Updated game state
 */
export async function passTurn() {
    return _request('/game/pass', { method: 'POST' });
}

/**
 * Reset the game to initial state.
 * @returns {Promise<Object>} Fresh game state
 */
export async function resetGame() {
    return _request('/game/reset', { method: 'POST' });
}

/**
 * Get AI suggested move for current player.
 * @returns {Promise<Object>} AI move suggestion with success status and move details
 */
export async function getAISuggestedMove() {
    return _request('/game/ai/suggest', { method: 'POST' });
}

/**
 * Check if the API server is reachable.
 * @returns {Promise<boolean>} True if server responds
 */
export async function isServerAvailable() {
    try {
        await _request('/');
        return true;
    } catch {
        return false;
    }
}

// Freeze the module exports for immutability
Object.freeze({
    setBaseUrl,
    getBaseUrl,
    createGame,
    getGameState,
    playMove,
    passTurn,
    resetGame,
    getAISuggestedMove,
    isServerAvailable,
});
