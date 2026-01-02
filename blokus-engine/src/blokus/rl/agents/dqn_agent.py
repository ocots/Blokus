"""
DQN Agent for Blokus.

Implements Double DQN with:
- Dueling architecture (in network)
- Prioritized Experience Replay
- Target network with soft updates
"""

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from collections import deque
from dataclasses import dataclass
from typing import Optional, Tuple, List
import random

from blokus.rl.agents.base import Agent
from blokus.rl.networks import BlokusQNetwork, create_network


@dataclass
class Transition:
    """Single experience transition."""
    state: np.ndarray
    action: int
    reward: float
    next_state: np.ndarray
    done: bool
    action_mask: np.ndarray
    next_action_mask: np.ndarray


class ReplayBuffer:
    """
    Experience replay buffer with uniform sampling.
    
    For simplicity, using uniform sampling first.
    PER can be added later.
    """
    
    def __init__(self, capacity: int = 100_000):
        self.buffer = deque(maxlen=capacity)
    
    def push(self, transition: Transition) -> None:
        """Add transition to buffer."""
        self.buffer.append(transition)
    
    def sample(self, batch_size: int) -> List[Transition]:
        """Sample batch of transitions."""
        return random.sample(self.buffer, min(batch_size, len(self.buffer)))
    
    def __len__(self) -> int:
        return len(self.buffer)


class DQNAgent(Agent):
    """
    Deep Q-Network agent for Blokus.
    
    Features:
    - Double DQN (uses online network for action selection, target for evaluation)
    - Dueling architecture (in network)
    - Epsilon-greedy exploration with decay
    - Experience replay
    - Soft target updates
    """
    
    def __init__(
        self,
        board_size: int = 14,
        learning_rate: float = 1e-4,
        gamma: float = 0.99,
        epsilon_start: float = 1.0,
        epsilon_end: float = 0.05,
        epsilon_decay: int = 50_000,
        buffer_size: int = 100_000,
        batch_size: int = 64,
        target_update_freq: int = 1000,
        tau: float = 0.005,
        device: str = "auto"
    ):
        """
        Initialize DQN agent.
        
        Args:
            board_size: Board size (14 or 20)
            learning_rate: Optimizer learning rate
            gamma: Discount factor
            epsilon_start: Initial exploration rate
            epsilon_end: Final exploration rate
            epsilon_decay: Episodes for epsilon decay
            buffer_size: Replay buffer capacity
            batch_size: Training batch size
            target_update_freq: Steps between target updates (if using hard updates)
            tau: Soft update coefficient
            device: "cpu", "cuda", or "auto"
        """
        # Device
        if device == "auto":
            device = "cuda" if torch.cuda.is_available() else "cpu"
        self.device = torch.device(device)
        
        self.board_size = board_size
        self.num_actions = 21 * 8 * board_size * board_size
        
        # Networks
        self.online_net = create_network(board_size, str(self.device))
        self.target_net = create_network(board_size, str(self.device))
        self.target_net.load_state_dict(self.online_net.state_dict())
        self.target_net.eval()
        
        # Optimizer
        self.optimizer = optim.Adam(self.online_net.parameters(), lr=learning_rate)
        
        # Replay buffer
        self.buffer = ReplayBuffer(buffer_size)
        self.batch_size = batch_size
        
        # Hyperparameters
        self.gamma = gamma
        self.tau = tau
        self.target_update_freq = target_update_freq
        
        # Exploration
        self.epsilon_start = epsilon_start
        self.epsilon_end = epsilon_end
        self.epsilon_decay = epsilon_decay
        self.epsilon = epsilon_start
        
        # Training state
        self.steps_done = 0
        self.episodes_done = 0
    
    def select_action(
        self,
        observation: np.ndarray,
        action_mask: np.ndarray,
        deterministic: bool = False
    ) -> int:
        """
        Select action using epsilon-greedy policy.
        
        Args:
            observation: Current state (board_size, board_size, 47)
            action_mask: Boolean mask of valid actions
            deterministic: If True, always use greedy action
            
        Returns:
            Selected action index, or 0 if no valid actions
        """
        valid_actions = np.where(action_mask)[0]
        if len(valid_actions) == 0:
            # No valid actions: return 0 (will trigger forced pass in environment)
            return 0
        
        epsilon = 0.0 if deterministic else self.epsilon
        
        if random.random() < epsilon:
            # Random valid action
            return int(np.random.choice(valid_actions))
        
        # Greedy action
        with torch.no_grad():
            state = torch.FloatTensor(observation).unsqueeze(0).to(self.device)
            mask = torch.BoolTensor(action_mask).unsqueeze(0).to(self.device)
            
            q_values = self.online_net(state)
            q_values[~mask] = -1e9
            
            return int(q_values.argmax(dim=1).item())
    
    def store_transition(
        self,
        state: np.ndarray,
        action: int,
        reward: float,
        next_state: np.ndarray,
        done: bool,
        action_mask: np.ndarray,
        next_action_mask: np.ndarray
    ) -> None:
        """Store transition in replay buffer."""
        transition = Transition(
            state=state,
            action=action,
            reward=reward,
            next_state=next_state,
            done=done,
            action_mask=action_mask,
            next_action_mask=next_action_mask
        )
        self.buffer.push(transition)
    
    def update(self) -> dict:
        """
        Perform one training step.
        
        Returns:
            Dict with loss and other metrics
        """
        if len(self.buffer) < self.batch_size:
            return {}
        
        # Sample batch
        transitions = self.buffer.sample(self.batch_size)
        
        # Convert to tensors
        states = torch.FloatTensor(
            np.array([t.state for t in transitions])
        ).to(self.device)
        actions = torch.LongTensor(
            [t.action for t in transitions]
        ).to(self.device)
        rewards = torch.FloatTensor(
            [t.reward for t in transitions]
        ).to(self.device)
        next_states = torch.FloatTensor(
            np.array([t.next_state for t in transitions])
        ).to(self.device)
        dones = torch.FloatTensor(
            [t.done for t in transitions]
        ).to(self.device)
        next_masks = torch.BoolTensor(
            np.array([t.next_action_mask for t in transitions])
        ).to(self.device)
        
        # Current Q values
        q_values = self.online_net(states)
        q_values = q_values.gather(1, actions.unsqueeze(1)).squeeze(1)
        
        # Double DQN: use online net for action selection, target for evaluation
        with torch.no_grad():
            # Select actions with online network
            next_q_online = self.online_net(next_states)
            next_q_online[~next_masks] = -1e9
            next_actions = next_q_online.argmax(dim=1)
            
            # Evaluate with target network
            next_q_target = self.target_net(next_states)
            next_q = next_q_target.gather(1, next_actions.unsqueeze(1)).squeeze(1)
            
            # TD target
            target = rewards + (1 - dones) * self.gamma * next_q
        
        # Loss
        loss = nn.SmoothL1Loss()(q_values, target)
        
        # Optimize
        self.optimizer.zero_grad()
        loss.backward()
        # Gradient clipping
        nn.utils.clip_grad_norm_(self.online_net.parameters(), max_norm=10.0)
        self.optimizer.step()
        
        # Soft update target network
        self._soft_update_target()
        
        self.steps_done += 1
        
        return {
            "loss": loss.item(),
            "q_mean": q_values.mean().item(),
            "q_max": q_values.max().item(),
        }
    
    def _soft_update_target(self) -> None:
        """Soft update of target network parameters."""
        for target_param, online_param in zip(
            self.target_net.parameters(),
            self.online_net.parameters()
        ):
            target_param.data.copy_(
                self.tau * online_param.data + (1 - self.tau) * target_param.data
            )
    
    def decay_epsilon(self) -> None:
        """Decay exploration rate."""
        self.episodes_done += 1
        
        # Linear decay
        decay_ratio = min(1.0, self.episodes_done / self.epsilon_decay)
        self.epsilon = self.epsilon_start + (self.epsilon_end - self.epsilon_start) * decay_ratio
    
    def reset(self) -> None:
        """Reset for new episode."""
        pass
    
    def state_dict(self) -> dict:
        """Get state dict for checkpointing."""
        return {
            "online_net": self.online_net.state_dict(),
            "target_net": self.target_net.state_dict(),
            "optimizer": self.optimizer.state_dict(),
            "epsilon": self.epsilon,
            "steps_done": self.steps_done,
            "episodes_done": self.episodes_done,
        }
    
    def load_state_dict(self, state_dict: dict) -> None:
        """Load state dict from checkpoint."""
        self.online_net.load_state_dict(state_dict["online_net"])
        self.target_net.load_state_dict(state_dict["target_net"])
        self.optimizer.load_state_dict(state_dict["optimizer"])
        self.epsilon = state_dict["epsilon"]
        self.steps_done = state_dict["steps_done"]
        self.episodes_done = state_dict["episodes_done"]
    
    def train_mode(self) -> None:
        """Set network to training mode."""
        self.online_net.train()
    
    def eval_mode(self) -> None:
        """Set network to evaluation mode."""
        self.online_net.eval()
