"""
Architecture GameManager - Gestion centralisée de l'ordre des joueurs.

Le GameManager gère:
- L'ordre de jeu (liste ordonnée)
- Le joueur actuel
- Les transitions de tours
- La configuration de départ
- L'état global des joueurs
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any, Iterator
from enum import Enum

# Import depuis la proposition précédente
from player_architecture_proposal import Player, PlayerType, PlayerStatus, PlayerFactory

@dataclass
class GameManager:
    """
    Gestionnaire centralisé pour l'ordre et l'état des joueurs.
    
    Responsabilités:
    - Maintenir une liste ordonnée de joueurs
    - Gérer le joueur actuel et les transitions
    - Fournir des itérateurs pour les différents ordres
    - Centraliser la logique de tour
    """
    
    # Liste ordonnée des joueurs = ordre de jeu
    players: List[Player] = field(default_factory=list)
    
    # Index du joueur actuel dans la liste
    current_player_index: int = 0
    
    # Historique des tours pour statistiques
    turn_history: List[int] = field(default_factory=list)
    
    # État du jeu
    game_finished: bool = False
    
    def __init__(self, players: List[Player] = None, starting_player_index: int = 0):
        """
        Initialise le GameManager.
        
        Args:
            players: Liste ordonnée des joueurs (ordre = ordre de jeu)
            starting_player_index: Index du joueur qui commence (dans la liste)
        """
        self.players = players or []
        self.current_player_index = starting_player_index
        self.turn_history = []
        self.game_finished = False
        
        # Initialiser les joueurs
        self._initialize_players()
    
    def _initialize_players(self):
        """Initialise l'état des joueurs au début du jeu."""
        for i, player in enumerate(self.players):
            player.turn_order = i
            player.status = PlayerStatus.WAITING
        
        # Activer le premier joueur
        if self.players:
            self.current_player.start_turn()
    
    # === PROPRIÉTÉS PRATIQUES ===
    
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
    
    @property
    def finished_players(self) -> List[Player]:
        """Joueurs qui ont passé."""
        return [p for p in self.players if p.has_passed]
    
    # === GESTION DES JOUEURS ===
    
    def get_player_by_id(self, player_id: int) -> Optional[Player]:
        """Récupère un joueur par son ID."""
        for player in self.players:
            if player.id == player_id:
                return player
        return None
    
    def get_player_by_name(self, name: str) -> Optional[Player]:
        """Récupère un joueur par son nom."""
        for player in self.players:
            if player.name == name:
                return player
        return None
    
    def get_player_index(self, player: Player) -> int:
        """Récupère l'index d'un joueur dans la liste."""
        return self.players.index(player)
    
    # === GESTION DES TOURS ===
    
    def next_turn(self) -> Player:
        """
        Passe au joueur suivant qui peut jouer.
        
        Returns:
            Le nouveau joueur actuel
            
        Algorithm:
        1. Marquer le joueur actuel comme terminé
        2. Chercher le prochain joueur qui n'a pas passé
        3. Si tout le monde a passé, fin du jeu
        4. Activer le nouveau joueur actuel
        """
        if not self.players:
            raise ValueError("No players in game")
        
        # Marquer le joueur actuel comme waiting
        self.current_player.end_turn()
        
        # Ajouter à l'historique
        self.turn_history.append(self.current_player_index)
        
        # Chercher le prochain joueur actif
        original_index = self.current_player_index
        attempts = 0
        
        while attempts < len(self.players):
            # Passer au joueur suivant
            self.current_player_index = (self.current_player_index + 1) % len(self.players)
            next_player = self.players[self.current_player_index]
            
            # Vérifier si ce joueur peut jouer
            if not next_player.has_passed:
                next_player.start_turn()
                return next_player
            
            # Si le joueur a passé, continuer la recherche
            attempts += 1
        
        # Si on a fait tout le tour, tout le monde a passé
        self.game_finished = True
        self.current_player_index = original_index
        return self.players[self.current_player_index]
    
    def set_starting_player(self, player_id: int):
        """
        Définit le joueur de départ par son ID.
        
        Args:
            player_id: ID du joueur qui doit commencer
        """
        for i, player in enumerate(self.players):
            if player.id == player_id:
                # Réinitialiser l'état
                self.current_player.end_turn()
                
                # Changer le joueur actuel
                self.current_player_index = i
                self.current_player.start_turn()
                
                # Vider l'historique
                self.turn_history = []
                return
        
        raise ValueError(f"Player with ID {player_id} not found")
    
    def set_starting_player_by_index(self, index: int):
        """
        Définit le joueur de départ par son index.
        
        Args:
            index: Index du joueur qui doit commencer
        """
        if 0 <= index < len(self.players):
            self.current_player.end_turn()
            self.current_player_index = index
            self.current_player.start_turn()
            self.turn_history = []
        else:
            raise ValueError(f"Invalid player index: {index}")
    
    def force_pass_turn(self):
        """Force le joueur actuel à passer son tour."""
        self.current_player.pass_turn()
        self.next_turn()
    
    # === ITÉRATEURS ET ORDRES ===
    
    def get_play_order(self) -> List[Player]:
        """
        Retourne les joueurs dans l'ordre de jeu actuel.
        
        Le premier joueur de la liste est celui qui joue en premier.
        """
        return self.players.copy()
    
    def get_turn_order_from_current(self) -> List[Player]:
        """
        Retourne les joueurs dans l'ordre des tours à partir du joueur actuel.
        
        Utile pour l'affichage: "qui joue après qui".
        """
        if not self.players:
            return []
        
        # Rotation de la liste pour commencer par le joueur actuel
        current_list = self.players[self.current_player_index:] + self.players[:self.current_player_index]
        return current_list
    
    def get_score_order(self) -> List[Player]:
        """
        Retourne les joueurs ordonnés par score (décroissant).
        
        Utile pour le classement final.
        """
        return sorted(self.players, key=lambda p: p.score, reverse=True)
    
    def get_players_by_type(self, player_type: PlayerType) -> List[Player]:
        """Retourne les joueurs d'un type spécifique."""
        return [p for p in self.players if p.type == player_type]
    
    def human_players(self) -> List[Player]:
        """Retourne les joueurs humains."""
        return self.get_players_by_type(PlayerType.HUMAN)
    
    def ai_players(self) -> List[Player]:
        """Retourne les joueurs IA."""
        return self.get_players_by_type(PlayerType.AI)
    
    # === ÉTAT DU JEU ===
    
    def is_game_over(self) -> bool:
        """Vérifie si le jeu est terminé."""
        return self.game_finished or all(p.has_passed for p in self.players)
    
    def get_winner(self) -> Optional[Player]:
        """
        Détermine le gagnant.
        
        Returns:
            Le joueur avec le plus haut score, ou None si égalité
        """
        if not self.is_game_over():
            return None
        
        scores = [(p, p.score) for p in self.players]
        max_score = max(score for _, score in scores)
        winners = [p for p, score in scores if score == max_score]
        
        return winners[0] if len(winners) == 1 else None
    
    def get_rankings(self) -> Dict[Player, int]:
        """
        Retourne le classement des joueurs.
        
        Returns:
            Dictionnaire {joueur: rang} où 1 = première place
        """
        sorted_players = self.get_score_order()
        rankings = {}
        
        for rank, player in enumerate(sorted_players, 1):
            rankings[player] = rank
        
        return rankings
    
    # === SÉRIALISATION ===
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit en dictionnaire pour l'API."""
        return {
            "players": [player.to_dict() for player in self.players],
            "current_player_index": self.current_player_index,
            "current_player": self.current_player.to_dict(),
            "turn_history": self.turn_history,
            "game_finished": self.game_finished,
            "player_count": self.player_count,
            "active_players": [p.to_dict() for p in self.active_players],
            "finished_players": [p.to_dict() for p in self.finished_players]
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GameManager":
        """Crée un GameManager depuis un dictionnaire."""
        players = [Player.from_dict(p_data) for p_data in data["players"]]
        
        manager = cls(
            players=players,
            starting_player_index=data["current_player_index"]
        )
        
        manager.turn_history = data.get("turn_history", [])
        manager.game_finished = data.get("game_finished", False)
        
        return manager
    
    # === MÉTHODES UTILITAIRES ===
    
    def __len__(self) -> int:
        """Nombre de joueurs."""
        return len(self.players)
    
    def __getitem__(self, index: int) -> Player:
        """Accès direct par index."""
        return self.players[index]
    
    def __iter__(self) -> Iterator[Player]:
        """Itération dans l'ordre de jeu."""
        return iter(self.players)
    
    def __repr__(self) -> str:
        """Représentation textuelle."""
        if not self.players:
            return "GameManager(no players)"
        
        current_name = self.current_player.name if self.current_player else "None"
        return f"GameManager({len(self.players)} players, current: {current_name})"


# === FACTORY POUR CRÉER DES GAMEMANAGER ===

class GameManagerFactory:
    """Factory pour créer des GameManager avec des configurations standards."""
    
    @classmethod
    def create_from_config(cls, player_configs: List[Dict], starting_player_id: int = 0) -> GameManager:
        """
        Crée un GameManager depuis une configuration de joueurs.
        
        Args:
            player_configs: Liste de configs joueurs (name, type, persona, etc.)
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
    def create_standard_game(cls, num_players: int = 4, starting_player_id: int = 0) -> GameManager:
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
    
    @classmethod
    def create_ai_game(cls, ai_config: List[Dict], starting_player_id: int = 0) -> GameManager:
        """
        Crée un jeu avec des IA.
        
        Args:
            ai_config: Configuration des IA [{"persona": "random"}, {"persona": "aggressive"}]
            starting_player_id: ID du joueur qui commence
            
        Returns:
            GameManager configuré
        """
        player_configs = []
        for i, config in enumerate(ai_config):
            player_configs.append({
                "id": i,
                "type": "ai",
                "persona": config["persona"]
            })
        
        return cls.create_from_config(player_configs, starting_player_id)


# === EXEMPLES D'UTILISATION ===

def example_usage():
    """Exemples d'utilisation du GameManager."""
    
    # 1. Création depuis une configuration
    config = [
        {"id": 0, "name": "Alice", "type": "human"},
        {"id": 1, "name": "Bob", "type": "ai", "persona": "random"},
        {"id": 2, "name": "Charlie", "type": "human"},
        {"id": 3, "name": "Diana", "type": "ai", "persona": "aggressive"}
    ]
    
    manager = GameManagerFactory.create_from_config(config, starting_player_id=2)
    
    print(f"Joueur actuel: {manager.current_player.display_name}")
    print(f"Ordre de jeu: {[p.name for p in manager.get_play_order()]}")
    
    # 2. Gestion des tours
    next_player = manager.next_turn()
    print(f"Prochain joueur: {next_player.display_name}")
    
    # 3. Classement
    # Simuler des scores
    manager.players[0].score = 50
    manager.players[1].score = 30
    manager.players[2].score = 70
    manager.players[3].score = 40
    
    print("Classement final:")
    for i, player in enumerate(manager.get_score_order(), 1):
        print(f"{i}. {player.display_name}: {player.score} points")
    
    # 4. Joueurs par type
    print(f"Joueurs humains: {[p.name for p in manager.human_players()]}")
    print(f"Joueurs IA: {[p.display_name for p in manager.ai_players()]}")

if __name__ == "__main__":
    example_usage()
