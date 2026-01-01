"""
Blokus placement rules validation.

Validates whether a piece can be placed at a given position on the board.
"""

from typing import Set, Tuple

from blokus.pieces import Piece
from blokus.board import Board, STARTING_CORNERS


def is_valid_placement(
    board: Board,
    piece: Piece,
    row: int,
    col: int,
    player_id: int,
    is_first_move: bool = False
) -> bool:
    """
    Check if a piece can be placed at the given position.
    
    Rules:
    1. All piece cells must be within board bounds
    2. All piece cells must be empty
    3. Piece must not touch player's own pieces by edge
    4. Piece must touch player's own pieces by corner (diagonal)
       OR cover starting corner on first move
    
    Args:
        board: Current board state
        piece: Piece to place
        row, col: Position (top-left of piece bounding box)
        player_id: Player making the move (0-3)
        is_first_move: Whether this is the player's first move
    
    Returns:
        True if placement is valid, False otherwise
    """
    # Get absolute positions
    positions = piece.translate(row, col)
    
    # Rule 1 & 2: Check all positions are valid and empty
    for r, c in positions:
        if not board.is_valid_position(r, c):
            return False
        if not board.is_empty(r, c):
            return False
    
    # Get player's current pieces
    player_cells = board.get_player_cells(player_id)
    
    if is_first_move or not player_cells:
        # First move: must cover starting corner
        starting_corner = STARTING_CORNERS[player_id]
        if starting_corner not in positions:
            return False
        return True
    
    # Rule 3: Must not touch own pieces by edge
    player_edges = board.get_player_edges(player_id)
    if positions & player_edges:  # Intersection
        return False
    
    # Rule 4: Must touch own pieces by at least one corner
    player_corners = board.get_player_corners(player_id)
    if not (positions & player_corners):  # No intersection
        return False
    
    return True


def get_valid_placements(
    board: Board,
    piece: Piece,
    player_id: int,
    is_first_move: bool = False
) -> Set[Tuple[int, int]]:
    """
    Get all valid positions where a piece can be placed.
    
    Args:
        board: Current board state
        piece: Piece to check
        player_id: Player making the move
        is_first_move: Whether this is the player's first move
    
    Returns:
        Set of valid (row, col) positions
    """
    valid_positions: Set[Tuple[int, int]] = set()
    
    if is_first_move or not board.get_player_cells(player_id):
        # First move: try positions around starting corner
        starting_corner = STARTING_CORNERS[player_id]
        for r, c in piece.coords:
            # Position piece so this cell covers starting corner
            pos_row = starting_corner[0] - r
            pos_col = starting_corner[1] - c
            if is_valid_placement(board, piece, pos_row, pos_col, player_id, is_first_move=True):
                valid_positions.add((pos_row, pos_col))
    else:
        # Normal move: try positions around player's corners
        corners = board.get_player_corners(player_id)
        
        for corner in corners:
            # Try placing piece so one of its cells is at this corner
            for r, c in piece.coords:
                pos_row = corner[0] - r
                pos_col = corner[1] - c
                if is_valid_placement(board, piece, pos_row, pos_col, player_id, is_first_move=False):
                    valid_positions.add((pos_row, pos_col))
    
    return valid_positions


def has_valid_move(board: Board, pieces: list[Piece], player_id: int, is_first_move: bool = False) -> bool:
    """
    Check if a player has any valid moves with their remaining pieces.
    
    Args:
        board: Current board state
        pieces: List of remaining pieces (all orientations will be checked)
        player_id: Player to check
        is_first_move: Whether this is the player's first move
    
    Returns:
        True if at least one valid move exists
    """
    for piece in pieces:
        if get_valid_placements(board, piece, player_id, is_first_move):
            return True
    return False
