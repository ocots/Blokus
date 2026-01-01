from dataclasses import dataclass, field
from typing import Set, Optional, Dict, Any
from blokus.pieces import PieceType, PIECES
from blokus.player_types import PlayerType, PlayerStatus


@dataclass
class Player:
    """
    Unified Player class.
    
    Responsibility: Centralize all player data and state.
    Follows SOLID principles:
    - SRP: Only player data and actions
    - OCP: Extensible via PlayerType enum
    - LSP: Consistent interface for all player types
    """
    
    # === IDENTITY (SRP: identification data) ===
    id: int
    name: str
    color: str
    type: PlayerType = PlayerType.HUMAN
    persona: Optional[str] = None
    
    # === GAME STATE (SRP: game data) ===
    remaining_pieces: Set[PieceType] = field(default_factory=set)
    has_passed: bool = False
    last_piece_was_monomino: bool = False
    status: PlayerStatus = PlayerStatus.WAITING
    
    # === METADATA (SRP: calculated data) ===
    score: int = 0
    turn_order: Optional[int] = None
    
    def __post_init__(self):
        """Initialize pieces if necessary."""
        if not self.remaining_pieces:
            self.remaining_pieces = set(PieceType)
    
    # === PROPERTIES (POLA: predictable names) ===
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
    
    @property
    def is_ai(self) -> bool:
        """This player is an AI."""
        return self.type == PlayerType.AI
    
    @property
    def is_human(self) -> bool:
        """This player is human."""
        return self.type == PlayerType.HUMAN
    
    @property
    def is_shared(self) -> bool:
        """This player is shared (3-player mode)."""
        return self.type == PlayerType.SHARED
    
    @property
    def display_name(self) -> str:
        """Display name with persona for AI."""
        if self.is_ai and self.persona:
            return f"{self.name} ({self.persona})"
        return self.name
    
    # === GAME ACTIONS (SRP: player actions) ===
    def play_piece(self, piece_type: PieceType) -> bool:
        """
        Play a piece.
        
        Args:
            piece_type: Type of piece to play
            
        Returns:
            True if piece was played, False otherwise
        """
        if piece_type in self.remaining_pieces:
            self.remaining_pieces.remove(piece_type)
            self.last_piece_was_monomino = (piece_type == PieceType.I1)
            return True
        return False
    
    def pass_turn(self) -> None:
        """Pass this player's turn."""
        self.has_passed = True
        self.status = PlayerStatus.PASSED
    
    def calculate_score(self) -> int:
        """
        Calculate the player's score.
        
        Scoring:
        - Each remaining square = -1 point
        - All pieces placed = +15 bonus
        - Last piece was monomino = +5 bonus
        
        Returns:
            The calculated score
        """
        score = -self.squares_remaining
        
        if self.pieces_count == 0:
            score += 15  # All pieces placed bonus
            if self.last_piece_was_monomino:
                score += 5  # Monomino last bonus
        
        self.score = score
        return score
    
    # === SERIALIZATION (SRP: data conversion) ===
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API."""
        return {
            "id": self.id,
            "name": self.name,
            "color": self.color,
            "type": self.type.value,
            "persona": self.persona,
            "remaining_pieces": sorted([pt.name for pt in self.remaining_pieces]),
            "has_passed": self.has_passed,
            "status": self.status.value,
            "score": self.score,
            "pieces_count": self.pieces_count,
            "squares_remaining": self.squares_remaining,
            "display_name": self.display_name,
            "is_ai": self.is_ai,
            "is_human": self.is_human,
            "is_shared": self.is_shared,
            "turn_order": self.turn_order
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Player":
        """Create Player from dictionary."""
        pieces = {PieceType[name] for name in data.get("remaining_pieces", [])}
        
        return cls(
            id=data["id"],
            name=data["name"],
            color=data["color"],
            type=PlayerType(data["type"]),
            persona=data.get("persona"),
            remaining_pieces=pieces,
            has_passed=data.get("has_passed", False),
            status=PlayerStatus(data.get("status", "waiting")),
            score=data.get("score", 0),
            turn_order=data.get("turn_order")
        )
