
import pytest
from blokus.game import Game, Move
from blokus.pieces import PieceType, PIECE_SHAPES, _generate_all_orientations
from blokus.board import BOARD_SIZE

def test_orientation_determinism():
    """
    Regression Test: Ensure orientations represent same shapes in same order across calls.
    Tests the internal generator directly.
    """
    piece_type = PieceType.L5
    base_shape = PIECE_SHAPES[piece_type]
    
    # Generate first time
    orientations1 = _generate_all_orientations(base_shape)
    
    # Generate second time
    orientations2 = _generate_all_orientations(base_shape)
    
    assert len(orientations1) == len(orientations2)
    
    for i, (o1, o2) in enumerate(zip(orientations1, orientations2)):
        # Convert frozensets to sorted lists of tuples for stable comparison
        coords1 = sorted(list(o1))
        coords2 = sorted(list(o2))
        assert coords1 == coords2, f"Orientation {i} mismatches between calls"

def test_game_sequence_turn_1_and_2():
    """
    Regression Test: Verify move validation for first move (corner) and second move (diagonal connection).
    """
    game = Game(4, 0)
    
    # --- Turn 1: Player 0 uses I1 ---
    move1_p0 = Move(0, PieceType.I1, 0, 0, 0)
    assert game.play_move(move1_p0) is True
    
    # --- Skip others ---
    game.pass_turn() # P1
    game.pass_turn() # P2
    game.pass_turn() # P3
    
    # --- Turn 2: Player 0 uses I2 ---
    # Connect to I1 at (0,0). Valid diagonal is (1,1).
    # Place I2 horizontal at (1,1) -> covers (1,1), (1,2)
    move2_p0 = Move(0, PieceType.I2, 0, 1, 1)
    
    reason = game.get_move_rejection_reason(move2_p0)
    assert reason is None, f"Player 0 second move rejected: {reason}"
    success = game.play_move(move2_p0)
    assert success is True
    
def test_invalid_edge_connection_rejection():
    """
    Regression Test: Ensure Edge Rule is enforced.
    """
    game = Game(4, 0)
    
    # P0 plays I1
    game.play_move(Move(0, PieceType.I1, 0, 0, 0))
    
    # Skip others
    game.pass_turn(); game.pass_turn(); game.pass_turn()
    
    # P0 tries to place I2 edge-adjacent at (0, 1) (horizontal)
    # I1 covers (0,0). I2 at (0,1) covers (0,1), (0,2).
    # (0,1) is edge-adjacent to (0,0).
    bad_move = Move(0, PieceType.I2, 0, 0, 1)
    
    reason = game.get_move_rejection_reason(bad_move)
    assert reason is not None
    assert "touches own pieces by edge" in reason

def test_invalid_no_corner_connection_rejection():
    """
    Regression Test: Ensure Corner Rule is enforced.
    """
    game = Game(4, 0)
    
    # P0 plays I1
    game.play_move(Move(0, PieceType.I1, 0, 0, 0))
    
    # Skip others
    game.pass_turn(); game.pass_turn(); game.pass_turn()
    
    # P0 tries to place I2 at (2, 2) (isolated)
    bad_move = Move(0, PieceType.I2, 0, 2, 2)
    
    reason = game.get_move_rejection_reason(bad_move)
    assert reason is not None
    # We accept either specific "doesn't touch" OR generic "geometric" depending on implementation details
    assert "doesn't touch any diagonal corner" in reason or "geometric placement invalid" in reason.lower()
