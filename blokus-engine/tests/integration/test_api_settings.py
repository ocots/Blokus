import pytest
from fastapi.testclient import TestClient
import sys
import os

# Adjust path to find server code
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../blokus-server")))

from main import app

client = TestClient(app)

def test_create_game_with_settings():
    """
    Test that the create_game endpoint accepts the 'settings' field payload
    and does not crash.
    """
    payload = {
        "num_players": 2,
        "players": [
            {"name": "Human", "type": "human"},
            {"name": "AI", "type": "ai", "persona": "random"}
        ],
        "settings": {
            "fastAIMode": True,
            "colorblindMode": False
        }
    }

    response = client.post("/game/new", json=payload)
    
    # Assert successful creation
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "in_progress"
    
    # Note: Currently the API response (GameState) does NOT include settings back.
    # So we just verify it accepted the payload without 422 Validation Error.

def test_create_game_without_settings():
    """
    Test that checking 'settings' is optional.
    """
    payload = {
        "num_players": 2
    }
    response = client.post("/game/new", json=payload)
    assert response.status_code == 200
