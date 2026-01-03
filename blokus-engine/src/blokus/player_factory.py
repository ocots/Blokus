"""
Factory for creating Player instances.

Follows SOLID principles:
- SRP: Only player creation logic
- OCP: Extensible via new player types
- DIP: Depends on Player abstraction
"""

from typing import List, Dict, Any
from blokus.player import Player
from blokus.player_types import PlayerType


class PlayerFactory:
    """
    Factory for creating Player instances.
    
    Responsibility: Standardized creation of players with default values.
    Follows SOLID principles:
    - SRP: Only player creation
    - OCP: Extensible via new types
    - DRY: Colors defined once
    """
    
    # Default colors (DRY: defined once)
    DEFAULT_COLORS = [
        "#3b82f6",  # Blue
        "#22c55e",  # Green
        "#eab308",  # Yellow
        "#ef4444"   # Red
    ]
    
    @classmethod
    def create_human_player(cls, id: int, name: str, color: str | None = None) -> Player:
        """
        Create a human player.
        
        Args:
            id: Player ID
            name: Player name
            color: Hex color (optional, uses default if None)
            
        Returns:
            Player instance
        """
        if color is None:
            color = cls.DEFAULT_COLORS[id % len(cls.DEFAULT_COLORS)]
        
        return Player(
            id=id,
            name=name,
            color=color,
            type=PlayerType.HUMAN
        )
    
    @classmethod
    def create_ai_player(cls, id: int, persona: str, color: str | None = None) -> Player:
        """
        Create an AI player.
        
        Args:
            id: Player ID
            persona: AI persona ("random", "aggressive", "defensive", "efficient")
            color: Hex color (optional, uses default if None)
            
        Returns:
            Player instance
        """
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
    def create_players_from_config(cls, player_configs: List[Dict[str, Any]]) -> List[Player]:
        """
        Create a list of players from configuration.
        
        Args:
            player_configs: List of player configuration dictionaries.
                Each dict should have: id, name, type, [persona], [color]
                
        Returns:
            List of Player instances
            
        Raises:
            ValueError: If unknown player type
        """
        players: list[Player] = []
        
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
            else:
                raise ValueError(f"Unknown player type: {player_type}")
            
            players.append(player)
        
        return players
    
    @classmethod
    def create_standard_players(cls, num_players: int = 4) -> List[Player]:
        """
        Create standard human players.
        
        Args:
            num_players: Number of players (2-4)
            
        Returns:
            List of Player instances
            
        Raises:
            ValueError: If num_players is not between 2 and 4
        """
        if num_players not in (2, 4):
            raise ValueError(f"num_players must be 2 or 4, got {num_players}")
        
        players = []
        for i in range(num_players):
            player = cls.create_human_player(i, f"Joueur {i + 1}")
            players.append(player)
        
        return players
