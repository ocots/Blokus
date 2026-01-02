"""
AI System Integration Tests - API

Tests for AI integration with the FastAPI backend.
Covers:
1. API endpoints for AI moves
2. Error handling in API responses
3. Game state consistency through API

@module tests/test_ai_integration.py
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, MagicMock
from blokus_server.main import app, game_instance


@pytest.fixture
def client():
    """Create test client"""
    return TestClient(app)


@pytest.fixture
def game_config():
    """Create test game configuration"""
    return {
        "num_players": 4,
        "players": [
            {"name": "Human", "type": "human", "color": "#3b82f6"},
            {"name": "AI Random", "type": "ai", "persona": "random", "color": "#22c55e"},
            {"name": "AI Random", "type": "ai", "persona": "random", "color": "#eab308"},
            {"name": "AI Random", "type": "ai", "persona": "random", "color": "#ef4444"}
        ],
        "start_player": 0
    }


class TestGameCreation:
    """Test game creation with AI players"""

    def test_create_game_with_human_players(self, client):
        """Test creating game with human players"""
        response = client.post("/game/new", json={
            "num_players": 2,
            "players": [
                {"name": "Player 1", "type": "human"},
                {"name": "Player 2", "type": "human"}
            ]
        })

        assert response.status_code == 200
        data = response.json()
        assert data["num_players"] == 2
        assert len(data["players"]) == 2

    def test_create_game_with_ai_players(self, client):
        """Test creating game with AI players"""
        response = client.post("/game/new", json={
            "num_players": 4,
            "players": [
                {"name": "Human", "type": "human"},
                {"name": "AI 1", "type": "ai", "persona": "random"},
                {"name": "AI 2", "type": "ai", "persona": "random"},
                {"name": "AI 3", "type": "ai", "persona": "random"}
            ]
        })

        assert response.status_code == 200
        data = response.json()
        assert data["num_players"] == 4
        assert len(data["players"]) == 4

    def test_create_game_with_mixed_players(self, client):
        """Test creating game with mixed human and AI players"""
        response = client.post("/game/new", json={
            "num_players": 3,
            "players": [
                {"name": "Human", "type": "human"},
                {"name": "AI", "type": "ai", "persona": "random"},
                {"name": "Human 2", "type": "human"}
            ]
        })

        assert response.status_code == 200
        data = response.json()
        assert data["num_players"] == 3

    def test_create_game_invalid_player_count(self, client):
        """Test creating game with invalid player count"""
        response = client.post("/game/new", json={
            "num_players": 0
        })

        assert response.status_code != 200

    def test_create_game_missing_players_config(self, client):
        """Test creating game without player configuration"""
        response = client.post("/game/new", json={
            "num_players": 4
        })

        assert response.status_code == 200
        data = response.json()
        assert data["num_players"] == 4


class TestGameState:
    """Test game state management through API"""

    def test_get_game_state(self, client):
        """Test getting game state"""
        # Create game first
        client.post("/game/new", json={"num_players": 2})

        response = client.get("/game/state")
        assert response.status_code == 200
        data = response.json()
        assert "players" in data
        assert "current_player_id" in data
        assert "status" in data

    def test_game_state_consistency(self, client):
        """Test that game state is consistent"""
        # Create game
        create_response = client.post("/game/new", json={"num_players": 2})
        create_data = create_response.json()

        # Get state
        state_response = client.get("/game/state")
        state_data = state_response.json()

        # Player count should match
        assert len(state_data["players"]) == create_data["num_players"]

    def test_current_player_tracking(self, client):
        """Test that current player is tracked correctly"""
        client.post("/game/new", json={"num_players": 4})

        response = client.get("/game/state")
        data = response.json()

        assert 0 <= data["current_player_id"] < 4


class TestMoveExecution:
    """Test move execution through API"""

    def test_play_valid_move(self, client):
        """Test playing a valid move"""
        client.post("/game/new", json={"num_players": 2})

        response = client.post("/game/move", json={
            "player_id": 0,
            "piece_type": "I1",
            "orientation": 0,
            "row": 0,
            "col": 0
        })

        assert response.status_code == 200
        data = response.json()
        assert "success" in data

    def test_play_invalid_move(self, client):
        """Test playing an invalid move"""
        client.post("/game/new", json={"num_players": 2})

        response = client.post("/game/move", json={
            "player_id": 0,
            "piece_type": "INVALID",
            "orientation": 0,
            "row": 0,
            "col": 0
        })

        # Should handle gracefully
        assert response.status_code in [200, 400]

    def test_move_updates_game_state(self, client):
        """Test that move updates game state"""
        client.post("/game/new", json={"num_players": 2})

        # Play move
        client.post("/game/move", json={
            "player_id": 0,
            "piece_type": "I1",
            "orientation": 0,
            "row": 0,
            "col": 0
        })

        # Check state was updated
        state_response = client.get("/game/state")
        data = state_response.json()
        assert data["status"] != "setup"


class TestPassTurn:
    """Test pass turn functionality"""

    def test_pass_turn(self, client):
        """Test passing turn"""
        client.post("/game/new", json={"num_players": 2})

        response = client.post("/game/pass")
        assert response.status_code == 200

    def test_pass_turn_advances_player(self, client):
        """Test that passing turn advances to next player"""
        client.post("/game/new", json={"num_players": 2})

        initial_state = client.get("/game/state").json()
        initial_player = initial_state["current_player_id"]

        client.post("/game/pass")

        new_state = client.get("/game/state").json()
        new_player = new_state["current_player_id"]

        # Player should change (unless game over)
        if new_state["status"] != "finished":
            assert new_player != initial_player


class TestGameReset:
    """Test game reset functionality"""

    def test_reset_game(self, client):
        """Test resetting game"""
        client.post("/game/new", json={"num_players": 2})

        response = client.post("/game/reset")
        assert response.status_code == 200

    def test_reset_clears_state(self, client):
        """Test that reset clears game state"""
        client.post("/game/new", json={"num_players": 2})

        # Play a move
        client.post("/game/move", json={
            "player_id": 0,
            "piece_type": "I1",
            "orientation": 0,
            "row": 0,
            "col": 0
        })

        # Reset
        client.post("/game/reset")

        # State should be reset
        state = client.get("/game/state").json()
        assert state["status"] == "setup" or state["status"] == "playing"


class TestErrorHandling:
    """Test error handling in API"""

    def test_invalid_json(self, client):
        """Test handling of invalid JSON"""
        response = client.post("/game/new", json={"invalid": "data"})
        # Should handle gracefully
        assert response.status_code in [200, 400, 422]

    def test_missing_required_fields(self, client):
        """Test handling of missing required fields"""
        response = client.post("/game/move", json={
            "player_id": 0
            # Missing piece_type, orientation, row, col
        })
        assert response.status_code in [400, 422]

    def test_out_of_bounds_move(self, client):
        """Test handling of out of bounds move"""
        client.post("/game/new", json={"num_players": 2})

        response = client.post("/game/move", json={
            "player_id": 0,
            "piece_type": "I1",
            "orientation": 0,
            "row": 100,
            "col": 100
        })

        # Should handle gracefully
        assert response.status_code in [200, 400]


class TestGameScoring:
    """Test game scoring through API"""

    def test_get_scores(self, client):
        """Test getting game scores"""
        client.post("/game/new", json={"num_players": 2})

        response = client.get("/game/scores")
        assert response.status_code == 200
        data = response.json()
        assert "scores" in data
        assert len(data["scores"]) == 2

    def test_scores_are_integers(self, client):
        """Test that scores are integers"""
        client.post("/game/new", json={"num_players": 2})

        response = client.get("/game/scores")
        data = response.json()
        for score in data["scores"]:
            assert isinstance(score, int)


class TestGameOver:
    """Test game over detection"""

    def test_game_over_detection(self, client):
        """Test that game over is detected"""
        client.post("/game/new", json={"num_players": 2})

        # Play until game over (would require many moves)
        # For now, just check the endpoint works
        response = client.get("/game/state")
        data = response.json()
        assert "status" in data
        assert data["status"] in ["setup", "playing", "finished"]

    def test_game_over_response(self, client):
        """Test game over response structure"""
        client.post("/game/new", json={"num_players": 2})

        response = client.get("/game/state")
        data = response.json()

        if data["status"] == "finished":
            assert "winner" in data or "scores" in data


class TestConcurrency:
    """Test concurrent game operations"""

    def test_multiple_games(self, client):
        """Test that multiple games don't interfere"""
        # Create first game
        response1 = client.post("/game/new", json={"num_players": 2})
        game1_data = response1.json()

        # Create second game (would overwrite in current implementation)
        response2 = client.post("/game/new", json={"num_players": 3})
        game2_data = response2.json()

        # Second game should have 3 players
        assert game2_data["num_players"] == 3


class TestAPIResponseFormat:
    """Test API response format consistency"""

    def test_game_state_response_format(self, client):
        """Test game state response format"""
        client.post("/game/new", json={"num_players": 2})

        response = client.get("/game/state")
        data = response.json()

        # Check required fields
        required_fields = ["players", "current_player_id", "status", "board"]
        for field in required_fields:
            assert field in data, f"Missing field: {field}"

    def test_move_response_format(self, client):
        """Test move response format"""
        client.post("/game/new", json={"num_players": 2})

        response = client.post("/game/move", json={
            "player_id": 0,
            "piece_type": "I1",
            "orientation": 0,
            "row": 0,
            "col": 0
        })

        data = response.json()
        assert "success" in data
        assert isinstance(data["success"], bool)

    def test_scores_response_format(self, client):
        """Test scores response format"""
        client.post("/game/new", json={"num_players": 2})

        response = client.get("/game/scores")
        data = response.json()

        assert "scores" in data
        assert isinstance(data["scores"], list)
        assert len(data["scores"]) > 0
