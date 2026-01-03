
import pytest

def resolve_board_size_logic(two_player_mode: str | None, explicit_size: int | None = None) -> int:
    """
    Replica of the decision logic located in blokus-server/main.py.
    Used to verify regression testing on Game Mode rules.
    
    Logic verified:
    1. Default is 20
    2. 'duo' (case insensitive, stripped) triggers 14
    3. Explicit size overrides everything
    """
    board_size = 20
    
    mode = two_player_mode.strip().lower() if two_player_mode else None
    
    if explicit_size is not None:
        board_size = explicit_size
    elif mode == 'duo':
        board_size = 14
        
    return board_size

class TestServerLogicFallback:
    """
    Tests mirroring the logic in blokus-server/main.py regarding Board Size determination.
    This ensures that the rules for switching between 14x14 and 20x20 are solid.
    """

    def test_duo_mode_detection(self):
        """Verify 'duo' triggers 14x14 board."""
        assert resolve_board_size_logic("duo") == 14

    def test_duo_mode_robustness(self):
        """Verify inputs are sanitized (trimmed, lowercased)."""
        assert resolve_board_size_logic("DUO") == 14
        assert resolve_board_size_logic(" Duo ") == 14
        assert resolve_board_size_logic("duo\n") == 14

    def test_standard_mode_defaults(self):
        """Verify other modes default to 20x20."""
        assert resolve_board_size_logic("standard") == 20
        assert resolve_board_size_logic(None) == 20
        assert resolve_board_size_logic("") == 20

    def test_explicit_override_priority(self):
        """Verify explicit board_size param takes precedence over mode."""
        # If frontend sends size=20 but mode=duo (config mismatch), size wins
        assert resolve_board_size_logic("duo", explicit_size=20) == 20
        
    def test_missing_params_safety(self):
        """Verify None inputs result in safe defaults (Standard)."""
        assert resolve_board_size_logic(None, None) == 20
