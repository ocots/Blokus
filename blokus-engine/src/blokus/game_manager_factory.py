"""
Factory for creating GameManager instances.

Follows SOLID principles:
- SRP: Only GameManager creation logic
- OCP: Extensible via player configurations
- DIP: Depends on PlayerFactory and GameManager abstractions
"""

from typing import List, Dict, Any
from blokus.game_manager import GameManager
from blokus.player_factory import PlayerFactory


class GameManagerFactory:
    """
    Factory for creating GameManager instances.
    
    Responsibility: Standardized creation of GameManager with various configurations.
    Follows SOLID principles:
    - SRP: Only GameManager creation
    - DIP: Uses PlayerFactory (abstraction)
    """
    
    @classmethod
    def create_from_config(
        cls, 
        player_configs: List[Dict[str, Any]], 
        starting_player_id: int = 0
    ) -> GameManager:
        """
        Create GameManager from player configuration.
        
        Args:
            player_configs: List of player configuration dicts
            starting_player_id: ID of player who starts
            
        Returns:
            GameManager instance
            
        Raises:
            ValueError: If starting_player_id not found
        """
        # Create players using PlayerFactory
        players = PlayerFactory.create_players_from_config(player_configs)
        
        # Find starting player index
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
        Create standard game with human players.
        
        Args:
            num_players: Number of players (2-4)
            starting_player_id: ID of player who starts
            
        Returns:
            GameManager instance
            
        Raises:
            ValueError: If num_players invalid
        """
        players = PlayerFactory.create_standard_players(num_players)
        
        # Validate starting player
        if not (0 <= starting_player_id < num_players):
            raise ValueError(
                f"starting_player_id must be between 0 and {num_players - 1}, "
                f"got {starting_player_id}"
            )
        
        return GameManager(players, starting_player_id)
    
    @classmethod
    def create_ai_game(
        cls, 
        ai_configs: List[Dict[str, str]], 
        starting_player_id: int = 0
    ) -> GameManager:
        """
        Create game with AI players.
        
        Args:
            ai_configs: List of AI configs [{"persona": "random"}, ...]
            starting_player_id: ID of player who starts
            
        Returns:
            GameManager instance
        """
        player_configs = []
        for i, config in enumerate(ai_configs):
            player_configs.append({
                "id": i,
                "type": "ai",
                "persona": config["persona"]
            })
        
        return cls.create_from_config(player_configs, starting_player_id)
    
    @classmethod
    def create_mixed_game(
        cls,
        num_humans: int,
        num_ais: int,
        ai_personas: List[str] = None,
        starting_player_id: int = 0
    ) -> GameManager:
        """
        Create game with mixed human and AI players.
        
        Args:
            num_humans: Number of human players
            num_ais: Number of AI players
            ai_personas: List of AI personas (defaults to "random")
            starting_player_id: ID of player who starts
            
        Returns:
            GameManager instance
            
        Raises:
            ValueError: If total players not between 2-4
        """
        total_players = num_humans + num_ais
        if not (2 <= total_players <= 4):
            raise ValueError(
                f"Total players must be between 2 and 4, got {total_players}"
            )
        
        if ai_personas is None:
            ai_personas = ["random"] * num_ais
        
        if len(ai_personas) != num_ais:
            raise ValueError(
                f"ai_personas length ({len(ai_personas)}) must match num_ais ({num_ais})"
            )
        
        player_configs = []
        
        # Add human players
        for i in range(num_humans):
            player_configs.append({
                "id": i,
                "name": f"Joueur {i + 1}",
                "type": "human"
            })
        
        # Add AI players
        for i in range(num_ais):
            player_configs.append({
                "id": num_humans + i,
                "type": "ai",
                "persona": ai_personas[i]
            })
        
        return cls.create_from_config(player_configs, starting_player_id)
