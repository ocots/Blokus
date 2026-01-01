"""Tests for the pieces module."""

import pytest
from blokus.pieces import (
    Piece, PieceType, PIECES, PIECE_SHAPES,
    get_piece, get_all_pieces, num_orientations,
    _normalize_coords, _rotate_90, _flip_horizontal
)


class TestPieceShapes:
    """Test piece definitions."""
    
    def test_all_21_pieces_defined(self):
        """Verify all 21 pieces are defined."""
        assert len(PieceType) == 21
        assert len(PIECE_SHAPES) == 21
        assert len(PIECES) == 21
    
    def test_piece_sizes(self):
        """Verify each piece has correct number of squares."""
        expected_sizes = {
            PieceType.I1: 1,
            PieceType.I2: 2,
            PieceType.I3: 3, PieceType.L3: 3,
            PieceType.I4: 4, PieceType.L4: 4, PieceType.T4: 4, PieceType.O4: 4, PieceType.S4: 4,
            PieceType.F: 5, PieceType.I5: 5, PieceType.L5: 5, PieceType.N: 5,
            PieceType.P: 5, PieceType.T5: 5, PieceType.U: 5, PieceType.V: 5,
            PieceType.W: 5, PieceType.X: 5, PieceType.Y: 5, PieceType.Z: 5,
        }
        
        for piece_type, expected_size in expected_sizes.items():
            piece = get_piece(piece_type)
            assert piece.size == expected_size, f"{piece_type.value} should have {expected_size} squares"
    
    def test_total_squares(self):
        """Verify total squares per player is 89."""
        total = sum(get_piece(pt).size for pt in PieceType)
        assert total == 89


class TestPieceOrientations:
    """Test piece rotations and orientations."""
    
    def test_monomino_has_one_orientation(self):
        """Monomino (single square) has only 1 orientation."""
        assert num_orientations(PieceType.I1) == 1
    
    def test_domino_has_two_orientations(self):
        """Domino has 2 orientations (horizontal/vertical)."""
        assert num_orientations(PieceType.I2) == 2
    
    def test_square_has_one_orientation(self):
        """O4 (square) has only 1 orientation."""
        assert num_orientations(PieceType.O4) == 1
    
    def test_x_has_one_orientation(self):
        """X pentomino (plus sign) has only 1 orientation."""
        assert num_orientations(PieceType.X) == 1
    
    def test_asymmetric_pieces_have_eight_orientations(self):
        """Asymmetric pieces like F, N, Y have 8 orientations. Z has 4 (rotational symmetry)."""
        for pt in [PieceType.F, PieceType.N, PieceType.Y]:
            assert num_orientations(pt) == 8, f"{pt.value} should have 8 orientations"
        # Z has rotational symmetry, so only 4 unique orientations
        assert num_orientations(PieceType.Z) == 4, "Z should have 4 orientations"
    
    def test_all_orientations_unique(self):
        """All orientations of a piece should be unique."""
        for piece_type in PieceType:
            orientations = PIECES[piece_type]
            coords_set = {piece.coords for piece in orientations}
            assert len(coords_set) == len(orientations), f"{piece_type.value} has duplicate orientations"


class TestPieceTransformations:
    """Test rotation and flip operations."""
    
    def test_normalize_coords(self):
        """Normalization should shift to origin."""
        coords = [(2, 3), (2, 4), (3, 3)]
        normalized = _normalize_coords(coords)
        assert normalized == frozenset([(0, 0), (0, 1), (1, 0)])
    
    def test_rotate_90_single(self):
        """Test 90 degree rotation."""
        # Horizontal line -> vertical line
        coords = frozenset([(0, 0), (0, 1), (0, 2)])
        rotated = _rotate_90(coords)
        expected = frozenset([(0, 0), (1, 0), (2, 0)])
        assert rotated == expected
    
    def test_four_rotations_returns_to_original(self):
        """Four 90° rotations should return to original."""
        original = frozenset([(0, 0), (0, 1), (1, 0)])
        current = original
        for _ in range(4):
            current = _rotate_90(current)
        assert current == original
    
    def test_flip_horizontal(self):
        """Test horizontal flip."""
        # L shape
        coords = frozenset([(0, 0), (0, 1), (1, 0)])
        flipped = _flip_horizontal(coords)
        expected = frozenset([(0, 0), (0, 1), (1, 1)])
        assert flipped == expected


class TestPieceCorners:
    """Test corner detection for placement rules."""
    
    def test_monomino_corners(self):
        """Monomino has 4 corner positions."""
        piece = get_piece(PieceType.I1)
        corners = piece.get_corners()
        assert len(corners) == 4
        expected = {(-1, -1), (-1, 1), (1, -1), (1, 1)}
        assert corners == expected
    
    def test_domino_corners(self):
        """Domino has 4 corner positions (at ends)."""
        piece = get_piece(PieceType.I2)
        corners = piece.get_corners()
        # Should have corners only at the ends, not in the middle
        assert len(corners) == 4
    
    def test_corners_not_edge_adjacent(self):
        """Corners should not be edge-adjacent to any piece square."""
        for piece_type in PieceType:
            piece = get_piece(piece_type)
            corners = piece.get_corners()
            for corner in corners:
                for r, c in piece.coords:
                    # Manhattan distance should be > 1 (not edge adjacent)
                    dist = abs(corner[0] - r) + abs(corner[1] - c)
                    assert dist > 1, f"Corner {corner} is edge-adjacent to ({r},{c}) in {piece_type.value}"


class TestPieceEdges:
    """Test edge detection."""
    
    def test_monomino_edges(self):
        """Monomino has 4 edge positions."""
        piece = get_piece(PieceType.I1)
        edges = piece.get_edges()
        assert len(edges) == 4
        expected = {(-1, 0), (1, 0), (0, -1), (0, 1)}
        assert edges == expected


class TestPieceMatrix:
    """Test matrix conversion."""
    
    def test_monomino_matrix(self):
        """Monomino should be 1x1 matrix."""
        piece = get_piece(PieceType.I1)
        matrix = piece.to_matrix()
        assert matrix.shape == (1, 1)
        assert matrix[0, 0] == 1
    
    def test_domino_matrix(self):
        """Domino should be 1x2 or 2x1 matrix depending on orientation."""
        piece = get_piece(PieceType.I2, orientation=0)
        matrix = piece.to_matrix()
        assert matrix.sum() == 2
        assert 1 in matrix.shape and 2 in matrix.shape
