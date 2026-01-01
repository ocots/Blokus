# Plan d'Action : Refactoring Architecture Player & GameManager

## 📋 Vue d'Ensemble

Ce plan d'action détaille l'implémentation de l'architecture unifiée des joueurs et du GameManager, en suivant les principes SOLID et les bonnes pratiques de test du projet Blokus RL.

---

## 🎯 Objectifs Qualité

### Principes SOLID à Respecter

- **SRP** : Chaque classe a une seule responsabilité
  - `Player` : État et données d'un joueur
  - `GameManager` : Gestion de l'ordre et des tours
  - `PlayerFactory` : Création de joueurs
  - `StateMachine` : Gestion des transitions d'états

- **OCP** : Extensible sans modification
  - Nouveaux types de joueurs via `PlayerFactory`
  - Nouveaux états via `Enum` extension
  - Nouveaux handlers via injection

- **LSP** : Contrats respectés
  - Tous les `Player` ont la même interface
  - Toutes les `StateMachine` respectent le protocole

- **ISP** : Interfaces minimales
  - `Player` expose uniquement ce qui est nécessaire
  - `GameManager` ne force pas d'implémentations inutiles

- **DIP** : Dépendre des abstractions
  - Injection de dépendances partout
  - Protocols et ABC pour les interfaces

### Autres Principes

- **DRY** : Pas de duplication de logique
- **KISS** : Solutions simples et directes
- **YAGNI** : Implémenter uniquement le nécessaire
- **POLA** : Noms clairs et comportements prévisibles

---

## 📊 Phase 1 : Player Unifié (Priorité 1)

### 1.1 Créer les Enums et Types de Base

**Fichier** : `blokus-engine/src/blokus/player_types.py`

```python
from enum import Enum

class PlayerType(Enum):
    """Types de joueurs."""
    HUMAN = "human"
    AI = "ai"
    SHARED = "shared"

class PlayerStatus(Enum):
    """États d'un joueur."""
    WAITING = "waiting"
    PLAYING = "playing"
    PASSED = "passed"
    FINISHED = "finished"
```

**Tests** : `tests/test_player_types.py`
- [ ] Test des valeurs d'enum
- [ ] Test de sérialisation/désérialisation

**Principes** :
- ✅ SRP : Uniquement les définitions de types
- ✅ OCP : Extensible via ajout d'enum values

---

### 1.2 Refactorer la Classe Player

**Fichier** : `blokus-engine/src/blokus/player.py`

```python
from dataclasses import dataclass, field
from typing import Set, Optional, Dict, Any
from blokus.pieces import PieceType, PIECES
from blokus.player_types import PlayerType, PlayerStatus

@dataclass
class Player:
    """
    Classe Player unifiée.
    
    Responsabilité : Centraliser toutes les données et l'état d'un joueur.
    """
    # === IDENTITÉ (SRP: données d'identification) ===
    id: int
    name: str
    color: str
    type: PlayerType = PlayerType.HUMAN
    persona: Optional[str] = None
    
    # === ÉTAT DU JEU (SRP: données de jeu) ===
    remaining_pieces: Set[PieceType] = field(default_factory=set)
    has_passed: bool = False
    last_piece_was_monomino: bool = False
    status: PlayerStatus = PlayerStatus.WAITING
    
    # === MÉTADONNÉES (SRP: données calculées) ===
    score: int = 0
    turn_order: Optional[int] = None
    
    def __post_init__(self):
        """Initialisation des pièces si nécessaire."""
        if not self.remaining_pieces:
            self.remaining_pieces = set(PieceType)
    
    # === PROPERTIES (POLA: noms prévisibles) ===
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
        """Nom à afficher."""
        if self.is_ai and self.persona:
            return f"{self.name} ({self.persona})"
        return self.name
    
    # === MÉTHODES DE JEU (SRP: actions sur le joueur) ===
    def play_piece(self, piece_type: PieceType) -> bool:
        """
        Joue une pièce.
        
        Returns:
            True si la pièce a été jouée, False sinon
        """
        if piece_type in self.remaining_pieces:
            self.remaining_pieces.remove(piece_type)
            self.last_piece_was_monomino = (piece_type == PieceType.I1)
            return True
        return False
    
    def pass_turn(self) -> None:
        """Passe le tour de ce joueur."""
        self.has_passed = True
        self.status = PlayerStatus.PASSED
    
    def calculate_score(self) -> int:
        """
        Calcule le score du joueur.
        
        Returns:
            Le score calculé
        """
        score = -self.squares_remaining
        
        if self.pieces_count == 0:
            score += 15  # Bonus toutes pièces placées
            if self.last_piece_was_monomino:
                score += 5  # Bonus monomino en dernier
        
        self.score = score
        return score
    
    # === SÉRIALISATION (SRP: conversion de données) ===
    def to_dict(self) -> Dict[str, Any]:
        """Convertit en dictionnaire pour l'API."""
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
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Player":
        """Crée un Player depuis un dictionnaire."""
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
```

**Tests** : `tests/test_player.py`

```python
class TestPlayerInitialization:
    """Test de l'initialisation."""
    
    def test_default_player(self):
        """Joueur par défaut."""
        player = Player(id=0, name="Alice", color="#3b82f6")
        assert player.id == 0
        assert player.name == "Alice"
        assert player.type == PlayerType.HUMAN
        assert len(player.remaining_pieces) == 21
    
    def test_ai_player(self):
        """Joueur IA."""
        player = Player(id=1, name="Bot", color="#22c55e", 
                       type=PlayerType.AI, persona="random")
        assert player.is_ai
        assert not player.is_human
        assert player.display_name == "Bot (random)"

class TestPlayerProperties:
    """Test des propriétés calculées."""
    
    def test_pieces_count(self):
        """Comptage des pièces."""
        player = Player(id=0, name="Test", color="#fff")
        assert player.pieces_count == 21
        
        player.play_piece(PieceType.I1)
        assert player.pieces_count == 20
    
    def test_squares_remaining(self):
        """Comptage des carrés."""
        player = Player(id=0, name="Test", color="#fff")
        assert player.squares_remaining == 89

class TestPlayerActions:
    """Test des actions."""
    
    def test_play_piece(self):
        """Jouer une pièce."""
        player = Player(id=0, name="Test", color="#fff")
        assert player.play_piece(PieceType.I1)
        assert PieceType.I1 not in player.remaining_pieces
        assert player.last_piece_was_monomino
    
    def test_pass_turn(self):
        """Passer le tour."""
        player = Player(id=0, name="Test", color="#fff")
        player.pass_turn()
        assert player.has_passed
        assert player.status == PlayerStatus.PASSED

class TestPlayerScoring:
    """Test du calcul de score."""
    
    def test_initial_score(self):
        """Score initial."""
        player = Player(id=0, name="Test", color="#fff")
        assert player.calculate_score() == -89
    
    def test_all_pieces_bonus(self):
        """Bonus toutes pièces."""
        player = Player(id=0, name="Test", color="#fff")
        player.remaining_pieces.clear()
        assert player.calculate_score() == 15
    
    def test_monomino_bonus(self):
        """Bonus monomino."""
        player = Player(id=0, name="Test", color="#fff")
        player.remaining_pieces.clear()
        player.last_piece_was_monomino = True
        assert player.calculate_score() == 20

class TestPlayerSerialization:
    """Test de la sérialisation."""
    
    def test_to_dict(self):
        """Conversion en dict."""
        player = Player(id=0, name="Alice", color="#3b82f6")
        data = player.to_dict()
        assert data["id"] == 0
        assert data["name"] == "Alice"
        assert len(data["remaining_pieces"]) == 21
    
    def test_from_dict(self):
        """Création depuis dict."""
        data = {
            "id": 0,
            "name": "Alice",
            "color": "#3b82f6",
            "type": "human",
            "remaining_pieces": ["I1", "I2"]
        }
        player = Player.from_dict(data)
        assert player.id == 0
        assert player.pieces_count == 2
```

**Commandes de test** :
```bash
// turbo
source .venv/bin/activate && python -m pytest tests/test_player.py -v --tb=short
```

**Principes** :
- ✅ SRP : Responsabilités séparées (identité, état, actions, sérialisation)
- ✅ DRY : Pas de duplication avec properties
- ✅ POLA : Noms prévisibles (`is_*`, `get_*`, `calculate_*`)

---

### 1.3 Créer PlayerFactory

**Fichier** : `blokus-engine/src/blokus/player_factory.py`

```python
from typing import List, Dict, Any
from blokus.player import Player
from blokus.player_types import PlayerType

class PlayerFactory:
    """
    Factory pour créer des joueurs.
    
    Responsabilité : Création standardisée de joueurs avec valeurs par défaut.
    """
    
    # Couleurs standard (DRY: définies une seule fois)
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
    def create_players_from_config(cls, player_configs: List[Dict[str, Any]]) -> List[Player]:
        """
        Crée une liste de joueurs depuis une configuration.
        
        Args:
            player_configs: Liste de configs [{id, name, type, persona, color}]
            
        Returns:
            Liste de joueurs créés
        """
        players = []
        
        for config in player_configs:
            player_type = config.get("type", "human")
            player_id = config.get("id", len(players))
            color = config.get("color")
            
            if player_type == "human":
                player = cls.create_human_player(
                    player_id, 
                    config.get("name", f"Joueur {player_id + 1}"),
                    color
                )
            elif player_type == "ai":
                player = cls.create_ai_player(
                    player_id,
                    config.get("persona", "random"),
                    color
                )
            elif player_type == "shared":
                player = cls.create_shared_player(player_id, color)
            else:
                raise ValueError(f"Unknown player type: {player_type}")
            
            players.append(player)
        
        return players
```

**Tests** : `tests/test_player_factory.py`

```python
class TestPlayerFactory:
    """Test du PlayerFactory."""
    
    def test_create_human_player(self):
        """Création joueur humain."""
        player = PlayerFactory.create_human_player(0, "Alice")
        assert player.id == 0
        assert player.name == "Alice"
        assert player.is_human
        assert player.color == "#3b82f6"  # Couleur par défaut
    
    def test_create_ai_player(self):
        """Création joueur IA."""
        player = PlayerFactory.create_ai_player(1, "random")
        assert player.is_ai
        assert player.persona == "random"
        assert player.name == "Bot Aléatoire"
    
    def test_create_from_config(self):
        """Création depuis config."""
        config = [
            {"id": 0, "name": "Alice", "type": "human"},
            {"id": 1, "type": "ai", "persona": "aggressive"},
            {"id": 2, "name": "Bob", "type": "human"}
        ]
        players = PlayerFactory.create_players_from_config(config)
        assert len(players) == 3
        assert players[0].name == "Alice"
        assert players[1].is_ai
```

**Principes** :
- ✅ SRP : Uniquement la création de joueurs
- ✅ OCP : Extensible via nouveaux types
- ✅ DRY : Couleurs définies une fois

---

## 📊 Phase 2 : GameManager (Priorité 1)

### 2.1 Créer GameManager

**Fichier** : `blokus-engine/src/blokus/game_manager.py`

```python
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from blokus.player import Player
from blokus.player_types import PlayerStatus

@dataclass
class GameManager:
    """
    Gestionnaire centralisé de l'ordre et de l'état des joueurs.
    
    Responsabilité : Gérer l'ordre de jeu, les tours, et l'état global.
    """
    
    players: List[Player] = field(default_factory=list)
    current_player_index: int = 0
    turn_history: List[int] = field(default_factory=list)
    game_finished: bool = False
    
    def __init__(self, players: List[Player] = None, starting_player_index: int = 0):
        """
        Initialise le GameManager.
        
        Args:
            players: Liste ordonnée des joueurs
            starting_player_index: Index du joueur qui commence
        """
        self.players = players or []
        self.current_player_index = starting_player_index
        self.turn_history = []
        self.game_finished = False
        
        # Initialiser l'ordre de tour
        for i, player in enumerate(self.players):
            player.turn_order = i
        
        # Activer le premier joueur
        if self.players:
            self.current_player.status = PlayerStatus.PLAYING
    
    # === PROPERTIES (POLA: accès simple) ===
    @property
    def current_player(self) -> Player:
        """Joueur actuel."""
        return self.players[self.current_player_index]
    
    @property
    def player_count(self) -> int:
        """Nombre de joueurs."""
        return len(self.players)
    
    @property
    def active_players(self) -> List[Player]:
        """Joueurs qui n'ont pas passé."""
        return [p for p in self.players if not p.has_passed]
    
    # === GESTION DES JOUEURS (SRP: recherche) ===
    def get_player_by_id(self, player_id: int) -> Optional[Player]:
        """Récupère un joueur par son ID."""
        for player in self.players:
            if player.id == player_id:
                return player
        return None
    
    def get_player_index(self, player: Player) -> int:
        """Récupère l'index d'un joueur."""
        return self.players.index(player)
    
    # === GESTION DES TOURS (SRP: transitions) ===
    def next_turn(self) -> Player:
        """
        Passe au joueur suivant qui peut jouer.
        
        Returns:
            Le nouveau joueur actuel
        """
        if not self.players:
            raise ValueError("No players in game")
        
        # Marquer le joueur actuel comme waiting
        self.current_player.status = PlayerStatus.WAITING
        
        # Ajouter à l'historique
        self.turn_history.append(self.current_player_index)
        
        # Chercher le prochain joueur actif
        attempts = 0
        while attempts < len(self.players):
            self.current_player_index = (self.current_player_index + 1) % len(self.players)
            next_player = self.players[self.current_player_index]
            
            if not next_player.has_passed:
                next_player.status = PlayerStatus.PLAYING
                return next_player
            
            attempts += 1
        
        # Tout le monde a passé
        self.game_finished = True
        return self.players[self.current_player_index]
    
    def set_starting_player(self, player_id: int):
        """Définit le joueur de départ par son ID."""
        for i, player in enumerate(self.players):
            if player.id == player_id:
                self.current_player.status = PlayerStatus.WAITING
                self.current_player_index = i
                self.current_player.status = PlayerStatus.PLAYING
                self.turn_history = []
                return
        raise ValueError(f"Player with ID {player_id} not found")
    
    # === ORDRES DIFFÉRENTS (SRP: vues) ===
    def get_play_order(self) -> List[Player]:
        """Retourne les joueurs dans l'ordre de jeu."""
        return self.players.copy()
    
    def get_score_order(self) -> List[Player]:
        """Retourne les joueurs ordonnés par score."""
        return sorted(self.players, key=lambda p: p.score, reverse=True)
    
    # === ÉTAT DU JEU (SRP: vérifications) ===
    def is_game_over(self) -> bool:
        """Vérifie si le jeu est terminé."""
        return self.game_finished or all(p.has_passed for p in self.players)
    
    def get_winner(self) -> Optional[Player]:
        """Détermine le gagnant."""
        if not self.is_game_over():
            return None
        
        scores = [(p, p.score) for p in self.players]
        max_score = max(score for _, score in scores)
        winners = [p for p, score in scores if score == max_score]
        
        return winners[0] if len(winners) == 1 else None
    
    # === SÉRIALISATION (SRP: conversion) ===
    def to_dict(self) -> Dict[str, Any]:
        """Convertit en dictionnaire."""
        return {
            "players": [player.to_dict() for player in self.players],
            "current_player_index": self.current_player_index,
            "current_player": self.current_player.to_dict(),
            "turn_history": self.turn_history,
            "game_finished": self.game_finished,
            "player_count": self.player_count
        }
    
    def __len__(self) -> int:
        """Nombre de joueurs."""
        return len(self.players)
    
    def __getitem__(self, index: int) -> Player:
        """Accès direct par index."""
        return self.players[index]
```

**Tests** : `tests/test_game_manager.py`

```python
class TestGameManagerInitialization:
    """Test de l'initialisation."""
    
    def test_default_initialization(self):
        """Initialisation par défaut."""
        players = [
            Player(id=0, name="Alice", color="#3b82f6"),
            Player(id=1, name="Bob", color="#22c55e")
        ]
        manager = GameManager(players)
        assert manager.player_count == 2
        assert manager.current_player.id == 0
    
    def test_custom_starting_player(self):
        """Joueur de départ personnalisé."""
        players = [
            Player(id=0, name="Alice", color="#3b82f6"),
            Player(id=1, name="Bob", color="#22c55e")
        ]
        manager = GameManager(players, starting_player_index=1)
        assert manager.current_player.id == 1

class TestGameManagerTurns:
    """Test de la gestion des tours."""
    
    def test_next_turn(self):
        """Passage au tour suivant."""
        players = [
            Player(id=0, name="Alice", color="#3b82f6"),
            Player(id=1, name="Bob", color="#22c55e")
        ]
        manager = GameManager(players)
        
        next_player = manager.next_turn()
        assert next_player.id == 1
        assert manager.current_player_index == 1
    
    def test_skip_passed_players(self):
        """Sauter les joueurs qui ont passé."""
        players = [
            Player(id=0, name="Alice", color="#3b82f6"),
            Player(id=1, name="Bob", color="#22c55e"),
            Player(id=2, name="Charlie", color="#eab308")
        ]
        manager = GameManager(players)
        
        # Bob passe
        manager.next_turn()
        manager.current_player.pass_turn()
        
        # Devrait passer à Charlie
        next_player = manager.next_turn()
        assert next_player.id == 2

class TestGameManagerQueries:
    """Test des requêtes."""
    
    def test_get_player_by_id(self):
        """Recherche par ID."""
        players = [
            Player(id=0, name="Alice", color="#3b82f6"),
            Player(id=1, name="Bob", color="#22c55e")
        ]
        manager = GameManager(players)
        
        player = manager.get_player_by_id(1)
        assert player.name == "Bob"
    
    def test_get_score_order(self):
        """Ordre par score."""
        players = [
            Player(id=0, name="Alice", color="#3b82f6", score=50),
            Player(id=1, name="Bob", color="#22c55e", score=30),
            Player(id=2, name="Charlie", color="#eab308", score=70)
        ]
        manager = GameManager(players)
        
        order = manager.get_score_order()
        assert order[0].name == "Charlie"
        assert order[1].name == "Alice"
        assert order[2].name == "Bob"
```

**Commandes de test** :
```bash
// turbo
source .venv/bin/activate && python -m pytest tests/test_game_manager.py -v --tb=short
```

**Principes** :
- ✅ SRP : Responsabilités séparées (recherche, tours, vues, état)
- ✅ KISS : Logique simple et directe
- ✅ POLA : Noms prévisibles et comportement attendu

---

### 2.2 Créer GameManagerFactory

**Fichier** : `blokus-engine/src/blokus/game_manager_factory.py`

```python
from typing import List, Dict, Any
from blokus.game_manager import GameManager
from blokus.player_factory import PlayerFactory

class GameManagerFactory:
    """
    Factory pour créer des GameManager.
    
    Responsabilité : Création standardisée de GameManager.
    """
    
    @classmethod
    def create_from_config(
        cls, 
        player_configs: List[Dict[str, Any]], 
        starting_player_id: int = 0
    ) -> GameManager:
        """
        Crée un GameManager depuis une configuration.
        
        Args:
            player_configs: Liste de configs joueurs
            starting_player_id: ID du joueur qui commence
            
        Returns:
            GameManager configuré
        """
        # Créer les joueurs
        players = PlayerFactory.create_players_from_config(player_configs)
        
        # Trouver l'index du joueur de départ
        starting_index = 0
        for i, player in enumerate(players):
            if player.id == starting_player_id:
                starting_index = i
                break
        
        return GameManager(players, starting_index)
    
    @classmethod
    def create_standard_game(
        cls, 
        num_players: int = 4, 
        starting_player_id: int = 0
    ) -> GameManager:
        """
        Crée un jeu standard avec joueurs humains.
        
        Args:
            num_players: Nombre de joueurs (2-4)
            starting_player_id: ID du joueur qui commence
            
        Returns:
            GameManager configuré
        """
        player_configs = []
        for i in range(num_players):
            player_configs.append({
                "id": i,
                "name": f"Joueur {i + 1}",
                "type": "human"
            })
        
        return cls.create_from_config(player_configs, starting_player_id)
```

**Tests** : `tests/test_game_manager_factory.py`

**Principes** :
- ✅ SRP : Uniquement la création de GameManager
- ✅ DIP : Utilise PlayerFactory (abstraction)

---

## 📊 Phase 3 : Intégration avec Game (Priorité 2)

### 3.1 Adapter la Classe Game

**Fichier** : `blokus-engine/src/blokus/game.py`

Modifier pour utiliser `GameManager` au lieu de gérer directement les joueurs.

**Tests** : Mettre à jour `tests/test_game.py`

**Principes** :
- ✅ DIP : Game dépend de GameManager (abstraction)
- ✅ SRP : Game orchestre, GameManager gère les joueurs

---

## 📊 Phase 4 : Machines à États (Priorité 3)

### 4.1 Créer StateMachine Générique

**Fichier** : `blokus-engine/src/blokus/state_machine.py`

**Tests** : `tests/test_state_machine.py`

### 4.2 Créer PlayerStateMachine

**Fichier** : `blokus-engine/src/blokus/player_state_machine.py`

**Tests** : `tests/test_player_state_machine.py`

---

## 📊 Phase 5 : API et Frontend (Priorité 4)

### 5.1 Mettre à Jour les Modèles API

**Fichier** : `blokus-server/api/models.py`

### 5.2 Adapter les Endpoints

**Fichier** : `blokus-server/main.py`

### 5.3 Adapter le Frontend

**Fichiers** : `blokus-web/js/*.js`

---

## ✅ Checklist de Qualité

### Avant Chaque Commit

- [ ] Tous les tests passent
- [ ] Couverture > 80%
- [ ] Type checking (mypy) sans erreur
- [ ] Linting (ruff) sans erreur
- [ ] Docstrings à jour
- [ ] Pas de code mort

### Code Review

**SOLID** :
- [ ] SRP : Une responsabilité par classe/fonction
- [ ] OCP : Extensible sans modification
- [ ] LSP : Contrats respectés
- [ ] ISP : Interfaces minimales
- [ ] DIP : Dépendances via abstractions

**Autres** :
- [ ] DRY : Pas de duplication
- [ ] KISS : Solution simple
- [ ] YAGNI : Pas de code spéculatif
- [ ] POLA : Comportement prévisible
- [ ] Tests complets

---

## 🎯 Commandes de Test

### Tests Unitaires
```bash
// turbo
source .venv/bin/activate && python -m pytest tests/ -v --tb=short
```

### Couverture
```bash
source .venv/bin/activate && python -m pytest tests/ --cov=src/blokus --cov-report=term-missing
```

### Type Checking
```bash
source .venv/bin/activate && mypy src/
```

### Linting
```bash
source .venv/bin/activate && ruff check src/
```

---

## 📈 Métriques de Succès

- ✅ **Tests** : 100% des tests passent
- ✅ **Couverture** : > 80% sur le nouveau code
- ✅ **Qualité** : 0 erreur mypy, 0 erreur ruff
- ✅ **Performance** : Pas de régression
- ✅ **Documentation** : Docstrings complètes

---

*Plan créé le 1er janvier 2026*
*Basé sur les workflows : blokus-design-principles.md et blokus-test-python.md*
