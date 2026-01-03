"""Tests for player types and enums."""

import pytest
from blokus.player_types import (
    PlayerType, PlayerStatus, GameState, TurnState, 
    MoveState, UIState
)


class TestPlayerType:
    """Test PlayerType enum."""
    
    def test_player_type_values(self):
        """Test enum values."""
        assert PlayerType.HUMAN.value == "human"
        assert PlayerType.AI.value == "ai"
    
    def test_player_type_count(self):
        """Test number of player types."""
        assert len(PlayerType) == 2
    
    def test_player_type_iteration(self):
        """Test enum iteration."""
        types = list(PlayerType)
        assert PlayerType.HUMAN in types
        assert PlayerType.AI in types


class TestPlayerStatus:
    """Test PlayerStatus enum."""
    
    def test_player_status_values(self):
        """Test enum values."""
        assert PlayerStatus.WAITING.value == "waiting"
        assert PlayerStatus.PLAYING.value == "playing"
        assert PlayerStatus.PASSED.value == "passed"
        assert PlayerStatus.FINISHED.value == "finished"
    
    def test_player_status_count(self):
        """Test number of player statuses."""
        assert len(PlayerStatus) == 4


class TestGameState:
    """Test GameState enum."""
    
    def test_game_state_values(self):
        """Test enum values."""
        assert GameState.INITIALIZING.value == "initializing"
        assert GameState.WAITING_START.value == "waiting_start"
        assert GameState.PLAYING.value == "playing"
        assert GameState.PAUSED.value == "paused"
        assert GameState.FINISHED.value == "finished"
        assert GameState.ABORTED.value == "aborted"
    
    def test_game_state_count(self):
        """Test number of game states."""
        assert len(GameState) == 6


class TestTurnState:
    """Test TurnState enum."""
    
    def test_turn_state_values(self):
        """Test enum values."""
        assert TurnState.STARTING.value == "starting"
        assert TurnState.SELECTING_PIECE.value == "selecting_piece"
        assert TurnState.PLACING_PIECE.value == "placing_piece"
        assert TurnState.VALIDATING_MOVE.value == "validating_move"
        assert TurnState.EXECUTING_MOVE.value == "executing_move"
        assert TurnState.ENDING.value == "ending"
        assert TurnState.PASSED.value == "passed"
    
    def test_turn_state_count(self):
        """Test number of turn states."""
        assert len(TurnState) == 7


class TestMoveState:
    """Test MoveState enum."""
    
    def test_move_state_values(self):
        """Test enum values."""
        assert MoveState.PROPOSED.value == "proposed"
        assert MoveState.VALIDATING.value == "validating"
        assert MoveState.VALID.value == "valid"
        assert MoveState.INVALID.value == "invalid"
        assert MoveState.EXECUTED.value == "executed"
        assert MoveState.ANIMATING.value == "animating"
        assert MoveState.COMPLETED.value == "completed"
        assert MoveState.FAILED.value == "failed"
    
    def test_move_state_count(self):
        """Test number of move states."""
        assert len(MoveState) == 8


class TestUIState:
    """Test UIState enum."""
    
    def test_ui_state_values(self):
        """Test enum values."""
        assert UIState.IDLE.value == "idle"
        assert UIState.HOVERING.value == "hovering"
        assert UIState.DRAGGING.value == "dragging"
        assert UIState.SELECTING.value == "selecting"
        assert UIState.ANIMATING.value == "animating"
        assert UIState.DISABLED.value == "disabled"
        assert UIState.LOADING.value == "loading"
    
    def test_ui_state_count(self):
        """Test number of UI states."""
        assert len(UIState) == 7


class TestEnumSerialization:
    """Test enum serialization and deserialization."""
    
    def test_player_type_serialization(self):
        """Test PlayerType serialization."""
        # String representation
        assert str(PlayerType.HUMAN) == "PlayerType.HUMAN"
        assert str(PlayerType.AI) == "PlayerType.AI"
        
        # Value access
        assert PlayerType.HUMAN.value == "human"
        
        # Creation from value
        assert PlayerType("human") == PlayerType.HUMAN
        assert PlayerType("ai") == PlayerType.AI
    
    def test_player_status_serialization(self):
        """Test PlayerStatus serialization."""
        assert PlayerStatus.WAITING.value == "waiting"
        assert PlayerStatus("waiting") == PlayerStatus.WAITING
    
    def test_invalid_enum_value(self):
        """Test invalid enum value raises error."""
        with pytest.raises(ValueError):
            PlayerType("invalid")
        
        with pytest.raises(ValueError):
            PlayerStatus("invalid")


class TestEnumComparison:
    """Test enum comparisons."""
    
    def test_player_type_equality(self):
        """Test PlayerType equality."""
        assert PlayerType.HUMAN == PlayerType.HUMAN
        assert PlayerType.HUMAN != PlayerType.AI
    
    def test_player_status_equality(self):
        """Test PlayerStatus equality."""
        assert PlayerStatus.WAITING == PlayerStatus.WAITING
        assert PlayerStatus.WAITING != PlayerStatus.PLAYING
    
    def test_enum_ordering(self):
        """Test enum ordering (by definition order)."""
        # Test using enum values for comparison
        assert list(PlayerType) == [PlayerType.HUMAN, PlayerType.AI]
        
        # Test that enums have defined order
        assert PlayerType.HUMAN.name == "HUMAN"
        assert PlayerType.AI.name == "AI"
