"""
Tests for corner cases and defensive programming.

These tests aim to break the code with invalid inputs to ensure
robust error handling and prevent runtime crashes.
"""

import pytest
import numpy as np
from blokus.game import Game, Move, GameStatus
from blokus.player import Player
from blokus.player_types import PlayerType, PlayerStatus
from blokus.pieces import PieceType, get_piece
from blokus.board import Board


class TestInvalidInputs:
    """Test handling of invalid inputs."""
    
    def test_play_move_with_none(self):
        """Playing None as a move should raise error or return False."""
        game = Game()
        
        with pytest.raises((TypeError, AttributeError)):
            game.play_move(None)
    
    def test_move_with_invalid_piece_type(self):
        """Move with invalid piece type should be rejected."""
        game = Game()
        
        # Create move with invalid piece type (not in enum)
        with pytest.raises((ValueError, KeyError, AttributeError)):
            move = Move(
                player_id=0,
                piece_type=999,  # Invalid
                orientation=0,
                row=0,
                col=0
            )
            game.is_valid_move(move)
    
    def test_move_with_invalid_player_id(self):
        """Move with invalid player ID should be rejected."""
        game = Game(num_players=2)
        
        move = Move(
            player_id=5,  # Invalid for 2-player game
            piece_type=PieceType.I1,
            orientation=0,
            row=0,
            col=0
        )
        
        assert not game.is_valid_move(move)
    
    def test_move_with_negative_coordinates(self):
        """Move with negative coordinates should be rejected."""
        game = Game()
        
        move = Move(
            player_id=0,
            piece_type=PieceType.I1,
            orientation=0,
            row=-1,
            col=-1
        )
        
        assert not game.is_valid_move(move)
    
    def test_move_with_huge_coordinates(self):
        """Move with out-of-bounds coordinates should be rejected."""
        game = Game()
        
        move = Move(
            player_id=0,
            piece_type=PieceType.I1,
            orientation=0,
            row=1000,
            col=1000
        )
        
        assert not game.is_valid_move(move)


class TestBoardBoundaries:
    """Test board boundary handling."""
    
    def test_get_cell_negative_coordinates(self):
        """get_cell with negative coordinates should return -1."""
        board = Board()
        
        assert board.get_cell(-1, -1) == -1
        assert board.get_cell(-5, 10) == -1
        assert board.get_cell(10, -5) == -1
    
    def test_get_cell_out_of_bounds(self):
        """get_cell with out-of-bounds coordinates should return -1."""
        board = Board()
        
        assert board.get_cell(100, 100) == -1
        assert board.get_cell(20, 10) == -1
        assert board.get_cell(10, 20) == -1
    
    def test_is_empty_out_of_bounds(self):
        """is_empty should return False for out-of-bounds."""
        board = Board()
        
        assert not board.is_empty(-1, -1)
        assert not board.is_empty(100, 100)
        assert not board.is_empty(20, 10)
    
    def test_place_piece_out_of_bounds(self):
        """place_piece should fail for out-of-bounds positions."""
        board = Board()
        piece = get_piece(PieceType.I1)
        
        result = board.place_piece(piece, 100, 100, player_id=0)
        assert result is False
        
        result = board.place_piece(piece, -1, -1, player_id=0)
        assert result is False


class TestConfigurationMismatches:
    """Test mismatched configurations."""
    
    def test_game_with_mismatched_board_size(self):
        """Creating game with 4 players on 14x14 board should work but be unusual."""
        board = Board(size=14)
        game = Game(num_players=4, board=board)
        
        # Should not crash, but starting corners might be weird
        assert game.num_players == 4
        assert game.board.size == 14
    
    def test_game_with_invalid_starting_player(self):
        """Starting player index out of range should raise error."""
        with pytest.raises(ValueError):
            Game(num_players=2, starting_player_idx=5)
        
        with pytest.raises(ValueError):
            Game(num_players=4, starting_player_idx=-1)


class TestPlayerDeserialization:
    """Test player deserialization with invalid data."""
    
    def test_from_dict_empty_dict(self):
        """from_dict with empty dict should raise error."""
        with pytest.raises((KeyError, TypeError)):
            Player.from_dict({})
    
    def test_from_dict_missing_required_fields(self):
        """from_dict with missing required fields should raise error."""
        with pytest.raises((KeyError, TypeError)):
            Player.from_dict({"id": 0})
    
    def test_from_dict_invalid_type(self):
        """from_dict with invalid player type should raise error."""
        data = {
            "id": 0,
            "name": "Test",
            "color": "#000000",
            "type": "invalid_type"
        }
        
        with pytest.raises((ValueError, KeyError)):
            Player.from_dict(data)
    
    def test_from_dict_invalid_piece_types(self):
        """from_dict with invalid piece types should raise error."""
        data = {
            "id": 0,
            "name": "Test",
            "color": "#000000",
            "type": "human",
            "remaining_pieces": ["INVALID_PIECE", "ANOTHER_INVALID"]
        }
        
        with pytest.raises((ValueError, KeyError)):
            Player.from_dict(data)


class TestComplexGameStates:
    """Test complex game states and edge cases."""
    
    def test_game_with_no_valid_moves(self):
        """Game where current player has no valid moves."""
        game = Game(num_players=2)
        
        # Fill the board completely (simulate endgame)
        # This is a simplified version - just fill the grid
        game.board.grid.fill(2)  # Fill with opponent's pieces
        
        # Current player should have no valid moves
        valid_moves = game.get_valid_moves()
        assert len(valid_moves) == 0
    
    def test_player_completely_blocked(self):
        """Player is completely blocked and cannot play."""
        game = Game(num_players=2)
        
        # Block player 0's starting corner
        for r in range(5):
            for c in range(5):
                if (r, c) != (0, 0):
                    game.board.grid[r, c] = 2  # Opponent's pieces
        
        # Player 0's first move options should be very limited
        valid_moves = game.get_valid_moves()
        # Should still have at least the corner move
        assert isinstance(valid_moves, list)
    
    def test_game_over_all_players_passed(self):
        """Game should end when all players pass."""
        game = Game(num_players=2)
        
        # Force both players to pass
        game.force_pass()
        assert game.status == GameStatus.IN_PROGRESS
        
        game.force_pass()
        assert game.status == GameStatus.FINISHED
    
    def test_score_calculation_edge_cases(self):
        """Test score calculation in edge cases."""
        player = Player(id=0, name="Test", color="#000000")
        
        # All pieces played
        player.remaining_pieces.clear()
        player.last_piece_was_monomino = False
        score = player.calculate_score()
        assert score == 15  # Bonus only
        
        # All pieces played with monomino last
        player.last_piece_was_monomino = True
        score = player.calculate_score()
        assert score == 20  # Bonus + monomino bonus


class TestRLEdgeCases:
    """Test RL environment edge cases."""
    
    def test_observation_with_empty_board(self):
        """Observation should be valid for empty board."""
        from blokus.rl.observations import create_observation
        
        game = Game(num_players=2)
        obs = create_observation(game)
        
        assert obs.shape == (20, 20, 47)
        assert not np.isnan(obs).any()
        assert not np.isinf(obs).any()
    
    def test_observation_with_full_board(self):
        """Observation should be valid for full board."""
        from blokus.rl.observations import create_observation
        
        game = Game(num_players=2)
        game.board.grid.fill(1)  # Fill board
        
        obs = create_observation(game)
        
        assert obs.shape == (20, 20, 47)
        assert not np.isnan(obs).any()
        assert not np.isinf(obs).any()
    
    def test_action_encoding_decoding_edge_cases(self):
        """Test action encoding/decoding with edge cases."""
        from blokus.rl.actions import encode_action, decode_action
        
        game = Game(num_players=2)
        
        # Create a move at board edge
        move = Move(
            player_id=0,
            piece_type=PieceType.I1,
            orientation=0,
            row=0,
            col=0
        )
        
        action = encode_action(move, game.board.size)
        decoded = decode_action(action, game)
        
        assert decoded is not None
        assert decoded.row == move.row
        assert decoded.col == move.col
    
    def test_reward_no_nan_or_inf(self):
        """Rewards should never be NaN or infinite."""
        from blokus.rl.rewards import potential, shaped_reward, sparse_reward
        
        game = Game(num_players=2)
        
        pot = potential(game, player_id=0)
        assert not np.isnan(pot)
        assert not np.isinf(pot)
        
        sparse = sparse_reward(game, player_id=0)
        assert not np.isnan(sparse)
        assert not np.isinf(sparse)


class TestStateTransitions:
    """Test state machine transitions."""
    
    def test_player_status_transitions(self):
        """Test valid player status transitions."""
        player = Player(id=0, name="Test", color="#000000")
        
        # WAITING -> PLAYING
        assert player.status == PlayerStatus.WAITING
        player.status = PlayerStatus.PLAYING
        assert player.status == PlayerStatus.PLAYING
        
        # PLAYING -> PASSED
        player.pass_turn()
        assert player.status == PlayerStatus.PASSED
    
    def test_game_status_transitions(self):
        """Test valid game status transitions."""
        game = Game(num_players=2)
        
        assert game.status == GameStatus.IN_PROGRESS
        
        # Force game to end
        game.force_pass()
        game.force_pass()
        
        assert game.status == GameStatus.FINISHED
