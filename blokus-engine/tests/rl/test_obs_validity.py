"""
Tests for RL observation content validity.

These tests verify that observations contain the correct data,
not just the correct shape. This prevents the RL agent from
learning on noise due to channel permutations or incorrect encoding.
"""

import pytest
import numpy as np
from blokus.game import Game, Move
from blokus.pieces import PieceType, ORIENTATION_HORIZONTAL
from blokus.rl.observations import create_observation
from blokus.rl.channels import ObservationChannel, NUM_CHANNELS


class TestObservationContent:
    """Test that observation tensors contain correct data."""
    
    def test_empty_board_all_zeros(self):
        """Empty board should have all piece channels at 0."""
        game = Game(num_players=2)
        obs = create_observation(game)
        
        # Channels 0-3 are player pieces (should be 0 on empty board)
        for player_id in range(2):
            channel = ObservationChannel.PLAYER_1_OCCUPANCY + player_id
            assert obs[:, :, channel].sum() == 0, f"Player {player_id} channel should be empty"
    
    def test_player_piece_placement_channel_0(self):
        """Placing a piece for player 0 should update channel 0."""
        game = Game(num_players=2)
        
        # Place I1 (monomino) at (0,0) for player 0
        move = Move(player_id=0, piece_type=PieceType.I1, orientation=0, row=0, col=0)
        game.play_move(move)
        
        obs = create_observation(game)
        
        # Channel 0 = player 0's pieces
        channel_p0 = ObservationChannel.PLAYER_1_OCCUPANCY
        channel_p1 = ObservationChannel.PLAYER_2_OCCUPANCY
        
        assert obs[0, 0, channel_p0] == 1.0, "Player 0's piece should be at (0,0)"
        assert obs[0, 0, channel_p1] == 0.0, "Player 1 should have no piece at (0,0)"
        
        # Rest of player 0's channel should be empty
        assert obs[:, :, channel_p0].sum() == 1.0, "Only one cell should be occupied"
    
    def test_player_piece_placement_channel_1(self):
        """Placing a piece for player 1 should update channel 1."""
        game = Game(num_players=2)
        
        # Player 0 plays first
        move0 = Move(player_id=0, piece_type=PieceType.I1, orientation=0, row=0, col=0)
        game.play_move(move0)
        
        # Player 1 plays at top-right corner
        move1 = Move(player_id=1, piece_type=PieceType.I1, orientation=0, row=0, col=19)
        game.play_move(move1)
        
        obs = create_observation(game)
        
        channel_p0 = ObservationChannel.PLAYER_1_OCCUPANCY
        channel_p1 = ObservationChannel.PLAYER_2_OCCUPANCY
        
        # Channel 1 = player 1's pieces
        assert obs[0, 19, channel_p1] == 1.0, "Player 1's piece should be at (0,19)"
        assert obs[0, 19, channel_p0] == 0.0, "Player 0 should have no piece at (0,19)"
        assert obs[0, 0, channel_p1] == 0.0, "Player 1 should have no piece at (0,0)"
    
    def test_multi_cell_piece_placement(self):
        """Placing a multi-cell piece should update all cells."""
        game = Game(num_players=2)
        
        # Place I2 (domino) at (0,0) for player 0
        # I2 orientation 0 is horizontal: occupies (0,0) and (0,1)
        move = Move(player_id=0, piece_type=PieceType.I2, orientation=0, row=0, col=0)
        game.play_move(move)
        
        obs = create_observation(game)
        
        channel_p0 = ObservationChannel.PLAYER_1_OCCUPANCY
        
        # Both cells should be marked
        assert obs[0, 0, channel_p0] == 1.0, "Cell (0,0) should be occupied"
        assert obs[0, 1, channel_p0] == 1.0, "Cell (0,1) should be occupied"
        assert obs[:, :, channel_p0].sum() == 2.0, "Exactly 2 cells should be occupied"
    
    def test_available_pieces_channels(self):
        """Channels 17-37 should indicate available pieces for current player."""
        game = Game(num_players=2)
        obs = create_observation(game)
        
        # Initially, all pieces should be available (channels 17-37 for current player)
        # Each piece channel should be all 1s if available
        for piece_idx in range(21):
            channel_idx = ObservationChannel.AVAILABLE_PIECES_START + piece_idx
            # Available piece = all cells set to 1
            assert obs[0, 0, channel_idx] == 1.0, f"Piece {piece_idx} should be available"
    
    def test_piece_becomes_unavailable_after_play(self):
        """After playing a piece, its channel should become 0."""
        game = Game(num_players=2)
        
        # Play I1 (index 0 in PieceType enum)
        move = Move(player_id=0, piece_type=PieceType.I1, orientation=0, row=0, col=0)
        game.play_move(move)
        
        # Observation from perspective of player 1 (current player after move)
        obs = create_observation(game, perspective_player=1)
        
        # For player 1, I1 should still be available (they haven't played it)
        i1_channel_idx = ObservationChannel.AVAILABLE_PIECES_START + list(PieceType).index(PieceType.I1)
        assert obs[0, 0, i1_channel_idx] == 1.0, "I1 should be available for player 1"
        
        # Check from player 0's perspective
        obs0 = create_observation(game, perspective_player=0)
        i1_channel_idx = ObservationChannel.AVAILABLE_PIECES_START + list(PieceType).index(PieceType.I1)
        assert obs0[0, 0, i1_channel_idx] == 0.0, "I1 should no longer be available for player 0"
    
    def test_first_move_flags(self):
        """Channels 42-45 should indicate first move status."""
        game = Game(num_players=4)
        obs = create_observation(game)
        
        # All players should have first move flag set initially
        for player_id in range(4):
            first_move_channel = ObservationChannel.PLAYER_1_FIRST_MOVE + player_id
            assert obs[0, 0, first_move_channel] == 1.0, f"Player {player_id} should have first move flag"
    
    def test_first_move_flag_cleared_after_move(self):
        """First move flag should be cleared after playing."""
        game = Game(num_players=2)
        
        # Player 0 plays
        move = Move(player_id=0, piece_type=PieceType.I1, orientation=0, row=0, col=0)
        game.play_move(move)
        
        obs = create_observation(game)
        
        # Player 0's first move flag should be cleared
        channel_p0_first = ObservationChannel.PLAYER_1_FIRST_MOVE
        assert obs[0, 0, channel_p0_first] == 0.0, "Player 0 should no longer have first move flag"
        
        # Player 1's first move flag should still be set
        channel_p1_first = ObservationChannel.PLAYER_2_FIRST_MOVE
        assert obs[0, 0, channel_p1_first] == 1.0, "Player 1 should still have first move flag"
    
    def test_current_player_channel(self):
        """Channel 46 should indicate current player."""
        game = Game(num_players=2)
        obs = create_observation(game)
        
        # Current player channel should be filled with player ID / (num_players - 1)
        # For player 0 in 2-player game: 0 / 1 = 0.0
        expected_value = 0.0 / (2 - 1) if 2 > 1 else 0.0
        channel = ObservationChannel.CURRENT_PLAYER_ID
        assert obs[0, 0, channel] == expected_value, "Current player channel incorrect"
    
    def test_no_nan_or_inf_values(self):
        """Observations should never contain NaN or Inf."""
        game = Game(num_players=2)
        
        # Play several moves
        for _ in range(5):
            valid_moves = game.get_valid_moves()
            if valid_moves:
                game.play_move(valid_moves[0])
        
        obs = create_observation(game)
        
        assert not np.isnan(obs).any(), "Observation contains NaN values"
        assert not np.isinf(obs).any(), "Observation contains Inf values"
    
    def test_observation_values_in_range(self):
        """All observation values should be in [0, 1]."""
        game = Game(num_players=2)
        
        # Play several moves
        for _ in range(5):
            valid_moves = game.get_valid_moves()
            if valid_moves:
                game.play_move(valid_moves[0])
        
        obs = create_observation(game)
        
        assert obs.min() >= 0.0, f"Observation has values < 0: {obs.min()}"
        assert obs.max() <= 1.0, f"Observation has values > 1: {obs.max()}"
    
    def test_observation_dtype(self):
        """Observations should be float32."""
        game = Game(num_players=2)
        obs = create_observation(game)
        
        assert obs.dtype == np.float32, f"Expected float32, got {obs.dtype}"
    
    def test_observation_deterministic(self):
        """Same game state should produce same observation."""
        game1 = Game(num_players=2)
        game2 = Game(num_players=2)
        
        # Play same moves in both games
        move = Move(player_id=0, piece_type=PieceType.I1, orientation=0, row=0, col=0)
        game1.play_move(move)
        game2.play_move(move)
        
        obs1 = create_observation(game1)
        obs2 = create_observation(game2)
        
        assert np.array_equal(obs1, obs2), "Same game state should produce identical observations"


class TestObservationEdgeCases:
    """Test observation generation in edge cases."""
    
    def test_observation_after_game_over(self):
        """Observation should be valid even after game over."""
        game = Game(num_players=2)
        
        # Force game over
        game.force_pass()
        game.force_pass()
        
        obs = create_observation(game)
        
        assert obs.shape == (20, 20, NUM_CHANNELS)
        assert not np.isnan(obs).any()
    
    def test_observation_with_full_board(self):
        """Observation should handle full board."""
        game = Game(num_players=2)
        
        # Simulate full board
        game.board.grid.fill(1)
        
        obs = create_observation(game)
        
        assert obs.shape == (20, 20, NUM_CHANNELS)
        assert not np.isnan(obs).any()
    
    def test_observation_duo_mode(self):
        """Observation should work for 14x14 Duo mode."""
        from blokus.board import Board
        
        board = Board(size=14)
        game = Game(num_players=2, board=board)
        
        obs = create_observation(game)
        
        assert obs.shape == (14, 14, NUM_CHANNELS)
        assert obs.dtype == np.float32
    
    def test_observation_consistency_across_turns(self):
        """Observation should remain consistent as game progresses."""
        game = Game(num_players=2)
        
        observations = []
        for _ in range(10):
            obs = create_observation(game)
            observations.append(obs.copy())
            
            valid_moves = game.get_valid_moves()
            if valid_moves:
                game.play_move(valid_moves[0])
            else:
                break
        
        # Each observation should be valid
        for i, obs in enumerate(observations):
            assert obs.shape == (20, 20, NUM_CHANNELS), f"Observation {i} has wrong shape"
            assert not np.isnan(obs).any(), f"Observation {i} contains NaN"
            assert not np.isinf(obs).any(), f"Observation {i} contains Inf"
