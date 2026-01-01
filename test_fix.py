#!/usr/bin/env python3
"""
Test script to verify the start player fix.
Tests that when we specify start_player=2 (yellow), the game actually starts with player 2.
"""

import requests
import json

def test_start_player_fix():
    """Test that start_player is correctly handled by the API."""
    
    # Test data
    base_url = "http://localhost:8000"
    
    # Test 1: Default game should start with player 0 (blue)
    print("🧪 Test 1: Default game (should start with player 0)")
    response = requests.post(f"{base_url}/game/new", json={"num_players": 4})
    if response.status_code == 200:
        state = response.json()
        current_player = state["current_player_id"]
        print(f"   ✅ Current player: {current_player} (expected: 0)")
        assert current_player == 0, f"Expected player 0, got {current_player}"
    else:
        print(f"   ❌ Failed: {response.status_code}")
        return False
    
    # Test 2: Game starting with player 1 (green)
    print("\n🧪 Test 2: Start with player 1 (green)")
    response = requests.post(f"{base_url}/game/new", json={"num_players": 4, "start_player": 1})
    if response.status_code == 200:
        state = response.json()
        current_player = state["current_player_id"]
        print(f"   ✅ Current player: {current_player} (expected: 1)")
        assert current_player == 1, f"Expected player 1, got {current_player}"
    else:
        print(f"   ❌ Failed: {response.status_code}")
        return False
    
    # Test 3: Game starting with player 2 (yellow) - this was the problematic case
    print("\n🧪 Test 3: Start with player 2 (yellow)")
    response = requests.post(f"{base_url}/game/new", json={"num_players": 4, "start_player": 2})
    if response.status_code == 200:
        state = response.json()
        current_player = state["current_player_id"]
        print(f"   ✅ Current player: {current_player} (expected: 2)")
        assert current_player == 2, f"Expected player 2, got {current_player}"
    else:
        print(f"   ❌ Failed: {response.status_code}")
        return False
    
    # Test 4: Game starting with player 3 (red)
    print("\n🧪 Test 4: Start with player 3 (red)")
    response = requests.post(f"{base_url}/game/new", json={"num_players": 4, "start_player": 3})
    if response.status_code == 200:
        state = response.json()
        current_player = state["current_player_id"]
        print(f"   ✅ Current player: {current_player} (expected: 3)")
        assert current_player == 3, f"Expected player 3, got {current_player}"
    else:
        print(f"   ❌ Failed: {response.status_code}")
        return False
    
    # Test 5: Invalid start player should return error
    print("\n🧪 Test 5: Invalid start player (should fail)")
    response = requests.post(f"{base_url}/game/new", json={"num_players": 4, "start_player": 5})
    if response.status_code == 422:
        print(f"   ✅ Correctly rejected invalid start player: {response.status_code}")
    else:
        print(f"   ❌ Should have failed with 422, got: {response.status_code}")
        return False
    
    print("\n🎉 All tests passed! The start player bug is fixed.")
    return True

if __name__ == "__main__":
    try:
        success = test_start_player_fix()
        if success:
            print("\n✅ Verification complete - the fix works correctly!")
        else:
            print("\n❌ Some tests failed - the fix needs more work.")
    except Exception as e:
        print(f"\n❌ Error running tests: {e}")
        print("Make sure the API server is running on http://localhost:8000")
