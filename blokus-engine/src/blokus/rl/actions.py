"""
Action space encoding and decoding for Blokus RL.

The action space is flattened to a single integer representing:
- Piece type (21 options)
- Orientation (8 options max)
- Position (board_size × board_size options)

Total theoretical: 21 × 8 × 400 = 67,200 actions for 20×20
With symmetry reduction: ~6,000 unique actions

For 14×14 Duo: 21 × 8 × 196 = 32,928 actions
"""

import numpy as np
from typing import Optional, List, Tuple
from dataclasses import dataclass

from blokus.game import Game, Move
from blokus.pieces import PieceType, PIECES, get_piece
from blokus.rl.encoding import ActionEncoding


# Maximum orientations per piece (some pieces have fewer due to symmetry)
MAX_ORIENTATIONS = ActionEncoding.NUM_ORIENTATIONS


@dataclass
class ActionSpaceConfig:
    """Configuration for action space encoding."""
    board_size: int = 20
    num_piece_types: int = ActionEncoding.NUM_PIECES
    max_orientations: int = ActionEncoding.NUM_ORIENTATIONS
    
    @property
    def total_actions(self) -> int:
        """Total number of possible actions."""
        return ActionEncoding.get_size(self.board_size)


def get_action_space_size(board_size: int = 20) -> int:
    """Get the total action space size for a given board size."""
    return ActionEncoding.get_size(board_size)


def encode_action(move: Move, board_size: int = 20) -> int:
    """
    Encode a Move object to a flat action index.
    
    Args:
        move: The Move to encode
        board_size: Size of the board
    
    Returns:
        Integer action index
    """
    piece_idx = list(PieceType).index(move.piece_type)
    return ActionEncoding.encode(
        piece_idx=piece_idx,
        orientation=move.orientation,
        row=move.row,
        col=move.col,
        board_size=board_size
    )


def decode_action(action: int, game: Game) -> Optional[Move]:
    """
    Decode an action index to a Move object.
    
    Args:
        action: Integer action index
        game: Current game state (needed for player_id and validation)
    
    Returns:
        Move object, or None if action is invalid
    """
    board_size = game.board.size
    
    # Decode using helper
    piece_idx, orientation, row, col = ActionEncoding.decode(action, board_size)
    
    # Validate piece index
    piece_types = list(PieceType)
    if piece_idx >= len(piece_types):
        return None
    
    piece_type = piece_types[piece_idx]
    
    # Check if this orientation exists for this piece
    piece_variants = PIECES.get(piece_type, [])
    if orientation >= len(piece_variants):
        return None
    
    return Move(
        player_id=game.current_player_idx,
        piece_type=piece_type,
        orientation=orientation,
        row=row,
        col=col
    )


def get_action_mask(game: Game) -> np.ndarray:
    """
    Generate a boolean mask indicating valid actions.
    
    Args:
        game: Current game state
    
    Returns:
        Boolean numpy array of shape (action_space_size,)
    """
    board_size = game.board.size
    action_space_size = get_action_space_size(board_size)
    mask = np.zeros(action_space_size, dtype=bool)
    
    # Get all valid moves from game
    valid_moves = game.get_valid_moves()
    
    # Encode each valid move and set mask
    for move in valid_moves:
        action = encode_action(move, board_size)
        if 0 <= action < action_space_size:
            mask[action] = True
    
    return mask


def get_valid_actions(game: Game) -> List[int]:
    """
    Get list of valid action indices.
    
    Args:
        game: Current game state
    
    Returns:
        List of valid action indices
    """
    mask = get_action_mask(game)
    return list(np.where(mask)[0])


def count_valid_actions(game: Game) -> int:
    """
    Count number of valid actions without creating full mask.
    
    Args:
        game: Current game state
    
    Returns:
        Number of valid actions
    """
    return len(game.get_valid_moves())
