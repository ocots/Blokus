
import pytest
from blokus.game_manager_factory import GameManagerFactory
from blokus.game import Game
from blokus.board import BOARD_SIZE

def test_standard_2p_creation():
    """
    Test creation of Standard 2-Player game (4 colors handled by 2 players).
    """
    # Config for 2 humans
    player_configs = [
        {"id": 0, "name": "Alice", "type": "human"}, # P1
        {"id": 1, "name": "Bob", "type": "human"}    # P2
    ]
    
    gm = GameManagerFactory.create_standard_2p_game(player_configs)
    
    # Must have 4 players
    assert len(gm.players) == 4
    
    # Check mapping
    # 0 (Blue) -> Alice
    assert gm.players[0].name == "Alice (Bleu)"
    assert gm.players[0].type.value == "human"
    
    # 1 (Green) -> Bob
    assert gm.players[1].name == "Bob (Vert)"
    
    # 2 (Yellow) -> Alice
    assert gm.players[2].name == "Alice (Jaune)"
    
    # 3 (Red) -> Bob
    assert gm.players[3].name == "Bob (Rouge)"

def test_standard_2p_game_integration():
    """
    Test game initialization with standard 2p configs.
    """
    player_configs = [
        {"id": 0, "name": "Alice", "type": "human"},
        {"id": 1, "name": "Bob", "type": "human"}
    ]
    
    gm = GameManagerFactory.create_standard_2p_game(player_configs)
    game = Game(game_manager=gm)
    
    assert game.board.size == 20
    assert len(game.players) == 4
    assert game.current_player_idx == 0 # start player default
    
    # Simulate turns (0 -> 1 -> 2 -> 3 -> 0)
    assert game.players[game.current_player_idx].name == "Alice (Bleu)"
    game.pass_turn()
    assert game.players[game.current_player_idx].name == "Bob (Vert)"
    game.pass_turn()
    assert game.players[game.current_player_idx].name == "Alice (Jaune)"
    game.pass_turn()
    assert game.players[game.current_player_idx].name == "Bob (Rouge)"
    game.pass_turn()
    # After 4 passes, game should be finished
    from blokus.game import GameStatus
    assert game.status == GameStatus.FINISHED

def test_standard_2p_invalid_config():
    """
    Test error raising if wrong config count.
    """
    with pytest.raises(ValueError):
        GameManagerFactory.create_standard_2p_game([{"id": 0}])
