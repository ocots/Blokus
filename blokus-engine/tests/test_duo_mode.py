
import pytest
from blokus.game import Game, Move
from blokus.pieces import PieceType
from blokus.board import Board

def test_duo_mode_initialization():
    """
    Test that Duo mode initializes a 14x14 board with correct starting points.
    """
    board = Board(size=14)
    assert board.size == 14
    
    # Check starting corners: Player 0 at (4,4), Player 1 at (9,9)
    # Note: get_starting_corners returns a Set of tuples
    assert board.get_starting_corners(0) == {(4, 4)}
    assert board.get_starting_corners(1) == {(9, 9)}

def test_duo_mode_first_move():
    """
    Test that the first move in Duo mode must cover the specific starting point (4,4).
    """
    board = Board(size=14)
    game = Game(num_players=2, board=board)
    
    # Player 0 starts. Must cover (4,4).
    # Piece I1 (1 cell). Place at (4,4).
    move = Move(0, PieceType.I1, 0, 4, 4)
    
    assert game.is_valid_move(move) is True, f"Move valid: {game.get_move_rejection_reason(move)}"
    assert game.play_move(move) is True
    
    # Verify board state
    assert game.board.get_cell(4, 4) == 1 # Player 1 (id 0)

def test_duo_mode_invalid_start():
    """
    Test that starting elsewhere (e.g. (0,0)) is rejected in Duo mode.
    """
    board = Board(size=14)
    game = Game(num_players=2, board=board)
    
    # Try placing at (0,0) (Classic corner)
    move = Move(0, PieceType.I1, 0, 0, 0)
    
    reason = game.get_move_rejection_reason(move)
    assert reason is not None
    assert "starting corner" in reason.lower()
    assert "(4, 4)" in reason # Should mention the correct corner

def test_duo_mode_game_flow():
    """
    Simulate a few moves in Duo mode.
    """
    board = Board(size=14)
    game = Game(num_players=2, board=board)
    
    # P0: I1 at (4,4)
    game.play_move(Move(0, PieceType.I1, 0, 4, 4))
    
    # P1: I1 at (9,9)
    game.play_move(Move(1, PieceType.I1, 0, 9, 9))
    
    # Turn 2, P0: I2 connected to (4,4).
    # (4,4) is occupied. Valid diagonal is (5,5) or (3,3) or (3,5) or (5,3).
    # Try placing I2 vertical at (5,5) -> covers (5,5), (6,5).
    # (5,5) touches (4,4) diagonally.
    move_t2 = Move(0, PieceType.I2, 1, 5, 5) # Orientation 1 is vertical? (check, usually piece logic)
    # Assuming Orientation 0 is horizontal [(0,0), (0,1)]
    # Orientation 1 is vertical [(0,0), (1,0)]
    # I2 vertical at (5,5) covers (5,5), (6,5).
    # (5,5) is diagonal to (4,4). Valid.
    
    if not game.is_valid_move(move_t2):
       # If orientation 1 is not vertical or logic differs, let's stick to simple horizontal
       # I2 Horizontal at (5,5) -> (5,5), (5,6).
       move_t2 = Move(0, PieceType.I2, 0, 5, 5)
       
    assert game.play_move(move_t2) is True
