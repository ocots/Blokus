"""Tests for PlayerFactory."""

import pytest
from blokus.player_factory import PlayerFactory
from blokus.player_types import PlayerType


class TestPlayerFactory:
    """Test PlayerFactory."""
    
    def test_create_human_player(self):
        """Test creating a human player."""
        player = PlayerFactory.create_human_player(0, "Alice")
        
        assert player.id == 0
        assert player.name == "Alice"
        assert player.is_human
        assert not player.is_ai
        assert player.color == "#3b82f6"  # Default color
        assert player.persona is None
    
    def test_create_human_player_with_color(self):
        """Test creating a human player with custom color."""
        player = PlayerFactory.create_human_player(1, "Bob", "#ff0000")
        
        assert player.id == 1
        assert player.name == "Bob"
        assert player.color == "#ff0000"
    
    def test_create_ai_player(self):
        """Test creating an AI player."""
        player = PlayerFactory.create_ai_player(1, "random")
        
        assert player.id == 1
        assert player.is_ai
        assert not player.is_human
        assert player.persona == "random"
        assert player.name == "Bot Aléatoire"
        assert player.color == "#22c55e"  # Default color
    
    def test_create_ai_player_with_persona(self):
        """Test creating AI players with different personas."""
        aggressive = PlayerFactory.create_ai_player(1, "aggressive")
        defensive = PlayerFactory.create_ai_player(2, "defensive")
        efficient = PlayerFactory.create_ai_player(3, "efficient")
        
        assert aggressive.name == "Bot Agressif"
        assert aggressive.persona == "aggressive"
        
        assert defensive.name == "Bot Défensif"
        assert defensive.persona == "defensive"
        
        assert efficient.name == "Bot Efficace"
        assert efficient.persona == "efficient"
    
    def test_create_ai_player_unknown_persona(self):
        """Test creating AI player with unknown persona."""
        player = PlayerFactory.create_ai_player(1, "unknown")
        
        assert player.name == "Bot unknown"
        assert player.persona == "unknown"
    
    
    def test_default_colors(self):
        """Test default colors are used correctly."""
        player0 = PlayerFactory.create_human_player(0, "Alice")
        player1 = PlayerFactory.create_human_player(1, "Bob")
        player2 = PlayerFactory.create_human_player(2, "Charlie")
        player3 = PlayerFactory.create_human_player(3, "Diana")
        
        assert player0.color == "#3b82f6"  # Blue
        assert player1.color == "#22c55e"  # Green
        assert player2.color == "#eab308"  # Yellow
        assert player3.color == "#ef4444"  # Red
    
    def test_default_colors_wrap_around(self):
        """Test default colors wrap around for IDs > 3."""
        player4 = PlayerFactory.create_human_player(4, "Eve")
        player5 = PlayerFactory.create_human_player(5, "Frank")
        
        assert player4.color == "#3b82f6"  # Back to Blue
        assert player5.color == "#22c55e"  # Green
    
    def test_create_players_from_config(self):
        """Test creating players from configuration."""
        config = [
            {"id": 0, "name": "Alice", "type": "human"},
            {"id": 1, "type": "ai", "persona": "random"},
            {"id": 2, "name": "Charlie", "type": "human"},
            {"id": 3, "type": "ai", "persona": "aggressive"}
        ]
        
        players = PlayerFactory.create_players_from_config(config)
        
        assert len(players) == 4
        
        # Check human players
        assert players[0].name == "Alice"
        assert players[0].is_human
        assert players[2].name == "Charlie"
        assert players[2].is_human
        
        # Check AI players
        assert players[1].is_ai
        assert players[1].persona == "random"
        assert players[3].is_ai
        assert players[3].persona == "aggressive"
    
    def test_create_players_from_config_with_defaults(self):
        """Test creating players from config with default values."""
        config = [
            {"type": "human"},  # No id, name, or color
            {"id": 1, "type": "ai", "persona": "defensive"},
            {"name": "Custom Name", "type": "human", "color": "#ff0000"}
        ]
        
        players = PlayerFactory.create_players_from_config(config)
        
        assert len(players) == 3
        
        # First player (defaults)
        assert players[0].id == 0
        assert players[0].name == "Joueur 1"
        assert players[0].is_human
        assert players[0].color == "#3b82f6"
        
        # Second player
        assert players[1].id == 1
        assert players[1].persona == "defensive"
        assert players[1].is_ai
        
        # Third player
        assert players[2].id == 2
        assert players[2].name == "Custom Name"
        assert players[2].color == "#ff0000"
    
    def test_create_players_from_config_invalid_type(self):
        """Test creating players with invalid type raises error."""
        config = [{"id": 0, "name": "Alice", "type": "invalid"}]
        
        with pytest.raises(ValueError, match="Unknown player type: invalid"):
            PlayerFactory.create_players_from_config(config)
    
    def test_create_standard_players(self):
        """Test creating standard human players."""
        players_2 = PlayerFactory.create_standard_players(2)
        players_4 = PlayerFactory.create_standard_players(4)
        
        assert len(players_2) == 2
        assert len(players_4) == 4
        
        # Check names
        assert players_2[0].name == "Joueur 1"
        assert players_2[1].name == "Joueur 2"
        
        assert players_4[3].name == "Joueur 4"
        
        # Check all are human
        for player in players_4:
            assert player.is_human
            assert not player.is_ai
    
    def test_create_standard_players_invalid_count(self):
        """Test creating standard players with invalid count."""
        with pytest.raises(ValueError, match="num_players must be 2 or 4"):
            PlayerFactory.create_standard_players(1)
        
        with pytest.raises(ValueError, match="num_players must be 2 or 4"):
            PlayerFactory.create_standard_players(3)
        
        with pytest.raises(ValueError, match="num_players must be 2 or 4"):
            PlayerFactory.create_standard_players(5)
    
    
    def test_factory_creates_consistent_players(self):
        """Test that factory creates consistent Player instances."""
        # Create same player multiple ways
        direct = PlayerFactory.create_human_player(0, "Alice", "#ff0000")
        from_config = PlayerFactory.create_players_from_config([
            {"id": 0, "name": "Alice", "type": "human", "color": "#ff0000"}
        ])[0]
        
        assert direct.id == from_config.id
        assert direct.name == from_config.name
        assert direct.color == from_config.color
        assert direct.type == from_config.type
        assert direct.pieces_count == from_config.pieces_count
