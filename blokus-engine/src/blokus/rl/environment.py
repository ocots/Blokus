"""
Blokus Gym-compatible environment for Reinforcement Learning.

This module provides a standard Gym interface for training RL agents
on the Blokus game, supporting both Duo (14×14) and Standard (20×20) modes.
"""

import numpy as np
from typing import Optional, Tuple, Dict, Any, List
from dataclasses import dataclass, field

try:
    import gymnasium as gym
    from gymnasium import spaces
except ImportError:
    # Fallback to old gym API
    import gym
    from gym import spaces

from blokus.game import Game, Move, GameStatus
from blokus.board import Board, STARTING_CORNERS
from blokus.player import Player
from blokus.rl.observations import create_observation, NUM_CHANNELS
from blokus.rl.actions import (
    get_action_space_size,
    encode_action,
    decode_action,
    get_action_mask,
    get_valid_actions
)
from blokus.rl.rewards import shaped_reward, sparse_reward


# Duo mode starting corners (14×14 board, positions 4 and 9)
DUO_STARTING_CORNERS: Dict[int, Tuple[int, int]] = {
    0: (4, 4),   # Player 0: near top-left
    1: (9, 9),   # Player 1: near bottom-right
}


@dataclass
class BlokusEnvConfig:
    """Configuration for Blokus environment."""
    board_size: int = 14  # Default: Duo mode
    num_players: int = 2  # Default: 2 players
    use_shaped_reward: bool = True  # Use potential-based shaping
    max_steps: int = 200  # Maximum steps before truncation
    
    @property
    def starting_corners(self) -> Dict[int, Tuple[int, int]]:
        """Get starting corners based on board size."""
        if self.board_size == 14:
            return DUO_STARTING_CORNERS
        else:
            # Standard 20×20 corners
            return {
                0: (0, 0),
                1: (0, self.board_size - 1),
                2: (self.board_size - 1, self.board_size - 1),
                3: (self.board_size - 1, 0),
            }


class BlokusEnv(gym.Env):
    """
    Blokus Reinforcement Learning Environment.
    
    A unified, configurable Gym environment supporting:
    - Duo 14×14 (default, for initial training)
    - Standard 20×20 (2P or 4P)
    
    Observations:
        shape (board_size, board_size, 47) float32 tensor
        
    Actions:
        Discrete action space with masking for valid moves
        Size = 21 pieces × 8 orientations × board_size²
        
    Rewards:
        Potential-based shaping by default, sparse terminal otherwise
    """
    
    metadata = {"render_modes": ["ansi", "human"]}
    
    def __init__(
        self,
        num_players: int = 2,
        board_size: int = 14,
        use_shaped_reward: bool = True,
        render_mode: Optional[str] = None
    ):
        """
        Initialize the Blokus environment.
        
        Args:
            num_players: Number of players (2 or 4)
            board_size: Board size (14 for Duo, 20 for Standard)
            use_shaped_reward: Whether to use potential-based reward shaping
            render_mode: Rendering mode ("ansi" or "human")
        """
        super().__init__()
        
        self.config = BlokusEnvConfig(
            board_size=board_size,
            num_players=num_players,
            use_shaped_reward=use_shaped_reward
        )
        
        self.render_mode = render_mode
        
        # Game state
        self.game: Optional[Game] = None
        self.game_history: List[Game] = []
        self.step_count: int = 0
        
        # Define spaces
        self.observation_space = spaces.Box(
            low=0.0,
            high=1.0,
            shape=(board_size, board_size, NUM_CHANNELS),
            dtype=np.float32
        )
        
        self.action_space = spaces.Discrete(
            get_action_space_size(board_size)
        )
    
    @property
    def board_size(self) -> int:
        """Get the board size."""
        return self.config.board_size
    
    @property
    def num_players(self) -> int:
        """Get the number of players."""
        return self.config.num_players
    
    def _create_game(self) -> Game:
        """Create a new game with the configured settings."""
        board = Board(size=self.config.board_size)
        players = [Player(id=i) for i in range(self.config.num_players)]
        return Game(
            num_players=self.config.num_players,
            board=board,
            players=players
        )
    
    def reset(
        self,
        seed: Optional[int] = None,
        options: Optional[Dict[str, Any]] = None
    ) -> Tuple[np.ndarray, Dict[str, Any]]:
        """
        Reset the environment to initial state.
        
        Args:
            seed: Random seed (optional)
            options: Additional options (optional)
            
        Returns:
            Tuple of (observation, info dict)
        """
        super().reset(seed=seed)
        
        self.game = self._create_game()
        self.game_history = []
        self.step_count = 0
        
        obs = self._get_obs()
        info = self._get_info()
        
        return obs, info
    
    def step(
        self,
        action: int
    ) -> Tuple[np.ndarray, float, bool, bool, Dict[str, Any]]:
        """
        Execute one step in the environment.
        
        Args:
            action: Action to take (encoded as integer)
            
        Returns:
            Tuple of (observation, reward, terminated, truncated, info)
        """
        if self.game is None:
            raise RuntimeError("Environment not initialized. Call reset() first.")
        
        # Store previous state for reward computation
        game_before = self.game.copy()
        
        # Decode action to move
        move = decode_action(action, self.game)
        
        # Track validity
        valid_move = False
        
        if move is not None:
            # Try to play the move
            valid_move = self.game.play_move(move)
        
        if not valid_move:
            # Invalid action: heavy penalty and end episode
            return (
                self._get_obs(),
                -10.0,  # Heavy penalty for invalid action
                True,   # Terminated
                False,  # Not truncated
                {"valid_action": False, "winner": None}
            )
        
        # Update history
        self.game_history.insert(0, game_before)
        if len(self.game_history) > 2:
            self.game_history = self.game_history[:2]
        
        self.step_count += 1
        
        # Calculate reward
        if self.config.use_shaped_reward:
            reward = shaped_reward(game_before, move, self.game, move.player_id)
        else:
            reward = sparse_reward(self.game, move.player_id)
        
        # Check termination
        terminated = self.game.status == GameStatus.FINISHED
        truncated = self.step_count >= self.config.max_steps
        
        obs = self._get_obs()
        info = self._get_info()
        info["valid_action"] = True
        
        return obs, reward, terminated, truncated, info
    
    def _get_obs(self) -> np.ndarray:
        """Get current observation tensor."""
        if self.game is None:
            return np.zeros(
                (self.config.board_size, self.config.board_size, NUM_CHANNELS),
                dtype=np.float32
            )
        return create_observation(self.game, self.game_history)
    
    def _get_info(self) -> Dict[str, Any]:
        """Get info dictionary."""
        if self.game is None:
            return {}
        
        info = {
            "current_player": self.game.current_player_idx,
            "turn_number": self.game.turn_number,
            "status": self.game.status.value,
            "scores": self.game.get_scores(),
            "valid_actions_count": len(self.game.get_valid_moves()),
        }
        
        if self.game.status == GameStatus.FINISHED:
            scores = self.game.get_scores()
            winner = int(np.argmax(scores))
            info["winner"] = winner
        else:
            info["winner"] = None
        
        return info
    
    def action_masks(self) -> np.ndarray:
        """
        Get boolean mask of valid actions.
        
        Required for algorithms like MaskablePPO in Stable Baselines3.
        
        Returns:
            Boolean array of shape (action_space.n,)
        """
        if self.game is None:
            return np.zeros(self.action_space.n, dtype=bool)
        return get_action_mask(self.game)
    
    def get_valid_actions(self) -> List[int]:
        """Get list of valid action indices."""
        if self.game is None:
            return []
        return get_valid_actions(self.game)
    
    def render(self) -> Optional[str]:
        """
        Render the environment.
        
        Returns:
            String representation if render_mode is "ansi", None otherwise
        """
        if self.game is None:
            return None
        
        if self.render_mode == "ansi" or self.render_mode == "human":
            board_str = self.game.board.to_string()
            scores = self.game.get_scores()
            status = (
                f"Turn {self.game.turn_number}, "
                f"Player {self.game.current_player_idx}, "
                f"Scores: {scores}"
            )
            output = f"{board_str}\n\n{status}"
            
            if self.render_mode == "human":
                print(output)
                return None
            return output
        
        return None
    
    def close(self):
        """Clean up resources."""
        self.game = None
        self.game_history = []


def make_duo_env(use_shaped_reward: bool = True) -> BlokusEnv:
    """Create a Blokus Duo (14×14, 2 players) environment."""
    return BlokusEnv(
        num_players=2,
        board_size=14,
        use_shaped_reward=use_shaped_reward
    )


def make_standard_env(
    num_players: int = 4,
    use_shaped_reward: bool = True
) -> BlokusEnv:
    """Create a Standard Blokus (20×20) environment."""
    return BlokusEnv(
        num_players=num_players,
        board_size=20,
        use_shaped_reward=use_shaped_reward
    )
