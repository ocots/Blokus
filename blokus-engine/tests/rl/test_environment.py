"""
Tests for the Blokus RL environment.
"""

import pytest
import numpy as np
from blokus.game import Game, GameStatus
from blokus.board import Board
from blokus.rl.observations import create_observation, NUM_CHANNELS
from blokus.rl.actions import (
    encode_action, 
    decode_action, 
    get_action_mask,
    get_action_space_size
)
from blokus.rl.rewards import potential, shaped_reward, sparse_reward


class TestObservations:
    """Tests for observation tensor creation."""
    
    def test_observation_shape_duo(self):
        """Duo mode should produce 14x14x47 tensor."""
        board = Board(size=14)
        game = Game(num_players=2, board=board)
        obs = create_observation(game)
        assert obs.shape == (14, 14, NUM_CHANNELS)
        assert obs.dtype == np.float32
    
    def test_observation_shape_standard(self):
        """Standard mode should produce 20x20x47 tensor."""
        game = Game(num_players=4)
        obs = create_observation(game)
        assert obs.shape == (20, 20, NUM_CHANNELS)
    
    def test_observation_values_in_range(self):
        """All observation values should be in [0, 1]."""
        game = Game(num_players=2)
        obs = create_observation(game)
        assert obs.min() >= 0.0
        assert obs.max() <= 1.0
    
    def test_first_move_flags_initially_set(self):
        """First move flags should all be 1 at start."""
        game = Game(num_players=4)
        obs = create_observation(game)
        # Channels 42-45 are first move flags
        for player_id in range(4):
            assert obs[0, 0, 42 + player_id] == 1.0


class TestActions:
    """Tests for action encoding/decoding."""
    
    def test_action_space_size_duo(self):
        """Duo (14x14) action space size."""
        size = get_action_space_size(14)
        # 21 pieces × 8 orientations × 14 × 14
        assert size == 21 * 8 * 14 * 14
    
    def test_action_space_size_standard(self):
        """Standard (20x20) action space size."""
        size = get_action_space_size(20)
        # 21 pieces × 8 orientations × 20 × 20
        assert size == 21 * 8 * 20 * 20
    
    def test_encode_decode_roundtrip(self):
        """Encoding then decoding should return equivalent move."""
        game = Game(num_players=2)
        valid_moves = game.get_valid_moves()
        assert len(valid_moves) > 0
        
        for move in valid_moves[:5]:  # Test first 5 moves
            action = encode_action(move, game.board.size)
            decoded = decode_action(action, game)
            
            assert decoded is not None
            assert decoded.piece_type == move.piece_type
            assert decoded.orientation == move.orientation
            assert decoded.row == move.row
            assert decoded.col == move.col
    
    def test_action_mask_has_valid_actions(self):
        """Action mask should have some True values at game start."""
        game = Game(num_players=2)
        mask = get_action_mask(game)
        assert mask.any()
    
    def test_action_mask_matches_valid_moves(self):
        """Number of True values should match valid moves count."""
        game = Game(num_players=2)
        mask = get_action_mask(game)
        valid_moves = game.get_valid_moves()
        assert mask.sum() == len(valid_moves)


class TestRewards:
    """Tests for reward functions."""
    
    def test_initial_potential(self):
        """Initial potential should be negative (big pieces penalty)."""
        game = Game(num_players=2)
        pot = potential(game, player_id=0)
        # Initial: 0 placed, starting corners, 12 big pieces
        assert pot < 0  # Big pieces penalty dominates
    
    def test_potential_increases_after_placement(self):
        """Potential should increase after placing a piece."""
        game = Game(num_players=2)
        pot_before = potential(game, player_id=0)
        
        # Play a move
        moves = game.get_valid_moves()
        game.play_move(moves[0])
        
        pot_after = potential(game, player_id=0)
        assert pot_after > pot_before
    
    def test_sparse_reward_zero_during_game(self):
        """Sparse reward should be 0 when game is not over."""
        game = Game(num_players=2)
        reward = sparse_reward(game, player_id=0)
        assert reward == 0.0
    
    def test_shaped_reward_positive_for_good_move(self):
        """Shaped reward should be positive for placing pieces."""
        game = Game(num_players=2)
        game_before = game.copy()
        moves = game.get_valid_moves()
        move = moves[0]
        game.play_move(move)
        
        reward = shaped_reward(game_before, move, game, player_id=0)
        assert reward > 0  # Placing a piece should give positive reward


class TestEnvironmentIntegration:
    """Integration tests (requires gymnasium)."""
    
    @pytest.fixture
    def env(self):
        """Create environment if gymnasium is available."""
        try:
            from blokus.rl import BlokusEnv
            if BlokusEnv is None:
                pytest.skip("gymnasium not installed")
            return BlokusEnv(num_players=2, board_size=14, render_mode="ansi")
        except ImportError:
            pytest.skip("gymnasium not installed")
    
    def test_reset_returns_valid_observation(self, env):
        """Reset should return observation with correct shape."""
        obs, info = env.reset()
        assert obs.shape == (14, 14, 47)
        assert "current_player" in info
    
    def test_step_with_valid_action(self, env):
        """Step with valid action should return proper tuple."""
        env.reset()
        mask = env.action_masks()
        valid_action = np.where(mask)[0][0]
        
        obs, reward, terminated, truncated, info = env.step(valid_action)
        
        assert obs.shape == (14, 14, 47)
        assert isinstance(reward, float)
        assert isinstance(terminated, bool)
        assert isinstance(truncated, bool)
        assert isinstance(info, dict)
    
    def test_step_with_invalid_action_terminates(self, env):
        """Step with invalid action should terminate with penalty."""
        env.reset()
        mask = env.action_masks()
        # Find an invalid action
        invalid_actions = np.where(~mask)[0]
        invalid_action = invalid_actions[0]
        
        obs, reward, terminated, truncated, info = env.step(invalid_action)
        
        assert terminated
        assert reward < 0
        assert info["valid_action"] == False
    
    def test_complete_episode(self, env):
        """Should be able to run a complete episode."""
        obs, info = env.reset()
        done = False
        steps = 0
        
        while not done and steps < 200:
            mask = env.action_masks()
            valid_actions = np.where(mask)[0]
            if len(valid_actions) == 0:
                break
            action = np.random.choice(valid_actions)
            obs, reward, terminated, truncated, info = env.step(action)
            done = terminated or truncated
            steps += 1
        
        # Game should have progressed
        assert steps > 0

    def test_render_modes(self, env):
        """Should support ansi and human render modes."""
        env.reset()
        ansi_render = env.render()
        assert isinstance(ansi_render, str)
        assert len(ansi_render) > 0
        
        # Human mode should not crash (usually prints)
        env.render_mode = "human"
        env.render()

    def test_close_env(self, env):
        """Close should not raise error and should be idempotent."""
        env.close()
        env.close()

    def test_step_before_reset_raises(self, env):
        """Stepping before reset should raise an error as per Gym API."""
        # Clean env (new instance)
        from blokus.rl.environment import BlokusEnv
        raw_env = BlokusEnv(num_players=2, board_size=14)
        with pytest.raises(RuntimeError, match="not initialized"):
             raw_env.step(0)

