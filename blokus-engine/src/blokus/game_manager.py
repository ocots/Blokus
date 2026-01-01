"""
GameManager for centralized player and turn management.

Follows SOLID principles:
- SRP: Only player order and turn management
- OCP: Extensible via player types
- DIP: Depends on Player abstraction
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from blokus.player import Player
from blokus.player_types import PlayerStatus


@dataclass
class GameManager:
    """
    Centralized manager for player order and game state.
    
    Responsibility: Manage player order, turns, and global state.
    Follows SOLID principles:
    - SRP: Only player/turn management
    - KISS: Simple and direct logic
    - POLA: Predictable behavior
    """
    
    players: List[Player] = field(default_factory=list)
    current_player_index: int = 0
    turn_history: List[int] = field(default_factory=list)
    game_finished: bool = False
    
    def __init__(self, players: List[Player] = None, starting_player_index: int = 0):
        """
        Initialize GameManager.
        
        Args:
            players: Ordered list of players (order = play order)
            starting_player_index: Index of starting player
            
        Raises:
            ValueError: If starting_player_index is invalid
        """
        self.players = players or []
        self.turn_history = []
        self.game_finished = False
        
        # Validate starting player index
        if self.players and not (0 <= starting_player_index < len(self.players)):
            raise ValueError(
                f"starting_player_index must be between 0 and {len(self.players) - 1}, "
                f"got {starting_player_index}"
            )
        
        self.current_player_index = starting_player_index
        
        # Initialize turn order for all players
        for i, player in enumerate(self.players):
            player.turn_order = i
        
        # Activate the starting player
        if self.players:
            self.current_player.status = PlayerStatus.PLAYING
    
    # === PROPERTIES (POLA: simple access) ===
    
    @property
    def current_player(self) -> Player:
        """Current player."""
        return self.players[self.current_player_index]
    
    @property
    def player_count(self) -> int:
        """Number of players."""
        return len(self.players)
    
    @property
    def active_players(self) -> List[Player]:
        """Players who haven't passed."""
        return [p for p in self.players if not p.has_passed]
    
    @property
    def finished_players(self) -> List[Player]:
        """Players who have passed."""
        return [p for p in self.players if p.has_passed]
    
    # === PLAYER QUERIES (SRP: search) ===
    
    def get_player_by_id(self, player_id: int) -> Optional[Player]:
        """
        Get player by ID.
        
        Args:
            player_id: Player ID to search for
            
        Returns:
            Player instance or None if not found
        """
        for player in self.players:
            if player.id == player_id:
                return player
        return None
    
    def get_player_index(self, player: Player) -> int:
        """
        Get player's index in the list.
        
        Args:
            player: Player instance
            
        Returns:
            Index in players list
            
        Raises:
            ValueError: If player not in list
        """
        return self.players.index(player)
    
    # === TURN MANAGEMENT (SRP: transitions) ===
    
    def next_turn(self) -> Player:
        """
        Advance to next player who can play.
        
        Returns:
            The new current player
            
        Algorithm:
        1. Mark current player as waiting
        2. Add to turn history
        3. Find next active player
        4. If all passed, game is finished
        5. Activate new current player
        """
        if not self.players:
            raise ValueError("No players in game")
        
        # Mark current player as waiting
        self.current_player.status = PlayerStatus.WAITING
        
        # Add to history
        self.turn_history.append(self.current_player_index)
        
        # Find next active player
        attempts = 0
        while attempts < len(self.players):
            self.current_player_index = (self.current_player_index + 1) % len(self.players)
            next_player = self.players[self.current_player_index]
            
            if not next_player.has_passed:
                next_player.status = PlayerStatus.PLAYING
                return next_player
            
            attempts += 1
        
        # All players have passed
        self.game_finished = True
        return self.players[self.current_player_index]
    
    def set_starting_player(self, player_id: int):
        """
        Set starting player by ID.
        
        Args:
            player_id: ID of player to start
            
        Raises:
            ValueError: If player not found
        """
        for i, player in enumerate(self.players):
            if player.id == player_id:
                # Reset current player status
                self.current_player.status = PlayerStatus.WAITING
                
                # Change current player
                self.current_player_index = i
                self.current_player.status = PlayerStatus.PLAYING
                
                # Clear history
                self.turn_history = []
                return
        
        raise ValueError(f"Player with ID {player_id} not found")
    
    def set_starting_player_by_index(self, index: int):
        """
        Set starting player by index.
        
        Args:
            index: Index of player to start
            
        Raises:
            ValueError: If index invalid
        """
        if not (0 <= index < len(self.players)):
            raise ValueError(
                f"Index must be between 0 and {len(self.players) - 1}, got {index}"
            )
        
        self.current_player.status = PlayerStatus.WAITING
        self.current_player_index = index
        self.current_player.status = PlayerStatus.PLAYING
        self.turn_history = []
    
    def force_pass_turn(self):
        """Force current player to pass their turn."""
        self.current_player.pass_turn()
        self.next_turn()
    
    # === DIFFERENT ORDERS (SRP: views) ===
    
    def get_play_order(self) -> List[Player]:
        """
        Get players in play order.
        
        Returns:
            Copy of players list
        """
        return self.players.copy()
    
    def get_turn_order_from_current(self) -> List[Player]:
        """
        Get players in turn order starting from current player.
        
        Useful for UI: "who plays after who"
        
        Returns:
            Rotated list starting with current player
        """
        if not self.players:
            return []
        
        return (
            self.players[self.current_player_index:] +
            self.players[:self.current_player_index]
        )
    
    def get_score_order(self) -> List[Player]:
        """
        Get players ordered by score (descending).
        
        Returns:
            Players sorted by score
        """
        return sorted(self.players, key=lambda p: p.score, reverse=True)
    
    def get_players_by_type(self, player_type) -> List[Player]:
        """
        Get players of specific type.
        
        Args:
            player_type: PlayerType enum value
            
        Returns:
            List of matching players
        """
        return [p for p in self.players if p.type == player_type]
    
    # === GAME STATE (SRP: checks) ===
    
    def is_game_over(self) -> bool:
        """
        Check if game is over.
        
        Returns:
            True if all players have passed
        """
        return self.game_finished or all(p.has_passed for p in self.players)
    
    def get_winner(self) -> Optional[Player]:
        """
        Determine the winner.
        
        Returns:
            Player with highest score, or None if tie or game not over
        """
        if not self.is_game_over():
            return None
        
        scores = [(p, p.score) for p in self.players]
        max_score = max(score for _, score in scores)
        winners = [p for p, score in scores if score == max_score]
        
        return winners[0] if len(winners) == 1 else None
    
    def get_rankings(self) -> Dict[int, int]:
        """
        Get player rankings.
        
        Returns:
            Dictionary mapping player IDs to their rank (1 = first place)
        """
        sorted_players = self.get_score_order()
        rankings = {}
        
        for rank, player in enumerate(sorted_players, 1):
            rankings[player.id] = rank
        
        return rankings
    
    # === SERIALIZATION (SRP: conversion) ===
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API."""
        return {
            "players": [player.to_dict() for player in self.players],
            "current_player_index": self.current_player_index,
            "current_player": self.current_player.to_dict() if self.players else None,
            "turn_history": self.turn_history,
            "game_finished": self.game_finished,
            "player_count": self.player_count,
            "active_players": [p.to_dict() for p in self.active_players],
            "finished_players": [p.to_dict() for p in self.finished_players]
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GameManager":
        """
        Create GameManager from dictionary.
        
        Args:
            data: Dictionary with game manager data
            
        Returns:
            GameManager instance
        """
        players = [Player.from_dict(p_data) for p_data in data["players"]]
        
        manager = cls(
            players=players,
            starting_player_index=data["current_player_index"]
        )
        
        manager.turn_history = data.get("turn_history", [])
        manager.game_finished = data.get("game_finished", False)
        
        return manager
    
    # === UTILITY METHODS ===
    
    def __len__(self) -> int:
        """Number of players."""
        return len(self.players)
    
    def __getitem__(self, index: int) -> Player:
        """Access player by index."""
        return self.players[index]
    
    def __iter__(self):
        """Iterate over players in play order."""
        return iter(self.players)
    
    def __repr__(self) -> str:
        """String representation."""
        if not self.players:
            return "GameManager(no players)"
        
        current_name = self.current_player.name if self.players else "None"
        return f"GameManager({len(self.players)} players, current: {current_name})"
