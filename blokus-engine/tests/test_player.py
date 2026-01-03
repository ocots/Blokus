"""Tests for the unified Player class."""

import pytest
from blokus.player import Player
from blokus.player_types import PlayerType, PlayerStatus
from blokus.pieces import PieceType


class TestPlayerInitialization:
    """Test player initialization."""
    
    def test_default_player(self):
        """Default player initialization."""
        player = Player(id=0, name="Alice", color="#3b82f6")
        
        assert player.id == 0
        assert player.name == "Alice"
        assert player.color == "#3b82f6"
        assert player.type == PlayerType.HUMAN
        assert player.persona is None
        assert player.status == PlayerStatus.WAITING
        assert player.score == 0
        assert len(player.remaining_pieces) == 21
        assert not player.has_passed
        assert not player.last_piece_was_monomino
    
    def test_ai_player_initialization(self):
        """AI player initialization."""
        player = Player(
            id=1, 
            name="Bot", 
            color="#22c55e", 
            type=PlayerType.AI, 
            persona="random"
        )
        
        assert player.is_ai
        assert not player.is_human
        assert player.persona == "random"
        assert player.display_name == "Bot (random)"
    
    
    def test_player_with_custom_status(self):
        """Player with custom status."""
        player = Player(
            id=0, 
            name="Alice", 
            color="#3b82f6",
            status=PlayerStatus.PLAYING
        )
        
        assert player.status == PlayerStatus.PLAYING
    
    def test_player_with_score(self):
        """Player with initial score."""
        player = Player(
            id=0, 
            name="Alice", 
            color="#3b82f6",
            score=50
        )
        
        assert player.score == 50


class TestPlayerProperties:
    """Test player properties."""
    
    def test_pieces_count(self):
        """Test pieces count property."""
        player = Player(id=0, name="Alice", color="#3b82f6")
        assert player.pieces_count == 21
        
        # Play a piece
        player.play_piece(PieceType.I1)
        assert player.pieces_count == 20
    
    def test_squares_remaining(self):
        """Test squares remaining property."""
        player = Player(id=0, name="Alice", color="#3b82f6")
        assert player.squares_remaining == 89  # All pieces sum to 89
        
        # Play a 5-square piece
        player.play_piece(PieceType.F)
        assert player.squares_remaining == 84  # 89 - 5
    
    def test_is_ai_property(self):
        """Test is_ai property."""
        human = Player(id=0, name="Alice", color="#3b82f6")
        ai = Player(id=1, name="Bot", color="#22c55e", type=PlayerType.AI)
        
        assert not human.is_ai
        assert ai.is_ai
    
    def test_is_human_property(self):
        """Test is_human property."""
        human = Player(id=0, name="Alice", color="#3b82f6")
        ai = Player(id=1, name="Bot", color="#22c55e", type=PlayerType.AI)
        
        assert human.is_human
        assert not ai.is_human
    
    
    def test_display_name_property(self):
        """Test display_name property."""
        human = Player(id=0, name="Alice", color="#3b82f6")
        ai = Player(id=1, name="Bot", color="#22c55e", type=PlayerType.AI, persona="random")
        ai_no_persona = Player(id=2, name="Bot", color="#eab308", type=PlayerType.AI)
        
        assert human.display_name == "Alice"
        assert ai.display_name == "Bot (random)"
        assert ai_no_persona.display_name == "Bot"


class TestPlayerActions:
    """Test player actions."""
    
    def test_play_piece_success(self):
        """Test successful piece play."""
        player = Player(id=0, name="Alice", color="#3b82f6")
        
        result = player.play_piece(PieceType.I1)
        
        assert result is True
        assert PieceType.I1 not in player.remaining_pieces
        assert player.last_piece_was_monomino
        assert player.pieces_count == 20
    
    def test_play_piece_failure(self):
        """Test failed piece play."""
        player = Player(id=0, name="Alice", color="#3b82f6")
        
        # Play the same piece twice
        player.play_piece(PieceType.I1)
        result = player.play_piece(PieceType.I1)
        
        assert result is False
        assert PieceType.I1 not in player.remaining_pieces
        assert player.pieces_count == 20
    
    def test_play_piece_non_monomino(self):
        """Test playing non-monomino piece."""
        player = Player(id=0, name="Alice", color="#3b82f6")
        
        result = player.play_piece(PieceType.F)  # 5-square piece
        
        assert result is True
        assert PieceType.F not in player.remaining_pieces
        assert not player.last_piece_was_monomino
    
    def test_pass_turn(self):
        """Test passing turn."""
        player = Player(id=0, name="Alice", color="#3b82f6")
        
        player.pass_turn()
        
        assert player.has_passed
        assert player.status == PlayerStatus.PASSED


class TestPlayerScoring:
    """Test player scoring."""
    
    def test_initial_score(self):
        """Test initial score."""
        player = Player(id=0, name="Alice", color="#3b82f6")
        
        score = player.calculate_score()
        
        assert score == -89  # All squares remaining
        assert player.score == -89
    
    def test_score_after_playing_piece(self):
        """Test score after playing pieces."""
        player = Player(id=0, name="Alice", color="#3b82f6")
        
        # Play a 5-square piece
        player.play_piece(PieceType.F)
        score = player.calculate_score()
        
        assert score == -84  # 89 - 5 = 84 remaining
        assert player.score == -84
    
    def test_all_pieces_bonus(self):
        """Test bonus for all pieces placed."""
        player = Player(id=0, name="Alice", color="#3b82f6")
        
        # Simulate all pieces placed
        player.remaining_pieces.clear()
        score = player.calculate_score()
        
        assert score == 15  # +15 bonus, 0 remaining squares
        assert player.score == 15
    
    def test_monomino_last_bonus(self):
        """Test bonus for monomino as last piece."""
        player = Player(id=0, name="Alice", color="#3b82f6")
        
        # Simulate all pieces placed with monomino last
        player.remaining_pieces.clear()
        player.last_piece_was_monomino = True
        score = player.calculate_score()
        
        assert score == 20  # 15 (all) + 5 (monomino bonus)
        assert player.score == 20
    
    def test_no_monomino_last_bonus(self):
        """Test no bonus when monomino not last."""
        player = Player(id=0, name="Alice", color="#3b82f6")
        
        # Simulate all pieces placed without monomino last
        player.remaining_pieces.clear()
        player.last_piece_was_monomino = False
        score = player.calculate_score()
        
        assert score == 15  # Only +15 bonus
        assert player.score == 15


class TestPlayerSerialization:
    """Test player serialization."""
    
    def test_to_dict(self):
        """Test conversion to dictionary."""
        player = Player(
            id=0, 
            name="Alice", 
            color="#3b82f6",
            type=PlayerType.HUMAN,
            persona=None,
            score=50
        )
        
        data = player.to_dict()
        
        assert data["id"] == 0
        assert data["name"] == "Alice"
        assert data["color"] == "#3b82f6"
        assert data["type"] == "human"
        assert data["persona"] is None
        assert data["score"] == 50
        assert data["status"] == "waiting"
        assert len(data["remaining_pieces"]) == 21
        assert data["pieces_count"] == 21
        assert data["squares_remaining"] == 89
        assert data["display_name"] == "Alice"
        assert data["is_ai"] is False
        assert data["is_human"] is True
    
    def test_to_dict_ai_player(self):
        """Test AI player serialization."""
        player = Player(
            id=1, 
            name="Bot", 
            color="#22c55e",
            type=PlayerType.AI,
            persona="random"
        )
        
        data = player.to_dict()
        
        assert data["type"] == "ai"
        assert data["persona"] == "random"
        assert data["display_name"] == "Bot (random)"
        assert data["is_ai"] is True
        assert data["is_human"] is False
    
    def test_from_dict(self):
        """Test creation from dictionary."""
        data = {
            "id": 0,
            "name": "Alice",
            "color": "#3b82f6",
            "type": "human",
            "remaining_pieces": ["I1", "I2", "F"],
            "has_passed": False,
            "status": "playing",
            "score": 25,
            "turn_order": 0
        }
        
        player = Player.from_dict(data)
        
        assert player.id == 0
        assert player.name == "Alice"
        assert player.color == "#3b82f6"
        assert player.type == PlayerType.HUMAN
        assert player.pieces_count == 3
        assert PieceType.I1 in player.remaining_pieces
        assert PieceType.I2 in player.remaining_pieces
        assert PieceType.F in player.remaining_pieces
        assert not player.has_passed
        assert player.status == PlayerStatus.PLAYING
        assert player.score == 25
        assert player.turn_order == 0
    
    def test_from_dict_minimal(self):
        """Test creation from minimal dictionary."""
        data = {
            "id": 1,
            "name": "Bob",
            "color": "#22c55e",
            "type": "ai",
            "persona": "aggressive"
        }
        
        player = Player.from_dict(data)
        
        assert player.id == 1
        assert player.name == "Bob"
        assert player.type == PlayerType.AI
        assert player.persona == "aggressive"
        assert player.pieces_count == 21  # Default pieces
        assert not player.has_passed  # Default
        assert player.status == PlayerStatus.WAITING  # Default
        assert player.score == 0  # Default
    
    def test_serialization_roundtrip(self):
        """Test serialization roundtrip."""
        original = Player(
            id=2, 
            name="Charlie", 
            color="#eab308",
            type=PlayerType.HUMAN,
            score=30,
            status=PlayerStatus.PASSED
        )
        
        # Serialize to dict
        data = original.to_dict()
        
        # Deserialize back
        restored = Player.from_dict(data)
        
        assert restored.id == original.id
        assert restored.name == original.name
        assert restored.color == original.color
        assert restored.type == original.type
        assert restored.score == original.score
        assert restored.status == original.status
        assert restored.pieces_count == original.pieces_count


class TestPlayerEdgeCases:
    """Test edge cases and error conditions."""
    
    def test_empty_remaining_pieces(self):
        """Test player with no remaining pieces."""
        player = Player(id=0, name="Alice", color="#3b82f6")
        player.remaining_pieces.clear()
        
        assert player.pieces_count == 0
        assert player.squares_remaining == 0
        assert player.calculate_score() == 15  # All pieces bonus
    
    def test_multiple_pass_turns(self):
        """Test multiple pass_turn calls."""
        player = Player(id=0, name="Alice", color="#3b82f6")
        
        player.pass_turn()
        player.pass_turn()  # Should not change anything
        
        assert player.has_passed
        assert player.status == PlayerStatus.PASSED
    
    def test_play_piece_after_pass(self):
        """Test playing piece after passing."""
        player = Player(id=0, name="Alice", color="#3b82f6")
        
        player.pass_turn()
        result = player.play_piece(PieceType.I1)
        
        assert result is True  # Should still be able to play piece
        assert PieceType.I1 not in player.remaining_pieces
