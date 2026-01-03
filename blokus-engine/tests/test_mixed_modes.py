
import pytest
from blokus.game_manager_factory import GameManagerFactory
from blokus.game import Game
from blokus.player_types import PlayerType
from blokus.board import Board

class TestMixedModes:
    """
    Integration tests for mixed Human/AI games across different modes.
    Ensures turn rotation and player configuration works as expected.
    """

    def test_std_4p_mixed(self):
        """Test Standard 4P: 1 Human, 3 AI."""
        player_configs = [
            {"id": 0, "name": "Human", "type": "human"},
            {"id": 1, "name": "AI 1", "type": "ai", "persona": "random"},
            {"id": 2, "name": "AI 2", "type": "ai", "persona": "random"},
            {"id": 3, "name": "AI 3", "type": "ai", "persona": "random"}
        ]
        
        gm = GameManagerFactory.create_from_config(player_configs)
        game = Game(game_manager=gm)
        
        assert len(game.players) == 4
        assert game.players[0].type == PlayerType.HUMAN
        assert game.players[1].type == PlayerType.AI
        assert game.players[2].type == PlayerType.AI
        assert game.players[3].type == PlayerType.AI
        
        # Verify turn rotation matches types
        assert game.current_player.type == PlayerType.HUMAN
        game.pass_turn()
        assert game.current_player.type == PlayerType.AI
        game.pass_turn()
        assert game.current_player.type == PlayerType.AI

    def test_duo_mixed(self):
        """Test Duo Mode (14x14): 1 Human, 1 AI."""
        player_configs = [
            {"id": 0, "name": "Human", "type": "human"},
            {"id": 1, "name": "AI", "type": "ai", "persona": "random"}
        ]
        
        # Simulate logic from main.py for Duo mode (Board size 14)
        board = Board(size=14)
        gm = GameManagerFactory.create_from_config(player_configs)
        game = Game(game_manager=gm, board=board)
        
        assert game.board.size == 14
        assert len(game.players) == 2
        
        # Turn 1: Human
        assert game.current_player.name == "Human"
        assert game.current_player.type == PlayerType.HUMAN
        
        game.pass_turn()
        
        # Turn 2: AI
        # AI name is generated based on persona
        assert "Bot" in game.current_player.name
        assert game.current_player.type == PlayerType.AI
        
        game.pass_turn()
        
        # Turn 3: Game Over (Both passed)
        from blokus.game import GameStatus
        assert game.status == GameStatus.FINISHED

    def test_std_2p_mixed_split_control(self):
        """
        Test Standard 2P Mode (20x20): 1 Human vs 1 AI.
        Each should control 2 colors.
        Order: Human(Blue) -> AI(Green) -> Human(Yellow) -> AI(Red).
        """
        player_configs = [
            {"id": 0, "name": "HumanMaster", "type": "human"}, # P1
            {"id": 1, "name": "AIMaster", "type": "ai", "persona": "random"}    # P2
        ]
        
        # Use formatting factory for Standard 2P
        gm = GameManagerFactory.create_standard_2p_game(player_configs)
        # Note: create_standard_2p_game calls create_from_config internally, which calls PlayerFactory
        game = Game(game_manager=gm) # Default board is 20
        
        assert game.board.size == 20
        assert len(game.players) == 4 # 4 Logical players
        
        # Verify Identity and Types
        # 0: Blue (Human)
        p0 = game.players[0]
        assert "HumanMaster" in p0.name
        assert "(Bleu)" in p0.name or p0.color == "#3b82f6"
        assert p0.type == PlayerType.HUMAN
        
        # 1: Green (AI)
        p1 = game.players[1]
        # AI Name is generated -> "Bot Aléatoire"
        assert "Bot" in p1.name
        assert p1.type == PlayerType.AI
        
        # 2: Yellow (Human)
        p2 = game.players[2]
        assert "HumanMaster" in p2.name
        assert "(Jaune)" in p2.name or p2.color == "#eab308"
        assert p2.type == PlayerType.HUMAN
        
        # 3: Red (AI)
        p3 = game.players[3]
        assert "Bot" in p3.name
        assert p3.type == PlayerType.AI
        
        # Verify Turn Sequence
        # Turn 1: Blue (Human)
        assert game.current_player_idx == 0
        assert game.current_player.type == PlayerType.HUMAN
        game.pass_turn()
        
        # Turn 2: Green (AI)
        assert game.current_player_idx == 1
        assert game.current_player.type == PlayerType.AI
        game.pass_turn()
        
        # Turn 3: Yellow (Human)
        assert game.current_player_idx == 2
        assert game.current_player.type == PlayerType.HUMAN
        game.pass_turn()
        
        # Turn 4: Red (AI)
        assert game.current_player_idx == 3
        assert game.current_player.type == PlayerType.AI
        game.pass_turn()
        
        # Turn 5: Game Over (All passed)
        from blokus.game import GameStatus
        assert game.status == GameStatus.FINISHED

    def test_std_2p_human_vs_ai_types(self):
        """
        Verify that in Standard 2P (1 Human vs 1 AI), the backend correctly
        assigns the AI type to both colors controlled by the AI.
        P1 (Human): Blue(0), Yellow(2)
        P2 (AI): Green(1), Red(3)
        """
        player_configs = [
            {"id": 0, "name": "Human", "type": "human"},
            {"id": 1, "name": "Bot", "type": "ai", "persona": "random"}
        ]
        
        gm = GameManagerFactory.create_standard_2p_game(player_configs)
        
        # Check P0 (Blue) -> Human
        p0 = gm.players[0]
        assert p0.type == PlayerType.HUMAN
        
        # Check P1 (Green) -> AI
        p1 = gm.players[1]
        assert p1.type == PlayerType.AI
        assert p1.persona == "random"
        
        # Check P2 (Yellow) -> Human
        p2 = gm.players[2]
        assert p2.type == PlayerType.HUMAN
        
        # Check P3 (Red) -> AI (CRITICAL CHECK)
        p3 = gm.players[3]
        assert p3.type == PlayerType.AI
        assert p3.persona == "random"
