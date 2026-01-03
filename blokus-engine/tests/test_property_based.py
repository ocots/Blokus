"""
Property-based tests using Hypothesis.

These tests generate random game scenarios and verify that
the game never crashes and maintains invariants.
"""

import pytest
from hypothesis import given, strategies as st, settings, assume
from blokus.game import Game, Move, GameStatus
from blokus.pieces import PieceType
from blokus.player_types import PlayerStatus


# Custom strategies for Blokus
@st.composite
def valid_game_config(draw):
    """Generate valid game configuration."""
    num_players = draw(st.sampled_from([2, 4]))
    starting_player = draw(st.integers(min_value=0, max_value=num_players - 1))
    return {"num_players": num_players, "starting_player_idx": starting_player}


@st.composite
def random_piece_type(draw):
    """Generate random piece type."""
    return draw(st.sampled_from(list(PieceType)))


class TestGameInvariants:
    """Test that game invariants hold under random operations."""
    
    @given(valid_game_config())
    @settings(max_examples=50)
    def test_game_initialization_never_crashes(self, config):
        """Game initialization should never crash with valid config."""
        game = Game(
            num_players=config["num_players"],
            starting_player_idx=config["starting_player_idx"]
        )
        
        # Invariants after initialization
        assert game.num_players == config["num_players"]
        assert game.current_player_idx == config["starting_player_idx"]
        assert game.status == GameStatus.IN_PROGRESS
        assert len(game.players) == config["num_players"]
        assert all(len(p.remaining_pieces) == 21 for p in game.players)
    
    @given(st.sampled_from([2, 4]))
    @settings(max_examples=20, deadline=None)
    def test_random_valid_moves_never_crash(self, num_players):
        """Playing random valid moves should never crash."""
        game = Game(num_players=num_players)
        moves_played = 0
        max_moves = 50
        
        while game.status == GameStatus.IN_PROGRESS and moves_played < max_moves:
            valid_moves = game.get_valid_moves()
            
            if not valid_moves:
                break
            
            # Pick a random valid move
            import random
            move = random.choice(valid_moves)
            
            # Play the move
            result = game.play_move(move)
            
            # Invariants
            assert result is True, "Valid move should succeed"
            assert move.piece_type not in game.players[move.player_id].remaining_pieces
            
            moves_played += 1
        
        # Game should still be in valid state
        assert game.status in [GameStatus.IN_PROGRESS, GameStatus.FINISHED]
        assert all(p.score <= 20 for p in game.players)  # Max score is 20
    
    @given(st.sampled_from([2, 4]), st.integers(min_value=1, max_value=10))
    @settings(max_examples=30, deadline=None)
    def test_force_pass_maintains_invariants(self, num_players, num_passes):
        """Forcing passes should maintain game invariants."""
        game = Game(num_players=num_players)
        
        for _ in range(min(num_passes, num_players)):
            if game.status == GameStatus.IN_PROGRESS:
                current_player = game.current_player
                game.force_pass()
                
                # Invariant: player should be marked as passed
                assert current_player.has_passed
                assert current_player.status in [PlayerStatus.PASSED, PlayerStatus.WAITING, PlayerStatus.PLAYING]
        
        # After all players pass, game should be finished
        if num_passes >= num_players:
            assert game.status == GameStatus.FINISHED
    
    @given(st.sampled_from([2, 4]))
    @settings(max_examples=20, deadline=None)
    def test_score_calculation_never_negative_beyond_limit(self, num_players):
        """Scores should never be below -89 (all pieces remaining)."""
        game = Game(num_players=num_players)
        
        # Play some random moves
        for _ in range(10):
            valid_moves = game.get_valid_moves()
            if valid_moves:
                import random
                game.play_move(random.choice(valid_moves))
        
        scores = game.get_scores()
        
        for score in scores:
            assert -89 <= score <= 20, f"Score {score} out of valid range [-89, 20]"
    
    @given(st.sampled_from([2, 4]))
    @settings(max_examples=20, deadline=None)
    def test_game_copy_is_independent(self, num_players):
        """Copied game should be independent of original."""
        game = Game(num_players=num_players)
        
        # Play a few moves
        for _ in range(5):
            valid_moves = game.get_valid_moves()
            if valid_moves:
                import random
                game.play_move(random.choice(valid_moves))
        
        # Copy the game
        game_copy = game.copy()
        
        # Modify the copy
        valid_moves = game_copy.get_valid_moves()
        if valid_moves:
            import random
            game_copy.play_move(random.choice(valid_moves))
        
        # Original should be unchanged
        assert game.turn_number != game_copy.turn_number or not valid_moves


class TestPlayerInvariants:
    """Test player-related invariants."""
    
    @given(st.sampled_from([2, 4]))
    @settings(max_examples=20, deadline=None)
    def test_pieces_count_decreases_monotonically(self, num_players):
        """Pieces count should only decrease, never increase."""
        game = Game(num_players=num_players)
        
        pieces_counts = {p.id: p.pieces_count for p in game.players}
        
        for _ in range(20):
            valid_moves = game.get_valid_moves()
            if not valid_moves:
                break
            
            import random
            move = random.choice(valid_moves)
            player_id = move.player_id
            
            old_count = pieces_counts[player_id]
            game.play_move(move)
            new_count = game.players[player_id].pieces_count
            
            # Invariant: pieces count should decrease
            assert new_count == old_count - 1, "Pieces count should decrease by 1"
            pieces_counts[player_id] = new_count
    
    @given(st.sampled_from([2, 4]))
    @settings(max_examples=20, deadline=None)
    def test_squares_remaining_decreases(self, num_players):
        """Squares remaining should only decrease."""
        game = Game(num_players=num_players)
        
        squares_remaining = {p.id: p.squares_remaining for p in game.players}
        
        for _ in range(20):
            valid_moves = game.get_valid_moves()
            if not valid_moves:
                break
            
            import random
            move = random.choice(valid_moves)
            player_id = move.player_id
            
            old_squares = squares_remaining[player_id]
            game.play_move(move)
            new_squares = game.players[player_id].squares_remaining
            
            # Invariant: squares should decrease
            assert new_squares < old_squares, "Squares should decrease"
            squares_remaining[player_id] = new_squares


class TestBoardInvariants:
    """Test board-related invariants."""
    
    @given(st.sampled_from([2, 4]))
    @settings(max_examples=20, deadline=None)
    def test_board_cells_never_overlap(self, num_players):
        """Board cells should never be overwritten."""
        game = Game(num_players=num_players)
        
        occupied_cells = set()
        
        for _ in range(30):
            valid_moves = game.get_valid_moves()
            if not valid_moves:
                break
            
            import random
            move = random.choice(valid_moves)
            
            # Get piece positions
            from blokus.pieces import get_piece
            piece = get_piece(move.piece_type, move.orientation)
            positions = piece.translate(move.row, move.col)
            
            # Check no overlap
            for pos in positions:
                assert pos not in occupied_cells, f"Cell {pos} already occupied!"
                occupied_cells.add(pos)
            
            game.play_move(move)
    
    @given(st.sampled_from([2, 4]))
    @settings(max_examples=20, deadline=None)
    def test_board_occupied_count_increases(self, num_players):
        """Board occupied count should only increase."""
        game = Game(num_players=num_players)
        
        occupied_count = game.board.count_occupied()
        
        for _ in range(20):
            valid_moves = game.get_valid_moves()
            if not valid_moves:
                break
            
            import random
            move = random.choice(valid_moves)
            game.play_move(move)
            
            new_count = game.board.count_occupied()
            
            # Invariant: occupied count should increase
            assert new_count > occupied_count, "Occupied count should increase"
            occupied_count = new_count


class TestEdgeCases:
    """Test edge cases with property-based testing."""
    
    @given(st.integers(min_value=0, max_value=3))
    @settings(max_examples=10)
    def test_starting_player_invariant(self, starting_player):
        """Game should start with specified player."""
        game = Game(num_players=4, starting_player_idx=starting_player)
        
        assert game.current_player_idx == starting_player
        assert game.current_player.status == PlayerStatus.PLAYING
    
    @given(st.sampled_from([2, 4]))
    @settings(max_examples=10)
    def test_get_valid_moves_returns_valid_moves(self, num_players):
        """All moves returned by get_valid_moves should be valid."""
        game = Game(num_players=num_players)
        
        valid_moves = game.get_valid_moves()
        
        # Check a sample of moves
        import random
        sample_size = min(10, len(valid_moves))
        sample = random.sample(valid_moves, sample_size)
        
        for move in sample:
            assert game.is_valid_move(move), f"Move {move} should be valid"
