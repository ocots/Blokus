"""Tests for the game module."""

import pytest
from blokus.game import Game, GameStatus, Move, Player
from blokus.pieces import PieceType, get_piece


class TestGameInitialization:
    """Test game initialization."""
    
    def test_default_four_players(self):
        """Default game has 4 players."""
        game = Game()
        assert game.num_players == 4
        assert len(game.players) == 4
    
    def test_two_player_game(self):
        """Can create 2-player game."""
        game = Game(num_players=2)
        assert game.num_players == 2
        assert len(game.players) == 2
    
    def test_all_pieces_available(self):
        """Each player starts with all 21 pieces."""
        game = Game()
        for player in game.players:
            assert len(player.remaining_pieces) == 21
    
    def test_starts_with_player_zero(self):
        """Game starts with player 0."""
        game = Game()
        assert game.current_player_idx == 0
    
    def test_game_in_progress(self):
        """Game starts in progress."""
        game = Game()
        assert game.status == GameStatus.IN_PROGRESS


class TestPlayerState:
    """Test player state tracking."""
    
    def test_player_squares_remaining(self):
        """Player starts with 89 squares."""
        player = Player(id=0)
        assert player.squares_remaining == 89
    
    def test_player_pieces_count(self):
        """Player starts with 21 pieces."""
        player = Player(id=0)
        assert player.pieces_count == 21


class TestMoveValidation:
    """Test move validation."""
    
    def test_valid_first_move(self):
        """First move at corner is valid."""
        game = Game()
        move = Move(
            player_id=0,
            piece_type=PieceType.I1,
            orientation=0,
            row=0,
            col=0
        )
        assert game.is_valid_move(move)
    
    def test_invalid_wrong_player(self):
        """Move by wrong player is invalid."""
        game = Game()
        move = Move(
            player_id=1,  # Not player 0's turn
            piece_type=PieceType.I1,
            orientation=0,
            row=0,
            col=19
        )
        assert not game.is_valid_move(move)
    
    def test_invalid_piece_not_available(self):
        """Cannot use piece already played."""
        game = Game()
        
        # Play monomino
        move1 = Move(
            player_id=0,
            piece_type=PieceType.I1,
            orientation=0,
            row=0,
            col=0
        )
        game.play_move(move1)
        
        # Advance to player 0's turn again
        for i in range(3):
            game.force_pass()
        
        # Try to play monomino again
        move2 = Move(
            player_id=0,
            piece_type=PieceType.I1,
            orientation=0,
            row=1,
            col=1
        )
        assert not game.is_valid_move(move2)


class TestPlayMove:
    """Test executing moves."""
    
    def test_play_first_move(self):
        """Play first move successfully."""
        game = Game()
        move = Move(
            player_id=0,
            piece_type=PieceType.I1,
            orientation=0,
            row=0,
            col=0
        )
        
        result = game.play_move(move)
        
        assert result is True
        assert game.board.grid[0, 0] == 1
        assert PieceType.I1 not in game.players[0].remaining_pieces
        assert game.turn_number == 1
    
    def test_turn_advances_after_move(self):
        """Turn advances to next player after move."""
        game = Game()
        assert game.current_player_idx == 0
        
        move = Move(
            player_id=0,
            piece_type=PieceType.I1,
            orientation=0,
            row=0,
            col=0
        )
        game.play_move(move)
        
        assert game.current_player_idx == 1
    
    def test_move_history_recorded(self):
        """Moves are recorded in history."""
        game = Game()
        move = Move(
            player_id=0,
            piece_type=PieceType.I1,
            orientation=0,
            row=0,
            col=0
        )
        game.play_move(move)
        
        assert len(game.move_history) == 1
        assert game.move_history[0] == move


class TestGetValidMoves:
    """Test getting all valid moves."""
    
    def test_first_move_has_valid_moves(self):
        """First move has many valid options."""
        game = Game()
        moves = game.get_valid_moves()
        
        assert len(moves) > 0
        
        # All moves should be for player 0
        for move in moves:
            assert move.player_id == 0
    
    def test_all_moves_are_valid(self):
        """All returned moves should be valid."""
        game = Game()
        moves = game.get_valid_moves()
        
        for move in moves[:10]:  # Check first 10
            assert game.is_valid_move(move)


class TestScoring:
    """Test score calculation."""
    
    def test_initial_score(self):
        """Initial score is -89 (all squares remaining)."""
        game = Game()
        scores = game.get_scores()
        
        for score in scores:
            assert score == -89
    
    def test_score_after_piece_played(self):
        """Score increases as pieces are played."""
        game = Game()
        
        # Play a 5-square piece
        for piece in game.get_valid_moves():
            if piece.piece_type == PieceType.F:
                game.play_move(piece)
                break
        
        scores = game.get_scores()
        assert scores[0] == -84  # 89 - 5 = 84 remaining
    
    def test_bonus_for_all_pieces_placed(self):
        """Bonus of +15 when all pieces placed."""
        game = Game()
        player = game.players[0]
        
        # Simulate all pieces placed
        player.remaining_pieces.clear()
        
        scores = game.get_scores()
        assert scores[0] == 15  # +15 bonus, 0 remaining squares


class TestGameCopy:
    """Test game state copying."""
    
    def test_copy_is_independent(self):
        """Copied game is independent."""
        game = Game()
        move = Move(
            player_id=0,
            piece_type=PieceType.I1,
            orientation=0,
            row=0,
            col=0
        )
        game.play_move(move)
        
        copy = game.copy()
        
        # Modify copy
        copy.board.grid[0, 0] = 0
        
        # Original unchanged
        assert game.board.grid[0, 0] == 1


class TestGameOver:
    """Test game over conditions and results."""

    def test_force_pass_game_over(self):
        """Game should end when everyone passes."""
        game = Game(num_players=2)
        assert game.status == GameStatus.IN_PROGRESS
        
        # Everyone passes
        game.force_pass()
        game.force_pass()
        
        assert game.status == GameStatus.FINISHED
        assert game.get_winner() is not None

    def test_scoring_bonus_edge_case(self):
        """Bonus of +20 if monomino is the last piece placed."""
        game = Game(num_players=2)
        player = game.players[0]
        
        # Simulate all pieces placed, monomino last
        player.remaining_pieces.clear()
        # In current implementation, it checks last_piece_was_monomino.
        player.last_piece_was_monomino = True
        
        scores = game.get_scores()
        assert scores[0] == 20 # 15 (all) + 5 (extra bonus for I1) = 20

