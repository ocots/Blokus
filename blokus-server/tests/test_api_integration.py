"""Test the updated API with new Player architecture."""

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../blokus-engine/src")))

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_create_game_default():
    """Test creating a game with default players."""
    response = client.post("/game/new", json={"num_players": 4})
    
    assert response.status_code == 200
    data = response.json()
    
    # Check basic game state
    assert len(data["players"]) == 4
    assert data["current_player_id"] == 0
    assert data["status"] == "in_progress"
    
    # Check new player fields
    player = data["players"][0]
    assert "name" in player
    assert "color" in player
    assert "type" in player
    assert "status" in player
    assert "display_name" in player
    assert player["type"] == "human"
    assert player["pieces_count"] == 21
    assert player["squares_remaining"] == 89


def test_create_game_with_player_configs():
    """Test creating a game with custom player configurations."""
    request_data = {
        "num_players": 4,
        "players": [
            {"name": "Alice", "type": "human"},
            {"name": "Bot", "type": "ai", "persona": "random"},
            {"name": "Bob", "type": "human"},
            {"name": "BotAggressive", "type": "ai", "persona": "aggressive"}
        ],
        "start_player": 1
    }
    
    response = client.post("/game/new", json=request_data)
    
    assert response.status_code == 200
    data = response.json()
    
    # Check players
    assert len(data["players"]) == 4
    assert data["players"][0]["name"] == "Alice"
    assert data["players"][0]["type"] == "human"
    
    assert data["players"][1]["name"] == "Bot"
    assert data["players"][1]["type"] == "ai"
    assert data["players"][1]["persona"] == "random"
    
    # Check starting player
    assert data["current_player_id"] == 1
    assert data["players"][1]["status"] == "playing"


def test_get_game_state():
    """Test getting game state."""
    # Create a game first
    client.post("/game/new", json={"num_players": 2})
    
    # Get state
    response = client.get("/game/state")
    
    assert response.status_code == 200
    data = response.json()
    
    assert len(data["players"]) == 2
    assert "board" in data
    assert "current_player_id" in data


def test_player_state_includes_all_fields():
    """Test that player state includes all new fields."""
    response = client.post("/game/new", json={"num_players": 4})
    data = response.json()
    
    player = data["players"][0]
    
    # Check all required fields
    required_fields = [
        "id", "name", "color", "type", "pieces_remaining",
        "pieces_count", "squares_remaining", "score", 
        "has_passed", "status", "display_name"
    ]
    
    for field in required_fields:
        assert field in player, f"Missing field: {field}"


if __name__ == "__main__":
    print("Running API tests...")
    test_create_game_default()
    print("✓ test_create_game_default passed")
    
    test_create_game_with_player_configs()
    print("✓ test_create_game_with_player_configs passed")
    
    test_get_game_state()
    print("✓ test_get_game_state passed")
    
    test_player_state_includes_all_fields()
    print("✓ test_player_state_includes_all_fields passed")
    
    print("\n✅ All API tests passed!")
