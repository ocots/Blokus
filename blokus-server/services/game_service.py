from typing import Optional, List
from fastapi import HTTPException

from blokus.game import Game
from blokus.board import Board
from blokus.game_manager_factory import GameManagerFactory

class GameService:
    """
    Singleton service to manage the global game state.
    Follows Singleton pattern for state persistence in memory.
    """
    _instance: Optional['GameService'] = None
    
    def __init__(self):
        self._game: Optional[Game] = None
        self._mode: str = 'standard'  # Track game mode for reset
    
    @classmethod
    def get_instance(cls) -> 'GameService':
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    @property
    def game(self) -> Game:
        if self._game is None:
            raise HTTPException(status_code=404, detail="Game not initialized")
        return self._game
    
    def create_game(self, 
                    num_players: int, 
                    players_config: Optional[List[dict]] = None, 
                    board_size: int = 20, 
                    starting_player_id: int = 0,
                    mode: str = 'standard') -> Game:
        """Create and store a new game instance."""
        
        board = Board(size=board_size)
        
        if players_config:
            # Create configured game
            if mode == 'standard' and len(players_config) == 2:
                game_manager = GameManagerFactory.create_standard_2p_game(
                    players_config,
                    starting_player_id=starting_player_id
                )
            else:
                game_manager = GameManagerFactory.create_from_config(
                    players_config, 
                    starting_player_id=starting_player_id
                )
        else:
            # Create default standard game
            game_manager = GameManagerFactory.create_standard_game(
                num_players=num_players,
                starting_player_id=starting_player_id
            )
        
        # Store mode for reset
        self._mode = mode
        self._game = Game(game_manager=game_manager, board=board)
        return self._game
    
    def reset_game(self) -> Game:
        """Reset the current game keeping players and config."""
        if not self._game:
            return self.create_game(num_players=4) # Default fallback
            
        old_game = self._game
        
        # Extract config to recreate similar game
        player_configs = []
        for p in old_game.players:
            config = {
                "id": p.id,
                "name": p.name,
                "type": p.type.value,
            }
            if p.persona:
                config["persona"] = p.persona
            player_configs.append(config)
            
        return self.create_game(
            num_players=len(old_game.players),
            players_config=player_configs,
            board_size=old_game.board.size,
            mode=self._mode
        )

# Dependency provider
def get_game_service() -> GameService:
    return GameService.get_instance()
