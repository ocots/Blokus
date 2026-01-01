"""
Base agent interface for Blokus RL.
"""

from abc import ABC, abstractmethod
import numpy as np


class Agent(ABC):
    """
    Abstract base class for Blokus agents.
    
    All agents must implement the select_action method.
    """
    
    @abstractmethod
    def select_action(
        self,
        observation: np.ndarray,
        action_mask: np.ndarray,
        deterministic: bool = False
    ) -> int:
        """
        Select an action given the current observation.
        
        Args:
            observation: Current state observation (board_size, board_size, channels)
            action_mask: Boolean mask of valid actions
            deterministic: If True, use greedy action selection
            
        Returns:
            Selected action index
        """
        pass
    
    def reset(self) -> None:
        """Reset agent state for new episode (optional)."""
        pass
    
    def update(self, *args, **kwargs) -> dict:
        """
        Update agent (training step).
        
        Returns:
            Dict of metrics (e.g., loss)
        """
        return {}
