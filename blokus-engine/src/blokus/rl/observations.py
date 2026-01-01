"""
Observation tensor creation for Blokus RL.

Creates a rich observation tensor with 47 channels following the
AlphaZero-style representation for optimal learning.

Channel Layout:
- 0-3: Player occupancy (4 channels)
- 4-7: Valid corners per player (4 channels)
- 8-11: History T-1 (4 channels)
- 12-15: History T-2 (4 channels)
- 16: Turn number (normalized 0-1)
- 17-37: Current player's remaining pieces (21 channels)
- 38-41: Other players' remaining piece count (normalized, 4 channels)
- 42-45: First move flag per player (4 channels)
- 46: Current player indicator
"""

import numpy as np
from typing import List, Optional
from blokus.game import Game
from blokus.pieces import PieceType, PIECES

# Total number of channels in observation tensor
NUM_CHANNELS = 47

# Maximum possible turns in a game (theoretical max with 4 players × 21 pieces)
MAX_TURNS = 84


def create_observation(
    game: Game,
    history: Optional[List[Game]] = None,
    perspective_player: Optional[int] = None
) -> np.ndarray:
    """
    Create a 47-channel observation tensor from game state.
    
    Args:
        game: Current game state
        history: List of previous game states [T-1, T-2, ...] (optional)
        perspective_player: Player perspective for observation (default: current player)
    
    Returns:
        numpy array of shape (board_size, board_size, 47)
    """
    if history is None:
        history = []
    
    if perspective_player is None:
        perspective_player = game.current_player_idx
    
    board_size = game.board.size
    obs = np.zeros((board_size, board_size, NUM_CHANNELS), dtype=np.float32)
    
    # Channels 0-3: Player occupancy
    for player_id in range(4):
        if player_id < game.num_players:
            obs[:, :, player_id] = (game.board.grid == player_id + 1).astype(np.float32)
    
    # Channels 4-7: Valid corners per player
    for player_id in range(4):
        if player_id < game.num_players:
            corners = _get_valid_corners(game, player_id)
            for row, col in corners:
                if 0 <= row < board_size and 0 <= col < board_size:
                    obs[row, col, 4 + player_id] = 1.0
    
    # Channels 8-11: History T-1
    if len(history) >= 1:
        prev_game = history[0]
        for player_id in range(min(4, prev_game.num_players)):
            obs[:, :, 8 + player_id] = (prev_game.board.grid == player_id + 1).astype(np.float32)
    
    # Channels 12-15: History T-2
    if len(history) >= 2:
        prev_game = history[1]
        for player_id in range(min(4, prev_game.num_players)):
            obs[:, :, 12 + player_id] = (prev_game.board.grid == player_id + 1).astype(np.float32)
    
    # Channel 16: Turn number (normalized)
    obs[:, :, 16] = min(game.turn_number / MAX_TURNS, 1.0)
    
    # Channels 17-37: Current player's remaining pieces (21 channels)
    current_player = game.players[perspective_player]
    for i, piece_type in enumerate(PieceType):
        if piece_type in current_player.remaining_pieces:
            # Fill channel with the piece shape as indicator
            obs[:, :, 17 + i] = 1.0
    
    # Channels 38-41: Other players' remaining piece count (normalized)
    for player_id in range(4):
        if player_id < game.num_players:
            player = game.players[player_id]
            normalized_count = len(player.remaining_pieces) / 21.0
            obs[:, :, 38 + player_id] = normalized_count
    
    # Channels 42-45: First move flag per player
    for player_id in range(4):
        if player_id < game.num_players:
            is_first = game.is_first_move(player_id)
            obs[:, :, 42 + player_id] = 1.0 if is_first else 0.0
    
    # Channel 46: Current player indicator
    obs[:, :, 46] = float(perspective_player) / 3.0  # Normalized 0-1
    
    return obs


def _get_valid_corners(game: Game, player_id: int) -> List[tuple]:
    """
    Get all valid corner positions for a player.
    
    A corner is valid if:
    - It's diagonally adjacent to one of the player's pieces
    - It's not edge-adjacent to any of the player's pieces
    - The cell is empty
    """
    board = game.board
    board_size = board.size
    corners = []
    
    # If first move, return starting corners
    if game.is_first_move(player_id):
        return list(board.get_starting_corners(player_id))
    
    # Find all positions diagonally adjacent to player's pieces
    for row in range(board_size):
        for col in range(board_size):
            if board.grid[row, col] == player_id + 1:
                # Check diagonal neighbors
                for dr, dc in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
                    nr, nc = row + dr, col + dc
                    if 0 <= nr < board_size and 0 <= nc < board_size:
                        if board.grid[nr, nc] == 0:  # Empty
                            # Check no edge contact
                            if not _has_edge_contact(board, nr, nc, player_id):
                                corners.append((nr, nc))
    
    return list(set(corners))  # Remove duplicates


def _has_edge_contact(board, row: int, col: int, player_id: int) -> bool:
    """Check if a position has edge contact with player's pieces."""
    board_size = board.size
    for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        nr, nc = row + dr, col + dc
        if 0 <= nr < board_size and 0 <= nc < board_size:
            if board.grid[nr, nc] == player_id + 1:
                return True
    return False
