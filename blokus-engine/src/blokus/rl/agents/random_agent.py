"""
Random agent for Blokus - used as baseline for evaluation.
"""

import numpy as np
from blokus.rl.agents.base import Agent


class RandomAgent(Agent):
    """
    Random agent that selects uniformly from valid actions.
    
    Used as a fixed baseline for measuring training progress.
    Always uses seed=42 for reproducibility in evaluations.
    """
    
    def __init__(self, seed: int = 42):
        """
        Initialize random agent.
        
        Args:
            seed: Random seed for reproducibility
        """
        self.seed = seed
        self.rng = np.random.default_rng(seed)
    
    def select_action(
        self,
        observation: np.ndarray,
        action_mask: np.ndarray,
        deterministic: bool = False
    ) -> int:
        """
        Select a random valid action.
        
        Args:
            observation: Current state (ignored by random agent)
            action_mask: Boolean mask of valid actions
            deterministic: Ignored (random is always stochastic)
            
        Returns:
            Randomly selected valid action, or 0 if no valid actions
        """
        valid_actions = np.where(action_mask)[0]
        if len(valid_actions) == 0:
            # No valid actions: return 0 (will trigger forced pass in environment)
            return 0
        return int(self.rng.choice(valid_actions))
    
    def reset(self) -> None:
        """Reset RNG for reproducible evaluation."""
        self.rng = np.random.default_rng(self.seed)
