"""
Blokus placement rules validation.

Validates whether a piece can be placed at a given position on the board.
"""

from typing import Set, Tuple, Optional

from blokus.pieces import Piece
from blokus.board import Board, STARTING_CORNERS


def get_placement_rejection_reason(
    board: Board,
    piece: Piece,
    row: int,
    col: int,
    player_id: int,
    is_first_move: bool = False
) -> Optional[str]:
    """
    Check if a piece can be placed and return reason if not.
    Returns None if placement is valid.
    """
    # Get absolute positions
    # positions = piece.translate(row, col) # Avoid list creation if possible
    
    # Combined Rule 1 & 2: Check bounds and vacancy in one pass
    # Using piece.coords directly to avoid intermediate list from translate()
    for r, c in piece.coords:
        abs_r, abs_c = row + r, col + c
        # Direct bounds check is faster than board.is_valid_position
        if not (0 <= abs_r < board.size and 0 <= abs_c < board.size):
            return f"Position ({abs_r}, {abs_c}) is out of bounds"
        # Direct grid access is faster than board.is_empty
        if board.grid[abs_r, abs_c] != 0: # 0 is BoardCell.EMPTY
            return f"Position ({abs_r}, {abs_c}) is already occupied"
    
    # We need the set for set operations below
    positions = piece.translate(row, col)
    
    # Get player's current pieces (Cached in Board)
    player_cells = board.get_player_cells(player_id)
    
    if is_first_move or not player_cells:
        # First move: must cover starting corner
        starting_corner = board.starting_corners.get(player_id) or STARTING_CORNERS.get(player_id)
        if starting_corner is None:
            return f"No starting corner defined for player {player_id}"
        if starting_corner not in positions:
            return f"First move must cover starting corner {starting_corner}"
        return None
    
    # Rule 3: Must not touch own pieces by edge (Cached in Board)
    player_edges = board.get_player_edges(player_id)
    if not positions.isdisjoint(player_edges):
        return "Piece touches own pieces by edge"
    
    # Rule 4: Must touch own pieces by at least one corner (Cached in Board)
    player_corners = board.get_player_corners(player_id)
    if positions.isdisjoint(player_corners):
        return "Piece doesn't touch any diagonal corner"
    
    return None


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
    """
    return get_placement_rejection_reason(board, piece, row, col, player_id, is_first_move) is None


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
    
    # Use board's starting corners, not the global constant
    starting_corners = board.starting_corners or STARTING_CORNERS
    
    if is_first_move or not board.get_player_cells(player_id):
        # First move: try positions around starting corner
        starting_corner = starting_corners.get(player_id)
        if starting_corner is None:
            return valid_positions
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
