"""Tests for GameManager."""

import pytest
from blokus.game_manager import GameManager
from blokus.player import Player
from blokus.player_types import PlayerType, PlayerStatus


class TestGameManagerInitialization:
    """Test GameManager initialization."""
    
    def test_default_initialization(self):
        """Test default initialization."""
        players = [
            Player(id=0, name="Alice", color="#3b82f6"),
            Player(id=1, name="Bob", color="#22c55e")
        ]
        manager = GameManager(players)
        
        assert manager.player_count == 2
        assert manager.current_player.id == 0
        assert manager.current_player.status == PlayerStatus.PLAYING
        assert not manager.game_finished
        assert len(manager.turn_history) == 0
    
    def test_custom_starting_player(self):
        """Test initialization with custom starting player."""
        players = [
            Player(id=0, name="Alice", color="#3b82f6"),
            Player(id=1, name="Bob", color="#22c55e"),
            Player(id=2, name="Charlie", color="#eab308")
        ]
        manager = GameManager(players, starting_player_index=2)
        
        assert manager.current_player.id == 2
        assert manager.current_player.name == "Charlie"
        assert manager.current_player.status == PlayerStatus.PLAYING
    
    def test_invalid_starting_player_index(self):
        """Test invalid starting player index raises error."""
        players = [
            Player(id=0, name="Alice", color="#3b82f6"),
            Player(id=1, name="Bob", color="#22c55e")
        ]
        
        with pytest.raises(ValueError, match="starting_player_index must be between"):
            GameManager(players, starting_player_index=5)
        
        with pytest.raises(ValueError, match="starting_player_index must be between"):
            GameManager(players, starting_player_index=-1)
    
    def test_empty_players_list(self):
        """Test initialization with empty players list."""
        manager = GameManager([])
        
        assert manager.player_count == 0
        assert not manager.game_finished
    
    def test_turn_order_initialization(self):
        """Test turn order is set correctly."""
        players = [
            Player(id=0, name="Alice", color="#3b82f6"),
            Player(id=1, name="Bob", color="#22c55e"),
            Player(id=2, name="Charlie", color="#eab308")
        ]
        manager = GameManager(players)
        
        assert players[0].turn_order == 0
        assert players[1].turn_order == 1
        assert players[2].turn_order == 2


class TestGameManagerProperties:
    """Test GameManager properties."""
    
    def test_current_player_property(self):
        """Test current_player property."""
        players = [
            Player(id=0, name="Alice", color="#3b82f6"),
            Player(id=1, name="Bob", color="#22c55e")
        ]
        manager = GameManager(players)
        
        assert manager.current_player.name == "Alice"
    
    def test_player_count_property(self):
        """Test player_count property."""
        players = [
            Player(id=0, name="Alice", color="#3b82f6"),
            Player(id=1, name="Bob", color="#22c55e"),
            Player(id=2, name="Charlie", color="#eab308")
        ]
        manager = GameManager(players)
        
        assert manager.player_count == 3
    
    def test_active_players_property(self):
        """Test active_players property."""
        players = [
            Player(id=0, name="Alice", color="#3b82f6"),
            Player(id=1, name="Bob", color="#22c55e"),
            Player(id=2, name="Charlie", color="#eab308")
        ]
        manager = GameManager(players)
        
        # Initially all active
        assert len(manager.active_players) == 3
        
        # One passes
        players[1].pass_turn()
        assert len(manager.active_players) == 2
        assert players[1] not in manager.active_players
    
    def test_finished_players_property(self):
        """Test finished_players property."""
        players = [
            Player(id=0, name="Alice", color="#3b82f6"),
            Player(id=1, name="Bob", color="#22c55e"),
            Player(id=2, name="Charlie", color="#eab308")
        ]
        manager = GameManager(players)
        
        # Initially none finished
        assert len(manager.finished_players) == 0
        
        # One passes
        players[1].pass_turn()
        assert len(manager.finished_players) == 1
        assert players[1] in manager.finished_players


class TestGameManagerQueries:
    """Test GameManager query methods."""
    
    def test_get_player_by_id(self):
        """Test getting player by ID."""
        players = [
            Player(id=0, name="Alice", color="#3b82f6"),
            Player(id=1, name="Bob", color="#22c55e"),
            Player(id=2, name="Charlie", color="#eab308")
        ]
        manager = GameManager(players)
        
        player = manager.get_player_by_id(1)
        assert player.name == "Bob"
        
        player = manager.get_player_by_id(2)
        assert player.name == "Charlie"
    
    def test_get_player_by_id_not_found(self):
        """Test getting non-existent player returns None."""
        players = [
            Player(id=0, name="Alice", color="#3b82f6"),
            Player(id=1, name="Bob", color="#22c55e")
        ]
        manager = GameManager(players)
        
        player = manager.get_player_by_id(99)
        assert player is None
    
    def test_get_player_index(self):
        """Test getting player index."""
        players = [
            Player(id=0, name="Alice", color="#3b82f6"),
            Player(id=1, name="Bob", color="#22c55e"),
            Player(id=2, name="Charlie", color="#eab308")
        ]
        manager = GameManager(players)
        
        assert manager.get_player_index(players[0]) == 0
        assert manager.get_player_index(players[1]) == 1
        assert manager.get_player_index(players[2]) == 2
    
    def test_get_player_index_not_found(self):
        """Test getting index of non-existent player raises error."""
        players = [
            Player(id=0, name="Alice", color="#3b82f6"),
            Player(id=1, name="Bob", color="#22c55e")
        ]
        manager = GameManager(players)
        
        other_player = Player(id=99, name="Other", color="#ff0000")
        
        with pytest.raises(ValueError):
            manager.get_player_index(other_player)


class TestGameManagerTurns:
    """Test turn management."""
    
    def test_next_turn(self):
        """Test advancing to next turn."""
        players = [
            Player(id=0, name="Alice", color="#3b82f6"),
            Player(id=1, name="Bob", color="#22c55e"),
            Player(id=2, name="Charlie", color="#eab308")
        ]
        manager = GameManager(players)
        
        # Initial player
        assert manager.current_player.name == "Alice"
        assert manager.current_player.status == PlayerStatus.PLAYING
        
        # Next turn
        next_player = manager.next_turn()
        assert next_player.name == "Bob"
        assert manager.current_player.name == "Bob"
        assert manager.current_player.status == PlayerStatus.PLAYING
        assert players[0].status == PlayerStatus.WAITING
        
        # Turn history
        assert len(manager.turn_history) == 1
        assert manager.turn_history[0] == 0
    
    def test_next_turn_wraps_around(self):
        """Test turn wraps around to first player."""
        players = [
            Player(id=0, name="Alice", color="#3b82f6"),
            Player(id=1, name="Bob", color="#22c55e")
        ]
        manager = GameManager(players)
        
        manager.next_turn()  # Alice -> Bob
        next_player = manager.next_turn()  # Bob -> Alice
        
        assert next_player.name == "Alice"
        assert manager.current_player_index == 0
    
    def test_next_turn_skips_passed_players(self):
        """Test next_turn skips players who have passed."""
        players = [
            Player(id=0, name="Alice", color="#3b82f6"),
            Player(id=1, name="Bob", color="#22c55e"),
            Player(id=2, name="Charlie", color="#eab308"),
            Player(id=3, name="Diana", color="#ef4444")
        ]
        manager = GameManager(players)
        
        # Bob passes
        players[1].pass_turn()
        
        # Alice -> should skip Bob -> Charlie
        next_player = manager.next_turn()
        assert next_player.name == "Charlie"
        assert manager.current_player_index == 2
    
    def test_next_turn_all_passed(self):
        """Test next_turn when all players have passed."""
        players = [
            Player(id=0, name="Alice", color="#3b82f6"),
            Player(id=1, name="Bob", color="#22c55e")
        ]
        manager = GameManager(players)
        
        # Both pass
        players[0].pass_turn()
        players[1].pass_turn()
        
        # Try next turn
        manager.next_turn()
        
        assert manager.game_finished
    
    def test_next_turn_empty_players(self):
        """Test next_turn with no players raises error."""
        manager = GameManager([])
        
        with pytest.raises(ValueError, match="No players in game"):
            manager.next_turn()
    
    def test_set_starting_player(self):
        """Test setting starting player by ID."""
        players = [
            Player(id=0, name="Alice", color="#3b82f6"),
            Player(id=1, name="Bob", color="#22c55e"),
            Player(id=2, name="Charlie", color="#eab308")
        ]
        manager = GameManager(players)
        
        # Change to Charlie
        manager.set_starting_player(2)
        
        assert manager.current_player.name == "Charlie"
        assert manager.current_player.status == PlayerStatus.PLAYING
        assert players[0].status == PlayerStatus.WAITING
        assert len(manager.turn_history) == 0
    
    def test_set_starting_player_not_found(self):
        """Test setting non-existent starting player raises error."""
        players = [
            Player(id=0, name="Alice", color="#3b82f6"),
            Player(id=1, name="Bob", color="#22c55e")
        ]
        manager = GameManager(players)
        
        with pytest.raises(ValueError, match="Player with ID 99 not found"):
            manager.set_starting_player(99)
    
    def test_set_starting_player_by_index(self):
        """Test setting starting player by index."""
        players = [
            Player(id=0, name="Alice", color="#3b82f6"),
            Player(id=1, name="Bob", color="#22c55e"),
            Player(id=2, name="Charlie", color="#eab308")
        ]
        manager = GameManager(players)
        
        manager.set_starting_player_by_index(1)
        
        assert manager.current_player.name == "Bob"
        assert manager.current_player_index == 1
        assert len(manager.turn_history) == 0
    
    def test_set_starting_player_by_index_invalid(self):
        """Test setting starting player with invalid index."""
        players = [
            Player(id=0, name="Alice", color="#3b82f6"),
            Player(id=1, name="Bob", color="#22c55e")
        ]
        manager = GameManager(players)
        
        with pytest.raises(ValueError, match="Index must be between"):
            manager.set_starting_player_by_index(5)
    
    def test_force_pass_turn(self):
        """Test forcing current player to pass."""
        players = [
            Player(id=0, name="Alice", color="#3b82f6"),
            Player(id=1, name="Bob", color="#22c55e")
        ]
        manager = GameManager(players)
        
        manager.force_pass_turn()
        
        assert players[0].has_passed
        # Status becomes WAITING after next_turn is called
        assert players[0].status == PlayerStatus.WAITING
        assert manager.current_player.name == "Bob"


class TestGameManagerOrders:
    """Test different player orderings."""
    
    def test_get_play_order(self):
        """Test getting play order."""
        players = [
            Player(id=0, name="Alice", color="#3b82f6"),
            Player(id=1, name="Bob", color="#22c55e"),
            Player(id=2, name="Charlie", color="#eab308")
        ]
        manager = GameManager(players)
        
        play_order = manager.get_play_order()
        
        assert len(play_order) == 3
        assert play_order[0].name == "Alice"
        assert play_order[1].name == "Bob"
        assert play_order[2].name == "Charlie"
        
        # Should be a copy
        assert play_order is not manager.players
    
    def test_get_turn_order_from_current(self):
        """Test getting turn order from current player."""
        players = [
            Player(id=0, name="Alice", color="#3b82f6"),
            Player(id=1, name="Bob", color="#22c55e"),
            Player(id=2, name="Charlie", color="#eab308"),
            Player(id=3, name="Diana", color="#ef4444")
        ]
        manager = GameManager(players, starting_player_index=2)
        
        turn_order = manager.get_turn_order_from_current()
        
        assert turn_order[0].name == "Charlie"  # Current
        assert turn_order[1].name == "Diana"
        assert turn_order[2].name == "Alice"
        assert turn_order[3].name == "Bob"
    
    def test_get_score_order(self):
        """Test getting players by score."""
        players = [
            Player(id=0, name="Alice", color="#3b82f6", score=50),
            Player(id=1, name="Bob", color="#22c55e", score=30),
            Player(id=2, name="Charlie", color="#eab308", score=70),
            Player(id=3, name="Diana", color="#ef4444", score=40)
        ]
        manager = GameManager(players)
        
        score_order = manager.get_score_order()
        
        assert score_order[0].name == "Charlie"  # 70
        assert score_order[1].name == "Alice"    # 50
        assert score_order[2].name == "Diana"    # 40
        assert score_order[3].name == "Bob"      # 30
    
    def test_get_players_by_type(self):
        """Test getting players by type."""
        players = [
            Player(id=0, name="Alice", color="#3b82f6", type=PlayerType.HUMAN),
            Player(id=1, name="Bot", color="#22c55e", type=PlayerType.AI, persona="random"),
            Player(id=2, name="Charlie", color="#eab308", type=PlayerType.HUMAN),
            Player(id=3, name="Diana", color="#ef4444", type=PlayerType.AI, persona="defensive")
        ]
        manager = GameManager(players)
        
        humans = manager.get_players_by_type(PlayerType.HUMAN)
        ais = manager.get_players_by_type(PlayerType.AI)
        
        assert len(humans) == 2
        assert len(ais) == 2
        
        assert humans[0].name == "Alice"
        assert humans[1].name == "Charlie"
        assert ais[0].name == "Bot"
        assert ais[1].name == "Diana"


class TestGameManagerState:
    """Test game state checks."""
    
    def test_is_game_over_false(self):
        """Test game not over when players active."""
        players = [
            Player(id=0, name="Alice", color="#3b82f6"),
            Player(id=1, name="Bob", color="#22c55e")
        ]
        manager = GameManager(players)
        
        assert not manager.is_game_over()
    
    def test_is_game_over_all_passed(self):
        """Test game over when all players passed."""
        players = [
            Player(id=0, name="Alice", color="#3b82f6"),
            Player(id=1, name="Bob", color="#22c55e")
        ]
        manager = GameManager(players)
        
        players[0].pass_turn()
        players[1].pass_turn()
        
        assert manager.is_game_over()
    
    def test_is_game_over_flag_set(self):
        """Test game over when flag is set."""
        players = [
            Player(id=0, name="Alice", color="#3b82f6"),
            Player(id=1, name="Bob", color="#22c55e")
        ]
        manager = GameManager(players)
        
        manager.game_finished = True
        
        assert manager.is_game_over()
    
    def test_get_winner_single(self):
        """Test getting winner with single highest score."""
        players = [
            Player(id=0, name="Alice", color="#3b82f6", score=50),
            Player(id=1, name="Bob", color="#22c55e", score=30),
            Player(id=2, name="Charlie", color="#eab308", score=70)
        ]
        manager = GameManager(players)
        manager.game_finished = True
        
        winner = manager.get_winner()
        
        assert winner.name == "Charlie"
    
    def test_get_winner_tie(self):
        """Test getting winner with tie returns None."""
        players = [
            Player(id=0, name="Alice", color="#3b82f6", score=50),
            Player(id=1, name="Bob", color="#22c55e", score=50)
        ]
        manager = GameManager(players)
        manager.game_finished = True
        
        winner = manager.get_winner()
        
        assert winner is None
    
    def test_get_winner_game_not_over(self):
        """Test getting winner when game not over returns None."""
        players = [
            Player(id=0, name="Alice", color="#3b82f6", score=50),
            Player(id=1, name="Bob", color="#22c55e", score=30)
        ]
        manager = GameManager(players)
        
        winner = manager.get_winner()
        
        assert winner is None
    
    def test_get_rankings(self):
        """Test getting player rankings."""
        players = [
            Player(id=0, name="Alice", color="#3b82f6", score=50),
            Player(id=1, name="Bob", color="#22c55e", score=30),
            Player(id=2, name="Charlie", color="#eab308", score=70),
            Player(id=3, name="Diana", color="#ef4444", score=40)
        ]
        manager = GameManager(players)
        
        rankings = manager.get_rankings()
        
        assert rankings[2] == 1  # Charlie - 70
        assert rankings[0] == 2  # Alice - 50
        assert rankings[3] == 3  # Diana - 40
        assert rankings[1] == 4  # Bob - 30


class TestGameManagerSerialization:
    """Test serialization."""
    
    def test_to_dict(self):
        """Test conversion to dictionary."""
        players = [
            Player(id=0, name="Alice", color="#3b82f6"),
            Player(id=1, name="Bob", color="#22c55e")
        ]
        manager = GameManager(players)
        
        data = manager.to_dict()
        
        assert data["player_count"] == 2
        assert data["current_player_index"] == 0
        assert data["current_player"]["name"] == "Alice"
        assert len(data["players"]) == 2
        assert data["game_finished"] is False
        assert len(data["turn_history"]) == 0
    
    def test_from_dict(self):
        """Test creation from dictionary."""
        data = {
            "players": [
                {"id": 0, "name": "Alice", "color": "#3b82f6", "type": "human"},
                {"id": 1, "name": "Bob", "color": "#22c55e", "type": "human"}
            ],
            "current_player_index": 1,
            "turn_history": [0],
            "game_finished": False
        }
        
        manager = GameManager.from_dict(data)
        
        assert manager.player_count == 2
        assert manager.current_player.name == "Bob"
        assert len(manager.turn_history) == 1
        assert not manager.game_finished
    
    def test_serialization_roundtrip(self):
        """Test serialization roundtrip."""
        players = [
            Player(id=0, name="Alice", color="#3b82f6"),
            Player(id=1, name="Bob", color="#22c55e"),
            Player(id=2, name="Charlie", color="#eab308")
        ]
        original = GameManager(players, starting_player_index=1)
        original.next_turn()
        
        # Serialize
        data = original.to_dict()
        
        # Deserialize
        restored = GameManager.from_dict(data)
        
        assert restored.player_count == original.player_count
        assert restored.current_player_index == original.current_player_index
        assert len(restored.turn_history) == len(original.turn_history)


class TestGameManagerUtility:
    """Test utility methods."""
    
    def test_len(self):
        """Test __len__ method."""
        players = [
            Player(id=0, name="Alice", color="#3b82f6"),
            Player(id=1, name="Bob", color="#22c55e"),
            Player(id=2, name="Charlie", color="#eab308")
        ]
        manager = GameManager(players)
        
        assert len(manager) == 3
    
    def test_getitem(self):
        """Test __getitem__ method."""
        players = [
            Player(id=0, name="Alice", color="#3b82f6"),
            Player(id=1, name="Bob", color="#22c55e")
        ]
        manager = GameManager(players)
        
        assert manager[0].name == "Alice"
        assert manager[1].name == "Bob"
    
    def test_iter(self):
        """Test __iter__ method."""
        players = [
            Player(id=0, name="Alice", color="#3b82f6"),
            Player(id=1, name="Bob", color="#22c55e"),
            Player(id=2, name="Charlie", color="#eab308")
        ]
        manager = GameManager(players)
        
        names = [p.name for p in manager]
        
        assert names == ["Alice", "Bob", "Charlie"]
    
    def test_repr(self):
        """Test __repr__ method."""
        players = [
            Player(id=0, name="Alice", color="#3b82f6"),
            Player(id=1, name="Bob", color="#22c55e")
        ]
        manager = GameManager(players)
        
        repr_str = repr(manager)
        
        assert "GameManager" in repr_str
        assert "2 players" in repr_str
        assert "Alice" in repr_str
    
    def test_repr_empty(self):
        """Test __repr__ with no players."""
        manager = GameManager([])
        
        repr_str = repr(manager)
        
        assert "no players" in repr_str
