import torch
import pytest
import numpy as np
from blokus.rl.networks import BlokusQNetwork, ResidualBlock, create_network

class TestResidualBlock:
    def test_residual_block_shape(self):
        """Residual block should preserve input shape and add residual."""
        channels = 64
        size = 14
        block = ResidualBlock(channels)
        x = torch.randn(2, channels, size, size)
        output = block(x)
        assert output.shape == (2, channels, size, size)

    def test_residual_block_gradient(self):
        """Residual block should allow gradient flow."""
        channels = 32
        block = ResidualBlock(channels)
        x = torch.randn(1, channels, 14, 14, requires_grad=True)
        output = block(x)
        loss = output.sum()
        loss.backward()
        assert x.grad is not None

class TestBlokusQNetwork:
    def test_network_init(self):
        """Network should initialize with correct dimensions."""
        board_size = 14
        num_actions = 21 * 8 * board_size * board_size
        network = BlokusQNetwork(
            board_size=board_size,
            num_actions=num_actions,
            hidden_channels=64,
            num_res_blocks=2
        )
        assert network.board_size == board_size
        assert network.num_actions == num_actions

    def test_network_forward_shape(self):
        """Forward pass should return correct Q-value shape."""
        batch_size = 4
        board_size = 14
        num_channels = 47
        num_actions = 100
        network = BlokusQNetwork(
            board_size=board_size,
            num_channels=num_channels,
            num_actions=num_actions,
            hidden_channels=32,
            num_res_blocks=1
        )
        
        # Input is NHWC: (batch, height, width, channels)
        x = torch.randn(batch_size, board_size, board_size, num_channels)
        output = network(x)
        assert output.shape == (batch_size, num_actions)

    def test_get_action_greedy(self):
        """get_action should return the best valid action when epsilon=0."""
        board_size = 14
        num_actions = 10
        network = BlokusQNetwork(
            board_size=board_size,
            num_actions=num_actions,
            hidden_channels=16,
            num_res_blocks=1
        )
        network.eval()
        
        obs = torch.randn(1, board_size, board_size, 47)
        mask = torch.ones(1, num_actions, dtype=torch.bool)
        # Disable one action
        mask[0, 2] = False
        
        with torch.no_grad():
            # Mock forward to return predictable values
            # We can't easily mock the call because it's nn.Module, 
            # but we can check if it respects the mask.
            action = network.get_action(obs, mask, epsilon=0.0)
            assert action.item() != 2
            assert 0 <= action.item() < num_actions

    def test_get_action_random(self):
        """get_action should return a random valid action when epsilon=1."""
        board_size = 14
        num_actions = 5
        network = BlokusQNetwork(
            board_size=board_size,
            num_actions=num_actions
        )
        
        obs = torch.randn(1, board_size, board_size, 47)
        # Only actions 1 and 3 are valid
        mask = torch.tensor([[False, True, False, True, False]], dtype=torch.bool)
        
        # Run multiple times to check if it only picks 1 or 3
        for _ in range(20):
            action = network.get_action(obs, mask, epsilon=1.0)
            assert action.item() in [1, 3]

    def test_create_network_helper(self):
        """create_network should return a network on the correct device."""
        network = create_network(board_size=14, device="cpu")
        assert isinstance(network, BlokusQNetwork)
        assert network.board_size == 14
