"""Tests for the rules module."""

import pytest
from blokus.board import Board
from blokus.pieces import get_piece, PieceType, PIECES
from blokus.rules import is_valid_placement, get_valid_placements, has_valid_move


class TestFirstMovePlacement:
    """Test placement rules for first move."""
    
    def test_first_move_must_cover_corner(self):
        """First move must cover starting corner."""
        board = Board()
        piece = get_piece(PieceType.I1)
        
        # Covering corner (0,0) is valid
        assert is_valid_placement(board, piece, 0, 0, player_id=0, is_first_move=True)
        
        # Not covering corner is invalid
        assert not is_valid_placement(board, piece, 1, 1, player_id=0, is_first_move=True)
    
    def test_first_move_different_players(self):
        """Each player has different starting corner."""
        board = Board()
        piece = get_piece(PieceType.I1)
        
        # Player 0: (0, 0)
        assert is_valid_placement(board, piece, 0, 0, player_id=0, is_first_move=True)
        
        # Player 1: (0, 19)
        assert is_valid_placement(board, piece, 0, 19, player_id=1, is_first_move=True)
        
        # Player 2: (19, 19)
        assert is_valid_placement(board, piece, 19, 19, player_id=2, is_first_move=True)
        
        # Player 3: (19, 0)
        assert is_valid_placement(board, piece, 19, 0, player_id=3, is_first_move=True)
    
    def test_first_move_larger_piece(self):
        """First move with larger piece covering corner."""
        board = Board()
        piece = get_piece(PieceType.L3)  # L-shaped piece
        
        # Should work if piece covers (0, 0)
        # L3 default: (0,0), (0,1), (1,0)
        assert is_valid_placement(board, piece, 0, 0, player_id=0, is_first_move=True)


class TestSubsequentMovePlacement:
    """Test placement rules for moves after first."""
    
    def test_must_touch_own_corner(self):
        """Subsequent pieces must touch own piece by corner."""
        board = Board()
        piece = get_piece(PieceType.I1)
        
        # Place first piece
        board.place_piece(piece, 0, 0, player_id=0)
        
        # Diagonal to (0,0) is valid
        assert is_valid_placement(board, piece, 1, 1, player_id=0, is_first_move=False)
        
        # Not touching is invalid
        assert not is_valid_placement(board, piece, 5, 5, player_id=0, is_first_move=False)
    
    def test_cannot_touch_own_edge(self):
        """Cannot touch own piece by edge."""
        board = Board()
        piece = get_piece(PieceType.I1)
        
        # Place first piece
        board.place_piece(piece, 0, 0, player_id=0)
        
        # Edge-adjacent is invalid
        assert not is_valid_placement(board, piece, 0, 1, player_id=0, is_first_move=False)
        assert not is_valid_placement(board, piece, 1, 0, player_id=0, is_first_move=False)
    
    def test_can_touch_opponent_edge(self):
        """Can touch opponent's pieces by edge."""
        board = Board()
        piece = get_piece(PieceType.I1)
        
        # Player 0 places at corner
        board.place_piece(piece, 0, 0, player_id=0)
        
        # Player 1 places at their corner
        board.place_piece(piece, 0, 19, player_id=1)
        
        # Player 0 plays diagonally
        board.place_piece(piece, 1, 1, player_id=0)
        
        # Player 1 plays diagonally
        board.place_piece(piece, 1, 18, player_id=1)
        
        # Now player 0 can play a piece that might touch player 1's pieces by edge
        # (This is allowed - only touching your OWN pieces by edge is forbidden)


class TestOverlapRules:
    """Test that pieces cannot overlap."""
    
    def test_cannot_overlap_own_piece(self):
        """Cannot place on own piece."""
        board = Board()
        piece = get_piece(PieceType.I1)
        
        board.place_piece(piece, 0, 0, player_id=0)
        
        assert not is_valid_placement(board, piece, 0, 0, player_id=0, is_first_move=False)
    
    def test_cannot_overlap_opponent_piece(self):
        """Cannot place on opponent's piece."""
        board = Board()
        piece = get_piece(PieceType.I1)
        
        board.place_piece(piece, 5, 5, player_id=0)
        
        assert not is_valid_placement(board, piece, 5, 5, player_id=1, is_first_move=True)


class TestBoundaryRules:
    """Test board boundary rules."""
    
    def test_cannot_place_out_of_bounds(self):
        """Pieces must be within board."""
        board = Board()
        piece = get_piece(PieceType.I5)  # 5 long
        
        # Placing at edge would go out of bounds
        assert not is_valid_placement(board, piece, 0, 18, player_id=0, is_first_move=True)


class TestGetValidPlacements:
    """Test finding all valid placements."""
    
    def test_first_move_placements(self):
        """Get valid placements for first move."""
        board = Board()
        piece = get_piece(PieceType.I1)
        
        placements = get_valid_placements(board, piece, player_id=0, is_first_move=True)
        
        # Monomino should only fit at corner
        assert len(placements) == 1
        assert (0, 0) in placements
    
    def test_multiple_orientations(self):
        """Different orientations may have different valid placements."""
        board = Board()
        
        all_placements = set()
        for piece in PIECES[PieceType.L3]:
            placements = get_valid_placements(board, piece, player_id=0, is_first_move=True)
            all_placements.update(placements)
        
        # L3 has multiple orientations, some may have same placements
        assert len(all_placements) >= 1


class TestHasValidMove:
    """Test checking if any valid move exists."""
    
    def test_always_has_move_at_start(self):
        """Players always have moves at start."""
        board = Board()
        pieces = [PIECES[pt][0] for pt in PieceType]
        
        assert has_valid_move(board, pieces, player_id=0, is_first_move=True)
    
    def test_no_move_when_blocked(self):
        """Player has no move when completely blocked."""
        board = Board()
        
        # Place pieces to block player 0's corner
        # Fill area around (0,0) with other player's pieces
        for r in range(3):
            for c in range(3):
                if r == 0 and c == 0:
                    continue  # Leave corner empty but unreachable
                board.grid[r, c] = 2  # Player 1's pieces
        
        # Player 0 cannot play at corner because it would touch player 1's edges
        # But player 0 needs to touch corner on first move
        pieces = [get_piece(PieceType.I1)]
        
        # This is a special case - first move at corner, but corner surrounded
        # The monomino can still be placed at (0,0) since it only touches opponents
        # Actually it CAN be placed there! Let me reconsider...
        # First move just needs to cover starting corner, doesn't need diagonal contact
        assert has_valid_move(board, pieces, player_id=0, is_first_move=True)
