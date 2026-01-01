"""
Blokus game board.

The board is a 20x20 grid where pieces are placed.
Each cell can be empty (0) or occupied by a player (1-4).
"""

from dataclasses import dataclass, field
from typing import List, Set, Tuple, Optional
import numpy as np

from blokus.pieces import Piece


BOARD_SIZE = 20

# Starting corners for each player (0-indexed)
STARTING_CORNERS: dict[int, Tuple[int, int]] = {
    0: (0, 0),                          # Player 0: top-left
    1: (0, BOARD_SIZE - 1),             # Player 1: top-right
    2: (BOARD_SIZE - 1, BOARD_SIZE - 1),# Player 2: bottom-right
    3: (BOARD_SIZE - 1, 0),             # Player 3: bottom-left
}


@dataclass
class Board:
    """
    Represents the Blokus game board.
    
    Attributes:
        grid: 2D numpy array where 0=empty, 1-4=player occupying
        size: Board dimension (default 20)
    """
    size: int = BOARD_SIZE
    grid: np.ndarray = field(default=None)
    
    def __post_init__(self):
        if self.grid is None:
            self.grid = np.zeros((self.size, self.size), dtype=np.int8)
    
    def copy(self) -> "Board":
        """Create a deep copy of the board."""
        new_board = Board(size=self.size)
        new_board.grid = self.grid.copy()
        return new_board
    
    def is_empty(self, row: int, col: int) -> bool:
        """Check if a cell is empty."""
        if not self.is_valid_position(row, col):
            return False
        return self.grid[row, col] == 0
    
    def is_valid_position(self, row: int, col: int) -> bool:
        """Check if position is within board bounds."""
        return 0 <= row < self.size and 0 <= col < self.size
    
    def get_cell(self, row: int, col: int) -> int:
        """Get the value at a cell (0=empty, 1-4=player)."""
        if not self.is_valid_position(row, col):
            return -1
        return self.grid[row, col]
    
    def place_piece(self, piece: Piece, row: int, col: int, player_id: int) -> bool:
        """
        Place a piece on the board.
        
        Args:
            piece: The piece to place
            row, col: Top-left position for the piece
            player_id: Player ID (0-3)
        
        Returns:
            True if placement was successful, False otherwise
        """
        # Get absolute positions
        positions = piece.translate(row, col)
        
        # Check all positions are valid and empty
        for r, c in positions:
            if not self.is_valid_position(r, c) or not self.is_empty(r, c):
                return False
        
        # Place the piece
        for r, c in positions:
            self.grid[r, c] = player_id + 1  # Store as 1-4
        
        return True
    
    def get_player_cells(self, player_id: int) -> Set[Tuple[int, int]]:
        """Get all cells occupied by a player."""
        positions = np.argwhere(self.grid == player_id + 1)
        return {(int(r), int(c)) for r, c in positions}
    
    def get_player_corners(self, player_id: int) -> Set[Tuple[int, int]]:
        """
        Get all valid corner positions where a player can connect.
        These are diagonal to existing pieces but not edge-adjacent.
        """
        player_cells = self.get_player_cells(player_id)
        
        if not player_cells:
            # First move: must use starting corner
            return {STARTING_CORNERS[player_id]}
        
        corners: Set[Tuple[int, int]] = set()
        
        for r, c in player_cells:
            # Check diagonal neighbors
            for dr, dc in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
                nr, nc = r + dr, c + dc
                if not self.is_valid_position(nr, nc):
                    continue
                if not self.is_empty(nr, nc):
                    continue
                    
                # Check it's not edge-adjacent to any of player's pieces
                is_edge_adjacent = False
                for er, ec in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    adj_r, adj_c = nr + er, nc + ec
                    if (adj_r, adj_c) in player_cells:
                        is_edge_adjacent = True
                        break
                
                if not is_edge_adjacent:
                    corners.add((nr, nc))
        
        return corners
    
    def get_player_edges(self, player_id: int) -> Set[Tuple[int, int]]:
        """Get all positions that are edge-adjacent to player's pieces."""
        player_cells = self.get_player_cells(player_id)
        edges: Set[Tuple[int, int]] = set()
        
        for r, c in player_cells:
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nr, nc = r + dr, c + dc
                if self.is_valid_position(nr, nc) and (nr, nc) not in player_cells:
                    edges.add((nr, nc))
        
        return edges
    
    def count_occupied(self) -> int:
        """Count total occupied cells."""
        return int(np.count_nonzero(self.grid))
    
    def count_player_cells(self, player_id: int) -> int:
        """Count cells occupied by a specific player."""
        return int(np.count_nonzero(self.grid == player_id + 1))
    
    def to_string(self) -> str:
        """Convert board to a string representation for display."""
        symbols = {0: ".", 1: "1", 2: "2", 3: "3", 4: "4"}
        lines = []
        
        # Column headers
        header = "   " + " ".join(f"{i:2d}" for i in range(self.size))
        lines.append(header)
        
        for r in range(self.size):
            row_str = f"{r:2d} "
            for c in range(self.size):
                row_str += f" {symbols[self.grid[r, c]]} "
            lines.append(row_str)
        
        return "\n".join(lines)
    
    def __repr__(self) -> str:
        occupied = self.count_occupied()
        return f"Board({self.size}x{self.size}, {occupied} cells occupied)"
