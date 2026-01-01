"""Tests for the board module."""

import pytest
import numpy as np
from blokus.board import Board, BOARD_SIZE, STARTING_CORNERS
from blokus.pieces import get_piece, PieceType


class TestBoardBasics:
    """Test basic board operations."""
    
    def test_board_default_size(self):
        """Board should be 20x20 by default."""
        board = Board()
        assert board.size == 20
        assert board.grid.shape == (20, 20)
    
    def test_board_empty_initially(self):
        """Board should be empty initially."""
        board = Board()
        assert board.count_occupied() == 0
        assert np.all(board.grid == 0)
    
    def test_is_valid_position(self):
        """Test position validation."""
        board = Board()
        assert board.is_valid_position(0, 0)
        assert board.is_valid_position(19, 19)
        assert not board.is_valid_position(-1, 0)
        assert not board.is_valid_position(0, 20)
        assert not board.is_valid_position(20, 0)
    
    def test_is_empty(self):
        """Test empty cell detection."""
        board = Board()
        assert board.is_empty(0, 0)
        board.grid[5, 5] = 1
        assert not board.is_empty(5, 5)
        assert not board.is_empty(-1, 0)  # Out of bounds


class TestStartingCorners:
    """Test starting corner positions."""
    
    def test_four_starting_corners(self):
        """Should have 4 starting corners."""
        assert len(STARTING_CORNERS) == 4
    
    def test_starting_corner_positions(self):
        """Verify starting corner positions."""
        assert STARTING_CORNERS[0] == (0, 0)               # Top-left
        assert STARTING_CORNERS[1] == (0, BOARD_SIZE - 1)  # Top-right
        assert STARTING_CORNERS[2] == (BOARD_SIZE - 1, BOARD_SIZE - 1)  # Bottom-right
        assert STARTING_CORNERS[3] == (BOARD_SIZE - 1, 0)  # Bottom-left


class TestPlacePiece:
    """Test piece placement on board."""
    
    def test_place_monomino(self):
        """Test placing a monomino."""
        board = Board()
        piece = get_piece(PieceType.I1)
        
        result = board.place_piece(piece, 0, 0, player_id=0)
        
        assert result is True
        assert board.grid[0, 0] == 1
        assert board.count_occupied() == 1
    
    def test_place_domino(self):
        """Test placing a domino."""
        board = Board()
        piece = get_piece(PieceType.I2)  # Horizontal by default
        
        result = board.place_piece(piece, 5, 5, player_id=1)
        
        assert result is True
        assert board.count_player_cells(1) == 2
    
    def test_place_out_of_bounds_fails(self):
        """Placing piece out of bounds should fail."""
        board = Board()
        piece = get_piece(PieceType.I5)  # 5-long vertical piece (5 rows, 1 col)
        
        # I5 vertical goes from row to row+4, so at row=16 it would go to row=20 (out of bounds)
        result = board.place_piece(piece, 16, 0, player_id=0)
        
        assert result is False
        assert board.count_occupied() == 0
    
    def test_place_overlapping_fails(self):
        """Placing piece on occupied cell should fail."""
        board = Board()
        piece1 = get_piece(PieceType.I1)
        piece2 = get_piece(PieceType.I1)
        
        board.place_piece(piece1, 5, 5, player_id=0)
        result = board.place_piece(piece2, 5, 5, player_id=1)
        
        assert result is False
        assert board.grid[5, 5] == 1  # Still player 0's piece


class TestPlayerCells:
    """Test player cell tracking."""
    
    def test_get_player_cells_empty(self):
        """Empty board has no player cells."""
        board = Board()
        cells = board.get_player_cells(0)
        assert len(cells) == 0
    
    def test_get_player_cells_after_placement(self):
        """Get cells after placing piece."""
        board = Board()
        piece = get_piece(PieceType.L3)  # 3 squares
        board.place_piece(piece, 0, 0, player_id=0)
        
        cells = board.get_player_cells(0)
        assert len(cells) == 3
    
    def test_multiple_players_cells(self):
        """Track cells for multiple players."""
        board = Board()
        piece = get_piece(PieceType.I1)
        
        board.place_piece(piece, 0, 0, player_id=0)
        board.place_piece(piece, 19, 19, player_id=1)
        
        assert len(board.get_player_cells(0)) == 1
        assert len(board.get_player_cells(1)) == 1
        assert (0, 0) in board.get_player_cells(0)
        assert (19, 19) in board.get_player_cells(1)


class TestPlayerCorners:
    """Test corner detection for placement."""
    
    def test_first_move_corner(self):
        """First move should return starting corner."""
        board = Board()
        corners = board.get_player_corners(0)
        assert corners == {(0, 0)}
    
    def test_corners_after_placement(self):
        """Corners should be diagonals after first placement."""
        board = Board()
        piece = get_piece(PieceType.I1)
        board.place_piece(piece, 0, 0, player_id=0)
        
        corners = board.get_player_corners(0)
        
        # Only (1, 1) is valid (others are out of bounds or edge-adjacent)
        assert (1, 1) in corners
        assert (0, 0) not in corners  # Now occupied
    
    def test_corners_not_edge_adjacent(self):
        """Corners should not be edge-adjacent to player's pieces."""
        board = Board()
        # Place an L-shaped piece
        piece = get_piece(PieceType.L3)
        board.place_piece(piece, 0, 0, player_id=0)
        
        corners = board.get_player_corners(0)
        player_cells = board.get_player_cells(0)
        
        for corner in corners:
            for cell in player_cells:
                # Manhattan distance should be > 1
                dist = abs(corner[0] - cell[0]) + abs(corner[1] - cell[1])
                assert dist > 1


class TestPlayerEdges:
    """Test edge detection."""
    
    def test_edges_after_placement(self):
        """Edges should surround placed pieces."""
        board = Board()
        piece = get_piece(PieceType.I1)
        board.place_piece(piece, 5, 5, player_id=0)
        
        edges = board.get_player_edges(0)
        
        expected = {(4, 5), (6, 5), (5, 4), (5, 6)}
        assert edges == expected


class TestBoardCopy:
    """Test board copying."""
    
    def test_copy_is_independent(self):
        """Copied board should be independent."""
        board = Board()
        piece = get_piece(PieceType.I1)
        board.place_piece(piece, 0, 0, player_id=0)
        
        copy = board.copy()
        copy.grid[0, 0] = 0  # Modify copy
        
        assert board.grid[0, 0] == 1  # Original unchanged
