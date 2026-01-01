"""Tests for the API models and game creation."""

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from api.models import CreateGameRequest, PlayerConfig


class TestCreateGameRequest:
    """Test CreateGameRequest model."""

    def test_default_request(self):
        """Default request should have 4 players."""
        request = CreateGameRequest()
        assert request.num_players == 4
        assert request.players is None
        assert request.start_player is None  # Will be added

    def test_request_with_start_player(self):
        """Request should accept start_player parameter."""
        # This test will fail until we add start_player to the model
        request = CreateGameRequest(num_players=4, start_player=2)
        assert request.num_players == 4
        assert request.start_player == 2

    def test_request_with_players_config(self):
        """Request should accept players configuration."""
        players = [
            PlayerConfig(name="Alice", type="human"),
            PlayerConfig(name="Bob", type="ai", persona="random"),
            PlayerConfig(name="Charlie", type="human"),
            PlayerConfig(name="Diana", type="ai", persona="aggressive"),
        ]
        
        request = CreateGameRequest(num_players=4, players=players, start_player=1)
        assert len(request.players) == 4
        assert request.start_player == 1
        assert request.players[0].name == "Alice"
        assert request.players[1].persona == "random"

    def test_invalid_start_player_raises_error(self):
        """Invalid start_player should raise validation error."""
        # Negative start player
        with pytest.raises(ValidationError):
            CreateGameRequest(num_players=4, start_player=-1)
            
        # Start player too high
        with pytest.raises(ValidationError):
            CreateGameRequest(num_players=4, start_player=4)
            
        # Start player too high for 2-player game
        with pytest.raises(ValidationError):
            CreateGameRequest(num_players=2, start_player=2)

    def test_start_player_with_two_player_mode(self):
        """Start player should work with 2-player games."""
        request = CreateGameRequest(num_players=2, start_player=1)
        assert request.start_player == 1
        
        # Test with players config
        players = [
            PlayerConfig(name="Alice", type="human"),
            PlayerConfig(name="Bob", type="ai", persona="defensive"),
        ]
        request = CreateGameRequest(num_players=2, players=players, start_player=0)
        assert request.start_player == 0


class TestPlayerConfig:
    """Test PlayerConfig model."""

    def test_human_player_config(self):
        """Human player configuration."""
        config = PlayerConfig(name="Alice", type="human")
        assert config.name == "Alice"
        assert config.type == "human"
        assert config.persona is None

    def test_ai_player_config(self):
        """AI player configuration."""
        config = PlayerConfig(name="Random Bot", type="ai", persona="random")
        assert config.name == "Random Bot"
        assert config.type == "ai"
        assert config.persona == "random"

    def test_shared_player_config(self):
        """Shared player configuration (for 3-player games)."""
        config = PlayerConfig(name="Neutre", type="shared")
        assert config.name == "Neutre"
        assert config.type == "shared"
        assert config.persona is None

    def test_invalid_player_type(self):
        """Invalid player type should raise validation error."""
        with pytest.raises(ValidationError):
            PlayerConfig(name="Invalid", type="invalid_type")
