"""Tests for GameManagerFactory."""

import pytest
from blokus.game_manager_factory import GameManagerFactory
from blokus.player_types import PlayerType


class TestGameManagerFactory:
    """Test GameManagerFactory."""
    
    def test_create_from_config(self):
        """Test creating GameManager from configuration."""
        config = [
            {"id": 0, "name": "Alice", "type": "human"},
            {"id": 1, "type": "ai", "persona": "random"},
            {"id": 2, "name": "Charlie", "type": "human"},
            {"id": 3, "type": "ai", "persona": "aggressive"}
        ]
        
        manager = GameManagerFactory.create_from_config(config, starting_player_id=2)
        
        assert manager.player_count == 4
        assert manager.current_player.name == "Charlie"
        assert manager.current_player.id == 2
        
        # Check all players created
        assert manager[0].name == "Alice"
        assert manager[0].is_human
        assert manager[1].is_ai
        assert manager[1].persona == "random"
        assert manager[2].name == "Charlie"
        assert manager[3].is_ai
        assert manager[3].persona == "aggressive"
    
    def test_create_from_config_default_starting_player(self):
        """Test creating with default starting player."""
        config = [
            {"id": 0, "name": "Alice", "type": "human"},
            {"id": 1, "name": "Bob", "type": "human"}
        ]
        
        manager = GameManagerFactory.create_from_config(config)
        
        assert manager.current_player.id == 0
        assert manager.current_player.name == "Alice"
    
    def test_create_standard_game(self):
        """Test creating standard game."""
        manager = GameManagerFactory.create_standard_game(4, starting_player_id=1)
        
        assert manager.player_count == 4
        assert manager.current_player.id == 1
        assert manager.current_player.name == "Joueur 2"
        
        # All players should be human
        for player in manager:
            assert player.is_human
            assert not player.is_ai
    
    def test_create_standard_game_2_players(self):
        """Test creating 2-player standard game."""
        manager = GameManagerFactory.create_standard_game(2)
        
        assert manager.player_count == 2
        assert manager[0].name == "Joueur 1"
        assert manager[1].name == "Joueur 2"
    
    def test_create_standard_game_3_players(self):
        """Test creating 3-player standard game."""
        manager = GameManagerFactory.create_standard_game(3)
        
        assert manager.player_count == 3
    
    def test_create_standard_game_invalid_count(self):
        """Test creating standard game with invalid player count."""
        with pytest.raises(ValueError, match="num_players must be between 2 and 4"):
            GameManagerFactory.create_standard_game(1)
        
        with pytest.raises(ValueError, match="num_players must be between 2 and 4"):
            GameManagerFactory.create_standard_game(5)
    
    def test_create_standard_game_invalid_starting_player(self):
        """Test creating standard game with invalid starting player."""
        with pytest.raises(ValueError, match="starting_player_id must be between"):
            GameManagerFactory.create_standard_game(4, starting_player_id=5)
        
        with pytest.raises(ValueError, match="starting_player_id must be between"):
            GameManagerFactory.create_standard_game(4, starting_player_id=-1)
    
    def test_create_ai_game(self):
        """Test creating AI-only game."""
        ai_configs = [
            {"persona": "random"},
            {"persona": "aggressive"},
            {"persona": "defensive"},
            {"persona": "efficient"}
        ]
        
        manager = GameManagerFactory.create_ai_game(ai_configs, starting_player_id=2)
        
        assert manager.player_count == 4
        assert manager.current_player.id == 2
        
        # All players should be AI
        for player in manager:
            assert player.is_ai
            assert not player.is_human
        
        # Check personas
        assert manager[0].persona == "random"
        assert manager[1].persona == "aggressive"
        assert manager[2].persona == "defensive"
        assert manager[3].persona == "efficient"
    
    def test_create_ai_game_2_players(self):
        """Test creating 2-player AI game."""
        ai_configs = [
            {"persona": "random"},
            {"persona": "aggressive"}
        ]
        
        manager = GameManagerFactory.create_ai_game(ai_configs)
        
        assert manager.player_count == 2
        assert all(p.is_ai for p in manager)
    
    def test_create_mixed_game(self):
        """Test creating mixed human/AI game."""
        manager = GameManagerFactory.create_mixed_game(
            num_humans=2,
            num_ais=2,
            ai_personas=["random", "aggressive"],
            starting_player_id=1
        )
        
        assert manager.player_count == 4
        assert manager.current_player.id == 1
        
        # First 2 should be human
        assert manager[0].is_human
        assert manager[0].name == "Joueur 1"
        assert manager[1].is_human
        assert manager[1].name == "Joueur 2"
        
        # Last 2 should be AI
        assert manager[2].is_ai
        assert manager[2].persona == "random"
        assert manager[3].is_ai
        assert manager[3].persona == "aggressive"
    
    def test_create_mixed_game_default_personas(self):
        """Test creating mixed game with default AI personas."""
        manager = GameManagerFactory.create_mixed_game(
            num_humans=1,
            num_ais=3
        )
        
        assert manager.player_count == 4
        assert manager[0].is_human
        
        # All AIs should have "random" persona by default
        for i in range(1, 4):
            assert manager[i].is_ai
            assert manager[i].persona == "random"
    
    def test_create_mixed_game_invalid_total(self):
        """Test creating mixed game with invalid total players."""
        with pytest.raises(ValueError, match="Total players must be between 2 and 4"):
            GameManagerFactory.create_mixed_game(num_humans=1, num_ais=0)
        
        with pytest.raises(ValueError, match="Total players must be between 2 and 4"):
            GameManagerFactory.create_mixed_game(num_humans=3, num_ais=2)
    
    def test_create_mixed_game_mismatched_personas(self):
        """Test creating mixed game with mismatched personas count."""
        with pytest.raises(ValueError, match="ai_personas length"):
            GameManagerFactory.create_mixed_game(
                num_humans=2,
                num_ais=2,
                ai_personas=["random"]  # Only 1 persona for 2 AIs
            )
    
    def test_create_mixed_game_all_humans(self):
        """Test creating mixed game with all humans."""
        manager = GameManagerFactory.create_mixed_game(
            num_humans=4,
            num_ais=0,
            ai_personas=[]
        )
        
        assert manager.player_count == 4
        assert all(p.is_human for p in manager)
    
    def test_create_mixed_game_all_ais(self):
        """Test creating mixed game with all AIs."""
        manager = GameManagerFactory.create_mixed_game(
            num_humans=0,
            num_ais=4,
            ai_personas=["random", "aggressive", "defensive", "efficient"]
        )
        
        assert manager.player_count == 4
        assert all(p.is_ai for p in manager)
    
    def test_factory_creates_playable_game(self):
        """Test that factory creates a playable game."""
        manager = GameManagerFactory.create_standard_game(4, starting_player_id=2)
        
        # Should be able to play turns
        assert manager.current_player.id == 2
        
        next_player = manager.next_turn()
        assert next_player.id == 3
        
        next_player = manager.next_turn()
        assert next_player.id == 0
    
    def test_factory_consistency(self):
        """Test that factory creates consistent GameManagers."""
        config = [
            {"id": 0, "name": "Alice", "type": "human"},
            {"id": 1, "name": "Bob", "type": "human"}
        ]
        
        manager1 = GameManagerFactory.create_from_config(config)
        manager2 = GameManagerFactory.create_from_config(config)
        
        # Should create equivalent managers
        assert manager1.player_count == manager2.player_count
        assert manager1.current_player.id == manager2.current_player.id
        assert manager1[0].name == manager2[0].name
        assert manager1[1].name == manager2[1].name
    
    def test_factory_with_shared_player(self):
        """Test factory with shared player type."""
        config = [
            {"id": 0, "name": "Alice", "type": "human"},
            {"id": 1, "type": "ai", "persona": "random"},
            {"id": 2, "type": "shared"}
        ]
        
        manager = GameManagerFactory.create_from_config(config)
        
        assert manager.player_count == 3
        assert manager[0].is_human
        assert manager[1].is_ai
        assert manager[2].is_shared
        assert manager[2].name == "Neutre (Partagé)"
