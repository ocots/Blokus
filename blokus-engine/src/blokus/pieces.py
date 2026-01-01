"""
Blokus pieces definitions.

Each piece is defined by its shape (coordinates relative to origin)
and can be rotated (4 rotations) and flipped (2 states) for up to 8 orientations.
"""

from dataclasses import dataclass
from enum import Enum
from typing import List, Tuple, Set, FrozenSet
import numpy as np


class PieceType(Enum):
    """All 21 Blokus piece types."""
    # Monomino (1 square)
    I1 = "I1"
    
    # Domino (2 squares)
    I2 = "I2"
    
    # Triminoes (3 squares)
    I3 = "I3"
    L3 = "L3"
    
    # Tetrominoes (4 squares)
    I4 = "I4"
    L4 = "L4"
    T4 = "T4"
    O4 = "O4"
    S4 = "S4"
    
    # Pentominoes (5 squares)
    F = "F"
    I5 = "I5"
    L5 = "L5"
    N = "N"
    P = "P"
    T5 = "T5"
    U = "U"
    V = "V"
    W = "W"
    X = "X"
    Y = "Y"
    Z = "Z"


# Base shapes as list of (row, col) coordinates relative to origin (0,0)
# Origin is chosen to be top-left of bounding box
PIECE_SHAPES: dict[PieceType, List[Tuple[int, int]]] = {
    # Monomino
    PieceType.I1: [(0, 0)],
    
    # Domino
    PieceType.I2: [(0, 0), (0, 1)],
    
    # Triminoes
    PieceType.I3: [(0, 0), (0, 1), (0, 2)],
    PieceType.L3: [(0, 0), (0, 1), (1, 0)],
    
    # Tetrominoes
    PieceType.I4: [(0, 0), (0, 1), (0, 2), (0, 3)],
    PieceType.L4: [(0, 0), (1, 0), (2, 0), (2, 1)],
    PieceType.T4: [(0, 1), (1, 0), (1, 1), (1, 2)],
    PieceType.O4: [(0, 0), (0, 1), (1, 0), (1, 1)],
    PieceType.S4: [(0, 0), (0, 1), (1, 1), (1, 2)],
    
    # Pentominoes
    PieceType.F: [(0, 1), (0, 2), (1, 0), (1, 1), (2, 1)],
    PieceType.I5: [(0, 0), (0, 1), (0, 2), (0, 3), (0, 4)],
    PieceType.L5: [(0, 0), (1, 0), (2, 0), (3, 0), (3, 1)],
    PieceType.N: [(0, 0), (1, 0), (1, 1), (2, 1), (3, 1)],
    PieceType.P: [(0, 0), (0, 1), (1, 0), (1, 1), (2, 0)],
    PieceType.T5: [(0, 0), (0, 1), (0, 2), (1, 1), (2, 1)],
    PieceType.U: [(0, 0), (0, 2), (1, 0), (1, 1), (1, 2)],
    PieceType.V: [(0, 0), (1, 0), (2, 0), (2, 1), (2, 2)],
    PieceType.W: [(0, 0), (1, 0), (1, 1), (2, 1), (2, 2)],
    PieceType.X: [(0, 1), (1, 0), (1, 1), (1, 2), (2, 1)],
    PieceType.Y: [(0, 1), (1, 0), (1, 1), (2, 1), (3, 1)],
    PieceType.Z: [(0, 0), (0, 1), (1, 1), (2, 1), (2, 2)],
}


def _normalize_coords(coords: List[Tuple[int, int]]) -> FrozenSet[Tuple[int, int]]:
    """Normalize coordinates to have minimum at (0, 0)."""
    if not coords:
        return frozenset()
    min_row = min(r for r, c in coords)
    min_col = min(c for r, c in coords)
    return frozenset((r - min_row, c - min_col) for r, c in coords)


def _rotate_90(coords: FrozenSet[Tuple[int, int]]) -> FrozenSet[Tuple[int, int]]:
    """Rotate coordinates 90 degrees clockwise."""
    rotated = [(c, -r) for r, c in coords]
    return _normalize_coords(rotated)


def _flip_horizontal(coords: FrozenSet[Tuple[int, int]]) -> FrozenSet[Tuple[int, int]]:
    """Flip coordinates horizontally."""
    if not coords:
        return frozenset()
    max_col = max(c for r, c in coords)
    flipped = [(r, max_col - c) for r, c in coords]
    return _normalize_coords(flipped)


def _generate_all_orientations(base_coords: List[Tuple[int, int]]) -> List[FrozenSet[Tuple[int, int]]]:
    """Generate all unique orientations (up to 8) for a piece."""
    orientations: Set[FrozenSet[Tuple[int, int]]] = set()
    
    normalized = _normalize_coords(base_coords)
    current = normalized
    
    # 4 rotations
    for _ in range(4):
        orientations.add(current)
        current = _rotate_90(current)
    
    # Flip and 4 more rotations
    flipped = _flip_horizontal(normalized)
    current = flipped
    for _ in range(4):
        orientations.add(current)
        current = _rotate_90(current)
    
    return list(orientations)


@dataclass(frozen=True)
class Piece:
    """
    Represents a Blokus piece with a specific orientation.
    
    Attributes:
        piece_type: The type of piece (I1, L3, etc.)
        coords: Frozen set of (row, col) coordinates relative to top-left
        orientation_id: Index of this orientation (0 to num_orientations-1)
    """
    piece_type: PieceType
    coords: FrozenSet[Tuple[int, int]]
    orientation_id: int
    
    @property
    def size(self) -> int:
        """Number of squares in this piece."""
        return len(self.coords)
    
    @property
    def coords_list(self) -> List[Tuple[int, int]]:
        """Coordinates as a sorted list."""
        return sorted(self.coords)
    
    def get_corners(self) -> Set[Tuple[int, int]]:
        """
        Get diagonal corner positions (where next pieces can connect).
        Returns positions that are diagonally adjacent but not edge-adjacent.
        """
        corners: Set[Tuple[int, int]] = set()
        for r, c in self.coords:
            # Diagonal neighbors
            for dr, dc in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
                corner = (r + dr, c + dc)
                if corner not in self.coords:
                    # Check it's not edge-adjacent to any piece square
                    edge_adj = False
                    for er, ec in self.coords:
                        if abs(corner[0] - er) + abs(corner[1] - ec) == 1:
                            edge_adj = True
                            break
                    if not edge_adj:
                        corners.add(corner)
        return corners
    
    def get_edges(self) -> Set[Tuple[int, int]]:
        """Get all edge-adjacent positions (where pieces cannot touch)."""
        edges: Set[Tuple[int, int]] = set()
        for r, c in self.coords:
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                edge = (r + dr, c + dc)
                if edge not in self.coords:
                    edges.add(edge)
        return edges
    
    def translate(self, row_offset: int, col_offset: int) -> Set[Tuple[int, int]]:
        """Get coordinates translated by offset."""
        return {(r + row_offset, c + col_offset) for r, c in self.coords}
    
    def bounding_box(self) -> Tuple[int, int]:
        """Get (height, width) of bounding box."""
        if not self.coords:
            return (0, 0)
        max_row = max(r for r, c in self.coords)
        max_col = max(c for r, c in self.coords)
        return (max_row + 1, max_col + 1)
    
    def to_matrix(self) -> np.ndarray:
        """Convert piece to a 2D numpy array (1 where piece exists, 0 elsewhere)."""
        height, width = self.bounding_box()
        matrix = np.zeros((height, width), dtype=np.int8)
        for r, c in self.coords:
            matrix[r, c] = 1
        return matrix
    
    def __repr__(self) -> str:
        return f"Piece({self.piece_type.value}, orientation={self.orientation_id})"


# Generate all pieces with all orientations
def _build_pieces_dict() -> dict[PieceType, List[Piece]]:
    """Build dictionary of all pieces with all their orientations."""
    pieces: dict[PieceType, List[Piece]] = {}
    
    for piece_type, base_coords in PIECE_SHAPES.items():
        orientations = _generate_all_orientations(base_coords)
        pieces[piece_type] = [
            Piece(piece_type=piece_type, coords=coords, orientation_id=i)
            for i, coords in enumerate(orientations)
        ]
    
    return pieces


# Global dictionary: PieceType -> List[Piece] (all orientations)
PIECES: dict[PieceType, List[Piece]] = _build_pieces_dict()


def get_piece(piece_type: PieceType, orientation: int = 0) -> Piece:
    """Get a specific piece with a specific orientation."""
    orientations = PIECES[piece_type]
    return orientations[orientation % len(orientations)]


def get_all_pieces() -> List[Piece]:
    """Get all 21 pieces in their default orientation."""
    return [orientations[0] for orientations in PIECES.values()]


def num_orientations(piece_type: PieceType) -> int:
    """Get number of unique orientations for a piece type."""
    return len(PIECES[piece_type])
