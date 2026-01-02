"""
Action encoding constants and logic for Reinforcement Learning.
"""

from typing import Tuple, Optional
from blokus.game import Move
from blokus.pieces import PieceType, PIECES

class ActionEncoding:
    """
    Constants and helper methods for action space encoding.
    
    Action Space Structure:
    - Discrete space of size: NUM_PIECES * NUM_ORIENTATIONS * BOARD_SIZE^2
    - Encoded as a single integer index.
    """
    NUM_PIECES = 21
    NUM_ORIENTATIONS = 8
    
    @staticmethod
    def get_size(board_size: int) -> int:
        """Get the total size of the action space."""
        return ActionEncoding.NUM_PIECES * ActionEncoding.NUM_ORIENTATIONS * board_size * board_size
    
    @staticmethod
    def encode(piece_idx: int, orientation: int, row: int, col: int, board_size: int) -> int:
        """
        Encode a move into a single integer action ID.
        
        Formula:
        action = piece_idx * (8 * S^2) + orientation * S^2 + row * S + col
        """
        spatial_size = board_size * board_size
        return (
            piece_idx * (ActionEncoding.NUM_ORIENTATIONS * spatial_size) +
            orientation * spatial_size +
            row * board_size +
            col
        )
    
    @staticmethod
    def decode(action: int, board_size: int) -> Tuple[int, int, int, int]:
        """
        Decode an action ID into (piece_idx, orientation, row, col).
        """
        spatial_size = board_size * board_size
        
        # Decode piece index
        piece_idx = action // (ActionEncoding.NUM_ORIENTATIONS * spatial_size)
        remainder = action % (ActionEncoding.NUM_ORIENTATIONS * spatial_size)
        
        # Decode orientation
        orientation = remainder // spatial_size
        remainder = remainder % spatial_size
        
        # Decode position
        row = remainder // board_size
        col = remainder % board_size
        
        return piece_idx, orientation, row, col
