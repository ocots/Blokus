"""
Neural Network architectures for Blokus RL.

Implements CNN-based Q-Network for DQN training.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Tuple


class BlokusQNetwork(nn.Module):
    """
    Deep Q-Network for Blokus.
    
    Architecture:
    - Input: (batch, board_size, board_size, 47) observation tensor
    - Conv layers with residual connections
    - Dueling architecture: separate value and advantage streams
    - Output: Q-values for each action
    
    Based on AlphaGo-style architecture adapted for Blokus.
    """
    
    def __init__(
        self,
        board_size: int = 14,
        num_channels: int = 47,
        num_actions: int = 32928,  # 21 * 8 * 14 * 14 for Duo
        hidden_channels: int = 128,
        num_res_blocks: int = 4,
        fc_hidden: int = 512
    ):
        """
        Initialize Q-Network.
        
        Args:
            board_size: Board size (14 for Duo, 20 for Standard)
            num_channels: Number of input channels (47)
            num_actions: Size of action space
            hidden_channels: Channels in conv layers
            num_res_blocks: Number of residual blocks
            fc_hidden: Hidden units in fully connected layers
        """
        super().__init__()
        
        self.board_size = board_size
        self.num_channels = num_channels
        self.num_actions = num_actions
        
        # Initial convolution
        self.conv_input = nn.Sequential(
            nn.Conv2d(num_channels, hidden_channels, kernel_size=3, padding=1),
            nn.BatchNorm2d(hidden_channels),
            nn.ReLU()
        )
        
        # Residual blocks
        self.res_blocks = nn.ModuleList([
            ResidualBlock(hidden_channels) for _ in range(num_res_blocks)
        ])
        
        # Calculate flattened size after conv
        self.flat_size = hidden_channels * board_size * board_size
        
        # Dueling architecture
        # Value stream
        self.value_conv = nn.Sequential(
            nn.Conv2d(hidden_channels, 32, kernel_size=1),
            nn.BatchNorm2d(32),
            nn.ReLU()
        )
        self.value_fc = nn.Sequential(
            nn.Linear(32 * board_size * board_size, fc_hidden),
            nn.ReLU(),
            nn.Linear(fc_hidden, 1)
        )
        
        # Advantage stream
        self.adv_conv = nn.Sequential(
            nn.Conv2d(hidden_channels, 64, kernel_size=1),
            nn.BatchNorm2d(64),
            nn.ReLU()
        )
        self.adv_fc = nn.Sequential(
            nn.Linear(64 * board_size * board_size, fc_hidden),
            nn.ReLU(),
            nn.Linear(fc_hidden, num_actions)
        )
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Forward pass.
        
        Args:
            x: Input tensor (batch, board_size, board_size, channels)
               Note: Input is NHWC, needs transpose to NCHW for PyTorch
               
        Returns:
            Q-values (batch, num_actions)
        """
        # Transpose from NHWC to NCHW
        x = x.permute(0, 3, 1, 2)  # (batch, channels, height, width)
        
        # Initial conv
        x = self.conv_input(x)
        
        # Residual blocks
        for block in self.res_blocks:
            x = block(x)
        
        # Value stream
        v = self.value_conv(x)
        v = v.reshape(v.size(0), -1)
        v = self.value_fc(v)
        
        # Advantage stream
        a = self.adv_conv(x)
        a = a.reshape(a.size(0), -1)
        a = self.adv_fc(a)
        
        # Combine: Q = V + (A - mean(A))
        q = v + (a - a.mean(dim=1, keepdim=True))
        
        return q
    
    def get_action(
        self,
        x: torch.Tensor,
        action_mask: torch.Tensor,
        epsilon: float = 0.0
    ) -> torch.Tensor:
        """
        Get action with epsilon-greedy exploration.
        
        Args:
            x: Observation (1, board_size, board_size, channels)
            action_mask: Boolean mask of valid actions (1, num_actions)
            epsilon: Exploration rate
            
        Returns:
            Selected action index
        """
        if torch.rand(1).item() < epsilon:
            # Random valid action
            valid_actions = torch.where(action_mask[0])[0]
            idx = torch.randint(len(valid_actions), (1,))
            return valid_actions[idx]
        
        with torch.no_grad():
            q_values = self(x)
            # Mask invalid actions with very negative value
            q_values[~action_mask] = -1e9
            return q_values.argmax(dim=1)


class ResidualBlock(nn.Module):
    """Residual block with batch normalization."""
    
    def __init__(self, channels: int):
        super().__init__()
        self.conv1 = nn.Conv2d(channels, channels, kernel_size=3, padding=1)
        self.bn1 = nn.BatchNorm2d(channels)
        self.conv2 = nn.Conv2d(channels, channels, kernel_size=3, padding=1)
        self.bn2 = nn.BatchNorm2d(channels)
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        residual = x
        x = F.relu(self.bn1(self.conv1(x)))
        x = self.bn2(self.conv2(x))
        x = F.relu(x + residual)
        return x


def create_network(
    board_size: int = 14,
    device: str = "cpu"
) -> BlokusQNetwork:
    """
    Create Q-Network for given board size.
    
    Args:
        board_size: 14 for Duo, 20 for Standard
        device: "cpu" or "cuda"
        
    Returns:
        Initialized network
    """
    num_actions = 21 * 8 * board_size * board_size
    
    network = BlokusQNetwork(
        board_size=board_size,
        num_channels=47,
        num_actions=num_actions,
        hidden_channels=128,
        num_res_blocks=4,
        fc_hidden=512
    )
    
    return network.to(device)
