"""
Proposition d'architecture unifiée pour la gestion des joueurs.

Centralise toutes les informations d'un joueur dans une seule classe Player.
"""

from dataclasses import dataclass, field
from typing import Set, Optional, Dict, Any
from enum import Enum
from blokus.pieces import PieceType, PIECES

class PlayerType(Enum):
    HUMAN = "human"
    AI = "ai"
    SHARED = "shared"

class PlayerStatus(Enum):
    WAITING = "waiting"
    PLAYING = "playing"
    PASSED = "passed"
    FINISHED = "finished"

@dataclass
class Player:
    """
    Classe Player unifiée qui centralise toutes les informations d'un joueur.
    
    Cette classe est utilisée partout:
    - Moteur de jeu (Python)
    - API (FastAPI)
    - Frontend (JavaScript/TypeScript)
    """
    
    # === IDENTITÉ ===
    id: int
    name: str
    color: str  # Hex color like "#3b82f6"
    type: PlayerType = PlayerType.HUMAN
    persona: Optional[str] = None  # "random", "aggressive", "defensive", etc.
    
    # === ÉTAT DU JEU ===
    remaining_pieces: Set[PieceType] = field(default_factory=set)
    has_passed: bool = False
    last_piece_was_monomino: bool = False
    status: PlayerStatus = PlayerStatus.WAITING
    
    # === MÉTADONNÉES ===
    score: int = 0
    turn_order: Optional[int] = None  # Position dans l'ordre de jeu (0-based)
    
    def __post_init__(self):
        if not self.remaining_pieces:
            self.remaining_pieces = set(PieceType)
    
    # === PROPERTIES ===
    @property
    def pieces_count(self) -> int:
        """Nombre de pièces restantes."""
        return len(self.remaining_pieces)
    
    @property
    def squares_remaining(self) -> int:
        """Total des carrés dans les pièces restantes."""
        total = 0
        for pt in self.remaining_pieces:
            piece = PIECES[pt][0]
            total += piece.size
        return total
    
    @property
    def is_ai(self) -> bool:
        """Ce joueur est une IA."""
        return self.type == PlayerType.AI
    
    @property
    def is_human(self) -> bool:
        """Ce joueur est humain."""
        return self.type == PlayerType.HUMAN
    
    @property
    def is_shared(self) -> bool:
        """Ce joueur est partagé (mode 3 joueurs)."""
        return self.type == PlayerType.SHARED
    
    @property
    def display_name(self) -> str:
        """Nom à afficher (avec type si IA)."""
        if self.is_ai and self.persona:
            return f"{self.name} ({self.persona})"
        return self.name
    
    # === MÉTHODES DE JEU ===
    def start_turn(self):
        """Démarre le tour de ce joueur."""
        self.status = PlayerStatus.PLAYING
    
    def end_turn(self):
        """Termine le tour de ce joueur."""
        self.status = PlayerStatus.WAITING
    
    def pass_turn(self):
        """Passe le tour de ce joueur."""
        self.has_passed = True
        self.status = PlayerStatus.PASSED
    
    def play_piece(self, piece_type: PieceType):
        """Joue une pièce."""
        if piece_type in self.remaining_pieces:
            self.remaining_pieces.remove(piece_type)
            self.last_piece_was_monomino = (piece_type == PieceType.I1)
            return True
        return False
    
    def calculate_score(self) -> int:
        """Calcule le score du joueur."""
        score = -self.squares_remaining
        
        if self.pieces_count == 0:
            score += 15  # Bonus toutes pièces placées
            if self.last_piece_was_monomino:
                score += 5  # Bonus monomino en dernier
        
        self.score = score
        return score
    
    # === SÉRIALISATION ===
    def to_dict(self) -> Dict[str, Any]:
        """Convertit en dictionnaire pour l'API."""
        return {
            "id": self.id,
            "name": self.name,
            "color": self.color,
            "type": self.type.value,
            "persona": self.persona,
            "remaining_pieces": [pt.name for pt in self.remaining_pieces],
            "has_passed": self.has_passed,
            "status": self.status.value,
            "score": self.score,
            "pieces_count": self.pieces_count,
            "squares_remaining": self.squares_remaining,
            "display_name": self.display_name,
            "is_ai": self.is_ai,
            "is_human": self.is_human,
            "is_shared": self.is_shared
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Player":
        """Crée un Player depuis un dictionnaire."""
        # Conversion des pièces
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
            score=data.get("score", 0)
        )
    
    def __repr__(self) -> str:
        return f"Player(id={self.id}, name='{self.name}', type={self.type.value}, color='{self.color}')"


# === FACTORY POUR CRÉER DES JOUEURS ===

class PlayerFactory:
    """Factory pour créer des joueurs avec des configurations standards."""
    
    # Couleurs standard du jeu
    DEFAULT_COLORS = [
        "#3b82f6",  # Blue
        "#22c55e",  # Green  
        "#eab308",  # Yellow
        "#ef4444"   # Red
    ]
    
    @classmethod
    def create_human_player(cls, id: int, name: str, color: str = None) -> Player:
        """Crée un joueur humain."""
        if color is None:
            color = cls.DEFAULT_COLORS[id % len(cls.DEFAULT_COLORS)]
        
        return Player(
            id=id,
            name=name,
            color=color,
            type=PlayerType.HUMAN
        )
    
    @classmethod
    def create_ai_player(cls, id: int, persona: str, color: str = None) -> Player:
        """Crée un joueur IA."""
        if color is None:
            color = cls.DEFAULT_COLORS[id % len(cls.DEFAULT_COLORS)]
        
        ai_names = {
            "random": "Bot Aléatoire",
            "aggressive": "Bot Agressif", 
            "defensive": "Bot Défensif",
            "efficient": "Bot Efficace"
        }
        
        return Player(
            id=id,
            name=ai_names.get(persona, f"Bot {persona}"),
            color=color,
            type=PlayerType.AI,
            persona=persona
        )
    
    @classmethod
    def create_shared_player(cls, id: int, color: str = None) -> Player:
        """Crée un joueur partagé (mode 3 joueurs)."""
        if color is None:
            color = cls.DEFAULT_COLORS[id % len(cls.DEFAULT_COLORS)]
        
        return Player(
            id=id,
            name="Neutre (Partagé)",
            color=color,
            type=PlayerType.SHARED
        )
    
    @classmethod
    def create_players_from_config(cls, player_configs: list) -> list[Player]:
        """Crée une liste de joueurs depuis une configuration."""
        players = []
        
        for i, config in enumerate(player_configs):
            if config["type"] == "human":
                player = cls.create_human_player(i, config["name"])
            elif config["type"] == "ai":
                player = cls.create_ai_player(i, config["persona"])
            elif config["type"] == "shared":
                player = cls.create_shared_player(i)
            else:
                raise ValueError(f"Unknown player type: {config['type']}")
            
            players.append(player)
        
        return players


# === GAME MANAGER AVEC LISTE DE JOUEURS ===

@dataclass
class GameManager:
    """
    Gestionnaire de jeu avec une liste ordonnée de joueurs.
    
    L'ordre dans la liste détermine l'ordre de jeu.
    Plus besoin de logique complexe sur les IDs.
    """
    
    players: list[Player] = field(default_factory=list)
    current_player_index: int = 0
    
    def __init__(self, players: list[Player] = None, starting_player_index: int = 0):
        if players is None:
            players = []
        
        self.players = players
        self.current_player_index = starting_player_index
        
        # Définir l'ordre de tour pour chaque joueur
        for i, player in enumerate(self.players):
            player.turn_order = i
    
    @property
    def current_player(self) -> Player:
        """Joueur actuel."""
        return self.players[self.current_player_index]
    
    def get_player_by_id(self, player_id: int) -> Optional[Player]:
        """Récupère un joueur par son ID."""
        for player in self.players:
            if player.id == player_id:
                return player
        return None
    
    def get_player_order(self) -> list[Player]:
        """Retourne les joueurs dans l'ordre de jeu."""
        return self.players.copy()
    
    def next_turn(self) -> Player:
        """Passe au joueur suivant."""
        self.current_player_index = (self.current_player_index + 1) % len(self.players)
        return self.current_player
    
    def set_starting_player(self, player_id: int):
        """Définit le joueur de départ."""
        for i, player in enumerate(self.players):
            if player.id == player_id:
                self.current_player_index = i
                return
        raise ValueError(f"Player {player_id} not found")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit en dictionnaire pour l'API."""
        return {
            "players": [player.to_dict() for player in self.players],
            "current_player_index": self.current_player_index,
            "current_player": self.current_player.to_dict()
        }
