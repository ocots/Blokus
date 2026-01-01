"""Integration tests for the FastAPI endpoints."""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch

from main import app


class TestGameCreationEndpoint:
    """Test /game/new endpoint."""

    def setup_method(self):
        """Setup test client."""
        self.client = TestClient(app)

    def test_create_default_game(self):
        """Create game with default settings."""
        response = self.client.post("/game/new", json={})
        assert response.status_code == 200
        
        game_state = response.json()
        assert game_state["current_player_id"] == 0  # Default start player
        assert len(game_state["players"]) == 4
        assert game_state["status"] == "in_progress"

    def test_create_game_with_start_player(self):
        """Create game with specified starting player."""
        request_data = {
            "num_players": 4,
            "start_player": 2  # Should start with player 2 (yellow)
        }
        
        response = self.client.post("/game/new", json=request_data)
        assert response.status_code == 200
        
        game_state = response.json()
        assert game_state["current_player_id"] == 2
        assert len(game_state["players"]) == 4

    def test_create_two_player_game_with_start_player(self):
        """Create 2-player game with specified starting player."""
        request_data = {
            "num_players": 2,
            "start_player": 1  # Should start with player 1 (green)
        }
        
        response = self.client.post("/game/new", json=request_data)
        assert response.status_code == 200
        
        game_state = response.json()
        assert game_state["current_player_id"] == 1
        assert len(game_state["players"]) == 2

    def test_create_game_with_players_config(self):
        """Create game with players configuration."""
        players = [
            {"name": "Alice", "type": "human"},
            {"name": "Random Bot", "type": "ai", "persona": "random"},
            {"name": "Charlie", "type": "human"},
            {"name": "Aggressive Bot", "type": "ai", "persona": "aggressive"}
        ]
        
        request_data = {
            "num_players": 4,
            "players": players,
            "start_player": 1
        }
        
        response = self.client.post("/game/new", json=request_data)
        assert response.status_code == 200
        
        game_state = response.json()
        assert game_state["current_player_id"] == 1
        assert len(game_state["players"]) == 4

    def test_create_game_with_invalid_start_player(self):
        """Create game with invalid starting player should return 422."""
        # Start player too high
        request_data = {
            "num_players": 4,
            "start_player": 5
        }
        
        response = self.client.post("/game/new", json=request_data)
        assert response.status_code == 422  # Validation error

    def test_create_game_with_negative_start_player(self):
        """Create game with negative starting player should return 422."""
        request_data = {
            "num_players": 4,
            "start_player": -1
        }
        
        response = self.client.post("/game/new", json=request_data)
        assert response.status_code == 422  # Validation error

    def test_random_start_player_simulation(self):
        """Test random start player behavior."""
        # Simulate frontend random choice
        import random
        random_start = random.randint(0, 3)
        
        request_data = {
            "num_players": 4,
            "start_player": random_start
        }
        
        response = self.client.post("/game/new", json=request_data)
        assert response.status_code == 200
        
        game_state = response.json()
        assert game_state["current_player_id"] == random_start

    def test_game_state_consistency_after_creation(self):
        """Game state should be consistent after creation with custom start player."""
        request_data = {
            "num_players": 4,
            "start_player": 3
        }
        
        response = self.client.post("/game/new", json=request_data)
        assert response.status_code == 200
        
        # Get game state again
        state_response = self.client.get("/game/state")
        assert state_response.status_code == 200
        
        game_state = state_response.json()
        assert game_state["current_player_id"] == 3
        assert game_state["turn_number"] == 0
        assert game_state["status"] == "in_progress"
        
        # All players should have all pieces initially
        for player in game_state["players"]:
            assert len(player["pieces_remaining"]) == 21
            assert player["score"] == -89  # All squares remaining
            assert not player["has_passed"]


class TestGamePlayWithCustomStart:
    """Test game play after custom start player."""

    def setup_method(self):
        """Setup test client and game."""
        self.client = TestClient(app)
        
        # Create game starting with player 1
        request_data = {
            "num_players": 4,
            "start_player": 1
        }
        response = self.client.post("/game/new", json=request_data)
        assert response.status_code == 200

    def test_first_move_from_start_player(self):
        """First move should be from the starting player."""
        # Try to make a move from player 1 (starting player)
        move_data = {
            "player_id": 1,
            "piece_type": "I1",
            "orientation": 0,
            "row": 0,
            "col": 19  # Top-right corner for player 1
        }
        
        response = self.client.post("/game/move", json=move_data)
        assert response.status_code == 200
        assert response.json()["success"] is True
        
        # Get updated game state
        state_response = self.client.get("/game/state")
        game_state = state_response.json()
        
        # Turn should have advanced to player 2
        assert game_state["current_player_id"] == 2
        assert game_state["turn_number"] == 1

    def test_wrong_player_cannot_move_first(self):
        """Wrong player should not be able to move first."""
        # Try to make a move from player 0 (not starting)
        move_data = {
            "player_id": 0,
            "piece_type": "I1",
            "orientation": 0,
            "row": 0,
            "col": 0  # Top-left corner for player 0
        }
        
        response = self.client.post("/game/move", json=move_data)
        assert response.status_code == 200
        assert response.json()["success"] is False
        
        # Game state should be unchanged
        state_response = self.client.get("/game/state")
        game_state = state_response.json()
        assert game_state["current_player_id"] == 1  # Still player 1's turn
        assert game_state["turn_number"] == 0
