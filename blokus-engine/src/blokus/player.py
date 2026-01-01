from dataclasses import dataclass, field
from typing import Set, List
from blokus.pieces import PieceType, PIECES

@dataclass
class Player:
    """Represents a player in the game."""
    id: int
    remaining_pieces: Set[PieceType] = field(default_factory=set)
    has_passed: bool = False
    last_piece_was_monomino: bool = False
    
    def __post_init__(self):
        if not self.remaining_pieces:
            self.remaining_pieces = set(PieceType)
    
    @property
    def pieces_count(self) -> int:
        """Number of remaining pieces."""
        return len(self.remaining_pieces)
    
    @property
    def squares_remaining(self) -> int:
        """Total squares in remaining pieces."""
        total = 0
        for pt in self.remaining_pieces:
            piece = PIECES[pt][0]  # Any orientation, same size
            total += piece.size
        return total
