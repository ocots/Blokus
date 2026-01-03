
import pytest
from blokus.game_manager_factory import GameManagerFactory
from blokus.game import Game, GameStatus

def test_4_random_ai_game_loop():
    """
    Simulate a game with 4 Random AI players to verify everyone gets to play.
    """
    player_configs = [
        {"id": 0, "name": "AI 1", "type": "ai", "persona": "random"},
        {"id": 1, "name": "AI 2", "type": "ai", "persona": "random"},
        {"id": 2, "name": "AI 3", "type": "ai", "persona": "random"},
        {"id": 3, "name": "AI 4", "type": "ai", "persona": "random"}
    ]
    
    gm = GameManagerFactory.create_from_config(player_configs)
    
    # Ensure 4 players
    assert len(gm.players) == 4
    for p in gm.players:
        assert p.type.value == "ai"
        
    game = Game(game_manager=gm)
    
    # Track moves per player
    moves_count = {0: 0, 1: 0, 2: 0, 3: 0}
    
    # Simulate loops until game over or max turns
    max_turns = 100
    turns = 0
    
    while game.status == GameStatus.IN_PROGRESS and turns < max_turns:
        current_pid = game.current_player_idx
        
        # Verify valid player index
        assert 0 <= current_pid <= 3
        
        # Get AI Move
        # Note: In real backend, this is handled by API calling game.play_move
        # Here we manually invoke the AI logic if available, or just random move via game logic
        
        # For this test, we can use the player's get_move method if it exists, 
        # or simulate a move. Since 'random' persona might not be fully wired in this unit test context 
        # without the AI model registry, we check if we can simply get all legal moves and pick one.
        
        legal_moves = game.get_valid_moves(current_pid)
        
        if legal_moves:
            # Play first available move
            move = legal_moves[0]
            game.play_move(move)
            moves_count[current_pid] += 1
        else:
            game.pass_turn()
            
        turns += 1
        
    print(f"Moves per player: {moves_count}")
    
    # Assert everyone played at least once (unless blocked immediately, which is impossible at start)
    assert moves_count[0] > 0
    assert moves_count[1] > 0
    assert moves_count[2] > 0
    assert moves_count[3] > 0
